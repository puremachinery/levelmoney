# Requirements:
# requests==2.7.0
# wheel==0.24.0

from __future__ import unicode_literals # python 2 only; for portability/i18n
from os import environ
from pprint import pprint
import json
import requests # needs to be installed separately

URL = 'https://2016.api.levelmoney.com'
API_TOKEN = 'AppTokenForInterview'
UID = int(1110590645)
TOKEN = 'EADCE81EC0B2CE7112E93E8321A71C6B'
DONUT_MERCHANTS = ['Krispy Kreme Donuts', 'Dunkin #336784']

def api_call(endpoint, content):
    content.setdefault("args", {})
    content['args']['api-token'] = API_TOKEN
    content['args'].setdefault('uid', UID)
    content['args'].setdefault('token', TOKEN)
    return requests.post(URL + endpoint,
                         data=json.dumps(content),
                         headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
                         ).json()


def get_spent_and_income_by_month(transactions, ignore_donuts=False, ignore_cc_payments=False):
	from datetime import datetime
	spent_and_income_by_month = {}
	transactions_by_amount = {}
	for t in transactions:
		amount = t['amount']
		amount_type = 'income' if amount > 0 else 'spent'
		month = t['transaction-time'][:7]  # e.g. '2014-10-24T07:20:00.000Z'
		
		if not ignore_donuts or t['merchant'] not in DONUT_MERCHANTS:
			if month in spent_and_income_by_month:
				spent_and_income_by_month[month][amount_type] += amount
			else:
				spent_and_income_by_month[month] = {'spent': 0, 'income': 0}
				spent_and_income_by_month[month][amount_type] = amount

		if ignore_cc_payments:
			tx_dt = datetime.strptime(t['transaction-time'],'%Y-%m-%dT%H:%M:%S.%fZ')
			t['transaction-date'] = tx_dt
			if amount*-1 in transactions_by_amount:
				transactions_by_amount[abs(amount)].append(t)
				# N.B. I'm going to assume there are only 2 transactions with the same amount.
				# Almost certainly a false assumption, but allows for a simpler first version of this feature.
				# ... and this needs tests.
				# Well, many of these functions will need tests. But especially this one.
			else:
				transactions_by_amount[abs(amount)] = [t]

	if ignore_cc_payments:
		for amount, tx_list in transactions_by_amount.iteritems():
			if len(tx_list) == 2:
				delta = tx_list[0]['transaction-date'] - tx_list[1]['transaction-date']
				if abs(delta.days) < 1:
					for tx in tx_list:
						amount_type = 'income' if tx['amount'] > 0 else 'spent'
						month = tx['transaction-time'][:7]
						spent_and_income_by_month[month][amount_type] -= tx['amount']

	return spent_and_income_by_month


def get_average_spent_and_income(spent_and_income_by_month):
	average_spent = sum(row['spent'] for row in spent_and_income_by_month.values()) / len(spent_and_income_by_month)
	average_income = sum(row['income'] for row in spent_and_income_by_month.values()) / len(spent_and_income_by_month)
	return {'spent': average_spent, 'income': average_income}


def format_financial_stats(spent_and_income_by_month):
	from decimal import Decimal
	import ast
	import collections

	printable_stats = collections.OrderedDict(sorted(spent_and_income_by_month.items()))
	for month in printable_stats:
		printable_stats[month] = {'spent': "$%.2f" % Decimal(printable_stats[month]['spent']*-1/10000).quantize(Decimal('.01')),
								  'income': "$%.2f" % Decimal(printable_stats[month]['income']/10000).quantize(Decimal('.01'))}

	return ast.literal_eval(json.dumps(printable_stats))
	

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--ignore_donuts', dest='ignore_donuts', action='store_true')
	parser.set_defaults(ignore_donuts=False)
	parser.add_argument('--ignore_cc_payments', dest='ignore_cc_payments', action='store_true')
	parser.set_defaults(ignore_cc_payments=False)
	args = parser.parse_args()

	# load a user's transactions
	response = api_call('/api/v2/core/get-all-transactions', {})

	# determine how much money the user spends and makes each month
	spent_and_income_by_month = get_spent_and_income_by_month(transactions=response['transactions'],
															  ignore_donuts=args.ignore_donuts,
															  ignore_cc_payments=args.ignore_cc_payments)

	# determine how much money the user spends and makes on average
	spent_and_income_by_month['average'] = get_average_spent_and_income(spent_and_income_by_month)

	# output these numbers in the following format: {"2014-10": {"spent": "$200.00", "income": "$500.00"}, [...]
	pprint(format_financial_stats(spent_and_income_by_month))


