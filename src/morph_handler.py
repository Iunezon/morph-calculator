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
            return 5 if pct >= 25 else 7
        except: return 4

    if gene_type == 'linebreed_combo':
        return 2.5
        
    if gene_type == 'polygenic':
        return 2.7
        
    if gene_type == 'recessive':
        if "het" in label:
            return 6
        if "ph" in label:
            return 8
        return 3
    
    if gene_type == 'combo':
        if "het" in label:
            return 5.5
        if "ph" in label:
            return 7.5
        return 2.6
        
    return 100


def reconstruct_combo(label):
    genes = [item[0] for item in label]
    visuals = {g for g in genes if not (g.startswith('het') or g.startswith('poss') or g.startswith('ph'))}
    hets = {g.replace('het ', '') for g in genes if g.startswith('het ')}
    ph = {g.replace('ph ', '') for g in genes if g.startswith('ph ')}
    new_morph = []
    possible_combos = {"visuals": {}, "hets": {}, "ph": {}}

    def get_combo_if_exists(k, parts, data):
        if parts.issubset(data):
            return parts
        return None

    def remove_combo_parts(k, parts, data, prefix=""):
        if parts.issubset(data):
            for part in parts:
                if prefix + part in genes:
                    genes.remove(prefix + part)
                    data.remove(part)
            return prefix+k

    for k, v in COMBO.items():
        if type(v["temperature"]) != str and MORPHS[k]["Type"] != "linebreed_combo":
            parts = set(v["components"].split(","))
            
            res_v = get_combo_if_exists(k, parts, visuals)
            if res_v: possible_combos["visuals"][k] = res_v
            
            res_h = get_combo_if_exists(k, parts, hets)
            if res_h: possible_combos["hets"][k] = res_h
            
            res_p = get_combo_if_exists(k, parts, ph)
            if res_p: possible_combos["ph"][k] = res_p
    
    for category, found_dict in possible_combos.items():
        if found_dict:
            sorted_combos = dict(sorted(found_dict.items(), key=lambda item: len(item[1]), reverse=True))
            
            for k2, parts in sorted_combos.items():
                if category == "visuals":
                    res = remove_combo_parts(k2, parts, visuals)
                elif category == "hets":
                    res = remove_combo_parts(k2, parts, hets, "het ")
                else:
                    res = remove_combo_parts(k2, parts, ph, "ph ")
                
                if res:
                    new_morph.append((res, k2))

    untouched_genes = []
    for gene in genes:
        gene_name = gene
        if "%" in gene:
            gene_name = gene.split('%')[1].strip()
        if "super" in gene.lower():
            gene_name = gene.replace("super ", "")
            gene_name = gene.replace("Super ", "")
        if gene.startswith('het '):
            gene_name = gene.replace('het ', '')
        elif gene.startswith('ph '):
            gene_name = gene.replace('ph ', '')
        untouched_genes.append((gene, gene_name))
    return new_morph + untouched_genes

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
        final_traits = reconstruct_combo(active_traits)
        final_traits.sort(key=lambda x: get_priority(x[0], x[1]))
        combo_string = " ".join(final_traits[0] for final_traits in final_traits)
        final_results.append((combo_string, prob * 100))

    return final_results