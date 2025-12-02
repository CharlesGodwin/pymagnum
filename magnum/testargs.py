import argparse

parser = argparse.ArgumentParser(description="Process a list of strings.")
parser.add_argument('--files', nargs='+', help='A list of filenames' default=["xx"])

args = parser.parse_args()

print(f"Received files: {args.files}")
