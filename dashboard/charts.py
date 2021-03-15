import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import streamlit as st

def plot_stock_price_area_chart(stock_prices: pd.DataFrame) -> None:
	c_area = px.area(stock_prices['Close'], title = 'Stock Price')
	c_area.update_xaxes(
    title_text = 'Date',
    rangeslider_visible = True,
    rangeselector = dict(
        buttons = list([
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
            dict(count = 5, label = '5Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))

	c_area.update_yaxes(title_text = 'Close Price', tickprefix = '$')
	c_area.update_layout(showlegend = False,
    title = {
        'text': 'Closing Share Price',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

	return c_area

def plot_stock_return_line_chart(stock_prices: pd.DataFrame) -> None:
	stock_daily_returns = stock_prices['Close'].pct_change()
	c_area = px.line(stock_daily_returns, title = 'Daily Returns')
	c_area.update_xaxes(
    title_text = 'Date',
    rangeslider_visible = True,
    rangeselector = dict(
        buttons = list([
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
            dict(count = 5, label = '5Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))

	c_area.update_yaxes(title_text = 'Daily Return', tickprefix = '%')
	c_area.update_layout(showlegend = False,
    title = {
        'text': 'Daily Return',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

	return c_area


def plot_stock_price_candle_chart(stock_prices: pd.DataFrame) -> None:
	c_candlestick = go.Figure(data = [go.Candlestick(x = stock_prices.index, 
                                               open = stock_prices['Open'], 
                                               high = stock_prices['High'], 
                                               low = stock_prices['Low'], 
                                               close = stock_prices['Close'])])

	c_candlestick.update_xaxes(
	    title_text = 'Date',
	    rangeslider_visible = True,
	    rangeselector = dict(
	        buttons = list([
	            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
	            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
	            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
	            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
	            dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),	
            	dict(count = 5, label = '5Y', step = 'year', stepmode = 'backward'),		
	            dict(step = 'all')])))

	c_candlestick.update_layout(
	    title = {
	        'text': 'Share Price Trends',
	        'y':0.9,
	        'x':0.5,
	        'xanchor': 'center',
	        'yanchor': 'top'})

	c_candlestick.update_yaxes(title_text = 'Close Price', tickprefix = '$')
	return c_candlestick

