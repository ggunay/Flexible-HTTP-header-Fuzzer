# Author: Gunay Geyik
# GitHub: https://github.com/ggunay
# Description: This Python script is designed for performing HTTP request 
# fuzzing against a specified IP address. 
# It allows you to fuzz various HTTP headers and values in your request (with your exploit) 
# to test the behavior of a target web server.

import subprocess
import sys
import random
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
import threading



def generate_unique_crit_file(iteration):
    return f"crit_{iteration}.txt"

def assign_random_value(header_lines, target_header_name):
    # Find the line with the target header name
    target_lines = [line for line in header_lines if line.startswith(target_header_name + ':')]
    if not target_lines:
        return None  # Header not found

    # Select a random line with the target header name
    selected_line = random.choice(target_lines)

    # Split the line by the colon to get the header name and values
    header_name, header_value_str = selected_line.split(":", 1)

    # Split the values by commas and strip whitespace
    header_values = [value.strip() for value in header_value_str.split(",")]

    selected_value = random.choice(header_values)

    return f"\n{header_name.strip()}: {selected_value}"

def get_random_header(header_lines):

    global selected_headers

    while True:

    # Split the line by the colon to get the header name and values
        selected_line = random.choice(header_lines)
        header_name, header_value_str = selected_line.split(":", 1)
        if header_name not in selected_headers:
            break

    selected_headers.append(header_name)

    # Split the values by commas and strip whitespace
    header_values = [value.strip() for value in header_value_str.split(",")]

    # Randomly select a value for the header
    selected_value = random.choice(header_values)

    return f"\n{header_name.strip()}: {selected_value}"


def run_command(command, iteration):
    try:
        for cmd in command:
            subprocess.run(cmd, shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}.")
        exit(1)
    except Exception as e:
        print(f"An error occurred while running the command: {str(e)}")
        exit(1)
    finally:
        semaphore.release()  # Release the semaphore

# Check if the correct number of command-line arguments is provided
parser = argparse.ArgumentParser(description="Fuzzing Script")
parser.add_argument("ip_address", help="IP address")
parser.add_argument("num_iterations", type=int, help="Number of iterations")
parser.add_argument("--fixed_headers", help="[Optional] comma-separated list of headers to include in every request")
args = parser.parse_args()

ip_address = args.ip_address
num_iterations = args.num_iterations
fixed_headers = args.fixed_headers.split(",") if args.fixed_headers else []

selected_headers = []

semaphore = threading.Semaphore(num_iterations)

# Read headers from a separate file
with open('headers.txt', 'r') as headers_file:
    headers = headers_file.read().splitlines()

# Define the base request with placeholders for the headers to fuzz, endpoint to be updated
base_request = """POST /your_endpoint HTTP/1.1
Host: {ip_address}:443""".format(
    ip_address=ip_address
)
#value to be updated depending on your exploit (hexdump.txt)
tail = "\n\n1"

# Run the first command only once
subprocess.run("awk -F' ' '{print $2$3$4$5$6$7$8$9}' hexdump.txt | xxd -r -p > output.bin", shell=True, check=True)
crit_file_paths = []
#total_requests = 0
with ThreadPoolExecutor(max_workers=10) as executor:


# Execute the commands with different headers and values
        for iteration in range(num_iterations):  
            semaphore.acquire()
            selected_headers = []
            fuzzed_request = ''
            final_request = ''
            for optional_header in fixed_headers:
                selected_headers.append(optional_header)
                fuzzed_request += assign_random_value(headers, optional_header)
            # Randomly choose values for the remaining headers
            num_headers = random.randint(1, 10)
            # Initialize the headers string
            headers_string = ""

            # Generate random headers and values
            for _ in range(num_headers):

                fuzzed_request +=get_random_header(headers)
            final_request = base_request + fuzzed_request + tail
            crit_file_path = generate_unique_crit_file(iteration)
            crit_file_paths.append(crit_file_path)
            with open(crit_file_path, "w") as crit_file:
                crit_file.write(final_request)

            # Run the commands with the modified crit.txt
            commands = [
                f"cat output.bin >> {crit_file_path}",
                f"cat {crit_file_path} | openssl s_client -connect {ip_address}:443"
            ]

            executor.submit(run_command, commands, iteration)

# Delete the unique crit.txt files after running all commands, avoiding potential race conditions
for crit_file_path in crit_file_paths:
    try:
        os.remove(crit_file_path)
    except Exception as e:
        print(f"Failed to delete '{crit_file_path}': {str(e)}")
print("All fuzzing iterations completed.")
