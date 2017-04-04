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
                         headers={
                         		  'Content-Type': 'application/json',
                                  'Accept': 'application/json'}
                         ).json()


if __name__ == "__main__":
	# load a user's transactions
	response = api_call('/api/v2/core/get-all-transactions', {})
	transactions = response['transactions']
	print transactions[0]['is-pending']

	# determine how much money the user spends and makes each month
	pending_count = sum(1 for trans in transactions if trans['is-pending'] == True)
	print 'pending_count:' + str(pending_count)
	print len(transactions)

	# determine how much money the user spends and makes on average

	# pprint(res)
	# print res['transactions'][0]['merchant']
	

# [{"amount":-34300,"is-pending":false,"aggregation-time":1412686740000,
# "account-id":"nonce:comfy-cc/hdhehe",
# "clear-date":1412790480000,"transaction-id":"1412790480000",
# "raw-merchant":"7-ELEVEN 23853","categorization":"Unknown",
# "merchant":"7-Eleven 23853","transaction-time":"2014-10-07T12:59:00.000Z"},

