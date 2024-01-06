from bsedata.bse import BSE


def get_current_price(company_id):
    b = BSE()
    q = b.getQuote(company_id)
    return (float(q["currentValue"]))