import os
import yfinance as yf
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand

from assets.models import Asset, AssetType
from apis.financial_modelling_prep.client import Client


class Command(BaseCommand):
	"""
	Update stock tickers
	"""
	def handle(self, *args, **kwargs):

		# Delete existing entries in Asset Type
		AssetType.objects.all().delete()

		# Create entries for Equity and ETF
		AssetType.objects.create(asset_type = 'EQ', description = 'Equity')
		AssetType.objects.create(asset_type = 'ETF', description = 'Exchange Traded Fund')

		URL = 'https://in.tradingview.com/markets/stocks-usa/market-movers-large-cap/'
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		fmp_client = Client()
		asset_type = AssetType.objects.get(asset_type = 'EQ')

		# Find all the ticker symbols and sectors
		ticker_data = []
		for ticker in soup.select('a[class*="tv-screener__symbol"]'):
			ticker_data.append(ticker.get_text())

		tickers = ticker_data[::2]

		# Create a dataframe to store closing prices for all tickers for last 5 years
		price_df = pd.DataFrame()
		start_date = datetime(datetime.now().year - 5,1,1).strftime('%Y-%m-%d')
		end_date = datetime.now().strftime('%Y-%m-%d')

		# We select stocks that have the entire history from start_date to end_date. No mid period listings
		# We do this by ensuring that the stock price data has the same number of rows as S&P price data
		s_p_ticker = yf.Ticker('^GSPC')
		s_p_data = s_p_ticker.history(start = start_date, end = end_date)
				
		# Fetch company profiles for ticker symbols
		for ticker in tickers:
			stock = yf.Ticker(ticker)
			stock_history = stock.history(start = start_date, end = end_date)
			company_profile = fmp_client.get_profile(ticker)[0]
			if not stock_history.empty:
				if stock_history.shape == s_p_data.shape:
					try:
						Asset.objects.get(asset_symbol = ticker)
					except Asset.DoesNotExist:
						Asset.objects.create(asset_type = asset_type, asset_symbol = ticker, asset_name = company_profile['companyName'], asset_industry = company_profile['industry'], asset_sector = company_profile['sector'], asset_country = company_profile['country'])
						print("Created entry for company {}".format(company_profile['companyName']))
					else:
						print("{} ticker exists".format(ticker))

				# Fetch historical stock prices
					closing_prices = stock_history['Close'].values
					price_df[ticker] = closing_prices

		# Create an asset entry for S&P 500
		Asset.objects.create(asset_type = asset_type, asset_symbol = '^GSPC', asset_name = 'S&P500', asset_country = 'US')
		price_df['Date'] = stock_history.index
		price_df['^GSPC'] = s_p_data['Close'].values
		print(price_df.head())
		price_data_path = os.path.join(str(Path(__file__).resolve().parents[3]), 'data/price_data.csv')
		price_df.to_csv(price_data_path, index = False)


			
