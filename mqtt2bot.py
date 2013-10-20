#!/usr/bin/python
import mosquitto
import random 
import socket

def send_to_bot(message, room="#hacman"):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 12345))
        s.send('%s %s' % (room, message))
        s.close()
    except Exception, e:
        pass

def on_message(mosq, obj, msg):
	if msg.topic == 'door/outer/open/username':
		send_to_bot("%s opened the outer door" % msg.payload)
	elif msg.topic == 'door/outer/buzzer':
		send_to_bot(random.choice(['Buzzer', 'Buzzer', 'Buzzer', 'rezzuB', 'Buzzard']))
	elif msg.topic == 'door/outer/invalidcard':
		send_to_bot("Unknown card at door")
	elif msg.topic == 'bot/outgoing':
		send_to_bot(msg.payload)
	
mqttc = mosquitto.Mosquitto("mqtt2bot")
mqttc.connect("alfred")
mqttc.subscribe("door/outer/#")
mqttc.subscribe("bot/outgoing")
mqttc.on_message = on_message
 
while mqttc.loop() == 0:
    pass

