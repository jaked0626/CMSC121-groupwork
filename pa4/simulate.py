'''
Polling places

Defne Buyukyazgan, Jake Underland

Main file for polling place simulation
'''

import sys
import random
import queue
import click
import util



class Voter(object):
    def __init__(self, arrival_time, voting_duration):
        self.arrival_time = arrival_time
        self.voting_duration = voting_duration
        self.start_time = None
        '''
        Constructor of the Voter class

        Input:
            arrivel_time: (float) Arrival time of voter to booth
            voting duration: (float) Time it takes voter to vote
        '''
        
    def departure_time(self):
        '''
        Calculates departure time of voter

        Inputs:
            start_time: (None, then float) voting start time
            voting_duration: (float) Time it takes voter to vote

        Returns departure time (float)
        '''
        if self.start_time is not None:
            departure = self.start_time + self.voting_duration
        
        return departure


    def to_string(self):
        '''
        Displays information about voter as a string

        Inputs:
            start_time: (None, then float) voting start time
            voting_duration: (float) Time it takes voter to vote
            arrival_time:
            departure_time:
            
        Returns list of voter information
        '''
        s = "arrival_time:{}, start_time:{}, voting_duration:{},"\
            " departure_time:{}".format(self.arrival_time, self.start_time,\
            self.voting_duration, self.departure_time)

        return s


class Precinct(object):
    def __init__(self, name, hours_open, 
                 max_num_voters, num_booths, 
                 arrival_rate, voting_duration_rate):
        '''
        Constructor for the Precinct class

        Input:
            name: (str) Name of the precinct
            hours_open: (int) Hours the precinct will remain open
            max_num_voters: (int) Number of voters in the precinct
            num_booths: (int) Number of voting booths in the precinct
            arrival_rate: (float) Rate at which voters arrive
            voting_duration_rate: (float) Lambda for voting duration
        '''
        self.name = name
        self.hours_open = hours_open
        self.max_num_voters = max_num_voters
        self.num_booths = num_booths
        self.arrival_rate = arrival_rate
        self.voting_duration_rate = voting_duration_rate

    
    def gen_voter_lst(self, percent_straight_ticket,
                      straight_ticket_duration, seed):
        '''
        Generate a list of voters

        Input:
            percent_straight_ticket: (float) Percentage of straight-ticket
              voters as a decimal between 0 and 1 (inclusive)
            straight_ticket_duration: (float) Voting duration for
              straight-ticket voters
            seed: (int) Random seed to use in the simulation

        Output:
            List of voters generated from given parameter function
        '''

        random.seed(seed)
        time = 0
        voter_lst = []

        for i in range(self.max_num_voters):

            gaps, duration = util.gen_voter_parameters(self.arrival_rate,\
                                self.voting_duration_rate,\
                                percent_straight_ticket,\
                                straight_ticket_duration)
            time += gaps

            if time < self.hours_open * 60:
                # For all arrivals during open hours, generate a voter
                voter = Voter(time, duration)
                voter_lst.append(voter)
            else:
                break

        return voter_lst


    def simulate(self, percent_straight_ticket, 
                 straight_ticket_duration, seed):
        '''
        Simulate a day of voting
        Input:
            percent_straight_ticket: (float) Percentage of straight-ticket
              voters as a decimal between 0 and 1 (inclusive)
            straight_ticket_duration: (float) Voting duration for
              straight-ticket voters
            seed: (int) Random seed to use in the simulation

        Output:
            List of voters who voted in the precinct
        '''

        voter_lst = self.gen_voter_lst(percent_straight_ticket,
                                       straight_ticket_duration, seed)
        
        booths = VotingBooths(self.num_booths)

        for voter in voter_lst:
            if not booths.full():
                # if there is an empty booth, voters start upon arrival
                voter.start_time = voter.arrival_time
                booths.enter_voter(voter.departure_time())

            else:
                # if booths are full, exit a voter first and compare next
                # voter's arrival time with exited voter's departure time
                prev_voter_depart_time = booths.exit_voter()

                if voter.arrival_time < prev_voter_depart_time:
                    voter.start_time = prev_voter_depart_time
                    booths.enter_voter(voter.departure_time())
                
                else:
                    voter.start_time = voter.arrival_time
                    booths.enter_voter(voter.departure_time())
        
        return voter_lst


class VotingBooths(object):
    def __init__(self, num_booths):
        '''
        Constructor for the Voting Booth

        Input:
            name: (str) Name of the precinct
            num_booths: (int) Number of voting booths in the precinct   
        '''
        self.booths = queue.PriorityQueue(num_booths)
        self.num_booths = num_booths
    
    def enter_voter(self, departure_time):
        '''
        Voter enters booth when another departs

        Input:
            name: (str) Name of the precinct
            departure_time: (float) time voter departs from booth
        '''
        self.booths.put(departure_time, block=False)
    

    def exit_voter(self):
        '''
        Removes voter from line

        Input:
            name: (str) Name of the precinct
            num_booths: (int) Number of voting booths in the precinct
        '''
        voter = self.booths.get(block=False)

        return voter
    

    def full(self):
        '''
        Checks if booth is full

        Input:
            instance of VotingBooths   
        '''

        return self.booths.full()
    

    def empty(self):
        '''
        Checks if booth is empty

        Input:
            instance of VotingBooths 
        '''
        return self.booths.empty()


def find_avg_wait_time(precinct, percent_straight_ticket, 
                       ntrials, initial_seed=0):
    '''
    Simulates a precinct multiple times with a given percentage of
    straight-ticket voters. For each simulation, computes the average
    waiting time of the voters, and returns the median of those average
    waiting times.

    Input:
        precinct: (dictionary) A precinct dictionary
        percent_straight_ticket: (float) Percentage straight-ticket voters
        ntrials: (int) The number of trials to run
        initial_seed: (int) Initial seed for random number generator

    Output:
        The median of the average waiting times returned by simulating
        the precinct 'ntrials' times.
    '''

    seed = initial_seed
    straight_ticket_duration = precinct["straight_ticket_duration"]
    
    p = Precinct(precinct["name"],
                 precinct["hours_open"],
                 precinct["num_voters"],
                 precinct["num_booths"],
                 precinct["arrival_rate"],
                 precinct["voting_duration_rate"])

    lst_avg_wt = []

    # simulate n times, compute average wt, and add average to list.
    for i in range(ntrials):
        voters = p.simulate(percent_straight_ticket,
                            straight_ticket_duration, seed)
        sum_wt = sum([v.start_time - v.arrival_time for v in voters])
        avg_wt = sum_wt / len(voters)
        lst_avg_wt.append(avg_wt)
        seed += 1  # increment seed for next simulation

    sorted_lst = sorted(lst_avg_wt)  # sort averages in ascending order

    return sorted_lst[ntrials//2]


def find_percent_split_ticket(precinct, target_wait_time, ntrials, seed=0):
    '''
    Finds the percentage of split-ticket voters needed to bound
    the (average) waiting time.

    Input:
        precinct: (dictionary) A precinct dictionary
        target_wait_time: (float) The minimum waiting time
        ntrials: (int) The number of trials to run when computing
                 the average waiting time
        seed: (int) A random seed

    Output:
        A tuple (percent_split_ticket, waiting_time) where:
        - percent_split_ticket: (float) The percentage of split-ticket
                                voters that ensures the average waiting time
                                is above target_waiting_time
        - waiting_time: (float) The actual average waiting time with that
                        percentage of split-ticket voters

        If the target waiting time is infeasible, returns (1, None)
    '''

    over_target_percentage = 0
    over_target_avg_wt = 0

    # i = percent split ticket by increments of 10, not decimal
    for i in range(0, 101, 10):
        percent_straight_ticket = (100 - i) / 100  # decimal form
        avg_wt = find_avg_wait_time(precinct, percent_straight_ticket,
                                    ntrials, seed)

        if avg_wt > target_wait_time:
            over_target_percentage = i / 100  # decimal form
            over_target_avg_wt = avg_wt
            return (over_target_percentage, over_target_avg_wt)
            # if above is never met, target wait time always feasible

    return (1, None)


# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg= invalid-name, len-as-condition, too-many-locals
# pylint: disable-msg= missing-docstring, too-many-branches
# pylint: disable-msg= line-too-long
@click.command(name="simulate")
@click.argument('precincts_file', type=click.Path(exists=True))
@click.option('--target-wait-time', type=float)
@click.option('--print-voters', is_flag=True)
def cmd(precincts_file, target_wait_time, print_voters):
    precincts, seed = util.load_precincts(precincts_file)

    if target_wait_time is None:
        voters = {}
        for p in precincts:
            precinct = Precinct(p["name"],
                                p["hours_open"],
                                p["num_voters"],
                                p["num_booths"],
                                p["arrival_rate"],
                                p["voting_duration_rate"])
            voters[p["name"]] = precinct.simulate(p["percent_straight_ticket"], 
                                p["straight_ticket_duration"], seed)
        print()
        if print_voters:
            for p in voters:
                print("PRECINCT '{}'".format(p))
                util.print_voters(voters[p])
                print()
        else:
            for p in precincts:
                pname = p["name"]
                if pname not in voters:
                    print("ERROR: Precinct file specified a '{}' precinct".format(pname))
                    print("       But simulate_election_day returned no such precinct")
                    print()
                    sys.exit(-1)
                pvoters = voters[pname]
                if len(pvoters) == 0:
                    print("Precinct '{}': No voters voted.".format(pname))
                else:
                    pl = "s" if len(pvoters) > 1 else ""
                    closing = p["hours_open"]*60.
                    last_depart = pvoters[-1].departure_time
                    avg_wt = sum([v.start_time - v.arrival_time for v in pvoters]) / len(pvoters)
                    print("PRECINCT '{}'".format(pname))
                    print("- {} voter{} voted.".format(len(pvoters), pl))
                    msg = "- Polls closed at {} and last voter departed at {:.2f}."
                    print(msg.format(closing, last_depart))
                    print("- Avg wait time: {:.2f}".format(avg_wt))
                    print()
    else:
        precinct = precincts[0]

        percent, avg_wt = find_percent_split_ticket(precinct, target_wait_time, 20, seed)

        if percent == 1:
            msg = "Waiting times are always below {:.2f}"
            msg += " in precinct '{}'"
            print(msg.format(target_wait_time, precinct["name"]))
        else:
            msg = "Precinct '{}' exceeds average waiting time"
            msg += " of {:.2f} with {} percent split-ticket voters"
            print(msg.format(precinct["name"], avg_wt, percent*100))


if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter
