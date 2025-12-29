from utils import *
import itertools

def get_priority(label, gene_name):
    gene_type = MORPHS[gene_name]["Type"]

    if gene_type in 'co-dominant':
        if "poss" in label:
            return 9
        return 1
    
    if gene_type == 'incomplete' and "poss" not in label:
        if "poss" in label:
            return 10
        return 2
    
    if gene_type == 'linebreed':
        try:
            pct = float(label.split('%')[0])
            return 3 if pct >= 25 else 7
        except: return 4
        
    if gene_type == 'polygenic':
        return 4
        
    if gene_type == 'recessive':
        if "het" in label:
            return 6
        if "ph" in label:
            return 8
        return 5
        
    return 100

def get_possible_outcomes(data):
    all_options = []
    
    for key, value in data.items():
        gene_choices = []
        if isinstance(value, dict):
            for status, weight in value.items():
                if weight > 0:
                    match status:
                        case 'wild': label = ""
                        case 'het':
                            if MORPHS[key]["Type"] == "recessive":
                                label = f"het {key}"
                            else:
                                label = f"{key}"
                        case 'homo': label = INC_DOM[key]["homo"] if key in INC_DOM.keys() else key
                    gene_choices.append((label, weight / 100, key))
        else:
            match value:
                case float():
                    gene_choices.append((f"{value:.2f}% {key}", 1.0, key))
                case  "":
                    gene_choices.append((f"{key}", 1.0, key))
                case _:
                    gene_choices.append((f"{value} {key}", 1.0, key))
        all_options.append(gene_choices)
    raw_combos = list(itertools.product(*all_options))

    final_results = []
    for combo in raw_combos:
        prob = 1.0
        for trait in combo:
            prob *= trait[1]
        
        active_traits = [t for t in combo if t[0]]
        
        active_traits.sort(key=lambda x: get_priority(x[0], x[2]))
        
        combo_string = " ".join([t[0] for t in active_traits])
        final_results.append((combo_string, prob * 100))

    return final_results