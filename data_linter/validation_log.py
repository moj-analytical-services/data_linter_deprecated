# -*- coding: utf-8 -*-


class ValidationLog:
    """
    Stores the log produced by the linter

    Responsible for the presentation of the log
    - outputting summary markdown
    - outputting tabular summary
    - outputting verbose log

    """

    def __init__(self, linter):

        self.log = {}

        # Create entries up front - user will want to know if a column has no entries as it would
        # indicate an error
        for c in linter.meta_cols:
            self._create_logentries_for_column(c["name"])

    def _create_logentries_for_column(self, colname):
        if colname not in self.log:
            self.log[colname] = ColumnLogEntries(colname)

    def get_log_entries_for_column(self, colname):
        return self.log[colname]


class LogEntry:
    """
    A single log result i.e. the output of checks of a given validation function (as described
    by check_desc) on a given column
    """

    def __init__(self, col_name, validation_description):
        self._success = None
        self._result = None
        self._exception_info = None
        self.col_name = col_name
        self.validation_description = validation_description

    @property
    def result(self):
        return self._result

    @property
    def success(self):
        return self._success

    @property
    def exception_info(self):
        return self._exception_info

    def set_result_key(self, key, value):
        if not self._result:
            self._result = {}
        self._result[key] = value

    def set_success_status(self, success):
        self._success = success

    def set_exception_info_key(self, key, value):
        if not self._exception_info:
            self._exception_info = {}

        # TODO check key is one of raised_exception,exception_message,exception_traceback
        self._exception_info[key] = value

    def _status(self):
        if self._success is None:
            return "Status not yet determined"

        if self._success:
            return "Success"
        else:
            return "Failure"

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

    def get_or_create_logentry(self, validation_description):
        if validation_description not in self.entries:
            self.entries[validation_description] = LogEntry(
                self.col_name, validation_description)
        return self.entries[validation_description]

    def create_logentry_from_ge_result(self, validation_description, ge_output):
        le = self.get_or_create_logentry(validation_description)
        le.set_success_status(ge_output["success"])

        for key, value in ge_output["result"].items():
            le.set_result_key(key, value)

        if "exception_info" in ge_output:
            for key, value in ge_output["exception_info"].items():
                le.set_exception_info_key(key, value)



    def __repr__(self):
        repr = ""
        for key, value in self.entries.items():
            repr += value.__repr__() +"\n"

        return repr
