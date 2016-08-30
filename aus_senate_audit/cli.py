# -*- coding: utf-8 -*-

""" Encapsulates a Utility Function for Creating the CLI. """

from argparse import ArgumentParser

from constants import DEFAULT_SAMPLE_INCREMENT_SIZE
from constants import DEFAULT_SIMULATED_SENATE_ELECTION_NUM_BALLOTS
from constants import DEFAULT_SIMULATED_SENATE_ELECTION_NUM_CANDIDATES
from constants import DEFAULT_UNPOPULAR_FREQUENCY_THRESHOLD
from constants import QUICK_MODE
from constants import REAL_MODE
from constants import SIMULATION_MODE
from constants import STATES

# -m simulation -s SEED --num-ballots 1000 --num-candidates 10
# -m quick -s SEED --state TAS --max-ballots 1000 --config-file config.json
# -m real -s SEED --state TAS --config-file config.json [--selecte-ballots-file ...]

def parse_command_line_args():
    """ Parses the command line arguments for running an audit. """
    parser = ArgumentParser()
    parser.add_argument(
        'mode',
        type=str,
        metavar='MODE',
        choices=[QUICK_MODE, REAL_MODE, SIMULATION_MODE],
        help='Mode in which to run the audit.',
    )
    parser.add_argument(
        '-s',
        '--seed',
        type=int,
        default=1,
        help='Starting value of the random number generator.'
    )
    parser.add_argument(
        '--num-ballots',
        type=int,
        default=DEFAULT_SIMULATED_SENATE_ELECTION_NUM_BALLOTS,
        help='Number of cast ballots for a simulated senate election.',
    )
    parser.add_argument(
        '--num-candidates',
        type=int,
        default=DEFAULT_SIMULATED_SENATE_ELECTION_NUM_CANDIDATES,
        help='Number of candidates for a simulated senate election.',
    )
    parser.add_argument(
        '--state',
        type=str,
        choices=STATES,
        help='Abbreviation of state name to run senate election audit for.',
    )
    parser.add_argument(
        '-c',
        '--config-file',
        type=str,
        help='Path to Australian senate election configuration file (see \
        https://github.com/grahame/dividebatur/blob/master/aec_data/fed2016/\
        aec_fed2016.json as an example).',
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Whether to sample the remaining ballots or run a stage of the audit',
    )
    parser.add_argument(
        '--max-ballots',
        type=int,
        help='Maximum number of ballots to check for a real senate election \
        audit.',
    )
    parser.add_argument(
        '-f',
        '--unpopular-frequency-threshold',
        type=float,
        default=DEFAULT_UNPOPULAR_FREQUENCY_THRESHOLD,
        help='Upper bound on the frequency of trials a candidate is elected \
        in order for the candidate to be deemed unpopular.',
    )
    parser.add_argument(
        '--sample-increment-size',
        type=int,
        default=DEFAULT_SAMPLE_INCREMENT_SIZE,
        help='Number of ballots to add to growing sample.'
    )
    return parser.parse_args()
