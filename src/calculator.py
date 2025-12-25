import itertools
from collections import Counter

class Gene:
    def __init__(self, name, type, percent=100):
        self.name = name
        self.type = type
        self.percent = percent 

class Animal:
    def __init__(self, gender, genes):
        self.gender = gender
        self.genes = genes

def get_linebred_label(trait_name, percent):
    """Applica le regole di naming precise per le percentuali linebred"""
    if percent <= 0: return None
    if percent == 100: return trait_name
    # Restituisce sempre la percentuale prima del nome se non è 100%
    return f"{percent:g}% {trait_name}"

def get_sort_priority(trait_part):
    """
    1. Co-dom / Inc-dom
    2. Rec (se homo/visual)
    3. Linea (se puro/100%)
    4. Polygenic
    5. Linea (se > 35% e < 100%, incl. cross)
    6. Rec (se het)
    7. Rec (se ph)
    8. Linea (se <= 35%, 'line')
    """
    name = trait_part.lower()
    
    # 1 & 2. Super e Inc-Dom/Rec Visuali
    if "super" in name: return 1
    # Se è un nome pulito senza %, het, ph, cross, line è un visual o un puro
    if not any(x in name for x in ["%", "het", "ph", "cross", "line"]):
        # Trattiamo i nomi mendeliani come priorità 2, linebred puri come 3
        return 2 
    
    if "possible" in name: return 4
    
    # 5. Linea con percentuale (es. 75% o 25%)
    if "%" in name:
        # Estraiamo il numero per distinguere tra alte percentuali e 'line'
        try:
            val = float(name.split("%")[0])
            return 5 if val > 35 else 8
        except: return 5
        
    if "het" in name and "ph" not in name: return 6
    if "ph" in name: return 7
    if "line" in name: return 8
    
    return 10

def get_offspring_genotypes(sire, dam):
    all_traits_info = {}
    for g in sire.genes + dam.genes:
        base = g.name.lower().replace("cross", "").replace("line", "").strip().title()
        # Se un tratto è marcato come 'line' in un genitore, lo trattiamo come tale
        all_traits_info[base] = g.type
    
    trait_possibilities = []

    for trait_name, g_type in all_traits_info.items():
        s_gene = next((g for g in sire.genes if trait_name in g.name.title()), None)
        d_gene = next((g for g in dam.genes if trait_name in g.name.title()), None)

        if g_type == "line":
            val_s = s_gene.percent if s_gene else 0
            val_d = d_gene.percent if d_gene else 0
            avg = (val_s + val_d) / 2
            label = get_linebred_label(trait_name, avg)
            trait_possibilities.append([(label, 1.0)])
        
        else:
            def get_mendelian_outcomes(g_s, g_d, t_name, t_type):
                def get_prob_dist(gene):
                    if not gene: return {(0,0): 1.0}
                    p_val = gene.percent / 100.0
                    if t_type == "rec" and gene.percent < 100:
                        return {(0,1): p_val, (0,0): 1 - p_val}
                    if t_type == "inc_dom" and "super" not in gene.name.lower(): return {(0,1): 1.0}
                    return {(1,1): 1.0}

                dist_s = get_prob_dist(g_s)
                dist_d = get_prob_dist(g_d)
                
                final_outcomes = Counter()
                for alleles_s, prob_s in dist_s.items():
                    for alleles_d, prob_d in dist_d.items():
                        for a_s in alleles_s:
                            for a_d in alleles_d:
                                score = a_s + a_d
                                prob = (prob_s * prob_d) * 0.25
                                if score == 0: res = None
                                elif score == 1:
                                    # Se la probabilità totale di questo Het è < 1.0 nel set mendeliano, è ph
                                    # Ma per semplicità seguiamo la tua etichetta:
                                    res = f"ph {t_name}" if (prob_s * prob_d) < 1.0 and t_type == "rec" else f"Het {t_name}"
                                    if t_type != "rec": res = t_name
                                else:
                                    res = f"Super {t_name}" if t_type == "inc_dom" else t_name
                                final_outcomes[res] += prob
                return final_outcomes

            outcomes = get_mendelian_outcomes(s_gene, d_gene, trait_name, g_type)
            trait_possibilities.append([(n, p) for n, p in outcomes.items()])

    final_morphs = Counter()
    for combo in itertools.product(*trait_possibilities):
        prob = 1.0
        parts = []
        for name, p in combo:
            prob *= p
            if name: parts.append(name)
        
        parts.sort(key=get_sort_priority)
        full_name = " ".join(parts) if parts else "Wild Type"
        final_morphs[full_name] += prob

    return final_morphs

def print_report(sire, dam):
    print(f"--- Crossing {sire.gender} x {dam.gender} ---")
    results = get_offspring_genotypes(sire, dam)
    print("Offspring Expectations:")
    for morph, chance in sorted(results.items(), key=lambda x: x[1], reverse=True):
        if chance > 0:
            print(f"{chance*100:g}% - {morph}")
    print("\n")

# --- TEST ---
sire = Animal("Male", [Gene("Tremper", "rec", percent=66), Gene("Black Night", "line", percent=50)])
dam = Animal("Female", [Gene("Mandarin Tangerine", "line", percent=50), Gene("Black Night", "line", percent=50), Gene("Tremper", "rec", percent=33)])

print_report(sire, dam)