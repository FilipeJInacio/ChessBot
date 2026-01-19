import argparse
from UI.UI_terminal import UI_terminal
from UI.UI_pygame import UI_pygame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose UI type")
    parser.add_argument('--ui', choices=['terminal', 'pygame'], default='pygame', help='Type of user interface to use')
    args = parser.parse_args()  
    if args.ui == 'terminal':
        ui = UI_terminal()
        ui.run()
    elif args.ui == 'pygame':
        ui = UI_pygame()
        ui.run()