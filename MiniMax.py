import array

# Get input and output filenames from the user and depth of the tree to be searched
input_filename = 'input.txt'#input("Enter the input board positions filename: ")
output_filename = 'output.txt'#input("Enter the output board positions filename: ")
tree_depth = 2#int(input("Enter the depth of the tree to be searched: "))

#insert the line of the input file into the array character by character
input_array = []
with open(input_filename, 'r') as file:
    count = 0
    for char in file.read():
        input_array.append(char)
        if count == 16:
            break
        count += 1
print(input_array)
copy_array = input_array.copy()

'''
Scan the array P for White pieces (the letters w or W). For each White piece found, let i be its
index in the array. The value of i satisfies: 0 ≤ i ≤ 15.
 if i == 15, set P[i] = x and return P. (Move out of board.)
 else if P[i + 1] == x, set P[i + 1] = P[i], P[i] = x, and return P. (Move one forward.)
 else (jump) compute j, the index of the first empty square to the right of i.
 if such j does not exist set P[i] = x and return P. (Jump out of board.)
 else set P[j] = P[i], P[i] = x and check if the jump is over one black piece.
 if(j  i > 2) (Jump over several) return P.
 else (here j==i+2, jump over one piece)
 if(P[i + 1] == w or W) (jump over one white piece) return P.
 else (here the jump is over one black piece)
compute k, the index of the rightmost empty square.
set P[k] = P[i + 1], P[i + 1] = x.
return P.
'''
def move_white(input_array, i):
    # Check if the move is out of bounds
    if i == 15:
        input_array[i] = 'x'
        return input_array

    # Check if the next position is empty
    elif input_array[i + 1] == 'x':
        input_array[i + 1] = input_array[i]
        input_array[i] = 'x'
        return input_array

    # Jump move
    else:
        j = i + 2
        while j < len(input_array) and input_array[j] != 'x':
            j += 1

        # If no empty square found, return
        if j == len(input_array):
            input_array[i] = 'x'
            return input_array

        # Perform the jump
        input_array[j] = input_array[i]
        input_array[i] = 'x'

        # Check if the jump is over a black piece
        if j - i > 2:
            return input_array
        else:
            # Check if the jump is over a white piece
            if input_array[i + 1] == 'w' or input_array[i + 1] == 'W':
                return input_array
            else:
                # Find the rightmost empty square
                k = len(input_array) - 1
                while k >= 0 and input_array[k] != 'x':
                    k -= 1
                
                # Now k is the index of the rightmost empty square
                if k >= 0:
                    # If the captured piece is in second to last position and white piece is king
                    if i + 1 == 14 and (input_array[j] == 'W'):
                        # White king should go to the last position (winning)
                        input_array[15] = input_array[j]
                        input_array[j] = 'x'
                    else:
                        # Otherwise, move the black piece to the rightmost empty square
                        input_array[k] = input_array[i + 1]
                        input_array[i + 1] = 'x'
                
                return input_array
            
print(move_white(copy_array, 13))  # Example usage of the move_white function