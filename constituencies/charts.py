import pandas as pd
import json

with open(
    "/Users/nikhilwoodruff/Downloads/uk-constituencies-2019-BBC.hexjson"
) as f:
    hexjson = json.load(f)

constituencies = pd.DataFrame(
    {
        "code": list(hexjson["hexes"].keys()),
        "x": [hexjson["hexes"][code]["q"] for code in hexjson["hexes"]],
        "y": [hexjson["hexes"][code]["r"] for code in hexjson["hexes"]],
    }
)
