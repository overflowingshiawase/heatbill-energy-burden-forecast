import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 避免跳出視窗導致當機
import matplotlib.pyplot as plt
import glob

pd.set_option("display.max_columns", None)

def try_read_csv(path):
    """政府資料常用Big5編碼，先試UTF-8，失敗改試Big5"""
    for enc in ["utf-8", "utf-8-sig", "big5", "cp950"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"成功讀取 {path}，使用編碼: {enc}")
            return df
        except Exception:
            continue
    print(f"警告：{path} 讀取失敗，四種編碼都試過了")
    return None

print("=" * 50)
print("1. 台電電價")
print("=" * 50)
price_df = try_read_csv("data/raw/taipower_price.csv")
if price_df is not None:
    print(price_df.columns.tolist())
    print(price_df.head())
    print(price_df.info())

print("=" * 50)
print("2. 家庭收支調查")
print("=" * 50)
income_df = try_read_csv("data/raw/household_income.csv")
print(income_df.columns.tolist())
print(income_df.head())
print(income_df.info())

print("=" * 50)
print("3. 能源統計")
print("=" * 50)
energy_df = pd.read_excel("data/raw/energy_statistics.xlsx")
print(energy_df.columns.tolist())
print(energy_df.head())
print(energy_df.info())

print("=" * 50)
print("4. 氣溫資料（五年合併）")
print("=" * 50)
temp_files = glob.glob("data/raw/taipei_temp_*.csv")
print(f"找到氣溫檔案：{temp_files}")

temp_list = []
for f in temp_files:
    df = try_read_csv(f)
    if df is not None:
        temp_list.append(df)

if temp_list:
    weather_df = pd.concat(temp_list, ignore_index=True)
    print(weather_df.columns.tolist())
    print(weather_df.head())
    print(weather_df.info())
    print("缺值狀況：")
    print(weather_df.isnull().sum())

    # 存一份合併後的原始氣溫資料，之後Phase3會用到
    weather_df.to_csv("data/processed/weather_combined_raw.csv", index=False)
    print("已儲存合併後的氣溫資料到 data/processed/weather_combined_raw.csv")

print("=" * 50)
print("EDA 第一輪檢查完畢，請把上面印出的欄位名稱回報給Claude")
print("=" * 50)