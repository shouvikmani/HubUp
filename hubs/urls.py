from django.conf.urls import patterns, url
from hubs import views

#Maps URLs to specific views in views.py
urlpatterns = patterns('',
	#ex:
	url(r'^$', views.index, name='index'),
	#ex /test/
	url(r'^/testPage/$', views.testPage, name = 'testPage'),
	#ex: /joinHub/
	url(r'^viewHub/$', views.viewHub, name = 'viewHub'),
	#ex: /createHub/
	url(r'^createHub/$', views.createHub, name = 'createHub'),
	#ex: /makeNewHub/
	url(r'^makeNewHub/$', views.makeNewHub, name = 'makeNewHub'),
	#ex: False/createAccount
	url(r'^(?P<blankErrorStatus>\w+)/createAccount/$', views.createAccount, name = 'createAccount'),
	#ex: /addUser
	url(r'^addUser/$', views.addUser, name = 'addUser'),
	#ex: /logInPage/
	url(r'^logInPage/$', views.logInPage, name = 'logInPage'),
	#ex: /logInAuthenticate/
	url(r'^logInAuthenticate/$', views.logInAuthenticate, name = "logInAuthenticate"),
	#ex: /userProfile/
	url(r'^/userProfile/$', views.userProfile, name = 'userProfile'),
	#ex /logout/
	url(r'^/logout/$', views.logout, name = 'logout'),
	#ex: /5/addMember/
	url(r'^(?P<hub_id>\d+)/addMember/$', views.addMember, name = 'addMember'),
	#ex: /2/viewHubDetails/
	url(r'^(?P<hub_id>\d+)/viewHubDetails/$', views.viewHubDetails, name = 'viewHubDetails'),
	#ex: /6/leaveHub/
	url(r'^(?P<hub_id>\d+)/leaveHub/$', views.leaveHub, name = 'leaveHub'),
	#ex: /3/deleteHub/
	url(r'^(?P<hub_id>\d+)/deleteHub/$', views.deleteHub, name = 'deleteHub'),
	#ex: /4/editHub/
	url(r'^(?P<hub_id>\d+)/editHub/$', views.editHub, name = 'editHub'),
	#ex: /4/makeHubEdits/
	url(r'^(?P<hub_id>\d+)/makeHubEdits/$', views.makeHubEdits, name = 'makeHubEdits'),
	)