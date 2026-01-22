import argparse
from Bot.bot1_1_0 import Bot1_1_0
from Bot.bot1_1_1 import Bot1_1_1
from Bot.bot1_1_2 import Bot1_1_2
from Bot.bot1_1_3 import Bot1_1_3
from Bot.bot1_1_4 import Bot1_1_4
from Bot.bot1_2 import Bot1_2
from Bot.bot1_2_4 import Bot1_2_4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Bot type")
    parser.add_argument('--b', choices=['1.1.0', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.2', '1.2.4'], default='1.2', help='Type of bot to use')
    args = parser.parse_args()  
    if args.b == '1.1.0':
        client = Bot1_1_0()
        client.run()
    elif args.b == '1.1.1':
        client = Bot1_1_1()
        client.run()
    elif args.b == '1.1.2':
        client = Bot1_1_2()
        client.run()
    elif args.b == '1.1.3':
        client = Bot1_1_3()
        client.run()
    elif args.b == '1.1.4':
        client = Bot1_1_4()
        client.run()
    elif args.b == '1.2':
        client = Bot1_2()
        client.run()
    elif args.b == '1.2.4':
        client = Bot1_2_4()
        client.run()
