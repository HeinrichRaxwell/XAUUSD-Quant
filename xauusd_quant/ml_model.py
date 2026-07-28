import os
import pickle
import logging
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier

logger = logging.getLogger(__name__)

# Version tag — bump this whenever features or labeling logic changes
# This forces auto-retraining when the saved model is incompatible
MODEL_VERSION = "v4_3class_wilder_swing"


class XauMLModel:
    """
    Quantitative Machine Learning Signal Model built on Microsoft Qlib & FinRL principles:
    - LightGBM GBDT Classifier (3-class: SELL_WIN=0, NEUTRAL=1, BUY_WIN=2)
    - Triple Barrier Target Labeling (Marcos Lopez de Prado / Qlib) — bidirectional
    - Persistent Weight State (.pkl) with version gating (auto-retrain on feature changes)
    - Threshold-based signal extraction from class probabilities
    """
    def __init__(self, forward_bars: int = 5, prob_threshold: float = 0.65, model_dir: str = "models"):
        self.forward_bars = forward_bars
        self.prob_threshold = prob_threshold
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "lightgbm_xauusd.pkl")
        self.version_path = os.path.join(model_dir, "model_version.txt")
        self.model = None

        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)

        self._load_model()

    def _load_model(self):
        # Version gate: if saved version != current version, force retrain
        saved_version = None
        if os.path.exists(self.version_path):
            try:
                with open(self.version_path, "r") as f:
                    saved_version = f.read().strip()
            except Exception:
                saved_version = None

        if saved_version != MODEL_VERSION:
            # Feature/label schema changed → delete old incompatible model
            if os.path.exists(self.model_path):
                os.remove(self.model_path)
                logger.info(f"[ML Model] Version changed ({saved_version} → {MODEL_VERSION}). Deleted stale model. Will retrain.")
            else:
                logger.info(f"[ML Model] No saved model found. Will train fresh 3-class model.")
            self._create_default_model()
            return

        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    loaded = pickle.load(f)
                    if hasattr(loaded, "fit"):
                        self.model = loaded
                    else:
                        self._create_default_model()
                logger.info(f"[ML Model] Loaded pre-trained model v{MODEL_VERSION} from {self.model_path}")
            except Exception as e:
                logger.warning(f"[ML Model] Failed to load model: {e}. Retraining.")
                self._create_default_model()
        else:
            self._create_default_model()


    def _create_default_model(self):
        """Regularized LightGBM Classifier — 3-class (SELL=0, NEUTRAL=1, BUY=2)."""
        self.model = LGBMClassifier(
            n_estimators=150,
            learning_rate=0.01,
            max_depth=4,
            num_leaves=15,
            min_child_samples=30,
            subsample=0.7,
            colsample_bytree=0.7,
            reg_alpha=0.5,
            reg_lambda=1.0,
            num_class=3,
            objective="multiclass",
            random_state=42,
            verbose=-1
        )


    def prepare_data(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """
        Prepares feature matrix X and 3-class target y using Triple Barrier Method.

        Target Labels (3-class):
          2 = BUY_WIN  — High hits entry + 2.0×ATR before Low hits entry - 2.0×ATR (within 24 bars)
          0 = SELL_WIN — Low hits entry - 2.0×ATR before High hits entry + 2.0×ATR (within 24 bars)
          1 = NEUTRAL  — Neither barrier hit within 24 bars (time-out)

        Both BUY and SELL winning conditions are explicitly labeled, so the model
        learns from actual SELL profitable setups, not just "BUY failure" proxies.
        """
        df = df.copy()
        high = df["High"].values
        low = df["Low"].values
        close = df["Close"].values
        atr = df["ATR"].values
        n = len(df)

        targets = np.ones(n, dtype=int)  # Default: NEUTRAL = 1

        for i in range(n - 24):
            entry_price = close[i]
            atr_i = atr[i] if atr[i] > 0 else 1.0

            # Symmetric barriers: BUY TP = +2×ATR, SELL TP = -2×ATR
            tp_buy  = entry_price + (2.0 * atr_i)
            tp_sell = entry_price - (2.0 * atr_i)

            label = 1  # Start as NEUTRAL
            for j in range(i + 1, min(i + 25, n)):
                buy_hit  = high[j] >= tp_buy
                sell_hit = low[j]  <= tp_sell

                if buy_hit and not sell_hit:
                    label = 2   # BUY_WIN
                    break
                elif sell_hit and not buy_hit:
                    label = 0   # SELL_WIN
                    break
                elif buy_hit and sell_hit:
                    label = 1   # Simultaneous = NEUTRAL (tie)
                    break
                # else: neither hit yet, continue scanning

            targets[i] = label

        df["Target"] = targets

        feature_cols = [
            "EMA20", "EMA50", "EMA_Spread", "Trend_EMA50", "RSI", "ATR",
            "BB_Position", "BB_Width", "Stoch_K", "Stoch_D",
            "MACD_Line", "MACD_Hist", "ADX14", "Plus_DI", "Minus_DI",
            "Supply_Zone_Dist", "Demand_Zone_Dist", "FVG_Bull", "FVG_Bear",
            "Pinbar_Bull", "Pinbar_Bear", "Engulf_Bull", "Engulf_Bear",
            "Doji", "Inside_Bar", "Morning_Star", "Evening_Star",
            "Three_White_Soldiers", "Three_Black_Crows", "Hammer", "Shooting_Star",
            "Double_Top", "Double_Bottom", "Head_Shoulders_Bear", "Head_Shoulders_Bull",
            "Triangle_Asc", "Triangle_Desc", "Triangle_Sym", "Flag_Bull", "Flag_Bear",
            "Harmonic_Fib_Score", "DXY_Mom5", "US10Y_Mom5", "Macro_Pressure"
        ]

        valid_df = df.dropna(subset=feature_cols + ["Target"]).copy()
        X = valid_df[feature_cols]
        y = valid_df["Target"]
        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Trains 3-class LightGBM model and saves weights + version tag to disk."""
        if len(X) < 100:
            logger.warning("[ML Model] Insufficient samples for training.")
            return {"Train_Accuracy": 0.0, "Test_Accuracy": 0.0}

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        logger.info(f"Training 3-class LightGBM Classifier (SELL=0 / NEUTRAL=1 / BUY=2)...")
        logger.info(f"  Class distribution — SELL: {(y_train==0).sum()} | NEUTRAL: {(y_train==1).sum()} | BUY: {(y_train==2).sum()}")
        self.model.fit(X_train, y_train)

        train_acc = float(self.model.score(X_train, y_train))
        test_acc  = float(self.model.score(X_test, y_test))

        # Save model + version tag
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        with open(self.version_path, "w") as f:
            f.write(MODEL_VERSION)

        logger.info(f"[ML Model] 3-class model saved → {self.model_path}")
        logger.info(f"[ML Model] Version tag written: {MODEL_VERSION}")
        logger.info(f"Model Training Complete. Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}")

        return {"Train_Accuracy": train_acc, "Test_Accuracy": test_acc}

    def predict_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Predicts directional trading signal (-1=SELL, 0=NEUTRAL, 1=BUY) from 3-class probabilities.

        3-class predict_proba columns (sorted class order: [0, 1, 2]):
          probs[:, 0] = P(SELL_WIN)
          probs[:, 1] = P(NEUTRAL)
          probs[:, 2] = P(BUY_WIN)

        Signal = 1  if P(BUY_WIN)  >= threshold
        Signal = -1 if P(SELL_WIN) >= threshold
        Signal = 0  otherwise (confidence too low)
        """
        X, _ = self.prepare_data(df)
        if len(X) == 0:
            return pd.Series(0, index=df.index)

        # Auto-train if model has never been fitted (fresh instance)
        try:
            probs = self.model.predict_proba(X)
        except Exception:
            logger.info("[ML Model] Model not trained yet — running initial training...")
            X_tr, y_tr = self.prepare_data(df)
            self.train(X_tr, y_tr)
            probs = self.model.predict_proba(X)

        signals = np.zeros(len(X), dtype=int)

        for i in range(len(probs)):
            prob_sell   = probs[i][0]   # class 0 = SELL_WIN
            # prob_neutral = probs[i][1] # class 1 = NEUTRAL (unused for signaling)
            prob_buy    = probs[i][2]   # class 2 = BUY_WIN

            if prob_buy >= self.prob_threshold:
                signals[i] = 1    # BUY signal
            elif prob_sell >= self.prob_threshold:
                signals[i] = -1   # SELL signal
            else:
                signals[i] = 0    # No signal — confidence below threshold

        res_series = pd.Series(0, index=df.index)
        res_series.loc[X.index] = signals
        return res_series
