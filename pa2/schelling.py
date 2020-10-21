"""
CS121: Schelling Model of Housing Segregation

  Program for simulating a variant of Schelling's model of
  housing segregation.  This program takes six parameters:

    filename -- name of a file containing a sample city grid

    R - The radius of the neighborhood: a home at Location (k, l) is in
        the neighborhood of the home at Location (i,j) if 0 <= k < N,
        0 <= l < N, and 0 <= |i-k| + |j-l| <= R.

    similarity_satisfaction_range (lower bound and upper bound) -
         acceptable range for ratio of the number of
         homes of a similar color to the number
         of occupied homes in a neighborhood.

   patience - number of satisfactory homes that must be visited before choosing
              the last one visited.

   max_steps - the maximum number of passes to make over the city
               during a simulation.

  Sample: python3 schelling.py --grid_file=tests/a20-sample-writeup.txt --r=1
         --sim_lb=0.40 --sim_ub=0.7 --patience=3 --max_steps=1
  The sample command is shown on two lines, but should be entered on
  a single line in the linux command-line
"""

import click
import utility

def is_satisfied(grid, R, location, sim_sat_range):
    '''
    Determine whether or not the homeowner at a specific location is
    satisfied using an R-neighborhood centered around the location.
    That is, is does their similarity score fall with the specified
    range (inclusive)

    Inputs:
        grid: the grid
        R (int): neighborhood parameter
        location (int, int): a grid location
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
    Returns: bool
    '''

    # Since it does not make sense to call this function on a home
    # that is for sale, we recommend adding an assertion to verify
    # that the home is not for sale
    
    satisfied = False
    in_neighborhood = False
    i, j = location
    S = 0
    H = 0
    assert grid[i][j] != "F"
    for k, _ in enumerate(grid): 
        for l, _ in enumerate(grid): 
            val = abs(i - k) + abs(j - l)
            if val <= R:
                in_neighborhood = True
                if in_neighborhood == True:
                    if grid[k][l] == grid[i][j]:
                        S += 1
                        H += 1
                    elif grid[k][l] == "F":
                        H += 0
                    else: 
                        H += 1
    sim_score = S / H
    if sim_sat_range[0] <= sim_score <= sim_sat_range[1]:
        satisfied = True

    
    return satisfied

    
def swap_n_swap_back(grid, R, location, sim_sat_range, homes_for_sale):
    temporary_status = is_satisfied(grid, R, location, sim_sat_range)
    temporary_location = location
    if temporary_status == False:
        for h, _ in enumerate(homes_for_sale):
            temporary_location = homes_for_sale[h]
            i, j = temporary_location 
            k, l = location
            grid[i][j] = grid[k][l]
            grid[k][l] = "F"
            if is_satisfied(grid, R, temporary_location, sim_sat_range) == True:
                print(temporary_location, "satisfied")
            else: 
                print(temporary_location, "not satisfied")
            grid[k][l] = grid[i][j]
            grid[i][j] = "F"
    else:

        return "not applicable"
def swap(grid, old_location, new_location):
    '''
    replaces
    '''
    i, j = new_location
    k,l = old_location
    grid[i][j] = grid[k][l]
    grid[k][l] = "F" 
    print(grid)



def relocation(grid, R, location, sim_sat_range, homes_for_sale, patience):
    '''
    Puts a homeowner at a given location through the list of homes_for_sale
    until the homeowner finds the ith listing that falls within her 
    satisfaction range, where i is equal to patience. 
    '''
    visits = 0
    temporary_status = is_satisfied(grid, R, location, sim_sat_range)
    temporary_location = location
    if temporary_status == False:
        for h, _ in enumerate(homes_for_sale):
            temporary_location = homes_for_sale[h]
            i, j = temporary_location 
            k, l = location
            grid[i][j] = grid[k][l]
            grid[k][l] = "F"
            if is_satisfied(grid, R, temporary_location, sim_sat_range) == True:
                visits += 1
                if visits == patience:
                    homes_for_sale.pop(h)
                    homes_for_sale.insert(0, location)
                    break                                       
                else:
                    grid[k][l] = grid[i][j]
                    grid[i][j] = "F"
            else: 
                visits += 0
                grid[k][l] = grid[i][j]
                grid[i][j] = "F"
    return homes_for_sale, grid
    

        
                    


                    
                        

        #else:
            #temporary_location





def do_simulation(grid, R, sim_sat_range, patience, max_steps, homes_for_sale):
    '''
    Do a full simulation.

    Inputs:
        grid (list of lists of strings): the grid
        R (int): neighborhood parameter
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
        max_steps (int): maximum number of steps to do
        for_sale (list of tuples): a list of locations with homes for sale

    Returns: (int) The number of relocations completed.
    '''

    # Replace 0 with an appropriate return value
    return 0


@click.command(name="schelling")
@click.option('--grid_file', type=click.Path(exists=True))
@click.option('--r', type=int, default=1,
              help="neighborhood radius")
@click.option('--sim_lb', type=float, default=0.40,
              help="Lower bound of similarity range")
@click.option('--sim_ub', type=float, default=0.70,
              help="Upper bound of similarity range")
@click.option('--patience', type=int, default=1, help="patience level")
@click.option('--max_steps', type=int, default=1)
def cmd(grid_file, r, sim_lb, sim_ub, patience, max_steps):
    '''
    Put it all together: do the simulation and process the results.
    '''

    if grid_file is None:
        print("No parameters specified...just loading the code")
        return

    grid = utility.read_grid(grid_file)
    for_sale = utility.find_homes_for_sale(grid)
    sim_sat_range = (sim_lb, sim_ub)


    if len(grid) < 20:
        print("Initial state of city:")
        for row in grid:
            print(row)
        print()

    num_relocations = do_simulation(grid, r, sim_sat_range, patience,
                                    max_steps, for_sale)

    if len(grid) < 20:
        print("Final state of the city:")
        for row in grid:
            print(row)
        print()

    print("Total number of relocations done: " + str(num_relocations))

if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter
