from flask import Flask, jsonify
from flask import request,redirect, url_for, make_response, session
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
#from gensim.summarization import summarize
import re
import jwt
from datetime import datetime, timedelta
from flask_basicauth import BasicAuth
from functools import wraps


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER =  os.path.join(APP_ROOT, 'static/')






app = Flask(__name__)
app.config['SECRET_KEY']= 'yashkantharia'


def check_token(func):
	@wraps(func)
	def wrapped(*args,**kwargs):
		token = request.args.get('token')
		if not token:
			return jsonify({'message':'Missing Token'}),403
		try:
			d = jwt.decode(token, app.config["SECRET_KEY"])
		except:
			session['logged_in']=False
			return jsonify({'message':'Invalid Token'}),403
		return func(*args,**kwargs)
	return wrapped



@app.route("/")
def index():

	if not session.get('logged_in'):
		return jsonify({'message':'Enter Credentials to login'}),401

	else: 
		return jsonify({'message':'use existing token or login again'})


@app.route('/login')
def login():
	if request.args.get('username')=='yash' and request.args.get('password')=='webscrapperapi':
		session['logged_in']=True
		token = jwt.encode({'username':request.args.get('username'), 'exp':datetime.utcnow() + timedelta(minutes=10)}, app.config['SECRET_KEY'])
		return jsonify({'token':token.decode('utf-8')})
	else:
		return make_response('unable to verify', 403, {'WWW-uthenticate':'Basic realm:"login required"'})

@app.route('/auth')
@check_token
def auth():

	url = request.args.get("url")
	print(url)


	#check the request and define response
	responseObject = {}

	if(url=="nan"):
		responseObject['statusCode'] = 400
		responseObject['error']='Bad request. Send parameter url with web site URL only'
	else:
		responseObject['statusCode'] = 200
		print('test')


		# target URL to scrap

		# headers
		headers = {
		    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
		    }

		# send request to download the data
		response = requests.request("GET", url, headers=headers)

		# parse the downloaded data
		data = BeautifulSoup(response.text, 'html.parser')
		#print(data)

		#get the required data from HTML using BeautifulSoup
		c_name = data.find('meta',attrs={'property': 'og:title'})
		#print(name.get('content'))
		if c_name != None:
			c_name = c_name.get('content')
		else:
			c_name="Not defiend"



		title = data.find('title')
		#print(title.text)
		if title != None:
			title = title.text
		else:
			title="Not defiend"

		description = data.find('meta',attrs={'name': 'description'})
		#print(description.get('content'))
		if description != None:
			description = description.get('content')
		else:
			description="Not defiend"

		linkedin = data.find('a',attrs={'class': 'linkedin'})
		#print(linkedin.get('href'))
		if linkedin != None:
			linkedin = linkedin.get('href')
		else:
			linkedin="Not defiend"

		email = data.find("meta",attrs={'property':'og:email'})
		#print(email)
		if email != None:
			email = email.get('content')
		else:
			name="Not defiend"

		icon_url = str(data.find("meta",attrs={"property":"og:image"}).get('content'))

		if re.search("http:|https:", icon_url) is None:
		  icon_url = str("http:"+icon_url)

		for inp in data.find_all():
		    if (inp.get_text() == "Pricing" or inp.get_text()== "subscription"):
		        #print ("found")
		        paid = "PAID"
		    else: 
		      paid ="Unkown"

		
		#fetch text from the page
		
		#remove scripts and css
		for s in data(['script', 'style']):
		  s.decompose()

		# Filter out sentences that contain newline characters '\n' or don't contain periods.
		sentence_list = [sentence for sentence in s if not '\n' in sentence]
		sentence_list = [sentence for sentence in s if '.' in sentence]

		article_text =  ' '.join(data.stripped_strings)

		#summary = summarize(article_text, ratio=0.3)

		#Make API call to meaningcloud for Summarization of text

		querystring = {"key":"c1c06e488f5be2f75f2d78fcc46aa28e","txt":article_text,"sentences":"10"}

		headers_summ = {
		'User-Agent': "PostmanRuntime/7.19.0",
		'Accept': "*/*",
		'Cache-Control': "no-cache",
		'Postman-Token': "f1733e8b-aac5-43a0-820e-2c44f8c23dd6,26322fee-b515-4baa-9f2a-d7c43142dd86",
		'Host': "api.meaningcloud.com",
		'Accept-Encoding': "gzip, deflate",
		'Content-Length': "0",
		'Connection': "keep-alive",
		'cache-control': "no-cache"
		}

		response_summ = requests.request("POST",url='https://api.meaningcloud.com/summarization-1.0', headers=headers_summ, params=querystring)

		summary=response_summ.json()['summary']

		print(summary)

		#Screenshot

		#init Chrome web driver 
		driver = webdriver.Chrome(ChromeDriverManager().install())
		driver.get(url);
		#save screenshot in the static folder
		target = os.path.join(APP_ROOT, 'static/')
		#give timestamps as name to the screenshots 
		ts = time.time()
		dest_filename= str(ts)+".png"
		driver.save_screenshot(target+"/"+dest_filename)
		img_url = url_for('static',filename=dest_filename)
		#kill the web driver
		driver.quit()


		#Generate CSV 
		csv = pd.read_csv("result.csv")
		result = pd.DataFrame()
		result= pd.DataFrame([[str(url),c_name,title,str("http://127.0.0.1:5000"+img_url),str(description),str(icon_url),str(email),str(linkedin),str(summary)]],columns=['Given_Website','Company_Name','Title','Website image/screenshot','Short_Description','company_icon','contact_email','LinkedIn','Summarize the website content'])
		df= pd.concat([csv,result],axis=0)
		df.to_csv('result.csv',index=False)

		result = None
		csv = None
		df =None


	return responseObject

if __name__=='__main__':
	app.run(debug=True)