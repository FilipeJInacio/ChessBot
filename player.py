import argparse
from Client.client_random import Client_random
from Client.client_manual import Client_manual

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Client type")
    parser.add_argument('--c', choices=['random', 'manual'], default='random', help='Type of client to use')
    args = parser.parse_args()  
    if args.c == 'random':
        client = Client_random()
        client.run()
    elif args.c == 'manual':
        client = Client_manual()
        client.run()
    
