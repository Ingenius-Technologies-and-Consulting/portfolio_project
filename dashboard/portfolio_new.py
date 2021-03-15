import os
from pathlib import Path
import pandas as pd  
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from operator import itemgetter
import requests
import yfinance as yf

from assets.models import Asset
from portfolio.models import Portfolio, Transaction
from users.models import User

plt.style.use('fivethirtyeight')
np.random.seed(777)

def get_company_name(ticker: str) -> str:
	"""
	Get company name for a symbol
	"""
	url = 'http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=' + ticker + '&region=1&lang=en'
	result = requests.get(url).json()
	for r in result['ResultSet']['Result']:
		if r['symbol'] == ticker:
			return r['name']

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
  returns = np.sum(mean_returns*weights ) *252
  std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
  return std, returns
  
def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
	results = np.zeros((3,num_portfolios))
	weights_record = []
	for i in range(num_portfolios):
		weights = np.random.random(mean_returns.shape[0])
		weights /= np.sum(weights)
		weights_record.append(weights)
		portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
		results[0,i] = portfolio_std_dev
		results[1,i] = portfolio_return
		results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
	return results, weights_record

def display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate, price_df):
  results, weights = random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)
  max_sharpe_idx = np.argmax(results[2])
  sdp, rp = results[0, max_sharpe_idx], results[1, max_sharpe_idx]
  max_sharpe_allocation = pd.DataFrame(weights[max_sharpe_idx], index=price_df.columns, columns=['allocation'])
  max_sharpe_allocation.allocation = [round(i*100,2) for i in max_sharpe_allocation.allocation]
  max_sharpe_allocation = max_sharpe_allocation.T
  
  min_vol_idx = np.argmin(results[0])
  sdp_min, rp_min = results[0, min_vol_idx], results[1, min_vol_idx]
  min_vol_allocation = pd.DataFrame(weights[min_vol_idx], index=price_df.columns, columns=['allocation'])
  min_vol_allocation.allocation = [round(i*100,2) for i in min_vol_allocation.allocation]
  min_vol_allocation = min_vol_allocation.T

  st.subheader('Recommended Portfolio')
  st.write("Based on the risk preference, we allocate investment between S&P500 (low risk asset) and an optimal stock portfolio (High Risk Diversified Asset)")
  st.write('We use the Efficient Frontier Portfolio Optimization Method to Select Optimal Portfolios')
  st.write('This is based on historical returns and risk of individual assets and their associated covariances')
  st.write('To avoid over diversification we limit portfolio to 10 stocks with the highest Sharpe Ratio in the period')
  st.write("-"*80)
  st.write("Maximum Sharpe Ratio Portfolio Allocation\n")
  st.write("Annualised Return:", round(rp, 2))
  st.write("Annualised Volatility:", round(sdp, 2))
  st.write("\n")
  # st.write('Allocation Percentages')
  # st.write(max_sharpe_allocation)
  st.write("-"*80)
  st.write("Minimum Volatility Portfolio Allocation\n")
  st.write("Annualised Return:", round(rp_min, 2))
  st.write("Annualised Volatility:", round(sdp_min, 2))
  st.write("\n")
  # st.write('Allocation Percentages')
  # st.write(min_vol_allocation)

  fig = plt.figure(figsize=(10, 7))
  plt.scatter(results[0,:],results[1,:],c=results[2,:],cmap='YlGnBu', marker='o', s=10, alpha=0.3)
  plt.colorbar()
  plt.scatter(sdp,rp,marker='*',color='r',s=500, label='Maximum Sharpe ratio')
  plt.scatter(sdp_min,rp_min,marker='*',color='g',s=500, label='Minimum volatility')
  plt.title('Portfolio Optimization based on Efficient Frontier')
  plt.xlabel('annualised volatility')
  plt.ylabel('annualised returns')
  plt.legend(labelspacing=0.8)
  st.pyplot(fig)

  return min_vol_allocation.T, max_sharpe_allocation.T
  # efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, target)
  # plt.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black', label='efficient frontier')
  # plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
  # plt.xlabel('annualised volatility')
  # plt.ylabel('annualised returns')
  # plt.legend(labelspacing=0.8)
  # st.pyplot(fig)


def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
	p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
	return -(p_ret - risk_free_rate) / p_var

def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
	num_assets = len(mean_returns)
	args = (mean_returns, cov_matrix, risk_free_rate)
	constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
	bound = (0.0,1.0)
	bounds = tuple(bound for asset in range(num_assets))
	result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,method='SLSQP', bounds=bounds, constraints= constraints)
	return result

def portfolio_volatility(weights, mean_returns, cov_matrix):
	return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]

def min_variance(mean_returns, cov_matrix):
	num_assets = len(mean_returns)
	args = (mean_returns, cov_matrix)
	constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
	bound = (0.0,1.0)
	bounds = tuple(bound for asset in range(num_assets))
	result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args,                     method='SLSQP', bounds=bounds, constraints=constraints)

def efficient_return(mean_returns, cov_matrix, target):
	num_assets = len(mean_returns)
	args = (mean_returns, cov_matrix)

	def portfolio_return(weights):
		return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[1]
	constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},{'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
	bounds = tuple((0,1) for asset in range(num_assets))
	result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
	return result


def efficient_frontier(mean_returns, cov_matrix, returns_range):
  efficients = []
  for ret in returns_range:
  	efficients.append(efficient_return(mean_returns, cov_matrix, ret))
  return efficients

def create_price_dataframe(tickers:list) -> pd.DataFrame:
	"""
	Use the yahoo finance API to fetch the list of historical stock prices 
	and create a dataframe
	"""
	price_df = pd.DataFrame()
	consol_data = []
	start_date = datetime(datetime.now().year - 5,1,1).strftime('%Y-%m-%d')
	end_date = datetime.now().strftime('%Y-%m-%d')
	for ticker in tickers:
		stock = yf.Ticker(ticker)
		stock_history = stock.history(start = start_date, end = end_date)
		consol_data.append([stock_history, min(stock_history.index), max(stock_history.index),ticker])
	min_time_stamp = max([x[1] for x in consol_data])
	max_time_stamp = min([x[2] for x in consol_data])
	price_data = [[x[0].loc[(x[0].index >= min_time_stamp) & (x[0].index <= max_time_stamp)]['Close']][0] for x in consol_data]
	
	price_df = pd.concat(price_data, axis = 1)
	price_df.dropna(inplace = True)
	
	column_names = [x[3] for x in consol_data]
	price_df.columns = column_names
	# print(price_df.shape)
	# print(price_df.head(10))
	return price_df


def create_portfolio() -> None:
	
	st.subheader("Portfolio Parameters")
	st.write("Portfolio Name")
	portfolio_name = st.text_input('Portfolio Name', 'Portfolio_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
	st.write("Portfolio Description")
	portfolio_description = st.text_input('Portfolio Description', 'General Investment')
	st.write("Investment Amount (USD)")
	portfolio_investment = st.number_input(label = '', min_value = 0, value = 100000)
	st.markdown("---")
	st.subheader('Risk Assessment Form')
	st.write('Investor Age')
	investor_age = st.text_input('Investor Age','30') 
	st.write('Portfolio Risk Preference')
	risk_level = st.selectbox('Portfolio Risk Preference',('Low','Moderate','High'))
	st.write('Market')
	market = st.selectbox('India',('USA','India')) 
		
	if st.button('Build Portfolio'):
		if risk_level == 'High':
			index_weight = 0.2
		elif risk_level == 'Moderate':
			index_weight = 0.4
		else:
			index_weight = 0.6
		st.markdown("---")

		# Separate investments into S&P 500 and Equities based on risk assessment
		index_investment = portfolio_investment * index_weight
		equity_investment = portfolio_investment - index_investment
		# print(s_p_investment, equity_investment)

		# Load price data
		# price_data_path = os.path.join(str(Path(__file__).resolve().parents[1]), 'data/price_data.csv')
		# price_df = pd.read_csv(price_data_path)
		# price_df['Date'] = pd.to_datetime(price_df['Date'])
		# price_df.set_index('Date', inplace = True)

		# # Drop S&P from the price data
		# s_p_df = price_df['^GSPC']
		# equity_df = price_df.drop(columns = ['^GSPC'], axis = 1)

		# To avoid over diversification we will consider only the top 10 stocks with highest sharpe ratio
		# stock_sharpe_ratios = []
		# for stock in equity_df.columns:
		# 	returns = equity_df[stock].pct_change()
		# 	mean_returns = returns.mean()
		# 	std = returns.std()
		# 	sharpe_ratio = mean_returns/std 
		# 	stock_sharpe_ratios.append((stock, sharpe_ratio))
		# top_stocks = [x[0] for x in sorted(stock_sharpe_ratios, key = itemgetter(1), reverse = True)[:11]]

		# Alternative method is to use specific stocks for US market and India market
		us_tickers = ['MSFT','AAPL','TSLA','AMZN','NVDA','AMD','GOOG','CRM','JPM','PG','JNJ','ABBV','NFLX','SHOP','SQ','^GSPC']
		ind_tickers = ['ASIANPAINT.NS','HDFC.NS','ADANIENT.NS','RELIANCE.NS','ADANIPORTS.NS','BAJAJ-AUTO.NS','M&M.NS','MARUTI.NS','BRITANNIA.NS','HINDUNILVR.NS','NESTLEIND.NS','TITAN.NS','DRREDDY.NS','TCS.NS','INFY.NS','WIPRO.NS','HDFCBANK.NS','ICICIBANK.NS','KOTAKBANK.NS','^BSESN']
		# create_price_dataframe(ind_tickers)

		if market == 'India':
			# Create equity price dataframe
			price_df = create_price_dataframe(ind_tickers)
			equity_df = price_df.drop('^BSESN', axis = 1)
			index_df = price_df['^BSESN']
			risk_free_rate = 0.05
			index_ticker = '^BSESN'
			index_name = 'BSE Sensex'

		if market == 'USA':
			price_df = create_price_dataframe(us_tickers)
			equity_df = price_df.drop('^GSPC', axis = 1)
			index_df = price_df['^GSPC']
			risk_free_rate = 0.0178
			index_ticker = '^GSPC'
			index_name = 'S&P500'

		returns = equity_df.pct_change()
		mean_returns = returns.mean()
		cov_matrix = returns.cov()
		num_portfolios = 25000
		
		# # Generate random portfolios
		min_vol_allocation, max_sharpe_allocation = display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate, equity_df)

		# # Create minimum value portfolio
		min_vol_portfolio_df = pd.DataFrame(columns = ['Company_Name', 'Ticker', 'Purchase_Units','Investment_Amount(USD)'])
		tickers = min_vol_allocation.index.values
		allocations = [x[0]/100 for x in min_vol_allocation.values.tolist()]

		company_name = []
		discrete_allocation = []
		investment_amount = []
		for ticker, allocation in zip(tickers, allocations):
			company_name.append(get_company_name(ticker))
			investment_amount.append(allocation * equity_investment)
			discrete_allocation.append(int((allocation * equity_investment)/equity_df[ticker].values[-1]))

		tickers = np.append(tickers,index_ticker)
		company_name.append(index_name)
		investment_amount.append(index_investment)
		discrete_allocation.append(int(index_investment/index_df.values[-1]))

		investment_amount = [ '%.2f' % elem for elem in investment_amount]
		min_vol_portfolio_df['Company_Name'] = company_name
		min_vol_portfolio_df['Investment_Amount(USD)'] = investment_amount
		min_vol_portfolio_df['Purchase_Units'] = discrete_allocation
		min_vol_portfolio_df['Ticker'] = tickers
		st.subheader('Minimum Volatility Portfolio')
		st.write(min_vol_portfolio_df)

		# # Create minimum value portfolio
		max_sharpe_portfolio_df = pd.DataFrame(columns = ['Company_Name', 'Ticker', 'Purchase_Units','Investment_Amount(USD)'])
		tickers = max_sharpe_allocation.index.values
		allocations = [x[0]/100 for x in max_sharpe_allocation.values.tolist()]
		
		company_name = []
		discrete_allocation = []
		investment_amount = []
		for ticker, allocation in zip(tickers, allocations):
			company_name.append(get_company_name(ticker))
			investment_amount.append(allocation * equity_investment)
			discrete_allocation.append(int((allocation * equity_investment)/equity_df[ticker].values[-1]))

		tickers = np.append(tickers,index_ticker)
		company_name.append(index_name)
		investment_amount.append(index_investment)
		discrete_allocation.append(int(index_investment/index_df.values[-1]))

		investment_amount = [ '%.2f' % elem for elem in investment_amount]
		max_sharpe_portfolio_df['Company_Name'] = company_name
		max_sharpe_portfolio_df['Investment_Amount(USD)'] = investment_amount
		max_sharpe_portfolio_df['Purchase_Units'] = discrete_allocation
		max_sharpe_portfolio_df['Ticker'] = tickers
		st.subheader('Maximum Sharpe Portfolio')
		st.write(max_sharpe_portfolio_df)

		

