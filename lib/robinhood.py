# I could roll my own method of obtaining the necessary data but the robin_stocks package
# looks like it has what I need and looks well-maintained so I'll use that for now.
import robin_stocks.robinhood as r


#!!! Fill out username and password
username = ''
password = ''
#!!!

login = r.login(username,password)

profileData = r.load_portfolio_profile()
allTransactions = r.get_bank_transfers()
cardTransactions= r.get_card_transactions()

deposits = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'completed'))
withdrawals = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'withdraw') and (x['state'] == 'completed'))
debits = sum(float(x['amount']['amount']) for x in cardTransactions if (x['direction'] == 'debit' and (x['transaction_type'] == 'settled')))
reversal_fees = sum(float(x['fees']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'reversed'))

money_invested = deposits + reversal_fees - (withdrawals - debits)
dividends = r.get_total_dividends()
percentDividend = dividends/money_invested*100

equity = float(profileData['extended_hours_equity'])
totalGainMinusDividends = equity - dividends - money_invested
percentGain = totalGainMinusDividends/money_invested*100

print("The total money invested is {:.2f}".format(money_invested))
print("The total equity is {:.2f}".format(equity))
print("The net worth has increased {:0.2}% due to dividends that amount to {:0.2f}".format(percentDividend, dividends))
print("The net worth has increased {:0.3}% due to other gains that amount to {:0.2f}".format(percentGain, totalGainMinusDividends))