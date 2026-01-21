import argparse
from Bot.bot1_1 import Bot1_1
from Bot.bot1_2 import Bot1_2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Bot type")
    parser.add_argument('--b', choices=['1.1', '1.2'], default='1.2', help='Type of bot to use')
    args = parser.parse_args()  
    if args.b == '1.1':
        client = Bot1_1()
        client.run()
    elif args.b == '1.2':
        client = Bot1_2()
        client.run()