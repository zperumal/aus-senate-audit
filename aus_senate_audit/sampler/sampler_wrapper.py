# -*- coding: utf-8 -*-

""" Wraps the Sampling Algorithm Used for the Australian Senate Audit. """

from json import load

from constants import AUDIT_STAGE_KEY
from constants import SAMPLE_SIZE_KEY
from sampler.sampler import generate_outputs


class SamplerWrapper(object):
    """ Encapsulates logic for sampling from the formal preferences CSV. """

    NUM_HEADER_LINES = 2

    def __init__(self, seed, config_file_name, state, sample_increment_size, audit_info, quick=False):
        """ Initializes a :class:`SamplerWrapper` object.

        :param int seed: The starting value for the random number generator.
        :param str config_file:_name The name of the configuration file 
            specifiyng details about the senate election contest to audit.
        :param str state: The abbreviation of the state name to run the senate
            election audit for.
        :param int sample_increment_size: The number of ballots to add to the
            growing sample of audited ballots.
        :param :class:`AuditInfo`: An object for interfacing with audit
            information recored thus far.
        """
        audit_info_dict = audit_info.get_audit_info()
        sample_size = audit_info_dict[SAMPLE_SIZE_KEY]
        audit_stage = audit_info_dict[AUDIT_STAGE_KEY]
        ballots = [
            line.rstrip() for line in open(
                SamplerWrapper._get_formal_preferences_from_config(
                    state,
                    config_file_name,
                ),
                'r',
            )
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
        audit_info.set_audit_info(
            audit_stage + 1,
            sample_size + sample_increment_size,
        )
        audit_info.write_audit_round_file(audit_stage + 1, sample)
        audit_info.write_selected_ballots_file(sample, quick=quick)

    @staticmethod
    def _get_formal_preferences_from_config(state, config_file_name):
        """ Returns the path to the formal preferences file.

        :param str state: The abbreviation of the state name to run the senate
            election audit for.
        :param str config_file:_name The name of the configuration file 
            specifiyng details about the senate election contest to audit.

        :returns: The path to the formal preferences file.
        :rtype: str
        """
        with open(config_file_name, 'r') as config_file:
            config = load(config_file)
            for state_config in config['count']:
                if state_config['name'] == state:
                    return state_config['aec-data']['formal-preferences']
