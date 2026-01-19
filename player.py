import argparse
from Client.client_random import Client_random

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Client type")
    parser.add_argument('--client', choices=['random'], default='random', help='Type of client to use')
    args = parser.parse_args()  
    if args.client == 'random':
        client = Client_random()
        client.run()
