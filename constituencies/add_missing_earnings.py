import pandas as pd

earnings = pd.read_csv("targets/employment_income.csv")
incomes = pd.read_csv("targets/total_income.csv")

# Earnings is missing NI numbers, so for each NI constituency, we'll find the closest match for total income amount and copy earnings distribution rows for that

missing_constituencies = list(set(incomes.code) - set(earnings.code))

codes = []
names = []
lower_bounds = []
upper_bounds = []
earnings_amounts = []
earnings_counts = []

for code in missing_constituencies:
    income = incomes[incomes.code == code].iloc[0].total_income_amount
    const_closest = incomes.iloc[(incomes.total_income_amount - income).abs().argsort()[1]].code
    earnings_closest = earnings[earnings.code == const_closest]
    for i, row in earnings_closest.iterrows():
        codes.append(code)
        names.append(incomes[incomes.code == code].iloc[0]["name"])
        lower_bounds.append(row.employment_income_lower_bound)
        upper_bounds.append(row.employment_income_upper_bound)
        earnings_amounts.append(row.employment_income_amount)
        earnings_counts.append(row.employment_income_count)

df = pd.DataFrame({
    "code": codes,
    "name": names,
    "employment_income_lower_bound": lower_bounds,
    "employment_income_upper_bound": upper_bounds,
    "employment_income_amount": earnings_amounts,
    "employment_income_count": earnings_counts
})

earnings = pd.concat([earnings, df])

earnings.to_csv("targets/employment_income.csv", index=False)
