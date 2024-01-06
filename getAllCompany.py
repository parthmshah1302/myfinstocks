# This is to be run every day

from bsedata.bse import BSE
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["myfincap_stock_portfolio"]
collection = db["company_list"]

bse = BSE()
bse = BSE(update_codes = True)
company_data = bse.getScripCodes()

for key, value in company_data.items():
    existing_doc = collection.find_one({"_id": key})
    if not existing_doc:
        collection.insert_one({"_id": key, "name": value})