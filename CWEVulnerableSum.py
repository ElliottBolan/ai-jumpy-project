import os

def load_previous_amount():
    # Load the previous amount from a file, or return a default value if unavailable
    try:
        with open("previous_amount.txt", "r") as file:
            return float(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 1.0

def save_result(result):
    # Save the computed result to a file.
    with open("previous_amount.txt", "w") as file:
        file.write(str(result))

def main():
    previous_amount = load_previous_amount()

    try:
        user_input = input("Enter numbers separated by space: ") # CWE-20: Improper Input Validation
        numbers = [float(x) for x in user_input.split()] # CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return

    total = sum(numbers)

    # Avoid division by zero
    if previous_amount == 0:
        previous_amount = 1

    result = total / previous_amount

    # Ensure result is not zero
    if result == 0:
        result = 1

    save_result(result)
    print(f"Result: {result}")

    # CWE-119: Memory Corruption - Dangerous buffer operation
    buffer = bytearray(10)
    buffer[20] = 100  # Writing out of bounds

if __name__ == "__main__":
    # Check for root privileges and warn the user if running as root
    if os.name != "nt" and os.geteuid() == 0: #CWE-285: Improper Authorization
        print("Warning: Running as root is not recommended.")
    main()
