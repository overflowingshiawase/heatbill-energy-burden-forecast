import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/processed/master_table.csv")
df = df.dropna(subset=["energy_burden_ratio", "annual_cdd", "electricity_price", "renewable_share"])
df = df.sort_values("year")
df = df.rename(columns={"year": "ds", "energy_burden_ratio": "y"})
df["ds"] = pd.to_datetime(df["ds"], format="%Y")

print(f"可用資料共 {len(df)} 筆，年份範圍 {df['ds'].dt.year.min()}-{df['ds'].dt.year.max()}")

train = df.iloc[:-3]
test = df.iloc[-3:]

# Baseline: Naive Forecast
naive_pred = [train["y"].iloc[-1]] * len(test)
baseline_mae = mean_absolute_error(test["y"], naive_pred)
print(f"Baseline MAE: {baseline_mae:.4f}")

# Prophet 正式模型
model = Prophet()
model.add_regressor("annual_cdd")
model.add_regressor("electricity_price")
model.add_regressor("renewable_share")
model.fit(train)

future = test[["ds", "annual_cdd", "electricity_price", "renewable_share"]]
forecast = model.predict(future)

model_mae = mean_absolute_error(test["y"], forecast["yhat"])
print(f"Prophet Model MAE: {model_mae:.4f}")
print(f"模型是否贏過Baseline: {model_mae < baseline_mae}")

forecast.to_csv("data/processed/forecast.csv", index=False)
print("已儲存預測結果到 data/processed/forecast.csv")