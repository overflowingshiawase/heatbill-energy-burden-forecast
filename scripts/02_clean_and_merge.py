import pandas as pd
import numpy as np

# ========== 1. 電價（已知格式，直接處理）==========
price_df = pd.read_csv("data/raw/taipower_price.csv")
price_df = price_df[["年度", "平均單價合計(元)"]].rename(
    columns={"年度": "year", "平均單價合計(元)": "electricity_price"}
)
print(f"✅ 電價資料：{len(price_df)} 筆，年份範圍 {price_df['year'].min()}-{price_df['year'].max()}")

# ========== 2. 能源統計（已知複雜表頭，用iloc直接定位）==========
raw_energy = pd.read_excel("data/raw/energy_statistics.xlsx", header=None)
# 第0欄是年度(民國年，如"96年")，第15欄是再生能源發電占比
energy_rows = raw_energy.iloc[3:].copy()  # 前3列是表頭說明，從第4列開始才是真正資料
energy_rows = energy_rows[[0, 15]]
energy_rows.columns = ["roc_year", "renewable_share"]
energy_rows = energy_rows.dropna(subset=["roc_year"])
# 過濾掉不是"XX年"格式的雜訊列
energy_rows = energy_rows[energy_rows["roc_year"].astype(str).str.contains("年", na=False)]
energy_rows["year"] = energy_rows["roc_year"].astype(str).str.replace("年", "").astype(int) + 1911
energy_rows["renewable_share"] = pd.to_numeric(energy_rows["renewable_share"], errors="coerce")
energy_df = energy_rows[["year", "renewable_share"]].dropna()
print(f"✅ 能源統計：{len(energy_df)} 筆，年份範圍 {energy_df['year'].min()}-{energy_df['year'].max()}")
if len(energy_df) == 0:
    print("⚠️ 需要人工確認：能源統計解析結果是0筆，請把 raw_energy.iloc[3:8] 的印出結果貼給Claude")
    print(raw_energy.iloc[3:8])

# ========== 3. 氣溫資料（月曆式格式，需轉置＋補年份）==========
import glob
temp_files = sorted(glob.glob("data/raw/taipei_temp_*.csv"))
all_weather = []
for f in temp_files:
    year = int(f.split("_")[-1].replace(".csv", ""))
    df = pd.read_csv(f)
    df = df.rename(columns={df.columns[0]: "day"})
    # 轉置：月份欄位變成一列，溫度變成值
    long_df = df.melt(id_vars="day", var_name="month", value_name="avg_temp")
    long_df["year"] = year
    long_df["month"] = pd.to_numeric(long_df["month"], errors="coerce")
    long_df["day"] = pd.to_numeric(long_df["day"], errors="coerce")
    long_df["avg_temp"] = pd.to_numeric(long_df["avg_temp"], errors="coerce")
    all_weather.append(long_df)

weather_long = pd.concat(all_weather, ignore_index=True)
weather_long = weather_long.dropna(subset=["day", "month", "avg_temp"])
# 過濾不存在的日期（例如2月30日）
weather_long = weather_long[weather_long["day"] <= 31]

# 計算冷房度日 CDD，年度加總
base_temp = 26
weather_long["cdd_daily"] = (weather_long["avg_temp"] - base_temp).clip(lower=0)
annual_cdd = weather_long.groupby("year")["cdd_daily"].sum().reset_index()
annual_cdd.columns = ["year", "annual_cdd"]
print(f"✅ 氣溫資料：{len(weather_long)} 筆逐日資料，年度CDD如下：")
print(annual_cdd)

# ========== 4. 家庭可支配所得（欄位名稱未知，自動搜尋關鍵字）==========
income_raw = pd.read_csv("data/raw/household_disposable_income.csv")
print("家庭可支配所得原始欄位：", income_raw.columns.tolist())
year_col = [c for c in income_raw.columns if "年" in c][0]
income_col_candidates = [c for c in income_raw.columns if "最低" in c and ("可支配" in c or "所得" in c)]
if income_col_candidates:
    income_col = income_col_candidates[0]
    income_df = income_raw[[year_col, income_col]].rename(
        columns={year_col: "year", income_col: "disposable_income"}
    )
    income_df["year"] = pd.to_numeric(income_df["year"], errors="coerce")
    income_df["disposable_income"] = pd.to_numeric(income_df["disposable_income"], errors="coerce")
    income_df = income_df.dropna()
    print(f"✅ 找到最低所得組欄位「{income_col}」，共 {len(income_df)} 筆")
else:
    print("⚠️ 需要人工確認：找不到「最低所得組」相關欄位，請把上面印出的欄位清單貼給Claude")
    income_df = pd.DataFrame(columns=["year", "disposable_income"])

# ========== 5. 消費結構占比 ==========
struct_df = pd.read_csv("data/raw/consumption_structure.csv")
util_col = [c for c in struct_df.columns if "水電" in c][0]
year_col2 = [c for c in struct_df.columns if "年" in c][0]
struct_df = struct_df[[year_col2, util_col]].rename(
    columns={year_col2: "year", util_col: "utility_share_pct"}
)
struct_df["year"] = pd.to_numeric(struct_df["year"], errors="coerce")
struct_df["utility_share_pct"] = pd.to_numeric(struct_df["utility_share_pct"], errors="coerce")
struct_df = struct_df.dropna()
print(f"✅ 消費結構占比：{len(struct_df)} 筆")

# ========== 5b. 最低所得組總消費支出（其實已經在income_raw裡，不用另外讀.xls）==========
consumption_col = [c for c in income_raw.columns if "消費支出" in c and "最低" in c][0]
cons_data = income_raw[[year_col, consumption_col]].rename(
    columns={year_col: "year", consumption_col: "lowest_consumption"}
)
cons_data["year"] = pd.to_numeric(cons_data["year"], errors="coerce")
cons_data["lowest_consumption"] = pd.to_numeric(cons_data["lowest_consumption"], errors="coerce")
cons_data = cons_data.dropna()
print(f"✅ 最低所得組總消費支出：{len(cons_data)} 筆")

# ========== 6. 完整合併 ==========
master = price_df.merge(energy_df, on="year", how="outer")
master = master.merge(annual_cdd, on="year", how="outer")
master = master.merge(income_df, on="year", how="outer")
master = master.merge(struct_df, on="year", how="outer")
master = master.merge(cons_data, on="year", how="outer")
master = master.sort_values("year")

master["utility_expense_est"] = master["lowest_consumption"] * (master["utility_share_pct"] / 100)
master["energy_burden_ratio"] = master["utility_expense_est"] / master["disposable_income"]

master.to_csv("data/processed/master_table.csv", index=False)
print(f"已儲存完整版 master_table.csv，共 {len(master)} 列")
print(master[["year", "energy_burden_ratio"]].dropna().tail(10))