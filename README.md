# 熱浪帳單 HeatBill

氣候暖化與綠能轉型雙重壓力下，台灣低所得家庭的能源貧窮風險預警系統。

## Demo
[線上Dashboard](https://heatbill-energy-poverty-forecast-05.streamlit.app)

## 動機
氣候暖化推升冷房用電需求，綠能轉型可能推升電價，這兩股力量同時作用在最脆弱的家庭身上。本專案用四個官方公開資料源，量化這個交叉風險。

## 資料來源
- 台灣電力公司歷年電價（data.gov.tw）
- 主計總處家庭收支調查：可支配所得、消費支出結構（data.gov.tw）
- 經濟部能源署能源統計月報：再生能源發電占比
- 中央氣象署CODiS逐日氣溫（2007-2026，台北測站）

## 方法論與關鍵假設
- 能源負擔比 = 最低所得組水電燃氣估算支出 ÷ 最低所得組可支配所得
- 因官方公開資料未提供按所得五分位交叉之水電燃氣細項支出，本專案以全國「住宅服務水電瓦斯及其他燃料」消費結構占比，推估最低所得組的水電燃氣支出，此為簡化假設
- 冷房度日（CDD）以日平均溫超過26°C的部分逐日累加，逐年加總

## 模型與評估
比較 Baseline（Naive Forecast）與 Prophet（多變量迴歸，外生變數：CDD、電價、再生能源占比）：

| 模型 | MAE | RMSE | MAPE |
|---|---|---|---|
| Baseline | 0.0044 | 0.0053 | 1.74% |
| Prophet | 0.0094 | - | - |

**關鍵發現**：初版僅10筆訓練資料時，Prophet MAE為0.0178；補齊資料至18筆（2007-2024）後，Prophet MAE降至0.0094，證實資料量對多變量時間序列模型穩定性的關鍵影響。即使如此，Baseline在此資料規模下仍優於Prophet，顯示此類問題可能需要更長期的資料累積才能穩定超越簡單基準——這是誠實的實驗發現，而非模型實作錯誤。

## 技術棧
Python, Pandas, Prophet, scikit-learn, Streamlit, Plotly

## Future Work
- 持續累積更多年份資料以改善模型穩定性
- 加入最高溫/最低溫、連續高溫日數等進階氣象特徵
- SARIMAX模型比較
- 若未來有按所得分位交叉的細項消費支出公開資料，替換現行估算假設

## 本機執行
\`\`\`
git clone https://github.com/overflowingshiawase/Heatbill-Energy-Poverty-Forecast.git
cd Heatbill-Energy-Poverty-Forecast
pip install -r requirements.txt
streamlit run dashboard/app.py
\`\`\`
