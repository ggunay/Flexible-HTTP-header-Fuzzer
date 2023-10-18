# Flexible HTTP Header Fuzzing

This Python script is designed for performing HTTP request fuzzing against a specified IP address. It allows you to fuzz various HTTP headers and values in your request (with your exploit) to test the behavior of a target web server. Ideal for testing if a fix really fixes the vulnerability.

## Prerequisites

Before using this script, make sure you have the following prerequisites:

- Python 3.x
- OpenSSL installed on your system
- A text file containing a list of HTTP headers (headers.txt)
- A hexdump file (hexdump.txt) to generate the POST input data, probably with your exploit

## Usage

1. Clone this repository to your local machine:

   ```shell
   git clone 
   ```
2. Copy your hexdump.txt to the same directory

3. Update your endpoint and "tail" inside the script, depending on your hexdump.txt

4. Run the following command:
```shell
sudo python3 header_fuzzing_script.py <ip_address> <num_iterations> --fixed_headers <fixed_headers_seperated_by_comma>
```
E.g.:
```shell
sudo python3 header_fuzzing_script.py <IP> 100 --fixed_headers "Transfer-Encoding","Content-Type","Content-Length","Connection"
```

<ip_address>: The IP address of the target server.

<num_iterations>: The number of fuzzing iterations to perform.

--fixed_headers <fixed_headers> (optional): A comma-separated list of headers to include in every request.

3. The script will generate unique crit.txt files for each iteration and run the specified number of fuzzing iterations in parallel.

# Contributing

Feel free to improve the script, especially the concurrency and by adding new header values

# Author

Gunay Geyik
