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

def profiles():
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles', headers=headers)

	data = r.json()
	return data['PROFILES']

def profile(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/' + str(profile), headers=headers)

	data = r.json();
	profile_collection = db.profile

	profile_collection.update({"ID": profile}, data, True)

def pages(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) + '/pages', headers=headers)

	return r.json()["PAGES"];

def page(profile, page):
	
	print "Get page " + str(page) + " for profile " + str(profile)
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) +'/pages/' + str(page), headers=headers)

	data = r.json();
	page_collection = db.page

	data["PAGE"]["PROFILE"] = profile

	page_collection.update({"PAGE.ID": page, "PAGE.PROFILE": profile}, data, True)

def page_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return page(*a_b)

def optionlists(profile):
	
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) + '/optionlists', headers=headers)

	return r.json()["OPTIONLISTS"];

def optionlist(profile, optionlist):
	
	print "Get optionlist " + str(optionlist) + " for profile " + str(profile)
	r = requests.get('https://abctest.iformbuilder.com/exzact/api/profiles/'+ str(profile) +'/optionlists/' + str(optionlist), headers=headers)

	data = r.json();
	optionlist_collection = db.optionlist

	data["OPTIONLIST"]["PROFILE"] = profile

	optionlist_collection.update({"OPTIONLIST.ID": optionlist, "OPTIONLIST.PROFILE": profile}, data, True)

def optionlist_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return optionlist(*a_b)

def syncProfile(zprofile): 

	profile(zprofile['ID'])
	print "Sync profile " + str(zprofile['ID']) + " "  + str(zprofile['NAME'])

def syncPages(zprofile): 

	print "get pages for " + zprofile['NAME']
	zpages = pages(zprofile['ID'])

	ids = [zpage['ID'] for zpage in zpages]
	
	ppool = ThreadPool(8)
	ppool.map(page_star, itertools.izip(itertools.repeat(zprofile['ID']), ids))

def syncOptionlists(zprofile): 

	print "get optionlists for " + zprofile['NAME']
	zoptionlists = optionlists(zprofile['ID'])

	ids = [zoptionlist['ID'] for zoptionlist in zoptionlists]
	
	ppool = ThreadPool(8)
	ppool.map(optionlist_star, itertools.izip(itertools.repeat(zprofile['ID']), ids))

if __name__ == '__main__':
		
	a = datetime.datetime.now()
	print "Get AccessToken"
	accessToken()
	
	print "get Profiles"
	data = profiles()
	
	pool = ThreadPool(8)
	pool.map(syncProfile, data)
	pool.close();
	pool.join();

	pool = ThreadPool(8)
	pool.map(syncPages, data)
	pool.close();
	pool.join();

	pool = ThreadPool(8)
	pool.map(syncOptionlists, data)
	pool.close();
	pool.join();

	b = datetime.datetime.now()
	print(b-a)
				