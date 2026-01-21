import argparse
from Client.client_random import Client_random
from Client.client_manual import Client_manual
from Client.client_minmax_V1 import Client_minmax
from Client.client_minmax_alpha_beta_V1 import Client_minmax_alpha_beta
from Client.client_V1_1 import Client_V1_1
from Client.client_V1_2 import Client_V1_2
from Client.client_V1_3 import Client_V1_3
from Client.client_V1_4 import Client_V1_4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Client type")
    parser.add_argument('--c', choices=['random', 'manual', 'minmax', 'minmax_alpha_beta', 'V1_1', 'V1_2', 'V1_3', 'V1_4'], default='V1_2', help='Type of client to use')
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
    elif args.c == 'V1_1':
        client = Client_V1_1()
        client.run()
    elif args.c == 'V1_2':
        client = Client_V1_2()
        client.run()
    elif args.c == 'V1_3':
        client = Client_V1_3()
        client.run()
    elif args.c == 'V1_4':
        client = Client_V1_4()
        client.run()