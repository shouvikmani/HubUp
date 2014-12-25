from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from hubs.models import *
from django.utils.safestring import mark_safe
from django.utils.timezone import utc
import hashlib
import datetime
import urllib2
import json

#Homepage
def index(request):
	#If user is logged in, redirects to user profile
	if ('user_id' in request.session):
		return HttpResponseRedirect(reverse('hubs:userProfile'))
	else:
		return render(request, 'hubs/index.html')

#Just for testing purposes
def testPage(request):
	return render(request, 'hubs/test.html')

#Create Hub page with form for user input
def createHub(request):
	#If user is not logged in, redirects to log in page
	if ('user_id' not in request.session):
		return HttpResponseRedirect(reverse('hubs:logInPage'))
	else:
		#current user is the context
		currentUser = User.objects.get(id = request.session['user_id'])
		context = {'currentUser': currentUser}
		return render(request, 'hubs/createHub.html', context)

#Creates a new Hub after retreiving request from createHub.html
def makeNewHub(request):
	#Checks if user inputs are valid, otherwise goes back to createHub.html
	#and notifies user
	context = checkRequestValidity(request)
	if (context != None):
		return render(request, 'hubs/createHub.html', context)
	coordinateOffset = 0.0001
	#Fields from the form on createHub.html
	eventName = request.POST['eventName']
	host = User.objects.get(id=request.session['user_id'])
	hostUsername = host.username_text
	time = getTime(request)
	date = getDate(request)
	location = request.POST['location']
	latLong = getLatLong(location)
	lat, lng = latLong[0], latLong[1]
	#Offsets the lat and lng measures by 0.0001 if the location is already
	#marked on the map and produces 2 separate markers
	for hub in Hub.objects.all():
		if (lat == hub.latCoordinate) and (lng == hub.longCoordinate):
			lat += coordinateOffset
			lng += coordinateOffset
	description = request.POST['description']
	#Obtains data from html form in createHub.html and adds to database
	newHub = Hub(eventName_text=eventName, eventHost_text = hostUsername,
				date_text = date, time_text = time, location_text=location, 
				latCoordinate = lat, longCoordinate = lng,
				description_text = description)
	newHub.save()
	newHub.users.add(host)
	#Every time a Hub is created, the memberCount is initialized to 1 and
	#viewsCount is initialized to 1 in the Trend
	newHub.trend_set.create(memberCount = 1, 
									viewsCount = 1)
	return HttpResponseRedirect(reverse('hubs:userProfile'))

#Verifies if all the user inputs from Create a Hub are valid and can be
#represented in the database and Google Maps
def checkRequestValidity(request):
	preEventName = request.POST['eventName']
	preDate = request.POST['date']
	preTime = request.POST['time']
	preLocation = request.POST['location']
	preDescription = request.POST['description']
	currentUser = User.objects.get(id = request.session['user_id'])
	context = {'currentUser': currentUser}
	#If the user didn't give the Hub a name
	if (request.POST['eventName'] == ""):
		context = {'error': "nameError", 'preEventName': preEventName, 
					'preDate': preDate, 'preTime': preTime, 
					'preLocation': preLocation, 
					'preDescription': preDescription,
					'currentUser': currentUser}
		return context
	#If the date is not valid --> error
	try:
		date = getDate(request)
	except:
		context = {'error': "dateError", 'preEventName': preEventName, 
					'preDate': preDate, 'preTime': preTime, 
					'preLocation': preLocation, 
					'preDescription': preDescription,
					'currentUser': currentUser}
		return context
	#If the time is not valid --> error
	try:
		time = getTime(request)
	except:
		context = {'error': "timeError", 'preEventName': preEventName, 
					'preDate': preDate, 'preTime': preTime, 
					'preLocation': preLocation, 
					'preDescription': preDescription,
					'currentUser': currentUser}
		return context
	#If the lat longs are not valid --> error
	try:
		latLong = getLatLong(preLocation)
	except:
		context = {'error': "locationError", 'preEventName': preEventName, 
					'preDate': preDate, 'preTime': preTime, 
					'preLocation': preLocation, 
					'preDescription': preDescription,
					'currentUser': currentUser}
		return context
	#If no problems, returns None
	return None

#Gets the latitude and longitude coordinates of a location string by using
#geocoding from Google Maps API
def getLatLong(location):
	latLong = []
	#Idea from: http://stackoverflow.com/questions/4639311/parsing-json-file-
	#with-python-google-map-api
	addressString = location.replace(" ", "+")
	#Makes a call to this link using the user-provided location string
	url="https://maps.googleapis.com/maps/api/geocode/json?address=%s" % addressString
	response = urllib2.urlopen(url)
	jsongeocode = json.loads(response.read())
	#Parses the json file to obtain latitude and longitude coordinates
	latitude = float(json.dumps(jsongeocode['results'][0]['geometry']['location']['lat']))
	longitude = float(json.dumps(jsongeocode['results'][0]['geometry']['location']['lng']))
	latLong = [latitude, longitude]
	return latLong

#Converts the time from the html form to a time string that's more readable
def getTime(request):
	#Hour and minute separated by colon
	colonIndex = (request.POST['time']).find(":")
	hour = int((request.POST['time'])[:colonIndex])
	#If the period is PM, adds 12 to the hour because it's represented in
	#military (24-hour) time
	if (request.POST['am/pm'] == "PM"):
		hour = (hour+12) if (hour != 12) else 12
	minute = int((request.POST['time'])[colonIndex+1:])
	time = datetime.time(hour, minute)
	return time

#Converts the date from the html form to a date string that's more readable
def getDate(request):
	date = request.POST['date']
	#Date elements are separated by -
	year = int(date.split("-")[0])
	month = int(date.split("-")[1])
	day = int(date.split("-")[2])
	date = datetime.date(year, month, day)
	return date

#Sends the request to edit a hub to editHub.html with the Hub's current
#properties
def editHub(request, hub_id):
	selectedHub = Hub.objects.get(id = hub_id)
	preEventName = selectedHub.eventName_text
	preLocation = selectedHub.location_text
	preDescription = selectedHub.description_text
	currentUser = User.objects.get(id = request.session['user_id'])
	context = {'preEventName': preEventName, 'preLocation': preLocation, 
				'preDescription': preDescription,'hub': selectedHub,
				'currentUser': currentUser}
	return render(request, 'hubs/editHub.html', context)

#Takes in request from the editHubs.html form and changes attributes of the Hub
#accordingly (similar to createHub)
def makeHubEdits(request, hub_id):
	#Checks if the inputs are valid, otherwise takes the User back to the Edit
	#page
	context = checkRequestValidity(request)
	if (context != None):
		return render(request, 'hubs/createHub.html', context)
	coordinateOffset = 0.0001
	eventName = request.POST['eventName']
	host = User.objects.get(id=request.session['user_id'])
	hostUsername = host.username_text
	time = getTime(request)
	date = getDate(request)
	location = request.POST['location']
	latLong = getLatLong(location)
	lat, lng = latLong[0], latLong[1]
	#Offsets the lat and lng measures by 0.0001 if the location is already
	#marked on the map and produces 2 separate markers
	for hub in Hub.objects.all():
		#Ensures that this Hub is not the Hub that's being edited,
		#since it's lat longs will definitely be in the database -->
		#exception case
		if (hub.id != hub_id):
			if (lat == hub.latCoordinate) and (lng == hub.longCoordinate):
				lat += coordinateOffset
				lng += coordinateOffset
	description = request.POST['description']
	#This is the hub that's being editted, changes it's properties
	selectedHub = Hub.objects.get(id = hub_id)
	selectedHub.eventName_text = eventName
	selectedHub.eventHost_text = hostUsername
	selectedHub.date_text = date
	selectedHub.time_text = time
	selectedHub.location_text = location
	selectedHub.latCoordinate = lat
	selectedHub.longCoordinate = lng
	selectedHub.description_text = description
	selectedHub.save()
	return HttpResponseRedirect(reverse('hubs:userProfile'))

#Lists all the hubs in one page with the User's hubs, trending hubs, and
#latest hubs
def viewHub(request):
	if ('user_id' not in request.session):
		return HttpResponseRedirect(reverse('hubs:logInPage'))
	else:
		eventList = Hub.objects.all()
		(hubNames, hubLocations, latLongList, hubDates, 
			hubTimes) = ([], [], [], [], [])
		#Gets properties for each Hub in the DB
		for hub in Hub.objects.all():
			hubNames += [str(hub.eventName_text)]
			hubLocations += [str(hub.location_text)]
			latLongList += [[hub.latCoordinate, hub.longCoordinate]]
			hubDates += [getHubDateString(hub.date_text)]
			hubTimes += [getHubTimeString(hub.time_text)]
		#mark_safe marks the string as safe for HTML output purposes
		hubNames, hubLocations = mark_safe(hubNames), mark_safe(hubLocations)
		hubDates, hubTimes = mark_safe(hubDates), mark_safe(hubTimes)
		currentUser = User.objects.get(id = request.session['user_id'])
		#Context is stored as a dictionary
		context = {'eventList': eventList, 'currentUser': currentUser, 
					'latLongList': latLongList, 'hubNames': hubNames,
					'hubLocations': hubLocations, 'hubDates': hubDates,
					'hubTimes': hubTimes}
		#Returns the HttpResponse object of the template rendered with the context
		return render(request, 'hubs/viewHub.html', context)

#Converts the datetime object stored in the database to a human-readable date
#string
def getHubDateString(date):
	monthList = ["January", "February", "March", "April", "May", "June",
	 	"July", "August", "September", "October", "November", "December"]
	monthStr = str(monthList[(date.month-1)])
	dayStr = str(date.day)
	hubDateString = monthStr + " " + dayStr
	return hubDateString

#Converts the datetime object stored in the database to a human-readable time
#string
def getHubTimeString(time):
	#AM/PM checks
	period = "p.m." if (time.hour >= 12) else "a.m."
	hour = str(time.hour%12) if (time.hour != 12) else "12"
	minute = str(time.minute) if (time.minute != 0) else "00"
	hubTimeString = hour + ":" + minute + " " + period
	return hubTimeString

#Lists details about a specific Hub
def viewHubDetails(request, hub_id):
	hub = Hub.objects.get(id=hub_id)
	#Gathering the details of the hub
	host = User.objects.get(username_text = hub.eventHost_text)
	hostName = host.firstName_text + " " + host.lastName_text
	currentUser = User.objects.get(id = request.session['user_id'])
	latCoord = hub.latCoordinate
	lngCoord = hub.longCoordinate
	hubName = mark_safe([str(hub.eventName_text)])
	hubLocation = mark_safe([str(hub.location_text)])
	hubDate = mark_safe([getHubDateString(hub.date_text)])
	hubTime = mark_safe([getHubTimeString(hub.time_text)])
	context = {'hub': hub, 'currentUser': currentUser, 'latCoord': latCoord,
				'lngCoord': lngCoord, 'hubName': hubName,
				'hubLocation': hubLocation, 'hubDate': hubDate, 
				'hubTime': hubTime, 'hostName': hostName}
	#Every time the Hub Details page is viewed, update the viewsCount in Trend
	memberCount = hub.users.count()
	#Gets the last number of page views in the database
	lastViewsCount = getLastViewsCount(hub)
	#Increments lastViewsCount by 1 to represent the new page view.
	newViewsCount = lastViewsCount + 1
	hub.trend_set.create(memberCount = memberCount, 
									viewsCount = newViewsCount)
	return render(request, 'hubs/viewHubDetails.html', context)

#Add a User to a Hub
def addMember(request, hub_id):
	selectedHub = Hub.objects.get(id = hub_id)
	selectedUser = User.objects.get(id=request.session['user_id'])
	selectedHub.users.add(selectedUser)
	#Every time a member is added, update the memberCount in Trend
	memberCount = selectedHub.users.count()
	#Gets the last number of page views in the database. So, when a 
	#member is added, viewsCount is not changed
	lastViewsCount = getLastViewsCount(selectedHub)
	#Creates a new Trend for selectedHub with an updated memberCount
	selectedHub.trend_set.create(memberCount = memberCount, 
									viewsCount = lastViewsCount)
	return HttpResponseRedirect(reverse('hubs:viewHub'))

#Removes the User from a Hub
def leaveHub(request, hub_id):
	selectedHub = Hub.objects.get(id = hub_id)
	selectedUser = User.objects.get(id=request.session['user_id'])
	selectedHub.users.remove(selectedUser)
	#Every time a member is removed, update the memberCount in Trend
	memberCount = selectedHub.users.count()
	#Gets the last number of page views in the database. So, when a 
	#member is removed, viewsCount is not changed
	lastViewsCount = getLastViewsCount(selectedHub)
	selectedHub.trend_set.create(memberCount = memberCount, 
									viewsCount = lastViewsCount)
	return HttpResponseRedirect(reverse('hubs:viewHub'))

#Gets the last number of page views in the Trend model
def getLastViewsCount(selectedHub):
	trendLength = len(selectedHub.trend_set.all())
	lastViewsCount = selectedHub.trend_set.all()[trendLength-1].viewsCount
	return lastViewsCount

#Removes a Hub from the database
def deleteHub(request, hub_id):
	selectedHub = Hub.objects.get(id = hub_id)
	selectedHub.delete()
	return HttpResponseRedirect(reverse('hubs:userProfile'))

#Create account page with form
def createAccount(request, blankErrorStatus):
	#Determines the error based on the URL string
	if blankErrorStatus == "True":
		context = {'error': False, 'blankErrorStatus': True}
	else:
		context = {'error': False, 'blankErrorStatus': False}
	return render(request, 'hubs/createAccount.html', context)

#Adds a user account to the database
def addUser(request):
	firstName = request.POST['First_Name']
	lastName = request.POST['Last_Name']
	username = request.POST['username']
	password = request.POST['password']
	#Password is encrypted by hashing
	encryptedPassword = hashlib.sha1(password).hexdigest()
	#If username already exists in database, then raises an error in the
	#createAccount page
	try:
		User.objects.get(username_text = username)
		context = {'error': True, 'blankErrorStatus': False}
		return render(request, 'hubs/createAccount.html', context)
	except:
		#If one or more fields are blank, raises an error
		if (firstName == "" or lastName == "" or username == "" or password == ""):
			blankErrorStatus = True
			###Probably not the best idea to redirect here, use render with context instead
			return HttpResponseRedirect(reverse('hubs:createAccount', args=(blankErrorStatus,)))
		else:
			#If the username does not exist and all fields are filled, creates a
			#new User instance
			newUser = User(firstName_text = firstName, lastName_text = lastName,
				username_text = username, hashedPassword_text = encryptedPassword)
			newUser.save()
			return HttpResponseRedirect(reverse('hubs:index'))

#Log In page with form
def logInPage(request):
	context = {'error': False}
	return render(request, 'hubs/logInPage.html', context)

#Verifies that the username and password entered are in the database
def logInAuthenticate(request):
	username = request.POST['username']
	password = request.POST['password']
	encryptedPassword = hashlib.sha1(password).hexdigest()
	try:
		#If username is in database and matches with password, go to
		#userProfile page
		currentUser = User.objects.get(username_text = username)
		if (encryptedPassword == currentUser.hashedPassword_text):
			request.session['user_id'] = currentUser.id
			return HttpResponseRedirect(reverse('hubs:userProfile'))
		#If username is in database but password is incorrect, raises an error
		#in the logInPage
		else:
			context = {'error': True, 'username': username}
			return render(request, 'hubs/logInPage.html', context) 
	except:
		#If username is not in database, raises an error in the
		##logInPage
		context = {'error': True}
		return render(request, 'hubs/logInPage.html', context) 

#User Profile
def userProfile(request):
	#Obtains the id of the currentUser from the cookie
	currentUser = User.objects.get(id = request.session['user_id'])
	username = currentUser.username_text
	#There can only be Hub Ranks if thre are Hubs in the first place
	if (len(Hub.objects.all()) > 0):
		rankList = getRankList()
		#Sort the rankList from greatest to least rank and only include the
		#first 5 ranked Hubs
		rankList = sorted(rankList)[::-1][:5]
	else:
		rankList = None
	latestHubs = latestHubs = Hub.objects.all()[::-1][:5]
	context = {'currentUser': currentUser, 'username': username, 
				'rankList': rankList, 'latestHubs': latestHubs}
	#return render(request, 'hubs/test.html', context)
	return render(request, 'hubs/userProfile.html', context)

#Returns the top 5 trending Hubs based on percent change algorithm
def getRankList():
	#Maps individual hubs to their ranks (based on percent change)
	hubRanks = []
	#Calculates the time exactly one hour ago
	currentTime = datetime.datetime.utcnow().replace(tzinfo=utc)
	oneHour = datetime.timedelta(hours=1)
	timeOneHourAgo = currentTime - oneHour
	averageMemberCount = getAverageMemberCount()
	averageViewsCount = getAverageViewsCount()
	for selectedHub in Hub.objects.all():
		#Current number of members and page views for the Hub used in percent
		#change calculation
		currentMemberCount = selectedHub.users.count()
		currentViewsCount = getLastViewsCount(selectedHub)
		#Only calculates percent change if the currentMemberCount and
		#currentViewsCount are above average 
		#Ex: 20 --> 25 is a 25% change
		#    2000 --> 2500 is also a 25% change 
		#But only the 2000 --> 2500 change matters because it is significant 
		#So, only consider the percent change if the Hub stats are above average
		if ((currentMemberCount + currentViewsCount) >= 
			(averageMemberCount + averageViewsCount)):
			#Gets the initial time closest to the time in the database 
			#one hour ago.
			initialTime = getInitialTime(selectedHub, timeOneHourAgo)
			selectedTrend = selectedHub.trend_set.get(time = initialTime)
			initialMemberCount = selectedTrend.memberCount
			initialViewsCount = selectedTrend.viewsCount
			#Calculates the percent change of the number of members and page views
			#over the past hour
			memberCount_PercentChange = ((currentMemberCount - initialMemberCount)/float(initialMemberCount)) * 100
			viewsCount_PercentChange = ((currentViewsCount - initialViewsCount)/float(initialViewsCount)) *100
			#Hub's rank is a combination of the change in memberCount and the change in viewsCount
			selectedHubRank = memberCount_PercentChange + viewsCount_PercentChange
			hubRanks += [(int(selectedHubRank), selectedHub)]
		else:
			#If the Hub's currentMemberCount and currentViewsCount are below
			#average, the Hub is not factored into Rank calculations
			hubRanks += [(0, selectedHub)]
	return hubRanks

#Finds the average number of members in each Hub
def getAverageMemberCount():
	memberCountSum = 0
	numberOfHubs = len(Hub.objects.all())
	#Gets the total number of members across all hubs
	for selectedHub in Hub.objects.all():
		memberCountSum += selectedHub.users.count()
	averageMemberCount = memberCountSum/float(numberOfHubs)
	return averageMemberCount

#Find the average number of page views for each Hub
def getAverageViewsCount():
	viewsCountSum = 0
	numberOfHubs = len(Hub.objects.all())
	#Total number of views across all hubs
	for selectedHub in Hub.objects.all():
		lastViewsCount = getLastViewsCount(selectedHub)
		viewsCountSum += lastViewsCount
	averageViewsCount = viewsCountSum/float(numberOfHubs)
	return averageViewsCount


#Finds the initial time closest to the time in the database one hour ago.
#This initial time will be helpful for the percent change calculation
def getInitialTime(selectedHub, timeOneHourAgo):
	firstTrendTime = selectedHub.trend_set.all()[0].time
	trendLength = len(selectedHub.trend_set.all())
	lastTrendTime = selectedHub.trend_set.all()[trendLength-1].time
	#Edge case 1: If the Hub didn't even exist an hour ago, it should not be
	#factored into Hub Rank calculations, or else it will cause errors.
	if (timeOneHourAgo < firstTrendTime):
		initialTime = firstTrendTime
	#Edge case 2: If there has been no change in the number of members or page
	#views in the past hour, then the initial time is the Hub's last Trend
	#time. Esentially, the percent change will be 0 (since no change).
	elif (timeOneHourAgo > lastTrendTime):
		initialTime = lastTrendTime
	#Normal Case: If the time one hour ago is between the Hub's first and
	#last Trend times
	else:
		#Loops through each trend of the selectedHub
		for trendIndex in xrange(trendLength):
			firstTime = selectedHub.trend_set.all()[trendIndex].time
			secondTime = selectedHub.trend_set.all()[trendIndex+1].time
			#If the time one hour ago is in between two of the Trend times
			if (timeOneHourAgo > firstTime
				and timeOneHourAgo < secondTime):
				#Finds which one of the Trend times is closer to the time one
				#hour ago and sets initialTime to that time
				firstTimeGap = timeOneHourAgo - firstTime
				secondTimeGap = secondTime - timeOneHourAgo
				initialTime = firstTime if (firstTimeGap < secondTimeGap) else secondTime
				break
	return initialTime


#Allows users to log out of their session
def logout(request):
	#Deketes the cookie storing user info
	del request.session['user_id']
	return HttpResponseRedirect(reverse('hubs:index'))


#fin#

