import torch
from policyengine_uk import Microsimulation
import pandas as pd
import numpy as np
from tqdm import tqdm

# Fill in missing constituencies with average column values
import pandas as pd
import numpy as np

from policyengine_uk_data.utils.loss import (
    create_target_matrix as create_national_target_matrix,
)

import h5py

ages = pd.read_csv("targets/age.csv")
incomes = pd.read_csv("targets/income.csv")

ENGLAND_CONSTITUENCY = "E14"
NI_CONSTITUENCY = "N06"
SCOTLAND_CONSTITUENCY = "S14"
WALES_CONSTITUENCY = "W07"

incomes = incomes[
    np.any(
        [
            incomes["code"].str.contains(country_code)
            for country_code in [
                ENGLAND_CONSTITUENCY,
                NI_CONSTITUENCY,
                SCOTLAND_CONSTITUENCY,
                WALES_CONSTITUENCY,
            ]
        ],
        axis=0,
    )
]

full_constituencies = incomes.code
missing_constituencies = pd.Series(list(set(incomes.code) - set(ages.code)))
missing_constituencies = pd.DataFrame(
    {
        "code": missing_constituencies.values,
        "name": incomes.set_index("code")
        .loc[missing_constituencies]
        .name.values,
    }
)
for col in ages.columns[2:]:
    # We only have England and Wales demographics- fill in the remaining with the average age profiles among the rest of the UK.
    missing_constituencies[col] = ages[col].mean()

ages = pd.concat([ages, missing_constituencies])

sim = Microsimulation()


def create_target_matrix():
    matrix = pd.DataFrame()
    y = pd.DataFrame()

    total_income = sim.calculate("total_income", period=2025).values
    matrix["hmrc/total_income_amount"] = sim.map_result(
        total_income, "person", "household"
    )
    y["hmrc/total_income_amount"] = incomes["total_income_amount"]

    matrix["hmrc/total_income_count"] = sim.map_result(
        total_income != 0, "person", "household"
    )
    y["hmrc/total_income_count"] = incomes["total_income_count"]

    age = sim.calculate("age", period=2025)

    for lower_age in range(0, 80, 10):
        upper_age = lower_age + 10

        in_age_band = (age >= lower_age) & (age < upper_age)

        age_str = f"{lower_age}_{upper_age}"
        matrix[f"age/{age_str}"] = sim.map_result(
            in_age_band, "person", "household"
        )

        age_count = ages[
            [str(age) for age in range(lower_age, upper_age)]
        ].sum(axis=1)

        age_str = f"{lower_age}_{upper_age}"
        y[f"age/{age_str}"] = age_count.values

    return matrix, y


matrix, y = create_target_matrix()

m_national, y_national = create_national_target_matrix(
    "enhanced_frs_2022_23", 2022
)

# Weights - 650 x 100180
original_weights = np.log(sim.calculate("household_weight", 2022).values / 650)
weights = torch.tensor(
    np.ones((650, 100180)) * original_weights,
    dtype=torch.float32,
    requires_grad=True,
)
metrics = torch.tensor(matrix.values, dtype=torch.float32)
weighted_metrics = weights.unsqueeze(-1) * metrics.unsqueeze(0)
totals = weighted_metrics.sum(dim=1)
y = torch.tensor(y.values, dtype=torch.float32)
matrix_national = torch.tensor(m_national.values, dtype=torch.float32)
y_national = torch.tensor(y_national.values, dtype=torch.float32)


def loss(w):
    pred_c = (w.unsqueeze(-1) * metrics.unsqueeze(0)).sum(dim=1)
    mse_c = torch.mean((pred_c / (1 + y) - 1) ** 2)

    pred_n = (w.sum(axis=0) * matrix_national.T).sum(axis=1)
    mse_n = torch.mean((pred_n / (1 + y_national) - 1) ** 2)

    return mse_c + mse_n


optimizer = torch.optim.Adam([weights], lr=0.5)

desc = tqdm(range(100))

for epoch in desc:
    optimizer.zero_grad()
    l = loss(torch.exp(weights))
    desc.set_description(f"Loss: {l.item()}")
    l.backward()
    optimizer.step()

final_weights = torch.exp(weights).detach().numpy()

with h5py.File("weights.h5", "w") as f:
    f.create_dataset("weights", data=final_weights)
