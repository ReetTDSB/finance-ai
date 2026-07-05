import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from src.pipeline import run_pipeline

st.set_page_config(
    page_title="Finance Analyst AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #222; }

    /* Metric cards — allow text to wrap */
    [data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 12px;
        overflow: visible;
    }
    [data-testid="metric-container"] label {
        color: #888 !important;
        font-size: 11px !important;
        white-space: normal !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f0b429 !important;
        font-size: 16px !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
    }

    h1 { color: #f0b429 !important; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    h2, h3 { color: #cccccc !important; border-bottom: 1px solid #2a2a2a; padding-bottom: 6px; }

    .stButton > button {
        background-color: #f0b429;
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        width: 100%;
        padding: 10px;
        letter-spacing: 1px;
    }
    .stButton > button:hover { background-color: #e0a419; }

    .stTextInput input, .stSelectbox select {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
    }

    .streamlit-expanderHeader { background-color: #1a1a1a; color: #aaa; border-radius: 4px; }
    hr { border-color: #222; }

    .report-box {
        background-color: #111;
        border: 1px solid #2a2a2a;
        border-left: 3px solid #f0b429;
        border-radius: 6px;
        padding: 20px;
        line-height: 1.8;
        color: #ccc;
    }

    .ticker-badge {
        display: inline-block;
        background-color: #f0b429;
        color: #000;
        font-weight: bold;
        padding: 2px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 14px;
    }

    .disclaimer {
        background-color: #1a1200;
        border: 1px solid #f0b42944;
        border-radius: 4px;
        padding: 10px 16px;
        color: #f0b429;
        font-size: 12px;
    }

    /* Comparison table */
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        font-size: 13px;
    }
    .compare-table th {
        background-color: #1a1a1a;
        color: #f0b429;
        padding: 10px 14px;
        text-align: left;
        border-bottom: 2px solid #333;
        font-family: monospace;
        letter-spacing: 1px;
    }
    .compare-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #1e1e1e;
        color: #ccc;
        vertical-align: top;
    }
    .compare-table tr:hover td { background-color: #111; }
    .compare-table .def {
        font-size: 11px;
        color: #555;
        margin-top: 3px;
    }

    /* Recommendation box */
    .rec-box {
        background-color: #0f1a0f;
        border: 1px solid #1a3a1a;
        border-left: 3px solid #00e676;
        border-radius: 6px;
        padding: 16px 20px;
        margin-top: 16px;
        color: #aaa;
        line-height: 1.8;
        font-size: 13px;
    }
    .rec-box b { color: #00e676; }
</style>
""", unsafe_allow_html=True)

plt.style.use("dark_background")
CHART_BG   = "#0a0a0a"
CHART_GRID = "#1e1e1e"
COLOR_PRICE = "#f0b429"
COLOR_MA    = "#4fc3f7"
COLOR_UP    = "#00e676"
COLOR_DOWN  = "#ff5252"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ CONTROLS")
    st.markdown("---")
    mode = st.radio("Mode", ["Single Stock", "Compare Two Stocks"], label_visibility="collapsed")
    st.markdown(f"**Mode:** `{mode}`")
    st.markdown("---")
    ticker1 = st.text_input("Ticker" if mode == "Single Stock" else "Ticker 1", value="AAPL").upper().strip()
    if mode == "Compare Two Stocks":
        ticker2 = st.text_input("Ticker 2", value="TSLA").upper().strip()
    period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    question = st.text_area("Your question", value="Should I buy this stock?", height=100)
    st.markdown("---")
    run_button = st.button("▶  ANALYZE")
    st.markdown("---")
    st.markdown("<div style='color:#444; font-size:11px'>Finance Analyst AI • Educational only</div>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📈 FINANCE ANALYST AI")
st.markdown("<div class='disclaimer'>⚠️ This tool is for educational purposes only and does not constitute financial advice.</div>", unsafe_allow_html=True)
st.markdown("")


# ── Charts ────────────────────────────────────────────────────────────────────
def draw_price_chart(df, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={"height_ratios": [3, 1]}, facecolor=CHART_BG)
    ax1.set_facecolor(CHART_BG)
    ax1.plot(df.index, df["Close"], color=COLOR_PRICE, linewidth=1.5, label="Close")
    if "MA_20" in df.columns:
        ax1.plot(df.index, df["MA_20"], color=COLOR_MA, linewidth=1, linestyle="--", label="MA 20")
    ax1.fill_between(df.index, df["Close"], df["Close"].min(), alpha=0.08, color=COLOR_PRICE)
    ax1.set_ylabel("Price (USD)", color="#888")
    ax1.tick_params(colors="#555")
    ax1.legend(facecolor="#1a1a1a", edgecolor="#333", labelcolor="#aaa", fontsize=9)
    ax1.grid(True, color=CHART_GRID, linewidth=0.5)
    ax1.set_title(f"{ticker} — Price & MA20", color="#aaa", fontsize=11, pad=8)
    for spine in ax1.spines.values():
        spine.set_edgecolor("#222")
    ax2.set_facecolor(CHART_BG)
    colors = [COLOR_UP if df["Close"].iloc[i] >= df["Close"].iloc[i-1] else COLOR_DOWN for i in range(len(df))]
    ax2.bar(df.index, df["Volume"], color=colors, alpha=0.7, width=1)
    ax2.set_ylabel("Volume", color="#888", fontsize=8)
    ax2.tick_params(colors="#555", labelsize=7)
    ax2.grid(True, color=CHART_GRID, linewidth=0.3)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#222")
    plt.tight_layout()
    return fig


def draw_rsi_gauge(rsi_value):
    fig, ax = plt.subplots(figsize=(3.5, 2.2), facecolor="#1a1a1a")
    ax.set_facecolor("#1a1a1a")
    theta = np.linspace(np.pi, 0, 300)
    for start, end, color in [(0, 30, "#ff5252"), (30, 70, "#f0b429"), (70, 100, "#ff5252")]:
        mask = (np.linspace(0, 100, 300) >= start) & (np.linspace(0, 100, 300) <= end)
        ax.plot(np.cos(theta[mask]), np.sin(theta[mask]), linewidth=10, color=color, alpha=0.4, solid_capstyle="butt")
    if rsi_value is not None:
        angle = np.pi - (rsi_value / 100) * np.pi
        ax.annotate("", xy=(0.7 * np.cos(angle), 0.7 * np.sin(angle)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color="white", lw=2))
    ax.text(0, -0.15, f"RSI  {rsi_value}", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
    ax.text(-0.95, -0.15, "0", color="#888", fontsize=8)
    ax.text(0.85, -0.15, "100", color="#888", fontsize=8)
    ax.text(-0.5, 0.55, "30", color="#888", fontsize=7)
    ax.text(0.42, 0.55, "70", color="#888", fontsize=7)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.4, 1.1)
    ax.axis("off")
    ax.set_title("RSI (14)", color="#aaa", fontsize=9, pad=2)
    return fig


def draw_macd_chart(df, ticker):
    if "MACD" not in df.columns:
        return None
    fig, ax = plt.subplots(figsize=(12, 2.5), facecolor=CHART_BG)
    ax.set_facecolor(CHART_BG)
    ax.plot(df.index, df["MACD"], color=COLOR_PRICE, linewidth=1, label="MACD")
    ax.plot(df.index, df["MACD_Signal"], color=COLOR_MA, linewidth=1, linestyle="--", label="Signal")
    hist_colors = [COLOR_UP if v >= 0 else COLOR_DOWN for v in df["MACD_Hist"].fillna(0)]
    ax.bar(df.index, df["MACD_Hist"], color=hist_colors, alpha=0.5, width=1)
    ax.axhline(0, color="#333", linewidth=0.8)
    ax.set_ylabel("MACD", color="#888", fontsize=8)
    ax.tick_params(colors="#555", labelsize=7)
    ax.legend(facecolor="#1a1a1a", edgecolor="#333", labelcolor="#aaa", fontsize=8)
    ax.grid(True, color=CHART_GRID, linewidth=0.3)
    ax.set_title(f"{ticker} — MACD", color="#aaa", fontsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor("#222")
    plt.tight_layout()
    return fig


# ── Comparison table with definitions and recommendation ─────────────────────
def render_comparison_table(results):
    t1, t2 = list(results.keys())
    i1 = results[t1]["indicators"]
    i2 = results[t2]["indicators"]
    p1 = results[t1]["prediction"]
    p2 = results[t2]["prediction"]

    definitions = {
        "Last Close":    "The most recent closing price of the stock.",
        "MA 20":         "20-day moving average. Price above MA20 = bullish momentum.",
        "RSI":           "0-100. Above 70 = overbought, below 30 = oversold, 30-70 = neutral.",
        "MACD Trend":    "Bullish = upward momentum. Bearish = downward pressure.",
        "Volatility":    "How much the price swings annually. Higher = more risk.",
        "Sharpe Ratio":  "Return per unit of risk. Above 1.0 = good. Below 0 = poor.",
        "ML Prediction": "Model estimate of next-day direction. Educational only.",
    }

    rows = {
        "Last Close":    [f"${i1['last_close']}", f"${i2['last_close']}"],
        "MA 20":         [f"${i1['ma_20']}", f"${i2['ma_20']}"],
        "RSI":           [f"{i1['rsi']} ({i1['rsi_zone']})", f"{i2['rsi']} ({i2['rsi_zone']})"],
        "MACD Trend":    [i1["macd_trend"].upper(), i2["macd_trend"].upper()],
        "Volatility":    [str(i1["volatility"]), str(i2["volatility"])],
        "Sharpe Ratio":  [str(i1["sharpe_ratio"]), str(i2["sharpe_ratio"])],
        "ML Prediction": [p1["prediction"].upper(), p2["prediction"].upper()],
    }

    def style_val(v):
        if v == "BULLISH":
            return "<span style=\"color:#00e676\">" + v + "</span>"
        elif v == "BEARISH":
            return "<span style=\"color:#ff5252\">" + v + "</span>"
        elif v == "UP":
            return "<span style=\"color:#00e676\">⬆ " + v + "</span>"
        elif v == "DOWN":
            return "<span style=\"color:#ff5252\">⬇ " + v + "</span>"
        return v

    rows_html = ""
    for key, vals in rows.items():
        rows_html += (
            "<tr>"
            "<td><b style=\"color:#ccc\">" + key + "</b>"
            "<div class=\"def\">" + definitions[key] + "</div></td>"
            "<td>" + style_val(vals[0]) + "</td>"
            "<td>" + style_val(vals[1]) + "</td>"
            "</tr>"
        )

    table_html = (
        "<table class=\"compare-table\">"
        "<tr><th>Indicator</th><th>" + t1 + "</th><th>" + t2 + "</th></tr>"
        + rows_html +
        "</table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # Recommendation box
    sharpe1 = i1["sharpe_ratio"] or 0
    sharpe2 = i2["sharpe_ratio"] or 0
    vol1    = i1["volatility"] or 0
    vol2    = i2["volatility"] or 0
    rsi1    = i1["rsi"] or 50
    rsi2    = i2["rsi"] or 50

    long_pick   = t1 if sharpe1 >= sharpe2 else t2
    long_sharpe = sharpe1 if long_pick == t1 else sharpe2

    score1      = abs(rsi1 - 50) + (vol1 * 100)
    score2      = abs(rsi2 - 50) + (vol2 * 100)
    short_pick  = t1 if score1 <= score2 else t2
    short_other = t2 if short_pick == t1 else t1

    st.markdown(
        "<div class=\"rec-box\">"
        "<b>📌 Which stock for which type of trader?</b><br><br>"
        "<b>Long-term investors</b> should lean toward <b>" + long_pick + "</b>. "
        "It has a higher Sharpe Ratio (" + str(round(long_sharpe, 3)) + "), meaning it delivers better "
        "returns relative to the risk it carries — an important quality for buy-and-hold strategies "
        "where you want steady, risk-adjusted growth over months or years.<br><br>"
        "<b>Short-term / swing traders</b> may prefer <b>" + short_pick + "</b>. "
        "Its RSI is closer to neutral (less likely to mean-revert abruptly) and its volatility "
        "profile offers more predictable short-term movement windows compared to " + short_other + ".<br><br>"
        "<span style=\"color:#444; font-size:11px\">⚠️ This is a rule-based summary for educational purposes only, not financial advice.</span>"
        "</div>",
        unsafe_allow_html=True
    )

    # ── AI recommendation paragraph ───────────────────────────────────────────
    sharpe1 = i1["sharpe_ratio"] or 0
    sharpe2 = i2["sharpe_ratio"] or 0
    vol1    = i1["volatility"] or 0
    vol2    = i2["volatility"] or 0
    rsi1    = i1["rsi"] or 50
    rsi2    = i2["rsi"] or 50

    # Long term: higher Sharpe = better risk-adjusted return
    long_pick  = t1 if sharpe1 >= sharpe2 else t2
    long_other = t2 if long_pick == t1 else t1
    long_sharpe = sharpe1 if long_pick == t1 else sharpe2

    # Short term: lower volatility + RSI closer to neutral (50)
    score1 = abs(rsi1 - 50) + (vol1 * 100)
    score2 = abs(rsi2 - 50) + (vol2 * 100)
    short_pick  = t1 if score1 <= score2 else t2
    short_other = t2 if short_pick == t1 else t1

    st.markdown(f"""
    <div class='rec-box'>
        <b>📌 Which stock for which type of trader?</b><br><br>
        <b>Long-term investors</b> should lean toward <b>{long_pick}</b>.
        It has a higher Sharpe Ratio ({round(long_sharpe, 3)}), meaning it delivers better
        returns relative to the risk it carries — an important quality for buy-and-hold strategies
        where you want steady, risk-adjusted growth over months or years.<br><br>
        <b>Short-term / swing traders</b> may prefer <b>{short_pick}</b>.
        Its RSI is closer to neutral (less likely to mean-revert abruptly) and its volatility
        profile offers more predictable short-term movement windows compared to {short_other}.<br><br>
        <span style='color:#444; font-size:11px'>⚠️ This is a rule-based summary for educational purposes only, not financial advice.</span>
    </div>
    """, unsafe_allow_html=True)


# ── Render single stock ───────────────────────────────────────────────────────
def render_stock(result):
    ticker = result["ticker"]
    info   = result["company_info"]
    ind    = result["indicators"]
    pred   = result["prediction"]
    df     = result["history_df"]

    st.markdown(f"<span class='ticker-badge'>{ticker}</span> &nbsp; <span style='color:#888'>{info.get('name','')}</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#555; font-size:12px'>{info.get('sector','')} • {info.get('industry','')}</span>", unsafe_allow_html=True)
    st.markdown("")

    # Metrics — custom cards that never cut off
    st.markdown(f"""
    <div style='display:flex; gap:10px; flex-wrap:wrap; margin-bottom:10px;'>
        <div style='background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:12px 16px; min-width:120px; flex:1;'>
            <div style='color:#888; font-size:11px; margin-bottom:4px;'>Last Close</div>
            <div style='color:#f0b429; font-size:16px; font-weight:bold; word-break:break-word;'>${ind['last_close']}</div>
        </div>
        <div style='background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:12px 16px; min-width:120px; flex:1;'>
            <div style='color:#888; font-size:11px; margin-bottom:4px;'>MA 20</div>
            <div style='color:#f0b429; font-size:16px; font-weight:bold; word-break:break-word;'>${ind['ma_20']}</div>
        </div>
        <div style='background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:12px 16px; min-width:120px; flex:1;'>
            <div style='color:#888; font-size:11px; margin-bottom:4px;'>Volatility</div>
            <div style='color:#f0b429; font-size:16px; font-weight:bold; word-break:break-word;'>{ind['volatility']}</div>
        </div>
        <div style='background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:12px 16px; min-width:120px; flex:1;'>
            <div style='color:#888; font-size:11px; margin-bottom:4px;'>Sharpe Ratio</div>
            <div style='color:#f0b429; font-size:16px; font-weight:bold; word-break:break-word;'>{ind['sharpe_ratio']}</div>
        </div>
        <div style='background:#1a1a1a; border:1px solid #2a2a2a; border-radius:8px; padding:12px 16px; min-width:140px; flex:1;'>
            <div style='color:#888; font-size:11px; margin-bottom:4px;'>ML Prediction</div>
            <div style='color:#f0b429; font-size:16px; font-weight:bold; word-break:break-word;'>{'⬆ UP' if pred['prediction']=='up' else '⬇ DOWN'}<br><span style="font-size:12px; color:#888;">confidence: {pred['confidence']}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<a href='#what-do-these-numbers-mean' style='color:#f0b429; font-size:12px;'>❓ What do these numbers mean?</a>", unsafe_allow_html=True)
    st.markdown("")

    st.pyplot(draw_price_chart(df, ticker))

    st.markdown("### 📊 Technical Indicators")
    col_rsi, col_macd = st.columns([1, 3])
    with col_rsi:
        st.pyplot(draw_rsi_gauge(ind["rsi"]))
        zone_color = "#ff5252" if ind["rsi_zone"] != "neutral" else "#f0b429"
        st.markdown(f"<div style='text-align:center; color:{zone_color}; font-size:12px'>{ind['rsi_zone'].upper()}</div>", unsafe_allow_html=True)
    with col_macd:
        macd_fig = draw_macd_chart(df, ticker)
        if macd_fig:
            st.pyplot(macd_fig)
        trend_color = COLOR_UP if ind["macd_trend"] == "bullish" else COLOR_DOWN
        st.markdown(f"<div style='color:{trend_color}; font-size:13px; font-weight:bold'>▶ MACD trend: {ind['macd_trend'].upper()}</div>", unsafe_allow_html=True)

    real_chunks = [c for c in result["context_chunks"] if c.get("text", "").strip() and len(c["text"].strip()) > 30]
    if real_chunks:
        with st.expander("📚 Retrieved company notes"):
            for chunk in real_chunks:
                st.markdown(f"**{chunk['source']}**")
                st.write(chunk["text"])
                st.markdown("---")

    st.markdown("### 📝 AI Analysis Report")
    st.markdown(f"<div class='report-box'>{result['report'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
if run_button:
    if mode == "Single Stock":
        with st.spinner(f"Analyzing {ticker1}..."):
            try:
                result = run_pipeline(ticker1, question, period=period)
                render_stock(result)
            except Exception as e:
                st.error(f"Error: {e}")

    else:
        col1, col2 = st.columns(2)
        results = {}
        with st.spinner(f"Analyzing {ticker1} and {ticker2}..."):
            for ticker, col in [(ticker1, col1), (ticker2, col2)]:
                try:
                    result = run_pipeline(ticker, question, period=period)
                    results[ticker] = result
                    with col:
                        render_stock(result)
                except Exception as e:
                    with col:
                        st.error(f"Error for {ticker}: {e}")

        if len(results) == 2:
            st.markdown("---")
            st.markdown("### ⚖️ Head-to-Head Comparison")
            render_comparison_table(results)

else:
    st.markdown("""
    <div style='text-align:center; padding: 80px 0; color:#333'>
        <div style='font-size:60px'>📈</div>
        <div style='font-size:18px; color:#555; margin-top:12px'>Enter a ticker and click ANALYZE</div>
        <div style='font-size:13px; color:#333; margin-top:8px'>Supports single stock analysis or side-by-side comparison</div>
    </div>
    """, unsafe_allow_html=True)

# ── Glossary ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div id='what-do-these-numbers-mean'></div>", unsafe_allow_html=True)
st.markdown("### ❓ What do these numbers mean?")
with st.expander("📖 Click to read the glossary", expanded=False):
    st.markdown("""
    <div style='color:#ccc; line-height:2'>
    <b>Last Close</b> — The most recent closing price. The price the stock ended at on the last trading day.<br><br>
    <b>MA 20 (20-Day Moving Average)</b> — Average closing price over the last 20 days.
    Price above MA20 = bullish. Price below MA20 = bearish.<br><br>
    <b>Volatility</b> — How wildly the stock swings annually. 0.20 = stable, 0.50+ = very risky.<br><br>
    <b>Sharpe Ratio</b> — Return per unit of risk. Above 1.0 = good. Below 0 = poor.<br><br>
    <b>RSI (0–100)</b> — Above 70 = overbought (may drop). Below 30 = oversold (may bounce). 30–70 = neutral.<br><br>
    <b>MACD</b> — Positive histogram = bullish momentum. Negative = bearish. Crossovers signal trend changes.<br><br>
    <b>ML Prediction</b> — A Random Forest model trained on indicators. UP or DOWN for the next day.
    Confidence shows certainty. Educational only — do not trade on this.
    </div>
    """, unsafe_allow_html=True)