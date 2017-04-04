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


def get_spent_and_income_by_month(transactions, ignore_donuts=False):
	spent_and_income_by_month = {}
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
		printable_stats[month] = {'spent': "$%.2f" % Decimal(printable_stats[month]['spent']*-1).quantize(Decimal('.01')),
								  'income': "$%.2f" % Decimal(printable_stats[month]['income']).quantize(Decimal('.01'))}

	return ast.literal_eval(json.dumps(printable_stats))
	

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--ignore_donuts', dest='ignore_donuts', action='store_true')
	parser.set_defaults(ignore_donuts=False)
	args = parser.parse_args()

	print args.ignore_donuts

	# load a user's transactions
	response = api_call('/api/v2/core/get-all-transactions', {})

	# determine how much money the user spends and makes each month
	spent_and_income_by_month = get_spent_and_income_by_month(transactions=response['transactions'],
															  ignore_donuts=args.ignore_donuts)

	# determine how much money the user spends and makes on average
	spent_and_income_by_month['average'] = get_average_spent_and_income(spent_and_income_by_month)

	# output these numbers in the following format: {"2014-10": {"spent": "$200.00", "income": "$500.00"}, [...]
	pprint(format_financial_stats(spent_and_income_by_month))

	

# [{"amount":-34300,"is-pending":false,"aggregation-time":1412686740000,
# "account-id":"nonce:comfy-cc/hdhehe",
# "clear-date":1412790480000,"transaction-id":"1412790480000",
# "raw-merchant":"7-ELEVEN 23853","categorization":"Unknown",
# "merchant":"7-Eleven 23853","transaction-time":"2014-10-07T12:59:00.000Z"},

