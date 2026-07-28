import pandas as pd

master = pd.read_csv("data/processed/master_table.csv")
latest = master.dropna(subset=["energy_burden_ratio", "disposable_income", "utility_expense_est"]).iloc[-1]

print(f"年份：{int(latest['year'])}")
print(f"最低所得組平均可支配所得：約 {latest['disposable_income']/10000:.1f} 萬元")
print(f"最低所得組估算水電燃氣支出：約 {latest['utility_expense_est']/10000:.1f} 萬元")
print(f"能源負擔比：{latest['energy_burden_ratio']:.1%}")
print(f"換句話說：每 100 元收入裡，約有 {latest['energy_burden_ratio']*100:.0f} 元花在水電燃氣上")