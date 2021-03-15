
import os
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

from dashboard.utils import get_stock_price
from dashboard.charts import plot_stock_price_area_chart, plot_stock_price_candle_chart, plot_stock_return_line_chart
from apis.financial_modelling_prep.client import Client

def load_company_profile(ticker: str) -> None:
	"""
	Display profile of company including fundamental data, historical prices
	and technical analysis in streamlit dashboard
	Args:
		ticker(str): Company stock ticker
	"""
	stock_prices = get_stock_price(ticker)
	fmp_client = Client()

	# Fundamental Analysis
	company_profile = fmp_client.get_profile(ticker)
	# print(company_profile)


	st.subheader("Fundamental Analysis")
	company_profile = fmp_client.get_profile(ticker)[0]
	print(company_profile)
	symbol = company_profile['symbol']
	isin = company_profile['isin']
	market_cap = company_profile['mktCap']/10**6
	industry = company_profile['industry']
	sector = company_profile['sector']


	st.markdown(f"**Symbol - **{symbol}")
	st.markdown(f"**ISIN - **{isin}")
	st.markdown(f"**Industry - **{industry}")
	st.markdown(f"**Sector - **{sector}")
	st.markdown(f"**Market Cap (USD Mn)- **{market_cap}")
	st.markdown("---")
	st.plotly_chart(plot_stock_price_area_chart(stock_prices))
	st.plotly_chart(plot_stock_return_line_chart(stock_prices))
	

	# Get financials
	income_profile = fmp_client.get_income_profile(ticker)
	if len(income_profile) > 0:
		date = [row['date'] for row in income_profile]
		revenue = [row['revenue']/10**6 for row in income_profile]
		gross_profit = [row['grossProfit']/10**6 for row in income_profile]
		ebitda = [row['ebitda']/10**6 for row in income_profile]
		net_income = [row['netIncome']/10**6 for row in income_profile]

	balance_sheet_profile = fmp_client.get_balance_sheet_profile(ticker)
	if len(balance_sheet_profile) > 0:
			total_assets = [row['totalAssets']/10**6 for row in balance_sheet_profile]
			cash = [row['cashAndCashEquivalents']/10**6 for row in balance_sheet_profile]

	financial_profile = pd.DataFrame()
	financial_profile['Period'] = date
	financial_profile['Revenue (USD Mn)'] = revenue 
	financial_profile['Gross_Profit (USD Mn)'] = gross_profit
	financial_profile['EBITDA (USD Mn)'] = ebitda
	financial_profile['Net_Income (USD Mn)'] = net_income
	financial_profile['Total_Assets (USD Mn)'] = total_assets 
	financial_profile['Cash (USD Mn)'] = cash

	st.write(financial_profile)

	# Techncical Analysis
	st.subheader("Technical Analysis")
	st.plotly_chart(plot_stock_price_candle_chart(stock_prices))

	avg_20 = stock_prices['Close'].rolling(window=20, min_periods=1).mean()
	avg_50 = stock_prices['Close'].rolling(window=50, min_periods=1).mean()
	avg_200 = stock_prices['Close'].rolling(window=200, min_periods=1).mean()
	set1 = { 'x': stock_prices.index, 'close': stock_prices['Close'], 'type': 'candlestick'}
	set2 = { 'x': stock_prices.index, 'y': avg_20, 'type': 'scatter', 'mode': 'lines', 'line': { 'width': 1, 'color': 'blue' },'name': 'MA 20 periods'}
	set3 = { 'x': stock_prices.index, 'y': avg_50, 'type': 'scatter', 'mode': 'lines', 'line': { 'width': 1, 'color': 'yellow' },'name': 'MA 50 periods'}
	set4 = { 'x': stock_prices.index, 'y': avg_200, 'type': 'scatter', 'mode': 'lines', 'line': { 'width': 1, 'color': 'black' },'name': 'MA 200 periods'}
	data = [set1, set2, set3, set4]
	fig = go.Figure(data=data)
	fig.update_layout(title = 'Moving Average Trends', title_x=0.5)
	st.plotly_chart(fig)

	

