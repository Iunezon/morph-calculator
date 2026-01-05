from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import csv
import os
import sys

# --- GESTIONE PERCORSI ---
# Capiamo dove ci troviamo.
# __file__ è il percorso di questo file (src/api.py).
# Il genitore è 'src', il genitore del genitore è la root del progetto.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) # La cartella 'morph-calculator'
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Assicuriamoci che python veda i moduli in src
sys.path.append(CURRENT_DIR)

# Importa i tuoi moduli
# Nota: se lanci da root come modulo, 'src.' è corretto.
# Se ci sono problemi di import, python cercherà anche grazie al sys.path.append sopra.
from src.calculator import calculate_offspring
from src.input_handler import get_genes
from src.morph_handler import get_possible_outcomes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Montiamo la cartella static (CSS/JS) usando il percorso assoluto
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"ATTENZIONE: Cartella static non trovata in {STATIC_DIR}")

# 2. Rotta Home Page
@app.get("/")
async def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": f"File index.html non trovato in {STATIC_DIR}"}

# --- MODELLI ---
class GeckoInput(BaseModel):
    morph: str

class BreedingPair(BaseModel):
    sire: GeckoInput
    dam: GeckoInput

# --- ENDPOINTS ---
@app.get("/morphs")
def get_morph_list():
    morphs = []
    # Puntiamo dritti alla cartella data/
    file_path = os.path.join(DATA_DIR, "morph_list.csv")
    
    if not os.path.exists(file_path):
        print(f"Errore: CSV non trovato in {file_path}")
        return []

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                morph_name = row.get("Morph", "").strip()
                morph_type = row.get("Type", "").strip()
                synonyms = row.get("Synonyms", "").strip()
                
                if morph_name:
                    morphs.append({
                        "name": morph_name,
                        "type": morph_type,
                        "synonyms": synonyms
                    })
        return morphs
    except Exception as e:
        print(f"Errore lettura CSV: {e}")
        return []

@app.post("/calculate")
async def calculate_genetics(pair: BreedingPair):
    sire_data = {"morph": pair.sire.morph}
    dam_data = {"morph": pair.dam.morph}

    sire_genes = get_genes(sire_data)
    dam_genes = get_genes(dam_data)

    offspring, messages = calculate_offspring(sire_genes, dam_genes)
    outcomes, phenotypes = get_possible_outcomes(offspring)

    sorted_outcomes = sorted(outcomes, key=lambda x: x[1], reverse=True)
    sorted_phenotypes = sorted(phenotypes, key=lambda x: x[1], reverse=True)
    
    def format_prob(p):
        p_rounded = round(p, 2)
        return str(int(p_rounded)) if p_rounded % 1 == 0 else f"{p_rounded:.2f}"
    
    return {
        "genotypes": [
            {"morph": outcome[0], "probability": format_prob(outcome[1])} 
            for outcome in sorted_outcomes
        ],
        "phenotypes": [
            {"morph": item[0], "probability": format_prob(item[1])}
            for item in sorted_phenotypes
        ],
        "notes": messages
    }