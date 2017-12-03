#!/usr/bin/env python
#-*- coding: utf-8 -*-
from slackclient import SlackClient
import time
import os
import psutil

slack_token = os.environ.get('SLACK_BOT_TOKEN')
BOT_TOKEN = slack_token
sc = SlackClient(slack_token)
CHANNEL_NAME = "piBot"
                         
def getStatus():
	# e = os.popen('top -n 1').readline()
	cpu= []
	for i in range(3):
		cpu.append(str(psutil.cpu_percent(interval =1)))
	memory_total = psutil.virtual_memory().total
	memory_avaible = psutil.virtual_memory().available
	memory_percent = psutil.virtual_memory().percent
	disk = psutil.disk_usage('/')
	disk_free = disk.free / 2**20   
	free_disk_space =  str(round(disk_free/float(1000),2))+' GB'
	users_shell = os.popen("who").read().strip()
	attachment =  [
		{
			"title": "Status",
			"color": "#3AA3E3",
			"attachment_type": "default",
			"fields": [
				{
					"title": "RAM",
					"value": str(memory_percent) +"%",
					"short": True
				},
				{
					"title": "Espace",
					"value": str(free_disk_space),
					"short": True
				},
				{
					"title": "cpu (3) ",
					"value": str("\n".join(cpu)),
					"short": True
				},
				{
					"title": "connectes",
					"value": users_shell,
					"short": True
				}
		]
		}
		]
	return attachment
def reboot():
	sc.api_call(
	"chat.postMessage",
	channel =response["channel"],
	text    ="Je me reboot ! ",
	)
	time.sleep(1)
	os.popen("sudo reboot")
def parseSlack(txt):
	txt = str(txt)
	txt = txt.replace("'",'')
	return txt

def sendStatus(response):
	sc.api_call(
	"chat.postMessage",
	channel =response["channel"],
	text    ="Voici les status actuel :tada:",
	attachments= getStatus()
	)
def listusb(response):
	usb = os.popen("ls -l /dev | grep -i usb").read().strip()
	sc.api_call(
	"chat.postMessage",
	channel =response["channel"],
	text    ="Voici les usbs connectes : \n"+usb,
	)
def dispatch(response):
	#print "dispatch"
	if "atu" in response["message"]:
		sendStatus(response)
	elif "reboot" in response["message"]:
		reboot()
	elif "usb" in response["message"]:
		listusb(response)
	else:
		sc.api_call(
		"chat.postMessage",
		channel =response["channel"],
		text    ="Je ne comprends pas ce que tu as demandé :-(",
		)

def parseMessage(slack_message):
	response = {}
	try:
		response['user'] = parseSlack(slack_message["subtitle"])
		response["message"] = parseSlack(slack_message["content"])
		response["channel"] = parseSlack(slack_message["channel"])
	except Exception as e:
		response = None
	return response
if sc.rtm_connect(with_team_state=False):
	print "starting...."
	while True:
		for slack_message in sc.rtm_read():
			response = parseMessage(slack_message)
			# print response
			if response != None and "pythonBOT (bot)" not in response["user"]:
				# sc.rtm_send_message(response["channel"], "wrote something...")
				dispatch(response)

		# Sleep for half a second
		time.sleep(0.5)