import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "src"
for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from data_fetch import fetch_history, fetch_company_info
from indicators import compute_all_indicators, summarize_indicators
from prediction import train_and_predict
from rag import NotesRetriever
from LLM import generate_report

_retriever = None

def get_retriever() -> NotesRetriever:
    global _retriever
    if _retriever is None:
        notes_dir = str(ROOT / "data" / "notes")
        _retriever = NotesRetriever(notes_dir=notes_dir)
    return _retriever

def run_pipeline(ticker: str, user_question: str, period: str = "6mo") -> dict:
    ticker = ticker.upper().strip()

    # 1. Financial Data
    history_df   = fetch_history(ticker, period=period)
    company_info = fetch_company_info(ticker)

    # 2. Indicators
    enriched_df       = compute_all_indicators(history_df)
    indicator_summary = summarize_indicators(enriched_df)

    # 3. ML Prediction
    prediction = train_and_predict(enriched_df)

    # 4. RAG retrieval
    retriever      = get_retriever()
    context_chunks = retriever.retrieve(ticker, user_question)

    # 5. LLM report generation
    prompt = f"""
    Stock: {ticker}
    User Question: {user_question}
    Indicators: {indicator_summary}
    Prediction: {prediction}
    Additional Context: {context_chunks}

    Write:
    1. Market Summary
    2. Bullish vs Bearish signals
    3. Risks
    4. Short conclusion
    """

    report_text = generate_report(prompt)

    # Return everything app.py needs
    return {
        "ticker":         ticker,
        "company_info":   company_info,
        "history_df":     enriched_df,
        "indicators":     indicator_summary,
        "prediction":     prediction,
        "context_chunks": context_chunks,
        "report":         report_text,
    }

if __name__ == "__main__":
    print(run_pipeline("AAPL", "Should I buy this stock?", period="1mo"))