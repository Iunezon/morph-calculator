from utils import *

def linebreed_calculation(sire_gene, dam_gene):
    if sire_gene == [(1, 1), 100]: 
        if dam_gene == [(1, 1), 100]:
            return [(1, 1), 100]

def punnett_square(sire_alleles, dam_alleles):
    pass

def calculate_offspring(sire, dam):
    gene_set = set(sire.keys()).union(set(dam.keys()))
    offspring = {}
    messag_poly = "I seguenti tratti sono poligenici e la loro presenza visiva potrebbe variare significativa nella prole:\n"
    message_poss = "I seguenti tratti non sono garantiti in quanto la presenza del gene nel/i genitore/i non è al 100%:\n"

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
            offspring[gene] = [(1, 1), 100]
            messag_poly += f"{gene}\n"
        else:
            offspring[gene] = punnett_square(m, f)
            if m[1] < 100 or f[1] < 100:
                message_poss += f"{gene}\n"

    message = None
    if len(messag_poly) > 0:
        message = messag_poly
    if len(message_poss) > 0:
        if message is not None:
            message += "\n" + message_poss
        else:
            message = message_poss

    return offspring, message