from __future__ import print_function
from flask import Flask, render_template
import datetime
import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import datetime
import dateutil.parser
import requests
import json


app = Flask(__name__)


SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential. 	
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=5, singleEvents=True, timeZone='America/New_York',
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    return events


def weather():
	resp = requests.get('http://api.openweathermap.org/data/2.5/weather?lat=39.161999&lon=-84.456886&appid=fc0f56aea3337963a7fa8c1124926f37')
	
	weatherData = resp.json()

	return weatherData


@app.route('/')
def home():

	# get all of the calendar data
	time = datetime.datetime.now()
	day = time.day
	month = time.strftime("%B")
	year = time.year
	minute = time.minute
	# for some reason, it won't put the zero for these times (ex: 2:03 would be 2:), so I had to add it in manually
	if minute < 10:
		minute = '0'+str(minute)
	hour = time.hour
	weekday = time.strftime("%A")

	date = weekday + ' ' + month + ',' + str(day)

	message = ''
	if 4 < hour <= 11:
		message='Good Morning!'
	elif 11 < hour <= 17:
		message = 'Good Afternoon!'
	elif 17 < hour <= 19:
		message = 'Good Evening!'
	elif 19 < hour <= 4:
		message = 'Good Night!'

	if (hour > 12):
		hour=hour-12

	events = main()
	event_display = []
	event_sum = []

	if not events:
	 	event_display = 'No events to display'


	for event in events:
	    start = event['start'].get('dateTime', event['start'].get('date'))

	    dt = dateutil.parser.parse(start)
	    start = dt.strftime('%m-%d-%Y %H:%M')
	    event_sum += event['summary']
	  	
	    location = event.get('location')
	    if location == None:
	    	location = ' '

	    event_display += event['summary'], start, location


	# get variables for the weather
	weatherData = weather()
	temp = weatherData['main']['temp']
	tempFar = (9/5)*(int(temp)-273)+32
	desc = weatherData['weather'][0]['description'].title()
	city = weatherData['name']
	state = 'OH'


	return render_template('home.html', date=date, hour=hour, minute=minute, 
		event_display=event_display, tempFar=tempFar, desc=desc, city=city,
		state=state, message=message)

if __name__ == '__main__':
        app.run(debug=True)