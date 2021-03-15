import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = 'https://in.tradingview.com/markets/stocks-usa/market-movers-large-cap/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# Find all the ticker symbols and sectors
ticker_data = []
for ticker in soup.select('a[class*="tv-screener__symbol"]'):
	ticker_data.append(ticker.get_text())

ticker_symbols = ticker_data[::2]
ticker_categories = ticker_data[1::2]

# Find company names
company_data = []
for company in soup.find_all("span", class_ = "tv-screener__description"):
	company_data.append(company.get_text().lstrip())

print(len(ticker_symbols), len(ticker_categories), len(company_data))
stock_data = zip(ticker_symbols, ticker_categories, company_data)
stock_data = pd.DataFrame(stock_data, columns = ['symbol','category','name'])
print(stock_data.head())
stock_data.to_csv('large_cap_us_stocks.csv')
