# -*- coding: utf-8 -*-

""" Wraps the Sampling Algorithm Used for the Australian Senate Audit. """

from os import listdir
from os import mkdir
from os.path import exists

from sampler import generate_outputs


class SamplerWrapper(object):
    """ Encapsulates logic for sampling from the formal preferences CSV. """

    ROUNDS_DIR = 'rounds'
    SAMPLE_SIZE_FN = '{}/sample_size'.format(ROUNDS_DIR)
    AUDIT_STAGE_FN = '{}/audit_stage'.format(ROUNDS_DIR)
    AGGREGATE_FN = '{}/aggregate.csv'.format(ROUNDS_DIR)
    SELECTED_BALLOTS_FN = 'selected_ballots.csv'
    AUDIT_ROUND_FN = '{}/ballots_added_in_stage_{}.csv'
    NUM_HEADER_LINES = 2

    COLUMN_HEADERS = [
        'ElectorateNm',
        'VoteCollectionPointNm',
        'VoteCollectionPointId',
        'BatchNo',
        'PaperNo',
        'Preferences',
    ]

    EXTRA_HEADERS = [
        'Match',
        'PreferencesAfterAudit',
    ]

    def __init__(self, all_formal_preferences_file, sample_increment_size, seed):
        """ Initializes a :class:`SamplerWrapper` object.

        :param str all_formal_preferences_file: Path to a CSV file containing
            all formal preferences for a given state senate election.
        :param int sample_increment_size: The number of ballots to add to the
            growing sample of audited ballots.
        :param int seed: The starting value for the random number generator.
        """
        if not exists(SamplerWrapper.ROUNDS_DIR):
            mkdir(SamplerWrapper.ROUNDS_DIR)
            SamplerWrapper.set_audit_stage(0)
            SamplerWrapper.set_sample_size(0)
            open(SamplerWrapper.AGGREGATE_FN, 'w').write(','.join(SamplerWrapper.COLUMN_HEADERS) + '\n')

        audit_stage = SamplerWrapper.get_audit_stage()
        sample_size = SamplerWrapper.get_sample_size()
        ballots = [
            line.rstrip() for line in open(all_formal_preferences_file, 'r')
        ][SamplerWrapper.NUM_HEADER_LINES:]

        _, ballot_indices = generate_outputs(
            sample_size + sample_increment_size,
            False,
            SamplerWrapper.NUM_HEADER_LINES,
            len(ballots) - 1,
            str(seed),
            sample_size,
        )

        sample = [ballots[i] for i in ballot_indices]
        SamplerWrapper.write_sample_to_csvs(sample, audit_stage + 1)
        SamplerWrapper.set_audit_stage(audit_stage + 1)
        SamplerWrapper.set_sample_size(sample_size + sample_increment_size)

    @staticmethod
    def set_sample_size(sample_size):
        """ Sets the current sample size to the given sample size.

        :param int sample_size: The size of the current sample.
        """
        open(SamplerWrapper.SAMPLE_SIZE_FN, 'w').write(str(sample_size))

    @staticmethod
    def get_sample_size():
        """ Returns the current sample size.

        :returns: The current sample size.
        :rtype: int
        """
        return int(open(SamplerWrapper.SAMPLE_SIZE_FN, 'r').read())

    @staticmethod
    def set_audit_stage(audit_stage):
        """ Sets the current audit stage to the given audit stage.

        :param int audit_stage: The current audit stage.
        """
        open(SamplerWrapper.AUDIT_STAGE_FN, 'w').write(str(audit_stage))

    @staticmethod
    def get_audit_stage():
        """ Returns the current audit stage.

        :returns: The current audit stage.
        :rtype: int
        """
        return int(open(SamplerWrapper.AUDIT_STAGE_FN, 'r').read())

    @staticmethod
    def write_sample_to_csvs(sample, audit_stage):
        """ Writes the given sample to CSVs.

        One of the CSVs produced does not contain the original formal 
        preferences as not to bias the auditor by the electronic 
        interpretation of the paper ballot.

        :param list sample: A list of ballots to write to a CSV.
        """
        with open(SamplerWrapper.AUDIT_ROUND_FN.format(
            SamplerWrapper.ROUNDS_DIR,
            audit_stage,
        ), 'w') as f:
            f.write(','.join(
                SamplerWrapper.COLUMN_HEADERS + SamplerWrapper.EXTRA_HEADERS
            ) + '\n')
            for ballot in sample:
                f.write(ballot + '\n')
        with open(SamplerWrapper.SELECTED_BALLOTS_FN, 'w') as f:
            f.write(','.join(SamplerWrapper.COLUMN_HEADERS) + '\n')
            for ballot in sample:
                f.write(ballot.split('"')[0] + '\n')
