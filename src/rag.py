import yfinance as yf


class NotesRetriever:

    def __init__(self, notes_dir=None):
        self.notes_dir = notes_dir

    def retrieve(self, ticker, query="", top_k=5):

        try:
            stock = yf.Ticker(ticker)

            info = stock.info

            context = []

            summary = info.get(
                "longBusinessSummary",
                ""
            )

            if summary:

                context.append({
                    "source": "Yahoo Finance Company Summary",
                    "text": summary,
                    "distance": 0
                })

            news = stock.news

            for article in news[:top_k]:

                context.append({
                    "source": article.get(
                        "title",
                        "Yahoo News"
                    ),
                    "text": article.get(
                        "summary",
                        ""
                    ),
                    "distance": 0
                })

            return context

        except Exception:

            return []