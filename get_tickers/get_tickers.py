import csv
import yahooquery as yq
import json

def get_yahoo_tickers(company_names):
    tickers = []
    errors = []
    for name in company_names:
        try:
            search_results = yq.search(name)
            ticker_found = False
            for result in search_results['quotes']:
                ticker = result['symbol']
                if ticker.endswith('.BO'):
                    tickers.append(ticker)
                    ticker_found = True
                    print(f"Success: {name} -> {ticker}")
                    break  # Assuming we want only the first match
            if not ticker_found:
                raise ValueError(f"No .BO ticker found for {name}")
        except Exception as e:
            print(f"Error: {name} -> {e}")
            tickers.append(None)
            errors.append(name)
    return tickers, errors

def read_company_names_and_quantities_from_csv(file_path):
    company_names = []
    quantities = []
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        # Assuming the first row is a header
        next(csvreader)
        for row in csvreader:
            company_names.append(row[0])  # Company Name
            quantities.append(row[1])     # Quantity
    return company_names, quantities

def write_tickers_to_csv(file_path, company_names, quantities, tickers):
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the header
        csvwriter.writerow(['Company Name', 'Quantity', 'Yahoo Ticker'])
        # Write the data
        for name, quantity, ticker in zip(company_names, quantities, tickers):
            csvwriter.writerow([name, quantity, ticker])

def create_user_data_json(file_path, user_name, tickers, quantities):
    stocks = {ticker: {"quantity": int(quantity)} for ticker, quantity in zip(tickers, quantities) if ticker}
    user_data = {
        "name": user_name,
        "stocks": stocks
    }
    with open(file_path, 'w') as jsonfile:
        json.dump(user_data, jsonfile, indent=4)

# File paths
input_csv = 'input_companies.csv'  # Replace with your input CSV file path if different
output_csv = 'output_tickers.csv'  # Replace with your desired output CSV file path if different
user_data_json = 'user_data.json'  # Replace with your desired JSON file path if different

# User details
user_name = 'Anup Kumar'

# Read company names and quantities from the input CSV
company_names, quantities = read_company_names_and_quantities_from_csv(input_csv)

# Get Yahoo tickers
tickers, errors = get_yahoo_tickers(company_names)

# Write the company names, quantities, and their corresponding tickers to the output CSV
write_tickers_to_csv(output_csv, company_names, quantities, tickers)

# Create the user data JSON file
create_user_data_json(user_data_json, user_name, tickers, quantities)

print(f'Tickers have been written to {output_csv}')
print(f'User data JSON has been created at {user_data_json}')

if errors:
    print("The following companies had errors and were skipped:")
    for error in errors:
        print(error)