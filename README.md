# aus-senate-audit

The Australian Senate Audit can be run in three different modes.

1. Simulation Mode: Runs a simulated audit on fake data using Borda Count.

``aus-senate-audit simulation --seed SEED --num-candidates NUM_CANDIDATES --num-ballots NUM_BALLOTS``

where

SEED is the starting value of the RNG used by the program.
NUM_CANDIDATES is the number of candidates in the simulation (default: 100). 
NUM_BALLOTS is the number of cast ballots in the simulation (default: 1000000).


2. Quick Mode: Runs a Bayesian audit on real data and automates reading paper ballots.

``aus-senate-audit quick --seed SEED --state STATE --data DATA``

where

SEED is the starting value of the RNG used by the program.
STATE is the abbreviated name of the Australian state to run the audit for (e.g. TAS).
DATA is the file path to all Australian senate election data.

3. Real Mode: Runs a Bayesian audit on real data.

Running a real audit requires two steps. First, the formal preferences must be sampled using

``aus-senate-audit real --seed SEED --state STATE --data DATA``

This command will generate a ``selected_ballots.csv`` file containing a 
sample of ballots that do not contain formal preferences. The auditor must
use the information in the file to retrieve the paper preferences and enter
them into the CSV file. For example, suppose a line in the ``selected_ballots.csv``
file appears as

``Denison,POSTAL 3,311,19,42,``

The auditor would retrieve that exact ballot and then add the preferences
read from that ballot to the ``selected_ballots.csv``, as shown below.

``Denison,POSTAL 3,311,19,42,",1,2,3,,6,,,,4,,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"``

Upon completing the ``selected_ballots.csv``, the auditor should run

``aus-senate-audit real --seed SEED --state STATE --selected-ballots SELECTED_BALLOTS_FILE --data DATA``

SELECTED_BALLOTS_FILE is the path to the ``selected_ballots.csv`` file. 

This command will run one audit stage on the sample of ballots audited thus far.
One should continue the audit in this manner (repeating step 3), until the audit
terminates (as will be indicated in the printout by the audit).

There are a handful of other options for fine tuning the audit. These can be seen by running

``aus-senate-audit -h``
