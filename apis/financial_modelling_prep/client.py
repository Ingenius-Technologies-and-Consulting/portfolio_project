import requests
import http.cookiejar

from ..exceptions import APIError
from ..config import FMP_API_KEY, FMP_BASE_URL


class BlockAll(http.cookiejar.CookiePolicy):
    def set_ok(self, cookie, request):
        return False

class Client:
	"""
	API Client for Financial Modelling Prep
	"""
	def __init__(self):
		self.base_url = FMP_BASE_URL
		self.session = requests.Session()
		self.session.cookies.policy = BlockAll()
		self.params = {'apikey': FMP_API_KEY}

	def __send_message(self, method, end_point, params = None, data = None):
		"""
		Send API Request
		Args:
			method(str): HTTP method
			endpoint(str): Endpoint to be added to base url
			params (Optional): HTTP request parameters
			data(optional): HTTP request payload
		Returns:
			dict/list: API Response
		"""
		url = self.base_url + end_point
		if params:
			params = {**self.params, **params}
		else:
			params = self.params
		print("Params:", params)
		print(url)

		try:
			r = self.session.request(method, url, params = params, data = data)
			r.raise_for_status()
		
		except (requests.ConnectionError, requests.Timeout) as e:
			raise APIError('Connection Error or Timeout')
		
		except requests.exceptions.HTTPError as e:
			error = e.response.json()
			code = error['status']
			message = error['message']
			raise APIError('-'.join([code, message]))

		return r.json()

	def get_profile(self, ticker: str) -> dict:
		"""
		Get profile of company for ticker
		Args:
			ticker(str): Company ticker symbol
		Returns:
			dict: API Response company profile
		"""
		end_point = 'profile/' + ticker
		company_profile = self.__send_message(method = 'GET', end_point = end_point)
		return company_profile

	def get_income_profile(self, ticker:str, period:str = '5') -> dict:
		"""
		Fetch the summary financials for the company
		Args:
			ticker(str): Company stock ticker
			period(str): Number of years for fetching financials
		Returns:
			DataFrame: A dataframe for with the summary income statement and balance sheet data
		"""

		# Fetch income summary
		income_end_point = 'income-statement/' + ticker
		params = {'limit': '5'}
		income_profile = self.__send_message(method = 'GET', end_point = income_end_point, params = params)
		return income_profile

	def get_balance_sheet_profile(self, ticker: str, period: str = '5') -> dict:

		balance_sheet_end_point = 'balance-sheet-statement/' + ticker
		params = {'limit': '5'}
		balance_sheet_profile = self.__send_message(method = 'GET', end_point = balance_sheet_end_point, params = params)
		return balance_sheet_profile





