from src.utils import MORPHS, COMBO, INC_DOM
import src.utils

def resolve_gene_name(trait):
    if trait in MORPHS:
        return trait
    for gene, data in MORPHS.items():
        if "Synonyms" in data:
            synonyms_str = str(data["Synonyms"]).strip()
            if synonyms_str and synonyms_str.lower() != 'nan':
                synonyms = [s.strip() for s in synonyms_str.split(",")]
                if trait in synonyms:
                    return gene
    return trait

def extract_name_perc(trait):
    base_trait = trait.replace("het", "").strip()
    base_trait = base_trait.replace("Super ", "").strip()
    base_trait = base_trait.replace("poss", "").strip()
    base_trait = base_trait.replace("ph ", "").strip()
    base_trait = base_trait.replace("Cross", "").strip()
    base_trait = base_trait.replace("Line", "").strip()
    base_trait = base_trait.replace("Pure", "").strip()
    perc = base_trait.split(" ")[0].replace("%","").strip()
    if not perc.isnumeric(): 
        perc = 100
        if "poss" in trait.lower():
            perc = 0.01
        elif "ph " in trait.lower() or "line" in trait.lower():
            perc = 0.01
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
    base_trait = resolve_gene_name(base_trait)

    match MORPHS[base_trait]["Type"]:
        case "incomplete":
            if "super" in trait.lower():
                parent_genes[base_trait] = [(1, 1), perc]
            else:
                parent_genes[base_trait] = [(1, 0), perc]
        case "recessive":
            if "het " in trait.lower() or "ph " in trait.lower():
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
        case "combo":
            for trait in COMBO[trait]["components"].split(","):
                identify_gene(trait.strip(), parent_genes)
        case "linebreed_combo":
            src.utils.LINEBREED_COMBO = base_trait
            for trait in COMBO[base_trait]["components"].split(","):
                identify_gene(trait.strip(), parent_genes)

def get_genes(parent):
    parent = parent["morph"].split(",")
    parent_genes = {}

    for trait in parent:
        identify_gene(trait, parent_genes)
    
    return parent_genes