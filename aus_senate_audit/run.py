# -*- coding: utf-8 -*-

""" Runs the Australian Senate Election Audit. """

from argparse import ArgumentParser

from audits.bayesian_audit import audit
from real_senate_election import RealSenateElection
from sampler_wrapper import SamplerWrapper
from simulated_senate_election import SimulatedSenateElection


DEFAULT_SIMULATED_SENATE_ELECTION_N = 1000000
DEFAULT_SIMULATED_SENATE_ELECTION_M = 100
DEFAULT_UNPOPULAR_FREQUENCY_THRESHOLD = 0.03
DEFAULT_SAMPLE_INCREMENT_SIZE = 1500


def parse_command_line_args():
    """ Parses the command line arguments for running an audit. """
    parser = ArgumentParser()
    parser.add_argument(
        '--seed',
        type=int,
        default=1,
        help='Starting value of the random number generator.'
    )
    parser.add_argument(
        '-s',
        '--state',
        type=str,
        choices=['TAS', 'QLD', 'NT', 'VIC', 'WA', 'ACT', 'NSW'],
        help='Abbreviation of state name to run senate election audit for.'
    )
    parser.add_argument(
        '--max-ballots',
        type=int,
        help='Maximum number of ballots to check for a real senate election \
        audit.',
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
        '--selected-ballots-file',
        type=str,
        help='Path to CSV file containing selected ballots for current audit\
        stage.',
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run a simulated senate election.',
    )
    parser.add_argument(
        '-n',
        '--num-cast-ballots',
        type=int,
        default=DEFAULT_SIMULATED_SENATE_ELECTION_N,
        help='Number of cast ballots for a simulated senate election.',
    )
    parser.add_argument(
        '-m',
        '--num-candidates',
        type=int,
        default=DEFAULT_SIMULATED_SENATE_ELECTION_M,
        help='Number of candidates for a simulated senate election.',
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
        '--all-formal-preferences-file',
        type=str,
        help='Path to CSV file containing all formal preferences.'
    )
    parser.add_argument(
        '--sample-increment-size',
        type=int,
        default=DEFAULT_SAMPLE_INCREMENT_SIZE,
        help='Number of ballots to add to growing sample.'
    )
    return parser.parse_args()


def compare_and_aggregate(selected_ballots_file):
    """ Compare preferences after paper inspection against electronic records. """
    with open(selected_ballots_file, 'r') as f:
        f.readline()
        paper_preferences = []
        for line in f:
            paper_preferences.append(line.rstrip().split('"')[1])
    audit_stage = SamplerWrapper.get_audit_stage()
    audit_round_fn = SamplerWrapper.AUDIT_ROUND_FN.format(
        SamplerWrapper.ROUNDS_DIR,
        audit_stage,
    )
    with open(audit_round_fn, 'r') as f:
        header = f.readline()
        records = [line.rstrip() for line in f]
    import os; os.unlink(audit_round_fn)
    with open(audit_round_fn, 'w') as f:
        f.write(header)
        for i in range(len(records)):
            electronic_preferences = records[i].split('"')[1]
            match = int(electronic_preferences == paper_preferences[i])
            f.write(records[i] + ',{},"{}"\n'.format(match, paper_preferences[i]))

    with open(SamplerWrapper.AGGREGATE_FN, 'a') as f:
        new_records = [line for line in open(selected_ballots_file, 'r')][1:]
        for new_record in new_records:
            f.write(new_record)

def main():
    """ Runs the Australian senate election audit. """
    args = parse_command_line_args()
    if args.simulate:
        election = SimulatedSenateElection(
            args.num_cast_ballots,
            args.num_candidates,
            args.seed,
        )
        audit(election, args.seed, args.unpopular_frequency_threshold)
    elif args.all_formal_preferences_file:
        SamplerWrapper(
            args.all_formal_preferences_file,
            args.sample_increment_size,
            args.seed,
        )
    else:
        compare_and_aggregate(args.selected_ballots_file)
        election = RealSenateElection(
            args.state,
            args.config_file,
            args.seed,
            max_ballots=args.max_ballots,
        )
        audit(election, args.seed, args.unpopular_frequency_threshold)


if __name__ == '__main__':
    main()
