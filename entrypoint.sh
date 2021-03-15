#!/bin/sh
rm db.sqlite3
touch db.sqlite3
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py setup_tickers_updated
python3 manage.py setup_dummy_user
python3 manage.py setup_dummy_portfolio
streamlit run home.py