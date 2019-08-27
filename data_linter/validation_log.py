# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from tabulate import tabulate
import json

from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader(
    'data_linter', 'templates'), trim_blocks=True, lstrip_blocks=True)

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

        return df.pipe(tabulate, headers='keys', tablefmt='pipe', showindex=False)

    def as_detailed_markdown(self):

        tdata = self.linter.df_ge.head(2).copy()

        # This is only needed beca
        try:
            tdata = tdata.fillna("")
        except TypeError:
            # the above line fails on an Int64 (nullable) column see https://github.com/pandas-dev/pandas/issues/25288
            tdata = tdata.fillna(np.nan)

        sample = tabulate(tdata, headers="keys", showindex=False, tablefmt='pipe')

        metadf = pd.DataFrame({c["name"]:[c["type"],]for c in self.linter.meta_data["columns"]})
        metadfmd = tabulate(metadf, headers="keys",
                            showindex=False, tablefmt='pipe')

        mds = [v.as_markdown() for v in self._vlog.values()]
        jinja_data = {
            "logentries_md_list": mds,
            "tabular_data_sample": sample,
            "meta_df": metadfmd,
            "success": self.success(),
            "dataset_name": self.linter.meta_data.get("name", None)
        }
        template = jinja_env.get_template('validationlog_detailed.j2')
        return template.render(jinja_data)

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

        self.meta_lookup = {v["name"]: v for v in linter.meta_data["columns"]}

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
        jinja_data = {
            "logentry_md_list":mds,
            "col_name": self.col_name,
            "metadata": json.dumps(self.meta_lookup[self.col_name])
        }
        template = jinja_env.get_template('logentries_detailed.j2')
        return template.render(jinja_data)



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

    def as_markdown(self, num_table_rows = 2, num_unexpected_values = 8):

        jinja_data = {
            "validation_description": self.validation_description,
            "status_emoji": self._status_emoji(),
            "status_string": self._status_string().lower(),
            "table_exists": False,
            "unexpected_list_exists": False,
            "success": self.success
        }

        if self.validation_description not in ["check_data_type", "check_column_exists_and_order"]:
            num_errors = len(self.result["unexpected_list"])

            if num_errors > 0:
                jinja_data["table_exists"] = True
                df = self.get_failure_rows(num_table_rows)
                jinja_data["table"] = tabulate(df, headers="keys", tablefmt="pipe", showindex=False)

            if num_errors > num_table_rows:
                jinja_data["unexpected_list_exists"] = True

                start = num_table_rows
                end = num_table_rows + num_unexpected_values
                unexpected_list = self.result["unexpected_list"][start:end]
                unexpected_list = [v.__repr__() for v in unexpected_list] #want e.g. 'a' to be rendered a such, not a
                unexpected_index = self.result["unexpected_index_list"][start:end]
                tuples = zip(unexpected_index, unexpected_list)
                unexpected_data = [{"index": v[0], "value":v[1]} for v in tuples]

                jinja_data["unexpected_data"] = unexpected_data


            template = jinja_env.get_template('logentry_detailed.j2')
            return template.render(jinja_data)

        if self.validation_description == "check_column_exists_and_order":

            jinja_data["exists"] = self.result["column_exists"]
            jinja_data["incorrect_order"] = not self.result["order_match"]

            if self.result["actual_pos"] is not None:
                jinja_data["actual_pos"] = self.result["actual_pos"] + 1 # Zero indexed in data
            else:
                jinja_data["actual_pos"] = "No position - col does not exist"
            jinja_data["expected_pos"] = self.result["expected_pos"] + 1 # Zero indexed in data


            template = jinja_env.get_template('logentry_detailed_column_exists_and_order.j2')
            return template.render(jinja_data)

        if self.validation_description == "check_data_type":
            template = jinja_env.get_template(
                'logentry_detailed_data_type.j2')
            return template.render(jinja_data)

        template = jinja_env.get_template('logentry_detailed.j2')
        return template.render(jinja_data)





    def __repr__(self):
        return f"data_linter.validation_log.LogEntry: This log entry checks {self.validation_description} for column {self.col_name}.  Current status: {self._status_string()}"


