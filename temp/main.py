import os
import streamlit as st
from utils import read_markdown_file
from config import MD_FILE_PATH

from assets.models import Asset

def main():
	body_md_file = os.path.join(MD_FILE_PATH, 'body.md')
	st.title("Portfolio Management")
	st.markdown(read_markdown_file(body_md_file), unsafe_allow_html=True)
	menu=["Company Analysis", "Portfolio Overview","Optimize Portfolio"]
	choices = st.sidebar.selectbox("Select Dashboard",menu, index = 2)

	if choices == 'Company Analysis':
		st.subheader('Stock Exploration & Feature extraction')
		stocks = Assets.objects.filter(asset_type__asset_type = 'EQ').values_list('asset_name')
		stock_choices = st.selectbox(stocks)
		print(stock_choices)


if __name__ == '__main__':
	main()