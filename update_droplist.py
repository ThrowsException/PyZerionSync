import requests
import pymongo
import json
import pprint

from pymongo import MongoClient

client = MongoClient()
db = client.zerion

ZerionClientKey = "717ee9267011f90f4d97ec1837ec20a30eb6d4c3"
ZerionRefreshKey ="27dcc34e838fbab8f0d03626a6e4151218d923da"
AccessToken = "";
headers = {};

json_data=open('json_data.json')

data = json.load(json_data)
json_data.close()


def accessToken():
	payload = {
		'code': ZerionRefreshKey, 
		'client_id': ZerionClientKey,
		'grant_type': 'refresh_token'
	}
	
	r = requests.post('https://abctest.iformbuilder.com/exzact/api/oauth/token', data=payload)
	global AccessToken 
	AccessToken = r.json()['access_token']
	
	global headers 
	headers = {'X-IFORM-API-VERSION': '5.4.1', 'Authorization' : 'Bearer '  + AccessToken}

def optionlist():
	
	print "Update optionlist"
	d = json.dumps(data)
	
	headers = {'X-IFORM-API-VERSION': '5.4.1', 'Authorization' : 'Bearer '  + AccessToken, 'X-IFORM-API-REQUEST-ENCODING': 'JSON', 'Content-Type': 'application/json'}

	r = requests.put('https://abctest.iformbuilder.com/exzact/api/profiles/10064/optionlists/145440', data=d, headers=headers)

	print(r.json())

if __name__ == '__main__':
	
	accessToken()
	optionlist()
	