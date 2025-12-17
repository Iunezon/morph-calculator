import itertools

class Gene:
    def __init__(self, name, type, percent=100):
        # type: "rec" (Recessive), "inc_dom" (Incomplete Dom), "dom" (Dominant), "line" (Linebred), "poly" (Polygenic)
        self.name = name
        self.type = type
        self.percent = percent  # Used for Linebred purity

class Animal:
    def __init__(self, name, genes):
        self.name = name
        self.genes = genes # List of Gene objects or tuples (Gene, count)

# --- HELPER FUNCTIONS ---

def calculate_mendelian(sire_alleles, dam_alleles):
    """
    Standard Punnett Square Logic.
    0 = Wild Type
    1 = Mutant Allele
    Input: (0, 1) means Het. (1, 1) means Homozygous.
    """
    offspring_combos = list(itertools.product(sire_alleles, dam_alleles))
    
    # Analyze results
    results = {"wild": 0, "het": 0, "homo": 0}
    total = len(offspring_combos)
    
    for pair in offspring_combos:
        score = sum(pair)
        if score == 0: results["wild"] += 1
        elif score == 1: results["het"] += 1
        elif score == 2: results["homo"] += 1
        
    return {k: (v/total)*100 for k, v in results.items()}

def parse_linebred_value(gene_obj):
    """
    Handles your specific Linebred rules:
    - If %, use it.
    - If no %, treat as 100%.
    - If 'Cross', treat as 50%.
    - If 'Line', return special tag.
    """
    name_lower = gene_obj.name.lower()
    
    if "line" in name_lower and "cross" not in name_lower:
        return "LINE"
    
    if "cross" in name_lower:
        return 50.0
        
    # If the object has a specific percent assigned manually
    if gene_obj.percent:
        return float(gene_obj.percent)
    
    return 100.0

# --- MAIN CALCULATOR ---

def calculate_offspring(sire, dam):
    print(f"--- Crossing {sire.name} x {dam.name} ---")
    
    # We must merge the gene lists to find common loci
    # In a real app, you would use a database of gene keys. 
    # Here we map by Name for simplicity.
    
    all_gene_names = set([g.name for g in sire.genes] + [g.name for g in dam.genes])
    
    offspring_report = []

    for trait in all_gene_names:
        # Find gene objects in parents (default to None if not present)
        sire_gene = next((g for g in sire.genes if g.name == trait), None)
        dam_gene = next((g for g in dam.genes if g.name == trait), None)
        
        # Determine Gene Type (Assume both parents have same gene type for same trait name)
        g_type = sire_gene.type if sire_gene else dam_gene.type
        
        # --- LOGIC 1: LINEBRED ---
        if g_type == "line":
            val_sire = parse_linebred_value(sire_gene) if sire_gene else 0
            val_dam = parse_linebred_value(dam_gene) if dam_gene else 0
            
            if val_sire == "LINE" or val_dam == "LINE":
                offspring_report.append(f"{trait}: Line (Purity Unknown)")
            else:
                # Average the purity
                avg_purity = (val_sire + val_dam) / 2
                if avg_purity > 0:
                    offspring_report.append(f"{trait}: {avg_purity}% Purity")

        # --- LOGIC 2: POLYGENIC ---
        elif g_type == "poly":
            # Rule: Consider as Dominant but add print warning
            # If either parent has it, we assume 50% chance (Het) or 100% (if Homo logic applied)
            # For simplicity, if present, we list it with the warning.
            offspring_report.append(f"{trait}: Possible (Polygenic - can be assigned to animals that show phenotype only)")

        # --- LOGIC 3: RECESSIVE / DOMINANT / INC-DOM ---
        else:
            # Assign Alleles: 0 = Wild, 1 = Mutant
            # This requires knowing if the parent is Het or Homo.
            # For this simplified code, we will assume:
            # If gene passed in list -> Homozygous (1,1) unless marked "het" in name
            
            def get_alleles(gene):
                if not gene: return (0, 0) # Wild type
                # Check for "Het" in name strictly for Recessive
                if gene.type == "rec" and "het" in gene.name.lower():
                    return (0, 1)
                elif gene.type == "inc_dom" and "super" not in gene.name.lower():
                    return (0, 1) # Single copy (Mack Snow)
                elif gene.type == "inc_dom" and "super" in gene.name.lower():
                    return (1, 1) # Super copy (Super Snow)
                else:
                    return (1, 1) # Visual Recessive or Dominant (assumed Homo for calc)

            s_alleles = get_alleles(sire_gene)
            d_alleles = get_alleles(dam_gene)
            
            stats = calculate_mendelian(s_alleles, d_alleles)
            
            # Format Output based on Type
            if g_type == "rec":
                if stats['homo'] > 0: offspring_report.append(f"{stats['homo']}% Visual {trait}")
                if stats['het'] > 0: offspring_report.append(f"{stats['het']}% Het {trait}")
            
            elif g_type == "inc_dom":
                # Example: Mack Snow
                if stats['homo'] > 0: offspring_report.append(f"{stats['homo']}% Super {trait}")
                if stats['het'] > 0: offspring_report.append(f"{stats['het']}% {trait}")
                
            elif g_type == "dom":
                visual_chance = stats['homo'] + stats['het']
                if visual_chance > 0: offspring_report.append(f"{visual_chance}% {trait}")

    # Print Report
    print("Offspring Expectations:")
    for line in offspring_report:
        print(f" - {line}")
    print("\n")

# --- TEST CASES ---

# 1. Recessive Test: Mack Snow (Inc-Dom) x Mack Snow (Inc-Dom)
sire1 = Animal("Male", [Gene("Mack Snow", "inc_dom")])
dam1 = Animal("Female", [Gene("Mack Snow", "inc_dom")])

# 2. Linebred Test: Black Night Cross (50%) x Black Night 100%
sire2 = Animal("Male", [Gene("Black Night Cross", "line")]) # "Cross" triggers 50%
dam2 = Animal("Female", [Gene("Black Night", "line", percent=100)])

# 3. Polygenic + Recessive Test: Tangerine (Poly) + Tremper Albino (Rec)
sire3 = Animal("Male", [Gene("Tangerine", "poly"), Gene("Tremper Albino", "rec")])
dam3 = Animal("Female", [Gene("Tremper Albino", "rec")])

# Run Calcs
calculate_offspring(sire1, dam1)
calculate_offspring(sire2, dam2)
calculate_offspring(sire3, dam3)