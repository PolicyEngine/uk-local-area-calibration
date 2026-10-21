import streamlit as st

st.title("Parliamentary constituency economic impacts")

from policyengine_uk import Microsimulation
from policyengine_core.reforms import Reform
import pandas as pd
import h5py
import numpy as np

from reform_parameters import parse_reform_parameters

weights_file = "weights.h5"

weights = h5py.File(weights_file, "r")
weights = np.array(weights["weights"])

reform_parameters_json = st.text_area(
    "Reform parameters (JSON)",
    value="{}",
    help=(
        "Each parameter path mapped to its values by period, for example "
        '{"gov.hmrc.income_tax.rates.uk[0].rate": {"2025": 0.21}}. '
        "An empty object is current law."
    ),
)
try:
    reform_parameters = parse_reform_parameters(reform_parameters_json)
except ValueError as error:
    st.error(str(error))
    st.stop()


@st.cache_data
def calculate_impacts(reform_parameters):
    reform = Reform.from_dict(reform_parameters, country_id="uk")

    baseline = Microsimulation()
    reformed = Microsimulation(reform=reform)

    baseline_hnet = baseline.calculate("household_net_income", 2025).values
    reformed_hnet = reformed.calculate("household_net_income", 2025).values
    gain = reformed_hnet - baseline_hnet
    revenue_impact = (
        reformed.calculate("gov_balance", 2025).sum() / 1e9
        - baseline.calculate("gov_balance", 2025).sum() / 1e9
    )

    return baseline_hnet, reformed_hnet, gain, revenue_impact


try:
    impacts = calculate_impacts(reform_parameters)
except ValueError as error:
    # Reform.from_dict raises ValueError for an unknown parameter path or a
    # malformed period key when the simulation applies the reform.
    st.error(f"The reform could not be applied: {error}")
    st.stop()

baseline, reformed, gain, revenue_impact = impacts

st.metric("Total revenue impact", f"£{revenue_impact:.2f}bn")

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
    missing_constituencies[col] = ages[col].mean()

ages = pd.concat([ages, missing_constituencies])

weighted_gain = np.dot(weights, gain)
populations = np.dot(weights, np.ones((100180)))
mean_gain = weighted_gain / populations

df = pd.DataFrame(
    {
        "name": incomes.name.values,
        "mean_gain": mean_gain,
    }
)

st.dataframe(df, use_container_width=True)
