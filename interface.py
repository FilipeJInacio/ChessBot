import argparse
from UI.UI_pygame import UI_pygame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose UI type")
    parser.add_argument('--c', choices=['pygame'], default='pygame', help='Type of user interface to use')
    args = parser.parse_args()  
    if args.c == 'pygame':
        ui = UI_pygame()
        ui.run()