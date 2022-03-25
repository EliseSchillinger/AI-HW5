import sys
import copy
import heapq
import time

class pengu: # class for attributes of pengu
    def __init__(pengu, score, death, location, can_move, game_grid, move_tracker, valid_move, total_fish) -> None:
        """ pengu class creation """
        pengu.score = score
        pengu.death = death
        pengu.location = location
        pengu.can_move = can_move
        pengu.move_tracker = move_tracker
        pengu.game_grid = game_grid
        pengu.valid_move = valid_move
        pengu.total_fish = total_fish

    def pengu_start():
        """ initialized upon object creation """
        pengu.score, pengu.total_fish = 0, 0
        pengu.death, pengu.can_move, pengu.valid_move = False, True, True
        pengu.location, pengu.game_grid, pengu.move_tracker = [], [], []
    
    def move_restart():
        """ reset for the beginning of every path test """
        pengu.score = 0
        pengu.death, pengu.can_move, pengu.valid_move = False, True, True
        pengu.move_tracker = []

def get_input(rows, columns, initial_game_grid):
    """ reads through the input file to create the grid for the game """
    with open(sys.argv[1], 'r') as input_file:
        rows, columns = [int(x) for x in next(input_file).split()]  # reads rows and columns from the first line
        initial_game_grid = []
        for line in input_file:  # read rest of lines and add symbols to game grid 2D list
            initial_game_grid.append([char for char in line.strip()])
        return rows, columns, initial_game_grid

def starting_game_info(rows, columns, initial_game_grid, pengu, num_of_fish, initial_location):
    """ determines pengu's initial location and the total number of fish on the board """

    for x in range(0, rows-1): # iterates through the game_grid array using rows & columns
        for y in range(0, columns-1):
            if initial_game_grid[x][y] == "P": # finds initial pengu location
                pengu.location = [x, y]
                initial_location = [x,y]

            if initial_game_grid[x][y] == "*": 
                num_of_fish += 1

    return pengu, num_of_fish, initial_location

def movement_choice(pengu, pengu_move):
    """ implements pengu's movement choice
        8 different directions according to keypad number.
        coordinates according to matrix, not xy coordinate system 
    """

    next_location = pengu.location[:]
    
    if pengu_move == 1: # southwest
        next_location[0] = next_location[0]+1
        next_location[1] = next_location[1]-1
    elif pengu_move == 2: # south
        next_location[0] = next_location[0]+1
    elif pengu_move == 3: # southeast
        next_location[0] = next_location[0]+1
        next_location[1] = next_location[1]+1
    elif pengu_move == 4: # west
        next_location[1] = next_location[1]-1
    elif pengu_move == 6: # east
        next_location[1] = next_location[1]+1
    elif pengu_move == 7: # northwest
        next_location[0] = next_location[0]-1
        next_location[1] = next_location[1]-1
    elif pengu_move == 8: # north
        next_location[0] = next_location[0]-1
    elif pengu_move == 9: # northeast
        next_location[0] = next_location[0]-1
        next_location[1] = next_location[1]+1
    elif pengu_move == 0:
        return
    # prevents pengu from going outside walls
    if next_location[0] < 0:
        next_location[0] = 0
    if next_location[1] < 0:
        next_location[1] = 0

    return next_location

def movement_check_function(pengu, path):
    """ determines if pengu can move, updates symbols and score accordingly """

    # reset before the start of next path tested just in case
    pengu.valid_move = True

    next_location = movement_choice(pengu, path)

    if pengu.game_grid[next_location[0]][next_location[1]] == '#': # Wall
        pengu.can_move = False
        pengu.valid_move = False
        return pengu
    elif pengu.game_grid[next_location[0]][next_location[1]] == '*': # Fish
        pengu.score += 1
        pengu.total_fish -= 1
        pengu.game_grid[next_location[0]][next_location[1]] = ' ' 
    elif pengu.game_grid[next_location[0]][next_location[1]] == ' ': # Ice
        pass
    elif pengu.game_grid[next_location[0]][next_location[1]] == '0': # Snow Block
        pengu.can_move = False
    elif pengu.game_grid[next_location[0]][next_location[1]] == 'S': # Shark: pengu dies and is replaced with 'X'
        pengu.game_grid[next_location[0]][next_location[1]] = 'X'
        pengu.can_move = False
        pengu.valid_move = False
        pengu.death = True
        return pengu
    elif pengu.game_grid[next_location[0]][next_location[1]] == 'U': # Bear: pengu dies and is replaced with 'X'
        pengu.game_grid[next_location[0]][next_location[1]] = 'X'
        pengu.can_move = False
        pengu.valid_move = False
        pengu.death = True
        return pengu
    pengu.location = next_location[:]

    return pengu

def copy_game_grid(initial_game_grid):
    """ copies the initial gameboard to pengu's current board """

    temp_grid = []
    for i in range(len(initial_game_grid)):
        temp_grid.append(initial_game_grid[i][:])
    return temp_grid

def write_output(pengu):
    """ opens up file for output and writes the updated game map to that file """

    original_stdout = sys.stdout

    with open(sys.argv[2], "w") as output_file:
        pengu.game_grid[pengu.location[0]][pengu.location[1]] = 'P'
        output_file.write(str(pengu.move_tracker).strip("'[']").replace(", ", '') + "\n")
        output_file.write(str(pengu.score) + "\n")
        sys.stdout = output_file  # alters the standard output to write directly to file
        for rows in pengu.game_grid:
            print(str(rows).strip("'[']").replace("', '", ''))
        sys.stdout = original_stdout
    return

def valid_move(pengu, current_test_location):
    """ determines whether pengu's move was actually valid
        for ex. pengu doesn't actually move bc his direction is directly towards a wall
        vs. can_move becoming false after actual movement in the grid
    """
    if pengu.location != current_test_location and (pengu.can_move == False and pengu.valid_move == False and pengu.death == False):
        return True
    elif pengu.valid_move == True:
        return True
    elif pengu.valid_move == False:
        return False

def cost_plus_heuristic(pengu, path):
    """ heuristic: adds to the priority queue frontier based on the number of fish remaining. 
        less fish remaining is better because the score is higher
        cost: based on the length of the path 
    """
    path_cost = 0
    path_cost = len(path)
    add_to_frontier = ()
    add_to_frontier = (path_cost + pengu.total_fish, path) # add together for A*

    return add_to_frontier

def main_A_star():
    """ main pengu loop: uses A* algorithm to collect fish """

    # initilization
    pengu_obj = pengu
    pengu_obj.pengu_start()

    num_of_fish, rows, columns = 0, 0, 0
    initial_location, initial_game_grid, current_test_location = [], [], []
    path = (0,[])

    # hw 5 specific variables
    frontier = [] # starts as a list, will be "heapified". esssentially list of tuples?
    current_num_fish = 0
    add_to_frontier = (0,[])
    comparison_path = (0,[])

    # starting state information
    rows, columns, initial_game_grid = get_input(rows, columns, initial_game_grid)
    pengu_obj, num_of_fish, initial_location = starting_game_info(rows, columns, initial_game_grid, pengu_obj, num_of_fish, initial_location)
    pengu_obj.game_grid = initial_game_grid[:]

    frontier.append(path)
    # A* Algorithm
    while frontier: # as long as the frontier priority queue isn't empty, test algorithm
        path = heapq.heappop(frontier)
        path = path[1]

        # reset every iteration: 
        pengu_obj.location = copy.copy(initial_location)
        pengu_obj.game_grid = copy_game_grid(initial_game_grid)  
        pengu_obj.move_restart()
        pengu_obj.total_fish = num_of_fish # reset every path test

        # clear the 'P' from pengu's initial location
        pengu_obj.game_grid[pengu_obj.location[0]][pengu_obj.location[1]] = ' '

        # movement_check_function is equiv. of transition function
        for move in path:
            pengu.can_move = True
            while pengu_obj.can_move:
                pengu_obj = movement_check_function(pengu_obj, move)

        # temporary location and number of fish remaining vars for pengu after the path is gone through above
        current_test_location = pengu_obj.location[:]
        current_num_fish = pengu_obj.total_fish

        if pengu_obj.score == num_of_fish: # if pengu finds goal state: write to output and exit algorithm loop
            pengu_obj.move_tracker = path
            write_output(pengu_obj)
            break
        
        for move in range(1,10): # test all keypad moves excluding 5
            # pengu starts from the path tested in previous segment of the loop. resets necessary attributes for path testing
            pengu_obj.location = current_test_location[:]
            pengu_obj.move_restart()
            pengu_obj.total_fish = current_num_fish # reset based on fish remaining before each test move

            if move == 5:
                continue
            # holds currently tested move instead of entire path so it doesn't move full path again at the changed location
            test_move = []
            test_move.append(move)
            while pengu_obj.can_move:
                pengu_obj = movement_check_function(pengu_obj, move)
            
            if valid_move(pengu_obj, current_test_location): # add to the frontier
                path.append(test_move[0])
                pengu.move_tracker = path

                # cost(p) + heuristic(p)
                add_to_frontier = cost_plus_heuristic(pengu_obj,path)

                heapq.heappush(frontier, add_to_frontier) # push onto priority queue: maintains invariant
                path = path[:-1] # remove test_move from path afterwards in order to check next valid move
            else: # otherwise ignore
                continue

start_time= time.time()
main_A_star()
print("---------- %s seconds ---------" % (time.time()- start_time))