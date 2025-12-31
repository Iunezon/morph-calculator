# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json

# Importa i tuoi moduli esistenti
# Assicurati che questi file siano nella stessa cartella o nel path
from src.calculator import calculate_offspring
from src.input_handler import get_genes
from src.morph_handler import get_possible_outcomes
from src.utils import *

app = FastAPI()

# Configurazione CORS (serve per far parlare il frontend con il backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione metti l'URL specifico del tuo sito
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definiamo la struttura dati identica al tuo JSON
class GeckoInput(BaseModel):
    morph: str

class BreedingPair(BaseModel):
    sire: GeckoInput
    dam: GeckoInput

@app.post("/calculate")
async def calculate_genetics(pair: BreedingPair):
    # 1. Preparazione dei dati come nel tuo main originale
    # pair.sire.morph arriverà come stringa: "Black Night cross,Tremper Albino,..."
    
    # Ricostruiamo i dizionari che si aspetta la tua funzione get_genes
    sire_data = {"morph": pair.sire.morph}
    dam_data = {"morph": pair.dam.morph}

    # 2. Chiamata alla tua logica esistente
    sire_genes = get_genes(sire_data)
    dam_genes = get_genes(dam_data)

    offspring, messages = calculate_offspring(sire_genes, dam_genes)
    outcomes = get_possible_outcomes(offspring)

    # 3. Formattazione della risposta
    # Ordiniamo i risultati per probabilità (dal più alto al più basso)
    sorted_outcomes = sorted(outcomes, key=lambda x: x[1], reverse=True)
    
    return {
        "results": [
            {"morph": outcome[0], "probability": round(outcome[1], 2)} 
            for outcome in sorted_outcomes
        ],
        "notes": messages
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")