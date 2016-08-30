# -*- coding: utf-8 -*-

""" Runs the Australian Senate Election Audit. """

from audit_info import AuditInfo
from audits.bayesian_audit import audit
from audit_validator import AuditValidator
from cli import parse_command_line_args
from constants import AUDIT_STAGE_KEY
from constants import QUICK_MODE
from constants import REAL_MODE
from constants import SIMULATION_MODE
from sampler.sampler_wrapper import SamplerWrapper
from senate_election.real_senate_election import RealSenateElection
from senate_election.simulated_senate_election import SimulatedSenateElection


def main():
    """ Runs the Australian senate election audit. """
    args = parse_command_line_args()
    if args.mode == SIMULATION_MODE:
        election = SimulatedSenateElection(
            args.seed,
            args.num_ballots,
            args.num_candidates,
        )
        audit(election, args.seed, args.unpopular_frequency_threshold, quick=True)
    elif args.mode == REAL_MODE:
        audit_info = AuditInfo(args.state)
        if args.sample:
            SamplerWrapper(
                args.seed,
                args.config_file,
                args.state,
                args.sample_increment_size,
                audit_info,
            )
        else:
            AuditValidator(audit_info).compare()
            election = RealSenateElection(
                args.state,
                args.config_file,
                args.seed,
                max_ballots=args.max_ballots,
            )
            audit(
                election,
                args.seed,
                args.unpopular_frequency_threshold,
                stage_counter=audit_info.get_audit_info()[AUDIT_STAGE_KEY] - 1,
            )
    else:
        done = False
        audit_info = AuditInfo(args.state)
        while not done:
            SamplerWrapper(
                args.seed,
                args.config_file,
                args.state,
                args.sample_increment_size,
                audit_info,
                quick=True,
            )
            AuditValidator(audit_info).compare()
            election = RealSenateElection(
                args.state,
                args.config_file,
                args.seed,
                max_ballots=args.max_ballots,
            )
            done = audit(
                election,
                args.seed,
                args.unpopular_frequency_threshold,
                stage_counter=audit_info.get_audit_info()[AUDIT_STAGE_KEY] - 1,
            )


if __name__ == '__main__':
    main()
