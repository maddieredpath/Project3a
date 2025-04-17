import csv
import requests
import pygal
import os
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

def get_stock_data(ticker, time_series):
    api_key = "JGSKV0LY50824HYL"
    url = "https://www.alphavantage.co/query"

    if time_series == "1":
        function = "TIME_SERIES_INTRADAY"
        time_key = "Time Series (60min)"
        params = {
            "function": function,
            "symbol": ticker,
            "interval": "60min",
            "apikey": api_key
        }
    elif time_series == "2":
        function = "TIME_SERIES_DAILY"
        time_key = "Time Series (Daily)"
        params = {"function": function, "symbol": ticker, "apikey": api_key}
    elif time_series == "3":
        function = "TIME_SERIES_WEEKLY"
        time_key = "Weekly Time Series"
        params = {"function": function, "symbol": ticker, "apikey": api_key}
    else:
        function = "TIME_SERIES_MONTHLY"
        time_key = "Monthly Time Series"
        params = {"function": function, "symbol": ticker, "apikey": api_key}

    response = requests.get(url, params=params)
    data = response.json()
    return data, time_key


def filter_data_by_date(data, time_key, time_series, start_date, end_date):
    filtered_data = {}

    for date in data.get(time_key, {}):
        date_only = date.split()[0] if time_series == "1" else date
        if start_date <= date_only <= end_date:
            filtered_data[date] = data[time_key][date]

    return filtered_data


def create_chart(ticker, chart_type, filtered_data, time_series, start_date, end_date):
    if not filtered_data:
        return None

    chart_title = f"{ticker.upper()} Stock Prices ({start_date} to {end_date})"
    dates = sorted(filtered_data.keys())
    closing_prices = []

    for date in dates:
        close_key = "4. close" if "4. close" in filtered_data[date] else "4. Close"
        closing_prices.append(float(filtered_data[date][close_key]))

    chart = pygal.Bar(x_label_rotation=45) if chart_type == "1" else pygal.Line(x_label_rotation=45)
    chart.title = chart_title
    chart.x_labels = [str(date) for date in dates]
    chart.add('Closing Price', closing_prices)

    output_file = f"static/{ticker}_chart.svg"
    chart.render_to_file(output_file)

    return output_file


def get_stock_symbols_from_csv(csv_path='stocks.csv'):
    stock_symbols = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'Symbol' in row:  # Check if 'Symbol' key exists
                    stock_symbols.append(row['Symbol'])
                else:
                    print(f"Skipping row with missing 'Symbol': {row}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return stock_symbols



@app.route("/", methods=["GET", "POST"])
def index():
    chart_url = None
    error_msg = None
    stock_symbols = get_stock_symbols_from_csv()  # Get stock symbols from CSV

    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper()
        chart_type = request.form.get("chart_type")
        time_series = request.form.get("time_series")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")

            data, time_key = get_stock_data(ticker, time_series)
            filtered_data = filter_data_by_date(data, time_key, time_series, start_date, end_date)
            chart_url = create_chart(ticker, chart_type, filtered_data, time_series, start_date, end_date)
        except Exception as e:
            error_msg = "An error occurred. Please check your input or try a different date range."

    return render_template("index.html", chart_url=chart_url, error=error_msg, stock_symbols=stock_symbols)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
