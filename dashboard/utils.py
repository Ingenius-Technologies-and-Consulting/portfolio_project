from pathlib import Path
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dashboard.config import STOCK_PRICE_HISTORY_YEARS


def read_markdown_file(markdown_file):
	return Path(markdown_file).read_text()

def get_stock_price(ticker: str) -> pd.DataFrame:
	"""
	Fetch historical stock prices from Yahoo finance
	Args:
		ticker(str): The stock ticker for which to fetch prices
	Returns:
		dict/list: Historical stock prices in requested period
	"""
	stock = yf.Ticker(ticker)
	
	# Start year is the beginning of the 5th year back
	start_date = datetime(datetime.now().year - STOCK_PRICE_HISTORY_YEARS,1,1).strftime('%Y-%m-%d')
	end_date = datetime.now().strftime('%Y-%m-%d') 
	return stock.history(start = start_date, end = end_date)
