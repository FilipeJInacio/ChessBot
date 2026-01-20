import argparse
from Client.client_random import Client_random
from Client.client_manual import Client_manual
from Client.client_minmax_V1 import Client_minmax
from Client.client_minmax_alpha_beta_V1 import Client_minmax_alpha_beta

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Client type")
    parser.add_argument('--c', choices=['random', 'manual', 'minmax', 'minmax_alpha_beta'], default='minmax_alpha_beta', help='Type of client to use')
    args = parser.parse_args()  
    if args.c == 'random':
        client = Client_random()
        client.run()
    elif args.c == 'manual':
        client = Client_manual()
        client.run()
    elif args.c == 'minmax':
        client = Client_minmax()
        client.run()
    elif args.c == 'minmax_alpha_beta':
        client = Client_minmax_alpha_beta()
        client.run()