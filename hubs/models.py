from django.db import models

###/Users/Shouvik/Documents/Shouvik/ComputerScience/Term\ Project/HubUp

#User model represents user accounts
class User(models.Model):
	firstName_text = models.CharField(max_length = 50)
	lastName_text = models.CharField(max_length = 50)
	username_text = models.CharField(max_length = 50)
	hashedPassword_text = models.CharField(max_length = 50)

	#Represents User as a string when it is called
	def __str__(self):
		return "%s, %s, %s" % (self.firstName_text, self.lastName_text, self.username_text)

	#Orders the Users in the database by first name
	class Meta:
		ordering = ('firstName_text',)

# Hub model represents the event 
class Hub(models.Model):
	#Each event has a name, description, and location
	eventName_text = models.CharField(max_length = 50)
	eventHost_text = models.CharField(max_length = 50)
	date_text = models.DateField()
	time_text = models.TimeField()
	location_text = models.CharField(max_length = 200)
	latCoordinate = models.FloatField()
	longCoordinate = models.FloatField()
	description_text = models.CharField(max_length = 1000)

	#Links the Hub class to User class via a many-to-many relationship
	#Each Hub has multiple users and each User goes to multiple Hubs
	users = models.ManyToManyField(User)

	#Represents the Hub object in a readable string format when called
	def __str__(self):
		return self.eventName_text

#Trend model represents the member count and page views count for each Hub
#over time
class Trend(models.Model):
	time = models.DateTimeField(auto_now=True)
	memberCount = models.IntegerField()
	viewsCount = models.IntegerField()

	def __str__(self):
		return "%s, %d, %d" % (self.time, self.memberCount, self.viewsCount)

	#Links the Trend class to User class via a one-to-many relationship
	#Each Trend has one Hub, but each Hub can have multiple Trends
	hub = models.ForeignKey(Hub)




