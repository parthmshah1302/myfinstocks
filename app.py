from flask import Flask, render_template, request, redirect, flash
from pymongo import MongoClient
import helper_functions
import locale
import uuid  # For generating unique IDs

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["myfincap_stock_portfolio"]
clients_collection = db["client"]
company_list_collection = db["company_list"]
client_holdings_collection = db["client_holdings"]

@app.route('/')
def index():
    clients = clients_collection.find()  # Retrieve all clients
    return render_template('index.html', clients=clients)

@app.route('/create_client', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        client_name = request.form['client_name']

        # Check if the client already exists
        existing_client = clients_collection.find_one({"name": client_name})
        if existing_client:
            flash('Client already exists', 'error')
            return redirect('/')

        # If client doesn't exist, create a new one
        client_id = str(uuid.uuid4())  # Generate a unique ID for the client
        clients_collection.insert_one({"name": client_name, "id": client_id})
        client_holdings_collection.insert_one({client_name: []})

        flash('Client created successfully', 'success')
        return redirect('/')

    return render_template('create_client.html')

@app.route('/select_stocks/<client_id>', methods=['GET', 'POST'])
def select_stocks(client_id):
    if request.method == 'POST':
        selected_company = request.form['selected_company']
        quantity = int(request.form['quantity'])

        # Fetch client by client ID
        client = clients_collection.find_one({"id": client_id})
        if client:
            client_name = client['name']

            # Fetch company details from company_list_collection
            company_details = company_list_collection.find_one({"name": selected_company})
            
            if company_details:
                company_id = company_details.get('_id')
                
                # Retrieve the client's stock holdings
                client_holdings = client_holdings_collection.find_one({client_name: []})
                
                # Update the client's stock holdings
                updated_holdings = {
                    "company": selected_company,
                    "quantity": quantity,
                    "id": company_id
                }

                client_holdings[client_name].append(updated_holdings)
                client_holdings_collection.update_one(
                    {client_name: {"$exists": True}},
                    {"$set": {client_name: client_holdings[client_name]}},
                    upsert=True
                )
        return redirect('/')

    companies = [company['name'] for company in company_list_collection.find({}, {"name": 1})]

    return render_template('select_stocks.html', client_id=client_id, companies=companies)

from bsedata.bse import BSE  # Import BSE module

@app.route('/view_portfolio/<client_id>')
def view_portfolio(client_id):
    # Fetch client by client ID
    client = clients_collection.find_one({"id": client_id})
    if client:
        client_name = client['name']
        
        # Retrieve the client's stock holdings
        client_portfolio = client_holdings_collection.find_one({client_name: []}).get(client_name, [])
        
        # Update current_price and current_value for each company in client_portfolio
        for company in client_portfolio:
            company["current_price"] = helper_functions.get_current_price(company["id"])
            company["current_value"] = company["current_price"] * company["quantity"]

        # Sort client_portfolio based on current_value in descending order
        client_portfolio = sorted(client_portfolio, key=lambda x: x["current_value"], reverse=True)

        # Calculate the total value
        total = sum(company["current_value"] for company in client_portfolio)

        return render_template('view_portfolio.html', client_name=client_name, client_portfolio=client_portfolio, total=total)
    
    return "Client portfolio not found."

if __name__ == '__main__':
    locale.setlocale(locale.LC_NUMERIC, 'en_IN.UTF-8')
    app.run(debug=True)
