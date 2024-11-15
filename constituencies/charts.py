import pandas as pd
import json
from pathlib import Path

constituencies = Path(__file__).parent / "hex_map" / "hex_map_2024.csv"
constituencies = pd.read_csv(constituencies)
