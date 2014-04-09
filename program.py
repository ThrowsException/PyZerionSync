import requests
import time
import pymongo
import datetime
import itertools

from pymongo import MongoClient
from datetime import timedelta
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

client = MongoClient()
db = client.zerion

ZerionClientKey = ""
ZerionRefreshKey =""
AccessToken = "";
headers = {};
threads = 1

def accessToken():
	payload = {
		'code': ZerionRefreshKey, 
		'client_id': ZerionClientKey,
		'grant_type': 'refresh_token'
	}
	
	r = requests.post('https://abctest.iformbuilder.com/exzact/api/oauth/token', data=payload)
	global AccessToken
	print(r.json())
	AccessToken = r.json()['access_token']
	
	global headers 
	headers = {'X-IFORM-API-VERSION': '5.4.1', 'Authorization' : 'Bearer '  + AccessToken}

def profiles():
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles', headers=headers)

	data = r.json()
	return data['PROFILES']

def profile(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/' + str(profile), headers=headers)

	data = r.json()

	if data["STATUS"] == True:
		profile_collection = db.profile
		profile_collection.update({"ID": profile}, data, True)
	else:
		print r.url + "return status False"

def pages(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) + '/pages?DETAIL=true', headers=headers)

	return r.json()["PAGES"];

def page(profile, page):
	
	page_id_str = str(page["ID"])
	page_id = page["ID"]

	print "Get page " + page_id_str + " for profile " + str(profile)
	page_collection = db.page

	p = page_collection.find_one({"PAGE.ID": page_id})

	if p != None and p["PAGE"]["VERSION"] == page["VERSION"]:
		print "page is same version not syncing"
	else:
		r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) +'/pages/' + page_id_str, headers=headers)

		data = r.json()
		if data["STATUS"] == True:
			page_collection = db.page
			data["PAGE"]["PROFILE"] = profile

			page_collection.update({"PAGE.ID": page_id, "PAGE.PROFILE": profile}, data, True)
		else:
			print r.url + "return status False"

def page_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return page(*a_b)

def optionlists(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) + '/optionlists', headers=headers)

	return r.json()["OPTIONLISTS"];

def optionlist(profile, optionlist):
	
	print "Get optionlist " + str(optionlist) + " for profile " + str(profile)
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) +'/optionlists/' + str(optionlist), headers=headers)

	data = r.json()
	if data["STATUS"] == True:
		optionlist_collection = db.optionlist

		data["OPTIONLIST"]["PROFILE"] = profile

		optionlist_collection.update({"OPTIONLIST.OPTION_LIST.ID": optionlist, "OPTIONLIST.PROFILE": profile}, data, True)
	else:
			print r.url + "return status False"

def optionlist_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return optionlist(*a_b)

def syncProfile(zprofile): 

	profile(zprofile['ID'])
	print "Sync profile " + str(zprofile['ID']) + " "  + str(zprofile['NAME'])

def syncPages(zprofile): 

	print "get pages for " + zprofile['NAME']
	zpages = pages(zprofile['ID'])
	
	ppool = ThreadPool(threads)
	ppool.map(page_star, itertools.izip(itertools.repeat(zprofile['ID']), zpages))

def syncOptionlists(zprofile): 

	print "get optionlists for " + zprofile['NAME']
	zoptionlists = optionlists(zprofile['ID'])

	ids = [zoptionlist['ID'] for zoptionlist in zoptionlists]
	
	ppool = ThreadPool(threads)
	ppool.map(optionlist_star, itertools.izip(itertools.repeat(zprofile['ID']), ids))

if __name__ == '__main__':
		
	a = datetime.datetime.now()
	print "Get AccessToken"
	accessToken()
	
	print "get Profiles"
	data = profiles()
	
	pool = ThreadPool(threads)
	pool.map(syncProfile, data)
	pool.close();
	pool.join();

	pool = ThreadPool(threads)
	pool.map(syncPages, data)
	pool.close();
	pool.join();

	pool = ThreadPool(threads)
	pool.map(syncOptionlists, data)
	pool.close();
	pool.join();

	b = datetime.datetime.now()
	print(b-a)
				