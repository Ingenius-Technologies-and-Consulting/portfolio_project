import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()


import streamlit as st 
from dashboard.config import MD_FILE_PATH
from dashboard.utils import read_markdown_file
from dashboard.company_profile import load_company_profile
from dashboard.portfolio_new import create_portfolio
from dashboard.portfolio_profile import portfolio_analysis


# Import models
from assets.models import Asset

body_md_file = os.path.join(MD_FILE_PATH, 'body.md')
st.title("Portfolio Management")
st.markdown(read_markdown_file(body_md_file), unsafe_allow_html=True)
menu=["Company Analysis", "Portfolio Overview","Create Portfolio"]
choices = st.sidebar.selectbox("Select Dashboard",menu, index = 2)

if choices == 'Company Analysis':
	st.subheader('Analyse Company')
	stocks = Asset.objects.filter(asset_type__asset_type = 'EQ').values_list('asset_name', flat = True)
	stock_choice = st.selectbox('Select a Company', stocks)
	if stock_choice:
		stock_ticker = Asset.objects.get(asset_name = stock_choice).asset_symbol
		load_company_profile(stock_ticker)

if choices == 'Create Portfolio':
	create_portfolio()

if choices == 'Portfolio Overview':
	portfolio_analysis()

	
