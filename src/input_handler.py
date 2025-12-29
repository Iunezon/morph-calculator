from utils import *

def extract_name_perc(trait):
    base_trait = trait.replace("het", "").strip()
    base_trait = base_trait.replace("Super ", "").strip()
    base_trait = base_trait.replace("poss", "").strip()
    base_trait = base_trait.replace("ph", "").strip()
    perc = base_trait.split(" ")[0].replace("%","").strip()
    if not perc.isnumeric(): 
        perc = 100
        if "poss" in trait.lower():
            perc = 1
        elif "ph" in trait.lower() or "line" in trait.lower():
            perc = 1
        elif "cross" in trait.lower():
            perc = 50
    else:
        base_trait = base_trait.replace(perc+"%", "").strip()
        perc = int(perc)
    base_trait = base_trait.replace("cross", "").strip()
    base_trait = base_trait.replace("line", "").strip()
    return base_trait, perc

def identify_gene(trait, parent_genes):
    base_trait, perc = extract_name_perc(trait)

    match MORPHS[base_trait]["Type"]:
        case "incomplete":
            if "super" in trait.lower():
                parent_genes[base_trait] = [(1, 1), perc]
            else:
                parent_genes[base_trait] = [(1, 0), perc]
        case "recessive":
            if "het" in trait.lower() or "ph" in trait.lower():
                parent_genes[base_trait] = [(0, 1), perc]
            else:
                parent_genes[base_trait] = [(1, 1), perc]
        case "co-dominant":
            parent_genes[base_trait] = [(1, 0), perc]
        case "dominant":
            parent_genes[base_trait] = [(1, 0), perc]
        case "linebreed":
            parent_genes[base_trait] = [(1, 1), perc]
        case "polygenic":
            parent_genes[base_trait] = [(1, 1), perc]
        case "combo" | "linebreed_combo":
            for trait in COMBO[trait]["components"].split(","):
                identify_gene(trait.strip(), parent_genes)

def get_genes(parent):
    parent = parent["morph"].split(",")
    parent_genes = {}

    for trait in parent:
        identify_gene(trait, parent_genes)
    
    return parent_genes