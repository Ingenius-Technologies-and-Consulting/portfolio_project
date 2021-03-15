import streamlit as st
import pandas as pd

from portfolio.models import Portfolio, Transaction

def portfolio_analysis() -> None:
	portfolios = Portfolio.objects.all()
	portfolio_name = st.selectbox('Select Portfolio', portfolios, index = 0)
	if portfolio_name:
		portfolio = Portfolio.objects.get(name = portfolio_name)
		transactions = pd.DataFrame(list(Transaction.objects.filter(portfolio = portfolio).values_list('asset__asset_name','transaction_type','amount','transaction_price','transaction_date')),columns = ['Asset Name','Transaction Type','Amount','Transaction_Price','Date'])
		st.write(transactions)


