import yfinance as yf

yf.set_tz_cache_location(".yfinance-cache")

stock = yf.Ticker("AAPL")
print(stock.history(period="5d"))
