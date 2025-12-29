import json
from calculator import *
from morph_handler import *
from input_handler import *
from utils import *

def main():
    with open(os.path.join("test", "test_1.json"), 'r') as f:
        input_file = json.load(f)

    sire = get_genes(input_file["sire"])
    dam = get_genes(input_file["dam"])

    offspring, messages = calculate_offspring(sire, dam)
    print(offspring)

    outcomes = get_possible_outcomes(offspring)
    print(outcomes)

if __name__ == "__main__":
    main()