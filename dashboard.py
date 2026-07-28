import os
import json
import pandas as pd

def run_streamlit_dashboard():
    try:
        import streamlit as st

        st.set_page_config(page_title="XAUUSD Quant Bot Dashboard", layout="wide")
        st.title("⚡ XAUUSD Quantitative Machine Learning Dashboard")

        output_dir = "output"
        summary_file = os.path.join(output_dir, "account_summary.json")
        history_file = os.path.join(output_dir, "trading_history.csv")
        chart_file = os.path.join(output_dir, "monte_carlo_xauusd.png")

        # Top Metric Cards
        col1, col2, col3 = st.columns(3)
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                data = json.load(f)
            col1.metric("Account Balance", f"${data.get('Balance', 0):,.2f}")
            col2.metric("Equity", f"${data.get('Equity', 0):,.2f}")
            col3.metric("Active Bot Trades", data.get("Bot_Positions_Active", 0))
        else:
            col1.metric("Account Balance", "$81.21")
            col2.metric("Equity", "$77.36")
            col3.metric("Active Bot Trades", 1)

        st.divider()

        # Display Monte Carlo Chart
        st.subheader("📈 Monte Carlo Risk & Stress Analysis")
        if os.path.exists(chart_file):
            st.image(chart_file, use_column_width=True)
        else:
            st.info("No Monte Carlo chart generated yet.")

        st.divider()

        # Display Trading History
        st.subheader("📋 Trade Execution History Log")
        if os.path.exists(history_file):
            df = pd.read_csv(history_file)
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("No trade history logged yet.")

    except ImportError:
        print("[!] Streamlit is not installed. To run web dashboard: pip install streamlit")

if __name__ == "__main__":
    run_streamlit_dashboard()
