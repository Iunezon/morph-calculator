import itertools
from utils import *

def linebreed_calculation(sire_gene, dam_gene):
    if sire_gene[0] == (1, 1): 
        if dam_gene[0] == (0, 0):
            return sire_gene[1]/2
        perc = (sire_gene[1] + dam_gene[1]) / 2
        return perc
    return dam_gene[1]/2

def punnett_square(sire_gene, dam_gene):
    sire_alleles, dam_alleles = sire_gene[0], dam_gene[0]
    s_pass_prob = sire_gene[1] * 0.5
    d_pass_prob = dam_gene[1] * 0.5
    s_weights = {0: 100 - s_pass_prob, 1: s_pass_prob}
    d_weights = {0: 100 - d_pass_prob, 1: d_pass_prob}
    offspring_combos = list(itertools.product(sire_alleles, dam_alleles))
    
    results = {"wild": 0.0, "het": 0.0, "homo": 0.0}
    
    for s_allele, d_allele in offspring_combos:
        score = s_allele + d_allele
        combo_prob = (s_weights[s_allele] / 100) * (d_weights[d_allele] / 100)
        
        if score == 0: results["wild"] += combo_prob
        elif score == 1: results["het"] += combo_prob
        elif score == 2: results["homo"] += combo_prob
    
    return {k: round(v * 100, 2) for k, v in results.items()}

def calculate_offspring(sire, dam):
    gene_set = set(sire.keys()).union(set(dam.keys()))
    offspring = {}
    messag_poly = "I seguenti tratti sono poligenici e la loro presenza visiva potrebbe variare significativa nella prole:\n"
    message_poss = "I seguenti tratti non sono garantiti in quanto la presenza del gene nel/i genitore/i non è al 100%:\n"
    message_ph = "I seguenti tratti non sono garantiti in quanto non si conosce la percentuale esatta della presenza del gene in almeno uno dei genitori:\n"

    for gene in gene_set:
        gene_type = MORPHS[gene]["Type"]
        if gene in sire: 
            m = sire[gene]
            if gene in dam:
                f = dam[gene]
            else:
                f = [(0, 0), 100]
        else:
            f = dam[gene]
            m = [(0, 0), 100]
        if gene_type == "linebreed":
            offspring[gene] = linebreed_calculation(m, f)
        elif gene_type == "polygenic":
            offspring[gene] = ""
            messag_poly += f"{gene}\n"
        else:
            if dam[gene][1] == 1 and sire[gene][1] == 1:
                if gene_type == "recessive":
                    offspring[gene] = "ph"
                    message_ph += f"{gene}\n"
                else:
                    offspring[gene] = "poss"
                    message_poss += f"{gene}\n"
            else:   
                offspring[gene] = punnett_square(m, f)
                if m[1] < 100 or f[1] < 100:
                    message_poss += f"{gene}\n"

    message = None
    if len(messag_poly.split("\n")) > 2:
        message = messag_poly
    if len(message_poss.split("\n")) > 2:
        if message is not None:
            message += "\n" + message_poss
        else:
            message = message_poss
    if len(message_ph.split("\n")) > 2:
        if message is not None:
            message += "\n" + message_ph
        else:
            message = message_ph

    return offspring, message