import os
from flask import Flask, redirect, url_for, request, render_template, session, make_response
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.secret_key = os.environ["SESSION_SECRET"]
app.api_backend_host = os.environ["BACKEND_HOST"]

app.api_backend_wcs_host = os.environ["BACKEND_HOST"]
app.api_backend_solr_host = os.environ["BACKEND_HOST"]
app.api_backend_iib_host = os.environ["BACKEND_HOST"]

app.api_backend_store = os.environ["BACKEND_STORE"]

client = MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.identity_db


@app.route('/')
def identity():

	identity = None
	if "userId" in session:
		identity = db.identity_db.find_one({"userId": session["userId"]})

	return render_template('identity.html', identity=identity)


@app.route('/guestidentity', methods=['POST'])
def guestidentity():
	
	if 'userId' in session and "delete" in request.form:
	
		db.identity_db.delete_one( {"userId" : session["userId"]} )
		session['userId'] = None
		session.clear()
	else: 
	
		task = {}
		resp = requests.post('https://%s/wcs/resources/store/%s/guestidentity' % (app.api_backend_host,app.api_backend_store), json=task, verify=False)
		
		identity_doc = {
			'userId': resp.json()['userId'],
			'WCTrustedToken': resp.json()['WCTrustedToken'],
			'WCToken': resp.json()['WCToken']
		}
		
		db.identity_db.insert_one(identity_doc)
		
		session['userId'] = resp.json()['userId']

	return redirect(url_for('identity'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
