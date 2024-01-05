import yfinance as yf


def get_stock_data(ticker: str, start: str, end: str):
    data = yf.download(ticker, start, end)
    data["Ticker"] = ticker
    data.reset_index(inplace=True)
    data.rename(columns={"High": "Price"}, inplace=True)
    return data
