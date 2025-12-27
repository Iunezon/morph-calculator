import pandas as pd
import os

DATA_FOLDER = "data"
COMBO = pd.read_csv(os.path.join(DATA_FOLDER, "combo.csv"), index_col=0).to_dict(orient='index')
INC_DOM = pd.read_csv(os.path.join(DATA_FOLDER, "incomplete.csv"), index_col=0).to_dict(orient='index')
MORPHS = pd.read_csv(os.path.join(DATA_FOLDER, "morph_list.csv"), index_col=0).to_dict(orient='index')