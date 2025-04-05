import random
import subprocess

def mutate_input(seed_input):
    # Introduce mutations by modifying characters or adding random values.
    mutated = list(seed_input)
    for _ in range(random.randint(1, 5)):
        pos = random.randint(0, len(mutated) - 1)
        mutated[pos] = str(random.randint(-1000, 1000))  # Insert random numbers
    return " ".join(mutated)

def fuzz():
    seed_inputs = ["1 2 3", "5 10 15", "-5 -10 -15", "0.1 0.2 0.3"]
    for _ in range(100):  # Run 100 fuzzing attempts
        mutated_input = mutate_input(random.choice(seed_inputs))
        process = subprocess.run(["python", "CWEVulnerableSum.py"], input=mutated_input, text=True, capture_output=True)
        print(f"Input: {mutated_input}\nOutput: {process.stdout}\nError: {process.stderr}")

if __name__ == "__main__":
    fuzz()
