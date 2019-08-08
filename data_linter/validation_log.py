# -*- coding: utf-8 -*-

# TODO:
# - Output as dict
# - Output summary table
# - Output as markdown
# - Overall success

from collections import defaultdict

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

        # It makes sense to create entries up front becayse user will want to know
        # if a column has no entries as it would indicate something had gone wrong
        for c in linter.meta_cols:
            self._create_logentries_for_column(c["name"])

    def __getitem__(self, col_name):
        return self._vlog[col_name]

    def _create_logentries_for_column(self, colname):
        if colname not in self._vlog:
            self._vlog[colname] = ColumnLogEntries(colname)

    # Serialisation/presentation functions
    def as_dict(self):
        return {k: v.as_dict() for k,v in self._vlog.items()}

    def as_table_rows(self):
        result = []
        for k,v in self._vlog.items():
            result.extend(v.as_table_rows())
        return result

    # def as_markdown():
        # df.pipe(tabulate, header='keys', tablefmt='pipe')


class LogEntry:
    """
    A single log result i.e. the output of checks of a given validation_description on a given column
    """

    def __init__(self, col_name, validation_description):
        self.success = None
        self._result = None
        self._exception_info = None
        self.col_name = col_name
        self.validation_description = validation_description

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

    def _status(self):
        if self.success is None:
            return "Status not yet determined"

        if self.success:
            return "Success"
        else:
            return "Failure"

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


    def __repr__(self):
        return f"data_linter.validation_log.LogEntry: This log entry checks {self.validation_description} for column {self.col_name}.  Current status: {self._status()}"


class ColumnLogEntries:
    """
    A collection of LogEntry objects, one for each function

    ColumnLogEntries knowns column name
    """

    def __init__(self, col_name):
        self.col_name = col_name
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
            le = LogEntry(self.col_name, key)
            self.entries[key] = le
        else:
            le = self.entries[key]
        return le

    # Serialisation/presentation functions
    def as_dict(self):
        return {k:v.as_dict() for k,v in self.entries.items()}

    def as_table_rows(self):
        return [v.as_table_row() for k, v in self.entries.items()]

    def __repr__(self):
        repr = ""
        for key, value in self.entries.items():
            repr += value.__repr__() +"\n"

        return repr
