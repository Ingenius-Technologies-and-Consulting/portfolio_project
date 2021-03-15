import pandas as pd
import os
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

		# Create entries for Equity and ETF
		eq_asset, created = AssetType.objects.get_or_create(asset_type = 'EQ', description = 'Equity')
		etf_asset, created = AssetType.objects.get_or_create(asset_type = 'ETF', description = 'Exchange Traded Fund')

		# Read the tickers file from data folder
		DATA_PATH = os.path.join(str(Path(__file__).resolve().parents[3]),'data','tickers.csv')
		ticker_data = pd.read_csv(DATA_PATH)
		us_tickers = ticker_data[ticker_data['country'] == 'USA'].values.tolist()
		ind_tickers = ticker_data[ticker_data['country'] == 'India'].values.tolist()
		
		# If the ticker does not exist in the database already, create it
		existing_tickers = Asset.objects.filter(asset_type__asset_type = 'EQ').values_list('asset_symbol', flat = True)
		
		if len(existing_tickers) > 0:
			us_tickers = [x for x in us_tickers if x[0] not in list(existing_tickers)]
			ind_tickers = [x for x in ind_tickers if x[0] not in list(existing_tickers)]

			us_tickers = [{'asset_symbol':x[0],'asset_type':eq_asset,'asset_name':x[1], 'asset_exchange':x[2],'asset_category':x[3],'asset_country':x[4]} for x in us_tickers]
			ind_tickers = [{'asset_symbol':x[0],'asset_type':eq_asset,'asset_name':x[1], 'asset_exchange':x[2],'asset_category':x[3],'asset_country':x[4]} for x in ind_tickers]
		else:
			us_tickers = [{'asset_symbol':x[0],'asset_type':eq_asset,'asset_name':x[1], 'asset_exchange':x[2],'asset_category':x[3],'asset_country':x[4]} for x in us_tickers]
			ind_tickers = [{'asset_symbol':x[0],'asset_type':eq_asset,'asset_name':x[1], 'asset_exchange':x[2],'asset_category':x[3],'asset_country':x[4]} for x in ind_tickers]
			
		print("Adding {} US tickers to db".format(len(us_tickers)))
		print("Adding {} India tickers to db".format(len(us_tickers)))
		us_tickers = [Asset(**data_dict) for data_dict in us_tickers]
		us_tickers = Asset.objects.bulk_create(us_tickers)

		ind_tickers = [Asset(**data_dict) for data_dict in ind_tickers]
		ind_tickers = Asset.objects.bulk_create(ind_tickers)

		price_df = pd.DataFrame()
		start_date = datetime(datetime.now().year - 5,1,1).strftime('%Y-%m-%d')
		end_date = datetime.now().strftime('%Y-%m-%d')
		

		

