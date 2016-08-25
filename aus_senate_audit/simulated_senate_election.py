# -*- coding: utf-8 -*-

""" Implements a class for representing a simulated senate election. """

from collections import Counter
from random import random
from random import seed as set_seed
from time import asctime
from time import localtime

from senate_election import SenateElection


class SimulatedSenateElection(SenateElection):
    """ Encapsulates information for running a simualted senate election.

    NOTE: The :attr:`_candidates` and :attr:`_candidate_ids` instance
    attributes are set as a [1, ..., :attr:`_m`].
    """
    TYPE = 'Simulated'
    DEFAULT_ID = 'SimulatedElection{}'

    def __init__(self, n, m, seed):
        """ Initializes a :class:`SimulatedSenateElection` object.

        The number of seats in a simulated senate eleciton is equal to the
        floor of the number of candidates in the election divided by two.

        :param int n: The total number of ballots cast in the election.
        :param int m: The total number of candidates in the election.
        :param int seed: The starting value for the random number generator.
        """
        super(SimulatedSenateElection, self).__init__()
        self._n = n
        self._m = m
        self._seats = int(self._m / 2)
        self._candidates = list(range(1, self._m + 1))
        self._candidate_ids = list(range(1, self._m + 1))
        self._election_id = SimulatedSenateElection.DEFAULT_ID.format(
            asctime(localtime()),
        )
        set_seed(seed)

    def draw_ballots(self, batch_size=100):
        """ Adds simulated ballots to the sample of ballots drawn thus far.

        :param int batch_size: The number of ballots drawn in this sample
            increment (default: 100).

        These ballots are biased so (1, 2, ..., m) is likely to be the winner.
        More precisely, each ballot candidate `i` is given a value `i + v * U`
        where `U = uniform(0, 1)` and `v` is the level of noise. Then the 
        candidates are sorted into increasing order by these values. Note that
        the total number of ballots drawn may not exceed the total number of 
        case votes, :attr:`_n`.
        """
        v = self._m / 2  # Noise level to control position variance.
        batch_size = min(batch_size, self._n - self._ballots_drawn)
        for _ in range(batch_size):
            L = []
            for i, cid in enumerate(self._candidate_ids):
                L.append((i + v * random(), cid))
            ballot = tuple(cid for val, cid in sorted(L))
            self.add_ballot(ballot, 1)
        self._ballots_drawn += batch_size

    def get_outcome(self, ballot_weights):
        """ Returns the outcome of a senate election with the given ballot 
        weights.

        The social choice function used in the simualted senate election is
        Borda count.

        :param :class:`Counter` ballot_weights: A mapping from a ballot type
            to the number of ballots drawn of that type.

        :returns: The IDs of the candidates elected to the available seats,
            sorted in lexicographical order.
        :rtype: tuple
        """
        counter = Counter()
        for ballot in self._ballots:
            weight = ballot_weights[ballot]
            for i, cid in enumerate(ballot):
                counter[cid] += weight * i
        # Get the :attr:`_seat` candidates with the lowest Borda counts in 
        # increasing order.
        L = counter.most_common()[-self._seats:][::-1]
        return tuple(sorted([cid for cid, count in L]))
