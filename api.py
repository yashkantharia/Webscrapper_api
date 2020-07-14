from flask import Flask, jsonify
from flask import request,redirect, url_for
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
import os
import time;
from gensim.summarization import summarize
import re




APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER =  os.path.join(APP_ROOT, 'static/')


app = Flask(__name__)

@app.route("/")
def hello():
	url="nan"
	url = request.args.get("url")
	print(url)


	#check the request and define response
	responseObject = {}

	if(url=="nan"):
		responseObject['statusCode'] = 400
		responseObject['error']='Bad request. Send parameter url with web site URL only'
	else:
		responseObject['statusCode'] = 200


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

		#Genereate summary of ratio 0.3
		
		#remove scripts and css
		for s in data(['script', 'style']):
		  s.decompose()

		# Filter out sentences that contain newline characters '\n' or don't contain periods.
		sentence_list = [sentence for sentence in s if not '\n' in sentence]
		sentence_list = [sentence for sentence in s if '.' in sentence]

		article_text =  ' '.join(data.stripped_strings)

		summary = summarize(article_text, ratio=0.3)

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