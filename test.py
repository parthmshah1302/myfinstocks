from bsedata.bse import BSE

b = BSE()
q = b.getQuote("534976")

print(type(q["currentValue"]))