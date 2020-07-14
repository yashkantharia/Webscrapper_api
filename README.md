# Webscrapper_api


This API will take a website URL as input and save the following values in a csv by webscraping:
'Given_Website','Company_Name','Title','Website image/screenshot','Short_Description','company_icon','contact_email','LinkedIn','Summarize the website content'


How To Use:     


Step 1: Install all the dependencies:
Selenium
Gensim
Webdriver_manager
Pillow
Bs4
Requests
Flask
Os
Re
Time
pandas

Step 2: Copy the project files including the template “result.csv” file in the desired folder.

Step 3: After the dependencies are installed, go the destination of api.py from your console and enter


python api.py 

Step 4: Copy the URL of the locally hosted flask API endpoint 

Use the API in browser by entering the following:
<localhost_address>/?url=<website_url>

Example: http://127.0.0.1:5000/?url=http://aytm.com

Or use curl

'''
curl http://127.0.0.1:5000/?url=http://aytm.com
'''

Step 5: The result will be saved in the file “result.csv”
