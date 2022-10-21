import os

import requests

server_url = os.getenv("SERVER_URL")

def random_req(subj):
    sess = requests.Session()
    url = f'{server_url}/random/{subj}'
    resp = sess.get(url)
    res = resp.json()

    return res

def search_req(subj, num, lang):

    sess = requests.Session()
    url = f'{server_url}/search/{subj}/{num}/{lang}'
    resp = sess.get(url)
    res = resp.json()
    return res

def translate_req(subj):
    sess = requests.Session()
    url = f'{server_url}/translate/{subj}'
    resp = sess.get(url)
    res = resp.json()
    print(res)
    return res

def trend_req():
    sess = requests.Session()
    url = f'{server_url}/trend'
    resp = sess.get(url)
    res = resp.json()
    dic = dict()
    key = 0
    for g in res:
        key= key+1
        dic[str(key)] = g
    return dic

def get_categories_tenor_req():
    # sess = requests.Session()
    url = f'{server_url}/categories'
    resp = requests.get(url)
    res = resp.json()
    return res

def get_category_list_tenor_req(category):
    sess = requests.Session()
    print(category)
    url = f'{server_url}/category/{category}'
    resp = sess.get(url)
    res = resp.json()
    return res

# https://tenor.googleapis.com/v2/search?q=%D0%BF%D0%BB%D0%B5%D0%B2%D0%B0%D1%82%D1%8C&locale=ru&component=categories&contentfilter=high&key=AIzaSyCy4R_YbUoICqwCH7JGtJiGmOqPDcCO-Uw&client_key=my_test_app
#
# https://tenor.googleapis.com/v2/categories?key=AIzaSyCy4R_YbUoICqwCH7JGtJiGmOqPDcCO-Uw&client_key=my_test_app&locale=ru&type=featured