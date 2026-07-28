import os
import json
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HistoryTracker:
    """
    Logs and tracks bot execution history, active trades, and closed position statistics to CSV/JSON.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.csv_path = os.path.join(self.output_dir, "trading_history.csv")
        self.json_path = os.path.join(self.output_dir, "account_summary.json")

    def log_trade_event(self, event_type: str, details: dict):
        """Appends a trade event to trading_history.csv."""
        details["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details["Event"] = event_type

        df_event = pd.DataFrame([details])

        if not os.path.exists(self.csv_path):
            df_event.to_csv(self.csv_path, index=False)
        else:
            df_event.to_csv(self.csv_path, mode="a", header=False, index=False)

        logger.info(f"[History Tracker] Recorded event '{event_type}' to {self.csv_path}")

    def update_account_summary(self, summary: dict):
        """Saves current account balance, equity, and open position state to JSON."""
        summary["Updated_At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.json_path, "w") as f:
            json.dump(summary, f, indent=4)
