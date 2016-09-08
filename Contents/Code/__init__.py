import os
import time
from time import sleep
from datetime import datetime, date
import websocket
import sys
import requests
import json
import re
import threading
import random
from astral import Astral
import pytz
import xml.etree.ElementTree as ElementTree
	
####################################################################################################

PREFIX       = "/applications/HelloHyperion"
NAME         = 'HelloHyperion'
ART          = 'background.png'
ICON         = 'HelloHyperion.png'
PREFS_ICON   = 'HelloHyperion.png'
PROFILE_ICON = 'HelloHyperion.png'

####################################################################################################

####################################################################################################
# Start function
####################################################################################################
def Start():
	Log('Starting HelloHyperion...')
	HTTP.CacheTime = 0
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)	
	ValidatePrefs()

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, art=R(ART), thumb=R(ICON))
def MainMenu(header=NAME, message="Hello"):
	oc = ObjectContainer(no_cache=True,no_history=True, replace_parent=True)
	if message is not "Hello":
		oc.header = header
		oc.message = message
	if "thread_websocket" in str(threading.enumerate()):
		oc.add(DisableHelloHyperion())
	if not "thread_websocket" in str(threading.enumerate()):
		oc.add(EnableHelloHyperion())
	oc.add(DirectoryObject(key = Callback(AdvancedMenu),title = 'Advanced Menu',thumb = R(PREFS_ICON)))
	# Add item for setting preferences	
	oc.add(PrefsObject(title = L('Preferences'), thumb = R(PREFS_ICON)))
	return oc

####################################################################################################
# Advanced Menu
####################################################################################################
@route(PREFIX + '/AdvancedMenu')
def AdvancedMenu(header="AdvancedMenu", message="Hello"):
	oc = ObjectContainer(title2 = "Advanced Menu",no_cache=True,no_history=True, replace_parent=True)
	if message is not "Hello":
		oc.header = header
		oc.message = message
	oc.add(PopupDirectoryObject(key = Callback(ResetPlexToken),title = 'Reset Plex.TV token',thumb = R(PREFS_ICON)))
	oc.add(RestartHelloHyperion())
	return oc
####################################################################################################
# Reset Plex Token
####################################################################################################
def ResetPlexToken():
	if Dict["token"]:
		Dict["token"] = ""
		if Dict["token"]:
			Log("TokenStillDetected")
			return AdvancedMenu(header="AdvancedMenu", message="Error while deleting.")
		else:
			Log("Token deleted")
			ValidatePrefs()
			return AdvancedMenu(header="AdvancedMenu", message="Token Deleted.")
	else:
		Log("Plex Foiray")

####################################################################################################
# Advanced Menu
####################################################################################################
# Item menu to Restart the Channel
####################################################################################################
def RestartHelloHyperion():
	return PopupDirectoryObject(key= Callback(ValidatePrefs),title = 'Restart HelloHyperion (must do after changing plex.tv login/password)',thumb = R('HelloHyperion.png'))

####################################################################################################
# Item menu to enable the Channel
####################################################################################################
def EnableHelloHyperion():
	return PopupDirectoryObject(key= Callback(EnableHelloHyperionCallback),title = 'Enable HelloHyperion',thumb = R('HelloHyperion.png'))

####################################################################################################
# Callback to enable the Channel
####################################################################################################
def EnableHelloHyperionCallback():
	Log("Trying to enable thread")
	#threading.Thread(target=run_websocket_watcher,name='thread_websocket').start()
	if not "thread_websocket" in str(threading.enumerate()):
		ValidatePrefs()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHyperion is now enabled.')

####################################################################################################
# Item menu to disable the Channel
####################################################################################################
def DisableHelloHyperion():
	return PopupDirectoryObject(key= Callback(DisableHelloHyperionCallback),title ='Disable HelloHyperion',thumb = R('HelloHyperion.png'))

####################################################################################################
# Callback to disable the Channel
####################################################################################################
def DisableHelloHyperionCallback():
	Log("Trying to disable thread")
	if "thread_websocket" in str(threading.enumerate()):
		ws.close()
	Log(threading.enumerate())
	return MainMenu(header=NAME, message='HelloHyperion is now disabled.')

####################################################################################################
# Called by the framework every time a user changes the prefs // Used to restart the Channel
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	global plex, active_clients, firstrun
	Log('Validating Prefs')
	getValueGain()
	InitiateStatus()
	plex = Plex()
	active_clients = []
	Log("Classes initiated")
	if "thread_websocket" in str(threading.enumerate()):
		Log("Closing daemon...")
		ws.close()
	if not "thread_websocket" in str(threading.enumerate()):
		Log("Starting websocket daemon...")
		threading.Thread(target=run_websocket_watcher,name='thread_websocket').start()
	if "thread_clients" in str(threading.enumerate()):
		Log("Setting firstrun to True")
		firstrun = True
	if not "thread_clients" in str(threading.enumerate()):
		Log("Starting clients daemon...")
		threading.Thread(target=watch_clients,name='thread_clients').start()
	Log(threading.enumerate())
	return MainMenu(header=NAME)

####################################################################################################
# Plex Commands
####################################################################################################

class Plex:
	def __init__(self):
		Log("Initializing Plex class")
		Log("-Getting Token")
		global HEADERS, ACCESS_TOKEN
		HEADERS = {'X-Plex-Product': 'Automating Home Lighting', 
		'X-Plex-Version': '1.0.1',
		'X-Plex-Client-Identifier': 'HelloHyperion',
		'X-Plex-Device': 'Server',
		'X-Plex-Device-Name': 'HelloHyperion'}
		if Dict["token"] == "Error" or not Dict["token"]:
			TOKEN = self.get_plex_token()
			ACCESS_TOKEN = TOKEN
		else:
			Log("Token retrieved from Dict")
			ACCESS_TOKEN = Dict["token"]

	def get_plex_token(self):
		plexauth = {'user[login]': Prefs['PLEX_USERNAME'], 'user[password]': Prefs['PLEX_PASSWORD']}
		r = requests.post('https://plex.tv/users/sign_in.json', params=plexauth, headers=HEADERS)
		data = json.loads(r.text)
		try:
			Dict["token"] = data['user']['authentication_token']
			Log("Token retrieved and saved")
			return Dict["token"]
		except (ValueError, KeyError, TypeError):
			Log("Error while retrieving token")
			Dict["token"] = "Error"
			return Dict["token"]

	def get_plex_status(self):
		r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/status/sessions?X-Plex-Token=' + ACCESS_TOKEN, headers=HEADERS)
		e = ElementTree.fromstring(r.text.encode('utf-8'))
		return e

	def get_plex_clients(self):
		r = requests.get('http://' + Prefs['PLEX_ADDRESS'] + '/clients?X-Plex-Token=' + ACCESS_TOKEN, headers=HEADERS)
		e = ElementTree.fromstring(r.text.encode('utf-8'))
		return e

####################################################################################################
# Compile settings in list/dictionary on plugin start or pref change
####################################################################################################

def GetSetting():
	pattern = re.compile("^\s+|\s*,\s*|\s+$")
	setting = {}
	if Prefs['HYPERION_SWITCH'] is True and not Prefs['PLEX_CLIENT'] == '' and not Prefs['PLEX_AUTHORIZED_USERS'] == '':
		setting['client'] = Prefs['PLEX_CLIENT']
		setting['users'] = [x for x in pattern.split(Prefs['PLEX_AUTHORIZED_USERS']) if x]
		setting['playing'] = Prefs['HYPERION_ACTION_PLAYING']
		setting['paused'] = Prefs['HYPERION_ACTION_PAUSED']
		setting['stopped'] = Prefs['HYPERION_ACTION_STOPPED']
		setting['brightness'] = Prefs['HYPERION_BRI']
		setting['bri_on_clear'] = Prefs['HYPERION_BRI_ON_CLEAR']
		setting['bri_on_black'] = Prefs['HYPERION_BRI_ON_BLACK']
		setting['randomize'] = Prefs['HYPERION_RANDOMIZE']
		setting['dark'] = Prefs['HYPERION_DARK']
		setting['min_duration'] = Prefs['PLEX_DURATION']
		setting['turned_on'] = Prefs['PLEX_ON']
		setting['turned_off'] = Prefs['PLEX_OFF']
		#Log("settings: %s", setting)
		#Log("Room check done")
		return setting
	else:
		Log("Skipping setting")

####################################################################################################
# Put all available clients status to '' on plugin start or pref change
####################################################################################################

def InitiateStatus():
	Log("Initiating duration and value gain")
	global VAL_DID_CHANGE, CURRENT_STATUS, DURATIONS

	VAL_DID_CHANGE = False

	client_name = GetSetting()['client']

	CURRENT_STATUS = {}
	DURATIONS = {}

	CURRENT_STATUS[client_name] = ''
	DURATIONS[client_name] = ''

####################################################################################################
# If websocket detected, trigger PMS sessions status analyze
####################################################################################################

def run_websocket_watcher():
	global ws
	Log('Starting websocket listener')
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://" + Prefs['PLEX_ADDRESS'] + "/:/websockets/notifications?X-Plex-Token=" + ACCESS_TOKEN, on_message = on_message)
	Log("Up and running, listening")
	ws.run_forever()

def on_message(ws, message):
	json_object = json.loads(message)
	#Log(json_object)
	if json_object['type'] == 'playing':
		plex_status = plex.get_plex_status()
		#Log(plex_status)
		is_plex_playing(plex_status)

def on_close(ws):
	Log("### closed ###")

####################################################################################################
# Get currently playing item duration
####################################################################################################

def get_playing_item_duration(video):
	Log("Getting duration...")
	duration = int(video.get('duration'))
	DURATIONS[GetSetting()['client']] = duration
	return duration

####################################################################################################
# Compare duration with preference
####################################################################################################

def compare_duration(duration, pref):
	if pref == "Disabled":
		Log("Duration pref is disabled: triggering")
		return True
	else:
		if pref == "1 minute":
			compared = 1 * 60 * 1000
		elif pref == "5 minutes":
			compared = 5 * 60 * 1000
		elif pref == "15 minutes":
			compared = 15 * 60 * 1000
		elif pref == "25 minutes":
			compared = 25 * 60 * 1000
		elif pref == "35 minutes":
			compared = 35 * 60 * 1000
		elif pref == "45 minutes":
			compared = 45 * 60 * 1000
		elif pref == "55 minutes":
			compared = 55 * 60 * 1000
		elif pref == "1 hour":
			compared = 60 * 60 * 1000
		elif pref == "1 hour and 20 minutes":
			compared = 80 * 60 * 1000
		elif pref == "1 hour and 40 minutes":
			compared = 100 * 60 * 1000
		elif pref == "2 hours":
			compared = 120 * 60 * 1000
		if duration > compared:
			Log("Duration is greater than preferences: triggering")
			return True
		else:
			Log("Duration is shorter than preferences: not triggering")
			return False

####################################################################################################
# Parse PMS sessions status
####################################################################################################

def is_plex_playing(plex_status):
	client_name = GetSetting()['client']
	min_duration = GetSetting()['min_duration']
	ACTIVE_CLIENTS = []
	somethingwasdone = False
	for item in plex_status.findall('Video'):
		if item.find('Player').get('title') == client_name:
			if not client_name in ACTIVE_CLIENTS:
				ACTIVE_CLIENTS.append(client_name)
			configuredusers = GetSetting()['users']
			for username in configuredusers:
				if item.find('User').get('title') == username:
					if item.find('Player').get('state') == 'playing' and CURRENT_STATUS[client_name] != item.find('Player').get('state') and compare_duration(duration=get_playing_item_duration(item), pref=min_duration) is True:
						plex_is_playing(client_name=client_name, user=item.find('User').get('title'), gptitle=item.get('grandparentTitle'), title=item.get('title'), state=item.find('Player').get('state'), item=item)
						somethingwasdone = True
					elif item.find('Player').get('state') == 'paused' and CURRENT_STATUS[client_name] != item.find('Player').get('state') and compare_duration(duration=get_playing_item_duration(item), pref=min_duration) is True:
						plex_is_playing(client_name=client_name, user=item.find('User').get('title'), gptitle=item.get('grandparentTitle'), title=item.get('title'), state=item.find('Player').get('state'), item=item)
						somethingwasdone = True
	
	if somethingwasdone is True:
		return False

	for client_name in CURRENT_STATUS:
		if not client_name in ACTIVE_CLIENTS:
			if not CURRENT_STATUS[client_name] == 'stopped' and not CURRENT_STATUS[client_name] == '':
				CURRENT_STATUS[client_name] = ''
				Log(time.strftime("%I:%M:%S") + " - Playback stopped on %s - Waiting for new playback" % (client_name));
				if isitdark() is True and compare_duration(duration=DURATIONS[client_name], pref=min_duration) is True:
					choose_action("stopped")
					DURATIONS[client_name] = ''

def plex_is_playing(client_name, user, gptitle, title, state, item):
	client_name = GetSetting()['client']
	if CURRENT_STATUS[client_name] == '':
		Log(time.strftime("%I:%M:%S") + " - New Playback (saving initial lights state): - %s %s %s - %s on %s."% (user, CURRENT_STATUS[client_name], gptitle, title, client_name))
	CURRENT_STATUS[client_name] = state
	Log(time.strftime("%I:%M:%S") + " - %s %s %s - %s on %s." % (user, CURRENT_STATUS[client_name], gptitle, title, client_name))
	if isitdark() is True and compare_duration(duration=get_playing_item_duration(item), pref=GetSetting()['min_duration']) is True:
		choose_action(CURRENT_STATUS[client_name])

####################################################################################################
# Choose action based on playback status and preferences
####################################################################################################

def choose_action(state):
	Log("Selecting LED action...")
	if GetSetting()[state] == "Turn Off (Black)":
		turn_off_led()
		pass
	elif GetSetting()[state] == "Turn On (Clear)":
		clear_led()
		pass
	elif GetSetting()[state] == "Brightness":
		bri_led()
		pass
	elif GetSetting()[state] == "Start Hyperion service":
		start_hyperion()
		pass
	elif GetSetting()[state] == "Stop Hyperion service":
		stop_hyperion()
		pass
	elif GetSetting()[state] == "Restart Hyperion service":
		restart_hyperion()
		pass
	elif GetSetting()[state] == "Preset 1":
		set_color_preset("1")
		pass
	elif GetSetting()[state] == "Preset 2":
		set_color_preset("2")
		pass
	elif GetSetting()[state] == "Preset 3":
		set_color_preset("3")
		pass
	elif GetSetting()[state] == "Preset 4":
		set_color_preset("4")
		pass
	elif GetSetting()[state] == "Preset 5":
		set_color_preset("5")
		pass
	elif GetSetting()[state] == "Nothing":
		Log("Doing nothing")
		pass
	else:
		Log("No matching action found")
		pass

####################################################################################################
# Calculate if it's dark outside at user's location
####################################################################################################

def isitdark():
	if GetSetting()['dark'] is False:
		Log("Dark pref set to false: triggering")
		return True
	else:
		city_name = Prefs['HYPERION_CITY']
		a = Astral()
		city = a[city_name]
		today_date = date.today()
		sun = city.sun(date=today_date, local=True)
		utc=pytz.UTC
		if sun['sunrise'] <= utc.localize(datetime.utcnow()) <= sun['sunset']:
			if sun['sunset'] >= utc.localize(datetime.utcnow()):
				event = "sunset"
				timediff = sun['sunset'] - utc.localize(datetime.utcnow())
			if sun['sunset'] <= utc.localize(datetime.utcnow()):
				event = "sunrise"
				timediff = utc.localize(datetime.utcnow()) - sun['sunrise']
			Log("It's sunny outside: not trigerring (%s in %s)" % (event, timediff))
			return False
		else:
			Log("It's dark outside: triggering")
			return True


####################################################################################################
# Color conversions
####################################################################################################

def hex_to_rgb(value):
	lv = len(value)
	#Log(value)
	#Log(lv)
	return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))


####################################################################################################
# Check if SSL is enabled
####################################################################################################

def getSSL():
	if Prefs['HYPERION_ADDRESS_SSL'] is True:
		return "https://"
	else:
		return "http://"

####################################################################################################
# Get ValueGain info from HyperionWeb
####################################################################################################

def getValueGain():
	global INIT_VAL, VAL_DID_CHANGE

	try:
		VAL_DID_CHANGE = False
		r = requests.get(getSSL() + Prefs['HYPERION_ADDRESS'] + "/get_value_gain")
		INIT_VAL = int(float(r.json()['valueGain']))
		#Log("INIT_VAL: %s"%INIT_VAL)
	except:
		Log("Could not fetch ValueGain data from HyperionWeb. Is server online?")


####################################################################################################
# Execute led actions
####################################################################################################

def set_color_preset(preset):
	Log("Setting color to preset %s "%preset)
	try:
		rgb = (hex_to_rgb(str(Prefs['HYPERION_PRESET_%s_HEX'%preset])))
		#Log(rgb)
	except:
		Log("Wrong hex color, doing nothing")
	else:
		if GetSetting()['randomize'] is True:
			rgb = []
			for i in range(3):
				rgb.append(random.randint(0,255))
		
		r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/set_static", data={'r':rgb[0], 'g':rgb[1], 'b':rgb[2]})
		r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/set_value_gain", data={'valueGain':str(Prefs['HYPERION_PRESET_%s_BRI'%preset])})
		Log("Changed color")
	pass

def start_hyperion():
	Log("Starting hyperion service")
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/do_start", data={'start':'start'})
	pass

def stop_hyperion():
	Log("Stopping hyperion service")
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/do_stop", data={'stop':'stop'})
	pass

def restart_hyperion():
	Log("Restarting hyperion service")
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/do_restart", data={'restart':'restart'})
	pass

def turn_off_led():
	global INIT_VAL, VAL_DID_CHANGE
	Log("Turning off led (sending black)")
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/set_color_name", data={'colorName':'black'})
	#Log("1: INIT_VAL: %s, VAL_DID_CHANGE: %s" %(INIT_VAL, VAL_DID_CHANGE))
	if VAL_DID_CHANGE is True:
		bri_led(INIT_VAL)
		VAL_DID_CHANGE = False
	pass

def clear_led():
	global VAL_DID_CHANGE
	getValueGain()
	Log("Clearing all priority channels")
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/do_clear", data={'clear':'clear'})
	if GetSetting()['bri_on_clear'] is True:
		bri_led(GetSetting()['brightness'])
		VAL_DID_CHANGE = True
	pass

def bri_led(bri_value):
	global INIT_VAL, VAL_DID_CHANGE
	#Log("2: bri_value: %s" %(bri_value))
	r = requests.post(getSSL() + Prefs['HYPERION_ADDRESS'] + "/set_value_gain", data={'valueGain':bri_value})
	if bri_value is INIT_VAL and VAL_DID_CHANGE is True: #Reverting
		VAL_DID_CHANGE = False
		Log("Reverting value gain")
	pass

def watch_clients():
	global firstrun
	firstrun = True
	while True:
		plex_status = plex.get_plex_clients()
		now_active = []
		for item in plex_status.findall('Server'):
			now_active.append(item.get('name'))
			if firstrun is True:
				active_clients.append(item.get('name'))
		#Log("now_active: %s"%now_active)
		#Log("active_clients: %s"%active_clients)
		#Log("firstrun: %s"%firstrun)
		if firstrun is False:
			for client in now_active:
				if not client in active_clients:
					Log("%s detected, running assigment for turned on"%client)
					choose_action("turned_on")
					active_clients.append(client)
			for client in active_clients:
				if not client in now_active:
					Log("%s went away, running event for turned off"%client)
					choose_action("turned_off")
					active_clients.remove(client)
		if firstrun is True:
			Log("Setting firstrun to False")
			firstrun = False
		sleep(1)
