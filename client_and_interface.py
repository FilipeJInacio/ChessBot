import argparse
from GUI.GUI_pygame import GUI_pygame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose Client type")
    parser.add_argument('--c', choices=['manual'], default='manual', help='Type of GUI to use')
    args = parser.parse_args()  
    if args.c == 'manual':
        gui = GUI_pygame()
        gui.run()

