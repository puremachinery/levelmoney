# Requirements:
# requests==2.7.0
# wheel==0.24.0

from __future__ import unicode_literals # python 2 only; for portability/i18n
import requests # needs to be installed separately
import json
from pprint import pprint

from os import environ

URL = 'https://2016.api.levelmoney.com'
API_TOKEN = 'AppTokenForInterview'
UID = int(1110590645)
TOKEN = 'EADCE81EC0B2CE7112E93E8321A71C6B'

def api_call(endpoint, content):
    content.setdefault("args", {})
    content['args']['api-token'] = API_TOKEN
    content['args'].setdefault('uid', UID)
    content['args'].setdefault('token', TOKEN)
    return requests.post(URL + endpoint,
                         data=json.dumps(content),
                         headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
                         ).json()


if __name__ == "__main__":
	# load a user's transactions
	response = api_call('/api/v2/core/get-all-transactions', {})
	transactions = response['transactions']
	print transactions[0]['is-pending']

	# determine how much money the user spends and makes each month
	spent_and_income_by_month = {}
	for t in transactions:
		amount = t['amount']
		amount_type = 'income' if amount > 0 else 'spent'
		month = t['transaction-time'][:7]  # e.g. '2014-10-24T07:20:00.000Z'
		
		if month in spent_and_income_by_month:
			spent_and_income_by_month[month][amount_type] += amount
		else:
			spent_and_income_by_month[month] = {'spent': 0, 'income': 0}
			spent_and_income_by_month[month][amount_type] = amount

	# determine how much money the user spends and makes on average
	average_spent = sum(row['spent'] for row in spent_and_income_by_month.values()) / len(spent_and_income_by_month)
	average_income = sum(row['income'] for row in spent_and_income_by_month.values()) / len(spent_and_income_by_month)



	

# [{"amount":-34300,"is-pending":false,"aggregation-time":1412686740000,
# "account-id":"nonce:comfy-cc/hdhehe",
# "clear-date":1412790480000,"transaction-id":"1412790480000",
# "raw-merchant":"7-ELEVEN 23853","categorization":"Unknown",
# "merchant":"7-Eleven 23853","transaction-time":"2014-10-07T12:59:00.000Z"},

