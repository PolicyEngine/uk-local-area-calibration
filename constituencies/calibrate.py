import torch
from policyengine_uk import Microsimulation
import pandas as pd
import numpy as np
from tqdm import tqdm
import h5py

# Fill in missing constituencies with average column values
import pandas as pd
import numpy as np

from loss import (
    create_constituency_target_matrix,
    create_national_target_matrix,
)


def calibrate():
    matrix, y = create_constituency_target_matrix("enhanced_frs_2022_23", 2025)

    m_national, y_national = create_national_target_matrix(
        "enhanced_frs_2022_23", 2025
    )

    sim = Microsimulation(dataset="enhanced_frs_2022_23")

    COUNT_CONSTITUENCIES = 650

    # Weights - 650 x 100180
    original_weights = np.log(
        sim.calculate("household_weight", 2025).values / COUNT_CONSTITUENCIES
    )
    weights = torch.tensor(
        np.ones((COUNT_CONSTITUENCIES, len(original_weights)))
        * original_weights,
        dtype=torch.float32,
        requires_grad=True,
    )
    metrics = torch.tensor(matrix.values, dtype=torch.float32)
    y = torch.tensor(y.values, dtype=torch.float32)
    matrix_national = torch.tensor(m_national.values, dtype=torch.float32)
    y_national = torch.tensor(y_national.values, dtype=torch.float32)

    def loss(w):
        pred_c = (w.unsqueeze(-1) * metrics.unsqueeze(0)).sum(dim=1)
        mse_c = torch.mean((pred_c / (1 + y) - 1) ** 2)

        pred_n = (w.sum(axis=0) * matrix_national.T).sum(axis=1)
        mse_n = torch.mean((pred_n / (1 + y_national) - 1) ** 2)

        return mse_c + mse_n

    optimizer = torch.optim.Adam([weights], lr=0.1)

    desc = tqdm(range(1_000))

    for epoch in desc:
        optimizer.zero_grad()
        l = loss(torch.exp(weights))
        desc.set_description(f"Loss: {l.item()}")
        l.backward()
        optimizer.step()

        if epoch % 100 == 0:
            final_weights = torch.exp(weights).detach().numpy()

            with h5py.File("weights.h5", "w") as f:
                f.create_dataset("weight", data=final_weights)


if __name__ == "__main__":
    calibrate()
