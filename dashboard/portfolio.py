import os
import streamlit as st
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import plotly.express as px

from django.utils import timezone

#Optimization imports
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models 
from pypfopt import expected_returns
from pypfopt import DiscreteAllocation, get_latest_prices

from assets.models import Asset
from portfolio.models import Portfolio, Transaction
from users.models import User

def get_company_name(ticker: str) -> str:
	"""
	Get company name for a symbol
	"""
	url = 'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=' + ticker + '&region=1&lang=en'
	result = requests.get(url).json()
	for r in result['ResultSet']['Result']:
		if r['symbol'] == ticker:
			return r['name']

def create_portfolio() -> None:
	"""
	Create portfolio based on risk assessment and 
	efficient portfolio optimization
	"""
	st.subheader("Portfolio Parameters")
	st.write("Portfolio Name")
	portfolio_name = st.text_input('Portfolio Name', 'Portfolio_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
	st.write("Portfolio Description")
	portfolio_description = st.text_input('Portfolio Description', 'General Investment')
	st.write("Investment Amount (USD)")
	portfolio_investment = st.number_input(label = '', min_value = 0, value = 100000)
	st.markdown("---")
	st.subheader('Risk Assessment Form')
	st.write('Portfolio Risk Preference')
	risk_level = st.selectbox('Portfolio Risk Preference',('Low','Moderate','High')) 
	if st.button('Build Portfolio'):
		if risk_level == 'High':
			s_p_weight = 0.2
			equity_investment = 0.8* portfolio_investment
		elif risk_level == 'Moderate':
			s_p_weight = 0.4
		else:
			s_p_weight = 0.6
		st.markdown("---")

		# Separate investments into S&P 500 and Equities based on risk assessment
		s_p_investment = portfolio_investment * s_p_weight
		equity_investment = portfolio_investment - s_p_investment

		# Create stock portfolio
		price_data_path = os.path.join(str(Path(__file__).resolve().parents[1]), 'data/price_data.csv')
		price_df = pd.read_csv(price_data_path)
		price_df['Date'] = pd.to_datetime(price_df['Date'])
		price_df.set_index('Date', inplace = True)

		# Drop the S&P from price data, portfolio is optimized only for stocks
		s_p_data = pd.DataFrame(index = price_df.index)
		s_p_data['Close'] = price_df['^GSPC']
		equity_df = price_df.drop(columns = ['^GSPC'], axis = 1)
			
		# Optimize portfolio
		# Calculate the expected annualized returns and annualized covariance matrix of daily returns
		mu = expected_returns.mean_historical_return(equity_df)
		S = risk_models.sample_cov(equity_df)

		# Optimize the Sharpe ratio
		ef = EfficientFrontier(mu, S)
		raw_weights = ef.max_sharpe()
		cleaned_weights = ef.clean_weights()
		
		latest_prices = get_latest_prices(equity_df)
		da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value = equity_investment)
		allocation, leftover = da.lp_portfolio()
		print('Discrete Allocation: ',allocation)
		print('Funds Remaining: ' ,leftover)

		# Store company name into a list
		company_name = []
		discrete_allocation = []
		symbols = list(allocation.keys())
		investment_amount = []
		for symbol in allocation:
			company_name.append(get_company_name(symbol))
			discrete_allocation.append(allocation.get(symbol))
			print(symbol, price_df[symbol].values[-1], allocation.get(symbol))
			investment_amount.append(price_df[symbol].values[-1] * allocation.get(symbol))

		# Append the S&P Investment to the portfolio
		s_p_allocation = int(s_p_investment/s_p_data.tail(1)['Close'])
		company_name.append("S&P 500")
		symbols.append('^GSPC')
		discrete_allocation.append(s_p_allocation)
		investment_amount.append(s_p_investment)

		# Round off investments to 2 decimal places
		investment_amount = [ '%.2f' % elem for elem in investment_amount]

		# Create the stock portfolio portfolio
		portfolio_df = pd.DataFrame(columns = ['Company_Name', 'Ticker', 'Purchase_Units','Investment_Amount'])
		portfolio_df['Company_Name'] = company_name
		portfolio_df['Ticker'] = symbols
		portfolio_df['Purchase_Units'] = discrete_allocation
		portfolio_df['Investment_Amount']  = investment_amount

		st.subheader('Recommended Portfolio')
		st.write('The recommended portfolio is designed using Markowtiz Portfolio Optimization, based on historical returns and risks for stocks and their associated covariances')
		st.write(portfolio_df)	
		
		# Convert weights to numpy array
		weights = np.array([(1 - s_p_weight) * x[1] for x in cleaned_weights.items()], dtype = float)

		# Add the S_P weight to weights
		weights = np.append(weights, s_p_weight)
		
		price_matrix = price_df.values
		initial_portfolio_holding =  ((portfolio_investment * weights).T / price_matrix[0,:])
		
		# # For comparison let's get historical S&P 500 values and get share holding
		s_p_prices = s_p_data['Close'].values.reshape(-1,1)
		initial_s_p_holding = portfolio_investment / s_p_prices[0,0]

		# # Compute portfolio value and s_p_holding value
		portfolio_value = np.sum(initial_portfolio_holding * price_matrix, axis = 1)
		s_p_value = np.sum(initial_s_p_holding * s_p_prices, axis = 1)
		
		performance_df = pd.DataFrame(index = s_p_data.index)
		performance_df['Portfolio'] = portfolio_value
		performance_df['SP500'] = s_p_value
		performance_df = performance_df[~performance_df.index.to_period('m').duplicated()]
		performance_df.to_csv('pf.csv')
		# df1 = performance_df.melt(id_vars=['Date']+list(performance_df.keys()[5:]), var_name='Value')
		line_chart = px.line(performance_df, x= performance_df.index, y = ['SP500','Portfolio'])
		st.subheader('Backtest Performance over Analysis Period')
		st.plotly_chart(line_chart)

		# Create New Portfolio
		new_portfolio = Portfolio.objects.create(user = User.objects.get(pk = 1), name = portfolio_name, description = portfolio_description)
		for index, row in portfolio_df.iterrows():
			new_transaction = Transaction.objects.create(portfolio = new_portfolio, asset = Asset.objects.get(asset_symbol = row['Ticker']), transaction_date = timezone.now(), transaction_type = 'Buy', amount = row['Investment_Amount'])
		st.write("Added New Portfolio - {}".format(new_portfolio.name))



	


