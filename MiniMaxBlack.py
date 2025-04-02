import sys
import array

positions_evaluated = 0

def move_white(copy_array, i):
    # Check if the move is out of bounds or not white
    if copy_array[i] != 'w' and copy_array[i] != 'W':
        print("invalid move: not a white piece at position", i)
        return copy_array
    if i == 15:
        return copy_array
    if i < 0 or i >= len(copy_array):
        print(f"index {i} out of bounds [0,15].")

    # Check if the next position is empty
    elif copy_array[i + 1] == 'x':
        copy_array[i + 1] = copy_array[i]
        copy_array[i] = 'x'
        return copy_array

    # Jump move
    else:
        j = i + 2
        while j < len(copy_array) and copy_array[j] != 'x':
            j += 1

        # If no empty square found, return
        if j == len(copy_array):
            copy_array[i] = 'x'
            return copy_array

        # Perform the jump
        copy_array[j] = copy_array[i]
        copy_array[i] = 'x'

        # Check if the jump is over a black piece
        if j - i > 2:
            return copy_array
        else:
            # Check if the jump is over a white piece
            if copy_array[i + 1] == 'w' or copy_array[i + 1] == 'W':
                return copy_array
            else:
                # Find the rightmost empty square
                k = len(copy_array) - 1
                while k >= 0 and copy_array[k] != 'x':
                    k -= 1
                
                # Now k is the index of the rightmost empty square
                if k >= 0:
                    # Only move the black piece if the rightmost 'x' is at a higher index
                    if k > i + 1:
                        # If the captured piece is in second to last position and white piece is king
                        if j == 14 and copy_array[j] == 'W':
                            # White king should go to the last position (winning)
                            copy_array[15] = copy_array[j]
                            copy_array[j] = 'x'
                            # Move the captured black piece to the rightmost empty square
                            copy_array[k] = 'b'
                        else:
                            # Otherwise, move the black piece to the rightmost empty square
                            copy_array[k] = copy_array[i + 1]
                            copy_array[i + 1] = 'x'
                return copy_array

def WhiteWin(board):
    return 'W' not in board

def BlackWin(board):
    return 'B' not in board

def EstimatePosition(board):
    if WhiteWin(board):
        return 100  # White wins
    elif BlackWin(board):
        return -100  # Black wins
    else:
        i = board.index('W') if 'W' in board else 0
        j = board.index('B') if 'B' in board else 0
        return i + j - 15

def minimax(copy_array, depth, maximizing_player):
    global positions_evaluated
    positions_evaluated += 1
    if depth == 0 or WhiteWin(copy_array) or BlackWin(copy_array):
        return EstimatePosition(copy_array)
    else:
        if maximizing_player:  # White's turn
            max_eval = float('-inf')
            for i in range(len(copy_array)):
                if copy_array[i] == 'w' or copy_array[i] == 'W':
                    new_copy = copy_array.copy()
                    new_copy = move_white(new_copy, i)
                    eval = minimax(new_copy, depth - 1, False)
                    max_eval = max(max_eval, eval)
            return max_eval
        else:  # Black's turn
            min_eval = float('inf')
            for i in range(len(copy_array)):
                if copy_array[i] == 'b' or copy_array[i] == 'B':
                    new_copy = copy_array.copy()
                    eval = minimax(new_copy, depth - 1, True)
                    min_eval = min(min_eval, eval)
            return min_eval

def main():
    if len(sys.argv) == 4:
        # Use input/output files and depth from command-line arguments
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        tree_depth = int(sys.argv[3])

    else:
        # Default behavior (interactive mode)
        input_filename = input("Enter the input board positions filename: ")
        output_filename = input("Enter the output board positions filename: ")
        tree_depth = int(input("Enter the depth of the tree to be searched: "))

    # Read the input board position
    with open(input_filename, 'r') as file:
        copy_array = list(file.readline().strip())

            # Reverse the board and convert it back to a list
    copy_array = list(reversed(copy_array))
    for idx, c in enumerate(copy_array):
        if c == 'b':
            copy_array[idx] = 'w'
        elif c == 'B':
            copy_array[idx] = 'W'
        elif c == 'w':
            copy_array[idx] = 'b'
        elif c == 'W':
            copy_array[idx] = 'B'
    
    # Run the minimax algorithm
    best_value = float('-inf')
    best_move = -1
    for i in range(len(copy_array)):
        if copy_array[i] == 'w' or copy_array[i] == 'W':
            new_copy = copy_array.copy()
            new_copy = move_white(new_copy, i)
            move_value = minimax(new_copy, tree_depth - 1, False)
            if move_value > best_value:
                best_value = move_value
                best_move = i

    # Make the best move
    new_board = move_white(copy_array.copy(), best_move)

    # Later in the code, when reversing the new board
    new_board = list(reversed(new_board))
    for idx, c in enumerate(new_board):
        if c == 'b':
            new_board[idx] = 'w'
        elif c == 'B':
            new_board[idx] = 'W'
        elif c == 'w':
            new_board[idx] = 'b'
        elif c == 'W':
            new_board[idx] = 'B'

    # Write the new board position to the output file
    with open(output_filename, 'w') as file:
        file.write(''.join(new_board))

    # Print the results
    print(f"Output board position: {''.join(new_board)}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}.")
    print(f"MINIMAX estimate: {best_value}.")
    # Write the new board position to the output file
    with open(output_filename, 'w') as file:
        for char in copy_array:
            file.write(char)

if __name__ == "__main__":
    main()