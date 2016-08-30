# -*- coding: utf-8 -*-

""" Validates Paper Preferences Against Electronic Preferences. """

from constants import AUDIT_STAGE_KEY
from constants import SELECTED_BALLOTS_FILE_NAME


class AuditValidator(object):
    """ Validates paper preferences against electronic preferences.

    :ivar :class:`AuditInfo` audit_info: An object for interfacing with
        audit information recorded thus far.
    """

    def __init__(self, audit_info):
        """ Initializes a :class:`AuditValidator` object.

        :param :class:`AuditInfo` audit_info: An object for interfacing
            with audit information recorded thus far.
        """
        self._audit_info = audit_info

    @staticmethod
    def get_paper_preference_readings():
        """ """
        with open(SELECTED_BALLOTS_FILE_NAME, 'r') as f:
            f.readline()  # Skip the header.
            paper_preferences = []
            for line in f:
                paper_preferences.append(line.rstrip().split('"')[1])
        return paper_preferences

    def get_electronic_ballots(self):
        """ """
        audit_round_file_name = self._audit_info.get_current_audit_round_file_name()
        with open(audit_round_file_name, 'r') as f:
            f.readline()  # Skip the header.
            ballots = [line.rstrip() for line in f]
        return ballots

    def compare(self):
        """ """
        paper_preferences = self.get_paper_preference_readings()
        electronic_ballots = self.get_electronic_ballots()
        match_records = []
        for i in range(len(electronic_ballots)):
            electronic_preferences = electronic_ballots[i].split('"')[1]
            match = int(electronic_preferences == paper_preferences[i])
            match_records.append(electronic_ballots[i] + ',{},"{}"\n'.format(
                match,
                paper_preferences[i],
            ))
        self._audit_info.set_current_audit_round_file(match_records)
        self._audit_info.add_new_ballots_to_aggregate()
