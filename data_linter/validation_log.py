# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import tabulate

from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('data_linter', 'templates'))

class ValidationLog:
    """
    Stores the log produced by the linter

    Along with LogEntry and LogEntries classes, Responsible for the presentation of the log
    - outputting summary markdown
    - outputting tabular summary
    - outputting verbose log

    """

    def __init__(self, linter):

        self._vlog = {}
        self.df_ge = linter.df_ge
        self.linter = linter

        # It makes sense to create entries up front becayse user will want to know
        # if a column has no entries as it would indicate something had gone wrong
        for c in linter.meta_cols:
            self._create_logentries_for_column(c["name"])

    def __getitem__(self, col_name):
        return self._vlog[col_name]

    def _create_logentries_for_column(self, colname):
        if colname not in self._vlog:
            self._vlog[colname] = ColumnLogEntries(colname, self.linter)

    def success(self):

        success_array = [v.success() for k, v in self._vlog.items()]

        if all(success_array):
            return True

        if False in success_array:
            return False


    # Serialisation/presentation functions
    def as_dict(self):
        return {k: v.as_dict() for k,v in self._vlog.items()}

    def as_table_rows(self):
        result = []
        for k,v in self._vlog.items():
            result.extend(v.as_table_rows())
        return result

    def as_summary_markdown(self):
        df = pd.DataFrame(self.as_table_rows())
        df = df.sort_values(["success", "col_name", "validation_description"])
        df["success"] = np.where(df["success"], "✅", "❌")
        return df.pipe(tabulate.tabulate, headers='keys', tablefmt='pipe')

    def as_detailed_markdown(self):
        ## TODO:  Add here's a few sample rows of data:

        md = """

        """

        ind_results = [v.as_markdown() for v in self._vlog.values()]


        return "".join(ind_results)


    def _repr_markdown_(self):
            return self.as_summary_markdown()


class ColumnLogEntries:
    """
    A collection of LogEntry objects, one for each function

    ColumnLogEntries knowns column name
    """

    def __init__(self, col_name, linter):
        self.col_name = col_name
        self.linter = linter
        self.entries = {}

    def create_logentry_from_ge_result(self, validation_description, ge_output):
        le = self[validation_description]
        le.success = ge_output["success"]

        for key, value in ge_output["result"].items():
            le.set_result_key(key, value)

        if "exception_info" in ge_output:
            for key, value in ge_output["exception_info"].items():
                le.set_exception_info_key(key, value)

    def __getitem__(self, key):
        if key not in self.entries:
            le = LogEntry(self.col_name, key, self.linter)
            self.entries[key] = le
        else:
            le = self.entries[key]
        return le

    # Serialisation/presentation functions
    def as_dict(self):
        return {k: v.as_dict() for k, v in self.entries.items()}

    def as_table_rows(self):
        return [v.as_table_row() for k, v in self.entries.items()]

    def success(self):

        success_array = [v.success for k, v in self.entries.items()]

        if None in success_array:
            raise Exception(
                "Some tests have failed to return a result.  This indicates a bug.")

        if len(success_array) == 0:
            raise Exception(
                f"No tests have yet been run for {self.col_name}.  You probably need to run linter.check_all()")

        if False in success_array:
            return False

        if all(success_array):
            return True

    def as_markdown(self):

        mds = [v.as_markdown() for v in self.entries.values()]
        template = jinja_env.get_template('logentries_detailed.j2')
        return template.render(jinja_data)

        return f"""
---

### Results for column {self.col_name}

{individual_results}
"""

    def __repr__(self):
        repr = ""
        for key, value in self.entries.items():
            repr += value.__repr__() + "\n"

        return repr


class LogEntry:
    """
    A single log result i.e. the output of checks of a given validation_description on a given column
    """

    def __init__(self, col_name, validation_description, linter):
        self.success = None
        self._result = None
        self._exception_info = None
        self.col_name = col_name
        self.validation_description = validation_description
        self.df_ge = linter.df_ge

    @property
    def result(self):
        return self._result

    @property
    def exception_info(self):
        return self._exception_info

    def set_result_key(self, key, value):
        if not self._result:
            self._result = {}
        self._result[key] = value

    def set_exception_info_key(self, key, value):
        if not self._exception_info:
            self._exception_info = {}

        allowed_keys = ["raised_exception", "exception_message", "exception_traceback"]
        if key not in allowed_keys:
            raise ValueError(f"Key must be one of {allowed_keys}")

        self._exception_info[key] = value

    def _status_string(self):
        if self.success is None:
            return "Status not yet determined"

        if self.success:
            return "Success"
        else:
            return "Failure"

    def _status_emoji(self):
        if self.success is None:
            return "🤷"

        if self.success:
            return "✅"
        else:
            return "❌"


    def get_rows(self, n):
        return self.df_ge.head(n).to_dict(orient='records')

    def get_failure_rows(self, n=5):
        if "unexpected_index_list" in self.result:
            indices =  self.result["unexpected_index_list"][:n]
            df = self.df_ge.loc[indices, :].copy()
            df = df.reset_index()
            return df
        else:
             return []


    # Serialisation/presentation functions

    def as_dict(self):
        return {"success": self.success,
                "result": self.result,
                "exception_info": self.exception_info}

    def as_table_row(self):
        return {
            "col_name": self.col_name,
            "validation_description": self.validation_description,
            "success": self.success
        }

    def as_markdown(self, table_rows = 2, unexpected_values = 8):

        unexpected_list = self.result["unexpected_list"][table_rows:table_rows+unexpected_values]
        unexpected_index = self.result["unexpected_index_list"][table_rows:table_rows+unexpected_values]

        unexpected_data = [{"index": v[0], "value":v[1].__repr__()} for v in zip(unexpected_index, unexpected_list)]

        jinja_data = {
            "validation_description": self.validation_description,
            "status_emoji": self._status_emoji(),
            "status_string": self._status_string(),
            "table_exists": len(self.result["unexpected_list"]) > 0,
            "table": tabulate.tabulate(self.get_failure_rows(table_rows), headers="keys", tablefmt="pipe", showindex=False),
            "unexpected_list_exists": len(self.result["unexpected_list"]) > table_rows,
            "unexpected_data": unexpected_data

        }

        template = jinja_env.get_template('logentry_detailed.j2')
        return template.render(jinja_data)



    def __repr__(self):
        return f"data_linter.validation_log.LogEntry: This log entry checks {self.validation_description} for column {self.col_name}.  Current status: {self._status_string()}"


