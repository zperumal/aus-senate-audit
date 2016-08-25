# -*- coding: utf-8 -*-

""" Implements a class for representing a real senate election. """

from json import load
from random import random

import dividebatur.counter as cnt
import dividebatur.senatecount as sc

from audit_tie_breaker import AuditTieBreaker
from senate_election import SenateElection
from real_senate_election_results import RealSenateElectionResults


class RealSenateElection(SenateElection):
    """ Encapsulates information for running a real senate election. """
    TYPE = 'Real'

    def __init__(self, state, conf, seed, max_ballots=None):
        """ Initializes a :class:`RealSenateElection` object.

        :param str state: The abbreviation of the state name to run the senate
            election audit for.
        :param str conf: The configuration file specifiyng details about the
            senate election contest to audit.
        :param int seed: The starting value for the random number generator.
        :param int max_ballots: The maximum number of ballots to check when
            performing the senate election audit (default: None).
        """
        # Read the configuration file for the election data.
        election_config = sc.read_config(conf)
        self._election_id = election_config['title']
        for contest in election_config['count']:
            if contest['name'] == state:
                contest_config = contest
        self._seats = contest_config['vacancies']
        self.remaining_tickets = []

        try:
            # Remove this key to suppress verification checks which would
            # not be valid for a subsample of the ballots from the contest.
            del contest_config['verified']
        except KeyError:
            pass

        # Get the social chocie function.
        input_cls = sc.get_input_method(contest_config['aec-data']['format'])

        data_options = {}  # Passed when getting data from :mod:`dividebatur`.
        if max_ballots is not None:
            data_options['max_ballots'] = max_ballots

        contest_config['aec-data']['all-preferences'] = 'rounds/aggregates.csv'

        # Get election data.
        self._data = sc.get_data(
            input_cls,
            '',
            contest_config,
            **data_options,
        )

        # Build remaining ticket data structure from tickets and randomly shuffle for sampling.
        for ticket, weight in self._data.tickets_for_count:
            # NOTE: We expand multiplicities here such that for each ticket, there are `weight` copies of that ticket 
            # in `self.remaining_tickets`. We do this for ease of random sampling (e.g. note that a dictionary mapping
            # tickets to their corresponding weights does not facilitate easy random sampling).
            for _ in range(weight):
                if max_ballots and len(self.remaining_tickets) >= max_ballots:
                    break
                self.remaining_tickets.append(copy.deepcopy(ticket))
                self.n += 1
            if max_ballots and len(self.remaining_tickets) >= max_ballots:
                    break

        random.shuffle(self.remaining_tickets)

        # Get candidate data.
        self._candidate_ids = self._data.get_candidate_ids()
        self._candidates = self._data.candidates.candidates

        # Initialize AuditTieBreaker with tie-breaking information from the contest.
        self._tie_breaker = AuditTieBreaker(self._candidate_ids)
        self._tie_breaker.load_events(
            contest_config['election_order_ties'],
            contest_config['election_ties'],
            contest_config['exclusion_ties'],
        )

    def draw_ballots(self, batch_size=100):
        # Make sure not to over draw remaining ballots.
        ballots_to_draw = min(batch_size, len(self.remaining_tickets))
        for _ in range(ballots_to_draw):
            # Pop off the first ticket in `self.remaining_tickets`, convert it from a ticket to a ballot,
            # and finally add it to the growing sample of ballots.
            self.add_ballot(self.remaining_tickets.pop(0), 1)
        self._ballots_drawn += ballots_to_draw

    def get_outcome(self, ballot_weights):
        """ Returns the outcome of a senate election with the given ballot 
        weights.

        :param :class:`Counter` ballot_weights: A mapping from a ballot type
            to the number of ballots drawn of that type.

        :returns: The IDs of the candidates elected to the available seats,
            sorted in lexicographical order.
        :rtype: tuple
        """
        # Reset tickets for count.
        self._data.tickets_for_count = sc.PapersForCount()
        for ballot, weight in ballot_weights.items():
            self._data.tickets_for_count.add_ticket(tuple(ballot), weight)

        # Set up and run counter.
        results = RealSenateElectionResults()
        counter = cnt.SenateCounter(
            results,
            self._seats,
            self._data.tickets_for_count,
            self._tie_breaker.break_election_order_tie,
            self._tie_breaker.break_exclusion_tie,
            self._tie_breaker.break_election_tie,
            self._data.get_candidate_ids(),
            self._data.get_candidate_order,
            disable_bulk_exclusions=True,
        ).run()

        return tuple(sorted(results.get_elected_candidates()))
