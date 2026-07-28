import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="熱浪帳單 HeatBill", layout="wide")
st.title("熱浪帳單：氣候與綠能轉型下的台灣能源貧窮風險預警")
st.caption("資料來源：台電、主計總處、能源署、中央氣象署")

master = pd.read_csv("data/processed/master_table.csv")
scenario = pd.read_csv("data/processed/scenario_results.csv")

tab1, tab2, tab3 = st.tabs(["發生了什麼", "未來會怎樣", "方法論與限制"])

with tab1:
    hist = master.dropna(subset=["energy_burden_ratio"])
    st.subheader(f"歷史能源負擔比走勢（{int(hist['year'].min())}-{int(hist['year'].max())}）")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=hist["year"], y=hist["energy_burden_ratio"], mode="lines+markers", name="歷史"))
    fig1.update_layout(yaxis_tickformat=".1%")
    st.plotly_chart(fig1, use_container_width=True)
    st.metric("2024年能源負擔比", f"{hist['energy_burden_ratio'].iloc[-1]:.1%}")

with tab2:
    st.subheader("三個情境下的2025-2027預測")
    fig2 = go.Figure()
    for col in scenario.columns[1:]:
        fig2.add_trace(go.Scatter(x=scenario["year"], y=scenario[col], mode="lines+markers", name=col))
    fig2.update_layout(yaxis_tickformat=".1%")
    fig2.update_xaxes(dtick=1, tickformat="d")
    st.plotly_chart(fig2, use_container_width=True)
    st.info("提醒：目前訓練資料18筆（2007-2024），模型評估顯示Baseline優於Prophet，此處情境預測僅供方向性參考，詳見「方法論與限制」頁。")

with tab3:
    st.subheader("方法論")
    st.markdown("""
    - **資料來源**：台電電價、主計總處家庭收支調查、能源署能源統計、中央氣象署逐日氣溫
    - **能源負擔比定義**：最低所得組（水電燃氣估算支出）÷ 最低所得組可支配所得
    - **重要假設**：因官方公開資料未提供按所得五分位交叉之水電燃氣細項支出，本專案以全國「住宅服務水電瓦斯及其他燃料」消費結構占比，推估最低所得組的水電燃氣支出
    - **模型**：Prophet多變量迴歸（外生變數：冷房度日CDD、電價、再生能源占比）
    - **限制**：訓練資料18年（2007-2024），Baseline在此資料量下優於Prophet，情境預測結果應謹慎解讀
    """)
    st.subheader("模型評估")
    with open("docs/model_evaluation.md", encoding="utf-8") as f:
        st.markdown(f.read())
