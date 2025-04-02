import sys
import array

positions_evaluated = 0
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

def move_white(copy_array, i):
    # Check if the move is out of bounds or not white
    if copy_array[i] != 'w' and copy_array[i] != 'W':
        return copy_array
    if i == 15:
        return copy_array
    if i < 0 or i >= len(copy_array):
        return copy_array

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

#alpha beta pruning
def AlphaBeta(board, depth, alpha, beta, maximizing_player):
    global positions_evaluated
    positions_evaluated += 1

    if depth == 0 or WhiteWin(board) or BlackWin(board):
        return EstimatePosition(board)

    if maximizing_player:
        max_eval = float('-inf')
        for i in range(len(board)):
            if board[i] == 'W' or board[i] == 'w':
                new_board = move_white(board.copy(), i)
                eval = AlphaBeta(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(len(board)):
            if board[i] == 'B' or board[i] == 'b':
                new_board = move_white(board.copy(), i)
                eval = AlphaBeta(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval
    
def main():
    if len(sys.argv) == 4:
        # Use input/output files and depth from command-line arguments
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        tree_depth = int(sys.argv[3])

    else:
        # interactive mode
        input_filename = input("Enter input filename: ")
        output_filename = input("Enter output filename: ")
        tree_depth = int(input("Enter tree depth: "))
    
    input_array = []
    # Read the input board position
    with open(input_filename, 'r') as file:
        input_array = list(file.readline().strip())
    copy_array = input_array.copy()

    # Run the AlphaBeta algorithm
    best_value = float('-inf')
    best_move = None
    for i in range(len(copy_array)):
        if copy_array[i] == 'W' or copy_array[i] == 'w':
            new_board = move_white(copy_array.copy(), i)
            move_value = AlphaBeta(new_board, tree_depth - 1, float('-inf'), float('inf'), False)
            if move_value > best_value:
                best_value = move_value
                best_move = i

    # Make the best move
    new_board = move_white(copy_array.copy(), best_move)

    # Write the new board position to the output file
    with open(output_filename, 'w') as file:
        file.write(''.join(new_board))

    # Print the results
    print(f"Output board position: {''.join(new_board)}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}.")
    print(f"MINIMAX estimate: {best_value}.")

if __name__ == "__main__":
    main()
    
