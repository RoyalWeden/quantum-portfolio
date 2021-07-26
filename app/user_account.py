from app import mongodb, stocks

def get_billing_info(id):
    info = mongodb.get_billing_info(id)
    return info

def update_billing_info(id, form):
    new_info = {
        'country': form['billingCountryInput'],
        'state': form['billingStateInput'],
        'city': form['billingCityInput'],
        'address1': form['billingAddressLine1Input'],
        'address2': form['billingAddressLine2Input'],
        'zipcode': form['billingZipcodeInput']
    }
    mongodb.set_billing_info(id, new_info)

def get_portfolio_settings(id):
    portfolio_settings = mongodb.get_portfolio_settings(id)
    portfolio_settings['stocks'] = ','.join(portfolio_settings['stocks'])
    return portfolio_settings

def update_portfolio_settings(id, form):
    portfolio_settings = get_portfolio_settings(id)
    selected_stocks = form['stockSelectionInput'].replace(' ', '').split(',')
    for i in range(len(selected_stocks)):
        selected_stocks[i] = selected_stocks[i].upper()
    possible_tickers = stocks.get_tickers().to_list()
    for i in range(len(selected_stocks)-1, -1, -1):
        if not selected_stocks[i] in possible_tickers:
            selected_stocks.pop(i)
    new_settings = {
        'stocks': selected_stocks,
        'auto_generate_rate': form['generateRateInput'],
        'last_generated_date': portfolio_settings['last_generated_date'],
        'next_generate_date': portfolio_settings['next_generate_date']
    }
    mongodb.set_portfolio_settings(id, new_settings)

def update_account(id, form):
    new_account = {
        'email': form['emailInput'],
        'password': form['passwordInput']
    }
    mongodb.set_account(id, new_account)