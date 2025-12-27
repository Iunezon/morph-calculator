from utils import *

def identify_gene(trait, parent_genes):
    base_trait = trait.replace("het", "").strip()
    base_trait = base_trait.replace("Super", "").strip()
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

    match MORPHS[base_trait]["Type"]:
        case "incomplete":
            if "Super" in trait.lower():
                parent_genes[base_trait] = [(1, 1), "inc", perc]
            else:
                parent_genes[base_trait] = [(1, 0), "inc", perc]
        case "recessive":
            if "het" in trait.lower():
                parent_genes[base_trait] = [(0, 1), "rec", perc]
            else:
                parent_genes[base_trait] = [(0, 1), "rec", perc]
        case "co-dominant":
            parent_genes[base_trait] = [(1, 0), "cod", perc]
        case "dominant":
            parent_genes[base_trait] = [(1, 0), "dom", perc]
        case "linebreed":
            parent_genes[base_trait] = [(1, 1), "lin", perc]
        case "polygenic":
            parent_genes[base_trait] = [(1, 1), "pol", perc]
        case "combo" | "linebreed_combo":
            for trait in COMBO[trait]["components"].split(","):
                identify_gene(trait.strip(), parent_genes)
    return

def get_genes(parent):
    parent = parent["morph"].split(",")
    parent_genes = {}

    for trait in parent:
        identify_gene(trait, parent_genes)
    
    return parent_genes