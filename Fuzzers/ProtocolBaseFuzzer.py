import json
import subprocess
import random

def generate_protocol_input():
    # Generate structured inputs for the protocol.
    cases = [
        json.dumps({"numbers": [1, 2, 3]}),
        json.dumps({"numbers": [-1, -2, -3]}),
        json.dumps({"invalid_key": "string_value"}),  # Invalid structure
        json.dumps({"numbers": [99999999999999999999, 2]}),  # Large numbers
        json.dumps({"numbers": []}),  # Empty array
    ]
    return random.choice(cases)

def fuzz():
    for _ in range(100):
        protocol_input = generate_protocol_input()
        process = subprocess.run(["python", "CWEVulnerableSum.py"], input=protocol_input, text=True, capture_output=True)
        print(f"Input: {protocol_input}\nOutput: {process.stdout}\nError: {process.stderr}")

if __name__ == "__main__":
    fuzz()
