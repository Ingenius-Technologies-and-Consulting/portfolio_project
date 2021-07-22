import random
import yfinance as yf

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from users.models import User 
from portfolio.models import Portfolio, Transaction
from assets.models import Asset



def gen_datetime(min_year= 2016, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		
		# Create a US portfolio
		us_portfolio_name = 'us_test_portfolio_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		user = User.objects.get(pk = 1)
		new_portfolio = Portfolio.objects.create(user = user, name = us_portfolio_name)
		us_stocks = Asset.objects.filter(asset_country = 'USA')
		# We add 10 transactions to the portfolio 
		for _ in range(10):
			# Select a random stock from US equities
			random_stock = random.choice(us_stocks)
			random_date = gen_datetime()
			investment_amount = random.randint(1000,20000)
			transaction_type = random.choice(['Buy','Sell'])
			start_date = random_date.strftime('%Y-%m-%d')
			end_date = (random_date + timedelta(days = 1)).strftime('%Y-%m-%d')
			ticker = yf.Ticker(random_stock.asset_symbol)
			try:
				ticker_price = ticker.history(start = start_date, end = end_date)
			except Exception as e:
				print("Error", str(e))
				continue
			if ticker_price.empty:
				continue
			else:
				ticker_price = ticker_price.head(1)['Close'].values[0]
				print(ticker_price)
				new_transaction = Transaction.objects.create(portfolio = new_portfolio, asset = random_stock, transaction_type = transaction_type, amount = investment_amount, transaction_price = ticker_price, transaction_date = random_date)

			



