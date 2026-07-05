"""
prediction.py
-------------
A small, fully local, educational ML layer that estimates whether the
stock's price is more likely to go UP or DOWN over the next day, based
on the technical indicators we already computed.

IMPORTANT: This is a toy model trained on a few months of data for one
ticker. It is NOT investment advice, and accuracy will be close to a
coin flip in many cases. It exists to demonstrate how a prediction
layer can be wired into the larger pipeline.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


FEATURE_COLUMNS = ["MA_20", "Volatility", "RSI", "MACD", "MACD_Signal", "MACD_Hist"]


def build_training_set(df: pd.DataFrame):
    """
    Builds (X, y) for supervised learning.
    Label y = 1 if next day's Close is higher than today's Close, else 0.
    """
    data = df.copy()
    data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)

    # Drop rows with NaNs from indicator rolling windows or the shift
    data = data.dropna(subset=FEATURE_COLUMNS + ["Target"])

    X = data[FEATURE_COLUMNS]
    y = data["Target"]
    return X, y


def train_and_predict(df: pd.DataFrame) -> dict:
    """
    Trains a RandomForestClassifier on historical indicator data and
    predicts the direction of the NEXT bar using the most recent row.

    Returns a dict with the prediction, a confidence score, and a
    rough train/test accuracy so the user can gauge reliability.
    """
    X, y = build_training_set(df)

    if len(X) < 30:
        return {
            "prediction": "insufficient_data",
            "confidence": None,
            "test_accuracy": None,
            "note": "Not enough historical rows after indicator calculation to train a model.",
        }

    # shuffle=False keeps chronological order — no lookahead leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    test_accuracy = (
        accuracy_score(y_test, model.predict(X_test)) if len(X_test) > 0 else None
    )

    # Predict using the most recent available indicator row
    latest_features = df[FEATURE_COLUMNS].dropna().iloc[[-1]]
    proba = model.predict_proba(latest_features)[0]
    pred_class = model.predict(latest_features)[0]

    return {
        "prediction": "up" if pred_class == 1 else "down",
        "confidence": round(float(max(proba)), 3),
        "test_accuracy": round(float(test_accuracy), 3) if test_accuracy is not None else None,
        "note": "Educational model only — not financial advice.",
    }