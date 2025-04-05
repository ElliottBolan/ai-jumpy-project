import random
import subprocess

def generate_input():
    # Generating random inputs for the vulnerable program.
    cases = [
        " ".join(str(random.randint(-1000, 1000)) for _ in range(random.randint(1, 10))),
        " ".join(str(random.uniform(-1000, 1000)) for _ in range(random.randint(1, 10))),
        "INVALID_INPUT",  # Non-numeric input
        "1000000000000000000000000000000 2",  # Large numbers
        "0 0 0 0 0",  # Edge case for division
    ]
    return random.choice(cases)

def fuzz():
    for _ in range(100):
        generated_input = generate_input()
        process = subprocess.run(["python", "CWEVulnerableSum.py"], input=generated_input, text=True, capture_output=True)
        print(f"Input: {generated_input}\nOutput: {process.stdout}\nError: {process.stderr}")

if __name__ == "__main__":
    fuzz()
