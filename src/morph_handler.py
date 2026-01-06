from src.utils import MORPHS, COMBO, INC_DOM
import src.utils
import itertools
from collections import defaultdict

def get_priority(label, gene_name):
    gene_type = MORPHS[gene_name]["Type"]

    if gene_type in 'dominant':
        return 0

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
            return 2.7 if pct > 24 else 7
        except: return 2.8

    if gene_type == 'linebreed_combo':
        return 2.5
        
    if gene_type == 'polygenic':
        return 2.9
        
    if gene_type == 'recessive':
        if "het" in label:
            return 6
        if "ph" in label:
            if "%" in label:
                return 7.9
            else:
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
    
    def get_combo_if_exists(parts, data):
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
    
    genes = [item[0] for item in label]
    visuals = {g for g in genes if not (g.startswith('het') or g.startswith('poss') or 'ph' in g)}
    initial_has_visuals = bool(visuals)
    hets = {g.replace('het ', '') for g in genes if g.startswith('het ')}
    ph_groups = defaultdict(set)
    for g in genes:
        if 'ph ' in g:
            parts = g.split('ph ', 1)
            prefix = parts[0].strip()
            gene = parts[1].strip()
            ph_groups[prefix].add(gene)
    new_morph = []
    possible_combos = {"visuals": {}, "hets": {}, "ph": defaultdict(dict)}

    untouched_genes = []

    for k, v in COMBO.items():
        if MORPHS[k]["Type"] != "linebreed_combo" or k == src.utils.LINEBREED_COMBO:
            parts = set(v["components"].split(","))
            
            res_v = get_combo_if_exists(parts, visuals)
            if res_v: possible_combos["visuals"][k] = res_v
            
            res_h = get_combo_if_exists(parts, hets)
            if res_h: possible_combos["hets"][k] = res_h
            
            for prefix, genes_in_prefix in ph_groups.items():
                res_p = get_combo_if_exists(parts, genes_in_prefix)
                if res_p:
                    possible_combos["ph"][prefix][k] = res_p
    
    for category, found_dict in possible_combos.items():
        if found_dict:
            if category == "ph":
                for prefix, combos in found_dict.items():
                    sorted_combos = dict(sorted(combos.items(), key=lambda item: len(item[1]), reverse=True))

                    for k, parts in sorted_combos.items():
                        if k == src.utils.LINEBREED_COMBO and len(parts) != len(genes):
                            continue
                        full_prefix = "ph " if prefix == '' else prefix + " ph "
                        res = remove_combo_parts(k, parts, ph_groups[prefix], full_prefix)
                        if res:
                            new_morph.append((res, k))
            else:
                sorted_combos = dict(sorted(found_dict.items(), key=lambda item: len(item[1]), reverse=True))

                for k, parts in sorted_combos.items():
                    if k == src.utils.LINEBREED_COMBO and len(parts) != len(genes):
                        continue
                    if category == "visuals":
                        res = remove_combo_parts(k, parts, visuals)
                    elif category == "hets":
                        res = remove_combo_parts(k, parts, hets, "het ")
                    if res:
                        new_morph.append((res, k))

    for gene in genes:
        gene_name = gene
        if "%" in gene:
            gene_name = gene.split('%')[1].strip()
            if gene_name.startswith('ph '):
                gene_name = gene_name.replace('ph ', '')
                if "." in gene:
                    decimals = gene.split("%")[0].split(".")[1]
                    gene = gene.replace(f".{decimals}", "")
        if "cross" in gene:
            gene_name = gene.replace("cross", "").strip()
        if "line" in gene:
            gene_name = gene.replace("line", "").strip()
        if "super" in gene.lower():
            gene_name = gene.replace("super ", "")
            gene_name = gene.replace("Super ", "")
        if gene.startswith('het '):
            gene_name = gene.replace('het ', '')
        elif gene.startswith('ph '):
            gene_name = gene.replace('ph ', '')
        untouched_genes.append((gene, gene_name))
    
    if not initial_has_visuals:
        untouched_genes.append(("Normal", "Normal"))
    return new_morph + untouched_genes

def merge_probs(morphs):
    hets_counter = {}

    for traits, _ in morphs:
        for trait in traits:
            gene_name = trait[-1]
            gene_type = MORPHS[gene_name]["Type"]
            if gene_type == "recessive":
                if "het" in trait[0]:
                    if gene_name in hets_counter.keys():
                        hets_counter[gene_name] += 1
                    else:
                        hets_counter[gene_name] = 1
    
    new_morphs = {}
    def format_pct(p):
        p_rounded = round(p, 0)
        pct_str = f"{p_rounded:.2f}".rstrip('0').rstrip('.')
        return pct_str + "% ph"
    
    for morph, pct in morphs:
        new_morph = []
        for trait in morph:
            if trait[-1] in hets_counter.keys():
                if "het" in trait[0]:
                    calc_pct = float(hets_counter[trait[-1]] / len(morphs)) * 100
                    if (calc_pct >= 50 and MORPHS[trait[-1]]["Type"] == "recessive") or calc_pct == 100:
                        new_morph.append(trait)
                    else:
                        new_label = trait[0].replace("het", format_pct(calc_pct))
                        new_morph.append((new_label, trait[-1]))
                else:
                    new_morph.append((trait[0], trait[-1]))
            else:
                new_morph.append((trait[0], trait[-1]))
        for rec in hets_counter.keys():
            if not rec in [t[-1] for t in morph]:
                calc_pct = float(hets_counter[rec] / len(morphs)) * 100
                if (calc_pct >= 50 and MORPHS[rec]["Type"] == "recessive") or calc_pct == 100:
                    new_morph.append((f"het {rec}", rec))
                else:
                    new_morph.append((format_pct(calc_pct) + f" {rec}", rec))
        if tuple(sorted(new_morph)) in new_morphs:
            new_morphs[tuple(sorted(new_morph))] += pct
        else:
            new_morphs[tuple(sorted(new_morph))] = pct
    
    return new_morphs

def generate_morph_name(final_traits, active_traits):
    combo_string = " ".join(final_traits[0] for final_traits in final_traits).replace(".0", "")
    if src.utils.LINEBREED_COMBO:
        print("here")
        current_morphs = set(trait[0] for trait in active_traits)
        required_morphs = set(COMBO[src.utils.LINEBREED_COMBO]["components"].split(","))
        if current_morphs != required_morphs:
            is_maker = True
            for req in required_morphs:
                req = req.replace("Super ", "")
                if MORPHS[req]["Type"] == "linebreed":
                    for trait in active_traits:
                        if MORPHS[trait[-1]]["Type"] == "linebreed":
                            if trait[-1] != trait[0]:
                                is_maker = False
            if is_maker:
                combo_string += f" {src.utils.LINEBREED_COMBO} maker"
    return combo_string

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
                case float() | int():
                    if value < 92:
                        gene_choices.append((f"{round(value,0)}% {key}", 1.0, key))
                    else:
                        gene_choices.append((f"{key}", 1.0, key))
                case  "":
                    gene_choices.append((f"{key}", 1.0, key))
                case _:
                    gene_choices.append((f"{value} {key}", 1.0, key))
        all_options.append(gene_choices)
    raw_combos = list(itertools.product(*all_options))

    possible_phenotypes = []
    genotypes = []
    for combo in raw_combos:
        prob = 1.0
        for trait in combo:
            prob *= trait[1]
        
        active_traits = [t for t in combo if t[0]]
        for trait in active_traits:
            if "%" in trait[0] and "ph" not in trait[0]:
                pct, name = trait[0].split("% ")
                if float(pct) == 50:
                    active_traits.remove(trait)
                    active_traits.append((name + " cross", trait[1], trait[2]))
                elif float(pct) < 25:
                    active_traits.remove(trait)
                    active_traits.append((name + " line", trait[1], trait[2]))
        possible_phenotypes.append([active_traits, prob])
        final_traits = reconstruct_combo(active_traits)
        final_traits.sort(key=lambda x: get_priority(x[0], x[1]))
        combo_string = generate_morph_name(final_traits, active_traits)
        genotypes.append((combo_string, prob * 100))
    
    phenotypes = []
    for morph, pct in merge_probs(possible_phenotypes).items():
        final_traits = reconstruct_combo(list(morph))
        final_traits.sort(key=lambda x: get_priority(x[0], x[1]))
        combo_string = generate_morph_name(final_traits, active_traits)
        phenotypes.append((combo_string, pct * 100))

    return genotypes, phenotypes