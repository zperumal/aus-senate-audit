# -*- coding: utf-8 -*-

""" Encapsulates Utilities for Recording Intermediate Audit Information. """

from json import load
from json import dumps
from os import makedirs
from os.path import exists

from constants import AGGREGATE_BALLOTS_FILE_NAME
from constants import AUDIT_DIR_NAME
from constants import AUDIT_INFO_FILE_NAME
from constants import COLUMN_HEADERS
from constants import MATCH_HEADERS
from constants import ROUND_DIR_NAME
from constants import SELECTED_BALLOTS_FILE_NAME
from constants import AUDIT_STAGE_KEY
from constants import SAMPLE_SIZE_KEY


class AuditInfo(object):
    """ Encapsulates utilities for recording intermediate audit information.

    :ivar str state: The abbreviated name of the state to run the audit for.
    """
    def __init__(self, state):
        """ Initializes an :class:`AuditResults` object.

        :param str state: The abbreviated name of the state to run the audit for.
        """
        self._state = state
        if not exists(self.get_audit_dir_name()):
            makedirs('{}/{}'.format(self.get_audit_dir_name(), ROUND_DIR_NAME))
            self.set_audit_info(0, 0)
            self.initialize_aggregate_ballots_csv()

    def get_audit_dir_name(self):
        """ Returns the audit directory name for the given state.

        :returns: The audit directory name for the given state.
        :rtype: str
        """
        return AUDIT_DIR_NAME.format(self._state)

    def get_audit_results_file_path(self, file_name):
        """ Returns the file path for the given audit results file name.

        :param str file_name: The name of the file to return the full file path for.

        :returns: The file path for the given audit results file name.
        :rtype: str
        """
        return '{}/{}'.format(
            self.get_audit_dir_name(),
            file_name,
        )

    def initialize_aggregate_ballots_csv(self):
        """ Initializes the CSV file holding the aggregate ballots for the current sample. """
        with open(self.get_audit_results_file_path(AGGREGATE_BALLOTS_FILE_NAME), 'w') as f:
            f.write('{}\n'.format(','.join(COLUMN_HEADERS)))
            f.write('{}\n'.format(
                ','.join(['------------', '---------------------', '---------------------', '-------', '-------', '-----------'])
            ))

    def add_new_ballots_to_aggregate(self):
        """ """
        with open(self.get_audit_results_file_path(AGGREGATE_BALLOTS_FILE_NAME), 'a') as f:
            new_ballots = [line for line in open(SELECTED_BALLOTS_FILE_NAME, 'r')][1:]
            for new_ballot in new_ballots:
                f.write(new_ballot)

    def set_audit_info(self, audit_stage, sample_size):
        """ Sets informatinon about the audit recored thus far.

        :param int audit_stage: The new stage of the audit.
        :param int sample_size: The sample size of the audit.
        """
        open(self.get_audit_results_file_path(AUDIT_INFO_FILE_NAME), 'w').write(
            dumps({AUDIT_STAGE_KEY: audit_stage, SAMPLE_SIZE_KEY: sample_size})
        )

    def get_audit_info(self):
        """ Returns information about the audit recorded thus far.

        Example of the audit information.

        .. code-block:: python

            {
                'audit_stage': 1,
                'sample_size': 1200,

            }

        :returns: A dictionary containing information about the audit recorded
            thus far.
        :rtype: dict
        """
        return load(open(self.get_audit_results_file_path(AUDIT_INFO_FILE_NAME), 'r'))

    def write_audit_round_file(self, audit_stage, sample):
        """ """
        with open(self.get_audit_results_file_path(
            '{}/round_{}.csv'.format(ROUND_DIR_NAME, audit_stage)),
             'w',
        ) as f:
            f.write('{}\n'.format(','.join(COLUMN_HEADERS + MATCH_HEADERS)))
            for ballot in sample:
                f.write('{}\n'.format(ballot))

    def write_selected_ballots_file(self, sample, quick):
        """ """
        with open(SELECTED_BALLOTS_FILE_NAME, 'w') as f:
            f.write('{}\n'.format(','.join(COLUMN_HEADERS)))
            for ballot in sample:
                if quick:
                    f.write('{}\n'.format(ballot))
                else:
                    f.write('{}\n'.format(ballot.split('"')[0]))

    def set_current_audit_round_file(self, ballots):
        """ """
        self.write_audit_round_file(self.get_audit_info()[AUDIT_STAGE_KEY], ballots)

    def get_current_audit_round_file_name(self):
        """ """
        return self.get_audit_results_file_path('{}/round_{}.csv'.format(
            ROUND_DIR_NAME,
            self.get_audit_info()[AUDIT_STAGE_KEY]),
        )
