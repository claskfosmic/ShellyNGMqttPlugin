# ShellyNGMqttPlugin
#
# NG Author: Claskfosmic
# Original Author: Alexander Nagy/enesbcs 
#
"""
<plugin key="ShellyNGMqttPlugin" name="Shelly NG Mqtt Plugin" version="0.0.2" wikilink="https://github.com/claskfosmic/ShellyNGMQTTPlugin/wiki" externallink="https://github.com/claskfosmic/ShellyNGMQTTPlugin">
	<description>

		<h2>Shelly NG Mqtt Plugin</h2><br/>
		Plugin to manage Shelly devices via MQTT, based on the original <a href='https://github.com/enesbcs/Shelly_MQTT' target='blank'>ShellyMQTT - Domoticz Python Plugin of Alexander Nagy/enesbcs</a>, which is discontinued.<br/>
        This plugin support Shelly Devices from the first generation AND the second generation (work in progress) of Shelly devices, called <a href='https://shelly-api-docs.shelly.cloud/gen2/#devices' target='blank'>Shelly-NG</a>.<br/>
		<br/>
		
		<h3>For Shelly Devices from the first generation, like the Shelly 2.5:</h3><br/>
	 	 - Enable 'MQTT' under 'Internet &amp; Security' -> 'ADVANCED - DEVELOPER SETTINGS'.<br/>
		 - Do&nbsp;<b>NOT</b>&nbsp;use a custom MQTT prefix, the topic should be 'shellies/shellyswitch25-XXXXXXXXXXXX'.<br/>
		 - <i>! WARNING:</i>If you enable MQTT - actions via Cloud connection will be disabled!<br/>
		 <br/>
		
		-current<h3>For Shelly Devices from the second generation, like the Shelly Plus 2 PM:</h3><br/>
		 - Enable the 'MQTT network' under 'Settings' -> 'MQTT'.<br/>
		 - Make sure the MQTT-prefix starts with 'shellies/', just like the first generation, so the MQTT prefix will look like: 'shellies/shellyplus2pm-XXXXXXXXXXXX'.<br/>
		 - Do <b>NOT</b> change the rest of the prefix, the part 'shellyplus2pm-XXXXXXXXXXXX' is used to detect the type of device.<br/>
		 - Make sure the options 'Enable "MQTT Control"', ' Enable RPC over MQTT' and 'RPC status notifications over MQTT' must be enabled.<br/>
		 - Do <b>NOT</b> enable the option 'Generic status update over MQTT', because this will break the energy measurements..<br/>
		<br/>
		
		<h3>Configuration</h3>
		<ul style="list-style-type:square">
			<li>MQTT Server address is the IP Address/jhostname of the MQTT broker. Default value is 127.0.0.1</li>
			<li>Port is the portnumber to connect to the MQTT Broker.</li>
			<li>The username to login onto the MQTT Broker.</li>
			<li>The password to login onto the MQTT Broker.</li>
			<li>Type is the type of Shelly device you want to add.<br/>
			</li>
		</ul>

		<h3>Supported</h3>
		<b>Supported Shelly Gen 1 Devices:</b><br/>
		Shelly 1, Shelly PM, Shelly 2.5 (relay and roller), Shelly Dimmer, Shelly RGBW2 (color and white), Shelly Bulb, Shelly Door/Window 2 and Shelly Plug-S<br/>
		<br/><b>Supported Shelly Gen 2 Devices:</b><br/>
		Shelly Plus 1, Shelly Plus 1 PM, Shelly Plus 2 PM (Not roller mode), Shelly Plus i4 (Beta), Shelly Plug H&amp;T (Beta).
        
        <h3>Notes</h3>
        Because this plugin uses MQTT to connect to shellies, Gen 1 devices will loose their connection
		to the Shelly Cloud. In order to control Shelly from Gen 1, connected to the cloud, use HTTP instead.
		See also my other plugin at
        <a href='https://github.com/claskfosmic/ShellyNGHttpPlugin' target='blank'>
            https://github.com/claskfosmic/ShellyNGHttpPlugin.
        </a><br/>
        Please keep in mind, when using the HTTP Plugin for Gen 1 devices, the status in Domoticz will be delayed. Also, using HTTP, only the current state of inputs can be used. Advanced input events like long push, double push etc. are not supported.
	
	</description>
	<params>
		<param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
		<param field="Port" label="Port" width="300px" required="true" default="1883"/>
		<param field="Username" label="Username" width="300px" default=""/>
		<param field="Password" label="Password" width="300px" default="" password="true"/>

		<param field="Mode1" label="Invert Roller mode globally" width="175px">
			<options>
				<option label="True" value="1"/>
				<option label="False" value="0" default="true" />
			</options>
		</param>

		<param field="Mode2" label="Add support of RGBW devices for Homebridge" width="175px">
			<options>
				<option label="True" value="1"/>
				<option label="False" value="0" default="true" />
			</options>
		</param>

		<param field="Mode3" label="I am accepting that Power reading may be inaccurate and is totally unsupported, just enable it!" width="175px">
			<options>
				<option label="Power and energy" value="2"/>
				<option label="Only Power" value="1" default="true"/>
				<option label="Not used" value="0" />
			</options>
		</param>

		<param field="Mode4" label="Use absolute value of energy readings" width="175px">
			<options>
				<option label="True" value="1"/>
				<option label="False" value="0" default="true" />
			</options>
		</param>

		<param field="Mode5" label="Enable heartbeat devices" width="175px">
			<options>
				<option label="True" value="1"/>
				<option label="False" value="0" default="true" />
			</options>
		</param>

		<param field="Mode6" label="Debug" width="175px">
			<options>
				<option label="Verbose" value="Verbose"/>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal" default="true" />
			</options>
		</param>
	</params>
</plugin>
"""

errmsg = ""
try:
	import Domoticz
except Exception as e:
	errmsg += "Domoticz core start error: "+str(e)

try:
	import os
except Exception as e:
	errmsg += " os import error: "+str(e)

try:
	import json
except Exception as e:
	errmsg += " Json import error: "+str(e)

try:
	import time
except Exception as e:
	errmsg += " time import error: "+str(e)
try:
	import re
except Exception as e:
	errmsg += " re import error: "+str(e)

try:
	from mqtt import MqttClientSH2
except Exception as e:
	errmsg += " MQTT client import error: "+str(e)

try:
	from datetime import datetime
except Exception as e:
	errmsg += "  datetime import error: "+str(e)

class BasePlugin:
	mqttClient = None

	SHELLY_GEN_2_PREFIXES = [
		'shellyplus1',
		'shellyplus1pm',
		'shellyplus2pm',
		'shellyplusi4',
		'shellyplusht',
	]

	#
	SHELLY_GEN_1="GEN1"
	SHELLY_GEN_2="GEN2"

	#
	def __init__(self):
		return

	#
	def getGen(self, topicPrefix):
		for gen2topixPrefix in self.SHELLY_GEN_2_PREFIXES:
			if topicPrefix.startswith(gen2topixPrefix):
				return self.SHELLY_GEN_2
		return self.SHELLY_GEN_1

	def _updatedevice(self,devname):
		doupdate = False
		try:
			if devname in self.sdevices:
				if time.time()-self.sdevices[devname]>=self.utimeout:
					self.sdevices[devname] = time.time()
					doupdate = True
				else:
					self.sdevices.update({devname:time.time()})
					doupdate = True
		except:
			pass
		return doupdate
	
	## Based on Domoticz_iConic Plugin
	## Source: https://github.com/d-EScape/Domoticz_iConic/tree/master
	#
	def _handleIcons(self):
		sourcepath = Parameters["HomeFolder"] #+"icons"
		if not os.path.isdir(sourcepath):
			Domoticz.Error(sourcepath + " not found")
		else:
			Domoticz.Status("Will import all zipfiles from " + sourcepath + ". Make sure they are all icon files!")
			allfiles = os.listdir(sourcepath)
			for thisfile in allfiles:
				if thisfile.startswith('ShellyNGMQTT-') and thisfile.endswith('.zip'):
					Domoticz.Status("Found " + thisfile)
					thisname = thisfile[:-4]
					if thisname in Images:
						Domoticz.Error("Iconset " + thisname + " already exists")
					else:
						fullpath = thisfile
						Domoticz.Status("Adding iconset " + thisname + " from " + fullpath)
						newimage = Domoticz.Image(fullpath)
						#newimage = Domoticz.Image(Filename=fullpath, Base='ShellyNGMqttPlugin') #, Name=thisname)
						#newimage.Base = 'ShellyNGMqttPlugin'
						Domoticz.Status("Newimage data=" + str(newimage))
						newimage.Create()
						if thisname in Images:
							Domoticz.Status("iconset " + thisname + " created")
						else:
							Domoticz.Error("iconset " + thisname + " was NOT created!")
				else:
					Domoticz.Status(thisfile + " is not a (zip) icon-file")
					
	def onStart(self):
		Domoticz.Log("onStart called")
		global errmsg
		if errmsg =="":
			if str(Settings["AcceptNewHardware"])!="0":
				Domoticz.Log("New hardware creation enabled ")
			else:
				Domoticz.Log("--> New hardware creation disabled! <-- ")

			# Add images
			#
			#Domoticz.Image('icons/kWhMeter.zip').Create()
			#Domoticz.Image('icons/Switch.zip').Create()
			self._handleIcons()
			
			try:
				Domoticz.Heartbeat(10)
				try:
					self.powerread  = int(Parameters["Mode3"])
				except:
					self.powerread  = 0
				try:
					self.abspwr  = int(Parameters["Mode4"])
				except:
					self.abspwr  = 0
				try:
					self.alive  = int(Parameters["Mode5"])
				except:
					self.alive  = 0
				self.debugging = Parameters["Mode6"]
				if self.debugging == "Verbose":
					Domoticz.Debugging(2+4+8+16+64)
				if self.debugging == "Debug":
					Domoticz.Debugging(2)
				self.base_topic = "shellies" # hardwired
				self.mqttserveraddress = Parameters["Address"].strip()
				self.mqttserverport = Parameters["Port"].strip()
				self.mqttClient = MqttClientSH2(self.mqttserveraddress, self.mqttserverport, "", self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
				self.sdevices = {} # list for heartbeat caching
				self.utimeout = 120 # 120 seconds timeout for device heartbeat
			except Exception as e:
				Domoticz.Error("MQTT client start error: "+str(e))
				self.mqttClient = None
		else:
			Domoticz.Error("Your Domoticz Python environment is not functional! "+errmsg)
			self.mqttClient = None

	def checkDevices(self):
		Domoticz.Debug("checkDevices called")

	def onStop(self):
		Domoticz.Debug("onStop called")

	def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
		if self.mqttClient is None:
			return False
		
		Domoticz.Debug("Command: " + Command + " (" + str(Level) + ") Color:" + Color)
		device_id = ""
		
		try:
			device = Devices[Unit]
			devname = device.DeviceID.replace("shellyplug-s","shellyplugs",1) # ugly fix for ShellyPlug-S "-"
			device_id = devname.split('-') # get device name from DeviceID field
		except Exception as e:
			Domoticz.Error("Device has no ID "+str(Unit)+" "+str(e))
			return False
		
		if "-" not in devname.strip():
			Domoticz.Debug("Unsupported device ID")
			return False
		relnum = -1
		
		try:
			relnum = int(device_id[2].strip()) # get channel if applicable
		except:
			relnum = -1
		
		device_id[0] = device_id[0].replace("shellyplugs","shellyplug-s",1) # ugly fix for ShellyPlug-S "-"

		# Shelly Gen 2
		if self.getGen(devname) == self.SHELLY_GEN_2:
			mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]
			cmd = getGen2DeviceCommand(devname, mqttpath, Command, Level, Color)
			Domoticz.Debug("Gen2: Got command '" + str(cmd) + "' for: '" + devname + "'")

			if isinstance(cmd, dict):
				try:
					if "src" not in cmd:
						cmd["src"] = mqttpath
					cmd = json.dumps(cmd)
				except:
					cmd = ""

			if cmd != "":
				
				Domoticz.Log("Gen2: Sending command '" + str(cmd) + "' to: '" + mqttpath + "/rpc'")

				try:
					self.mqttClient.publish(mqttpath+"/rpc", cmd)
				except Exception as e:
					Domoticz.Debug(str(e))
		
		# Check if is it a normal relay
		#
		if relnum in range(0,4) and len(device_id)==3: 
			mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/relay/"+device_id[2]+"/command" # reconstrutct necessarry mqtt path
			cmd = Command.strip().lower()
			Domoticz.Debug(mqttpath+" "+cmd)
			if cmd in ["on","off"]:        # commands are simply on or off
				try:
					self.mqttClient.publish(mqttpath, cmd)
					# if cmd=="off":
					# device.Update(nValue=int(Level),sValue=str(Command)) # force device update if it is offline
				except Exception as e:
					Domoticz.Debug(str(e))
		
		# Otherwise check if it is a roller shutter
		#
		elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1]=="roller":
			cmd = Command.strip().lower()
			scmd = ""                      # Translate Domoticz command to Shelly command
			if str(Parameters["Mode1"])=="1": # check if global inversion requested
				if cmd == "stop":
					scmd = "stop"
				elif cmd == "open" or cmd == "on":
					scmd = "close"
				elif cmd == "close" or cmd == "off":
					scmd = "open"
			else:
				if cmd == "stop":
					scmd = "stop"
				elif cmd == "open" or cmd == "on":
					scmd = "open"
				elif cmd == "close" or cmd == "off":
					scmd = "close"
			if scmd != "":
				mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command"
				try:
					self.mqttClient.publish(mqttpath, scmd)
				except Exception as e:
					Domoticz.Debug(str(e))

		# Otherwise, handle percentage poisitioning
		#
		elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1]=="pos":
			cmnd = str(Command).strip().lower()
			if (cmnd=="set level"): # percentage requested
				if str(Parameters["Mode1"])!="1": # check if global inversion requested
						pos = str(Level).strip().lower()
				else:
						pos = str(100-Level).strip().lower()
				mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command/pos"
				Domoticz.Debug(mqttpath+" "+str(Command)+" "+str(Level))
				try:
					self.mqttClient.publish(mqttpath, pos)
				except Exception as e:
					Domoticz.Debug(str(e))
			else: # command arrived
				scmd = ""
				Domoticz.Debug(cmnd)                      # Translate Domoticz command to Shelly command
				if str(Parameters["Mode1"])=="1": # check if global inversion requested
					if cmnd == "open" or cmnd == "on":
						scmd = "close"
					elif cmnd == "close" or cmnd == "off":
						scmd = "open"
					elif cmnd == "stop":
						scmd = "stop"
				else:
					if cmnd == "open" or cmnd == "on":
						scmd = "open"
					elif cmnd == "close" or cmnd == "off":
						scmd = "close"
					elif cmnd == "stop":
						scmd = "stop"
				if scmd != "":
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/roller/"+device_id[2]+"/command"
					Domoticz.Debug(mqttpath)
					try:
						self.mqttClient.publish(mqttpath, scmd)
					except Exception as e:
						Domoticz.Debug(str(e))
						
		# Handle RGB Device
		#
		elif relnum in range(0,4) and len(device_id)==4 and device_id[len(device_id)-1] in ["rgb","w","dimmer"]:
			if (Command == "Set Level"):
				mqttpath = ""
				if int(Level)>0:
					amode = '"turn": "on"'    # standard RGB device
				else:
					amode = '"turn": "off"'
				if device_id[3]=="rgb":
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/color/"+device_id[2]+"/set"
					scmd = '{'+amode+',"mode":"color","gain":'+str(Level)+'}'
				elif device_id[3]=="dimmer": # Dimmer support added by asquelt
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/light/"+device_id[2]+"/set"
					scmd = '{'+amode+',"brightness":'+str(Level)+'}'
				else:
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/white/"+device_id[2]+"/set"
					scmd = '{'+amode+',"brightness":'+str(Level)+'}'
				if ("2LED" in device_id[0]): # try to support Shelly2LED
					scmd = '{"brightness":'+str(Level)+'}'
				Domoticz.Debug('RGB Level:' + scmd)
				if mqttpath:
					try:
						self.mqttClient.publish(mqttpath, scmd)
					except Exception as e:
						Domoticz.Debug(str(e))
			elif (Command == "Set Color"):
				try:
					color = json.loads(Color)
				except Exception as e:
					Domoticz.Debug(str(e))
				if len(color)>0:
					if device_id[3]=="rgb":
						mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/color/"+device_id[2]+"/set"
						if "bulb" in device_id[0]: # Handle Bulb device
							if color["r"] == 0 and color["g"] == 0 and color["b"] == 0:
								scmd = '{"turn":"on","mode":"white","white":'+str(color["cw"])+',"brightness":'+str(Level)+'}'
							else:
								scmd = '{"turn":"on","mode":"color","red":'+str(color["r"])+',"green":'+str(color["g"])+',"blue":'+str(color["b"]) +',"white":'+str(color["cw"])+',"gain":'+str(Level)+'}'
						else: # Handle standard RGB device
							scmd = '{"turn":"on","mode":"color","red":'+str(color["r"])+',"green":'+str(color["g"])+',"blue":'+str(color["b"]) +',"white":'+str(color["cw"])+'}'
						Domoticz.Debug('RGB Color:' + scmd)
						try:
							self.mqttClient.publish(mqttpath, scmd)
						except Exception as e:
							Domoticz.Debug(str(e))
					elif device_id[3]=="dimmer": # BulbDuo
						mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/light/"+device_id[2]+"/set"
						if int(Level)<=0:
							state = "off"
						else:
							state = "on"
						wlevel = int((255-int(color["ww"]))/2.55) # translate range 255 to range 100
						scmd = '{"turn":"'+str(state)+'","white":'+str(wlevel)+',"brightness":'+str(Level)+'}'
						Domoticz.Debug('WW Dimmer:' + scmd)
						try:
							self.mqttClient.publish(mqttpath, scmd)
						except Exception as e:
							Domoticz.Debug(str(e))
			else:
				if device_id[3]=="rgb":
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/color/"+device_id[2]+"/command"
				elif device_id[3]=="dimmer":
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/light/"+device_id[2]+"/command"
				else:
					mqttpath = self.base_topic+"/"+device_id[0]+"-"+device_id[1]+"/white/"+device_id[2]+"/command"
				cmd = Command.strip().lower()
				if cmd in ["on","off"]:        # commands are simply on or off
					scmd = str(cmd)
					try:
						self.mqttClient.publish(mqttpath, scmd)
						# if cmd=="off":
						# device.Update(nValue=int(Level),sValue=str(Command)) # force device update if it is offline
					except Exception as e:
						Domoticz.Debug(str(e))

	def onConnect(self, Connection, Status, Description):
		if self.mqttClient is not None:
			self.mqttClient.onConnect(Connection, Status, Description)

	def onDisconnect(self, Connection):
		if self.mqttClient is not None:
			self.mqttClient.onDisconnect(Connection)

	def onMessage(self, Connection, Data):
		if self.mqttClient is not None:
			self.mqttClient.onMessage(Connection, Data)

	def onHeartbeat(self):
		Domoticz.Debug("Heartbeating...")
		if self.mqttClient is not None:
			try:
				# Reconnect if connection has dropped
				if (self.mqttClient._connection is None) or (not self.mqttClient.isConnected):
					Domoticz.Debug("Reconnecting")
					self.mqttClient._open()
				else:
					self.mqttClient.ping()
			except Exception as e:
				Domoticz.Error(str(e))

	def onMQTTConnected(self):
		if self.mqttClient is not None:
			self.mqttClient.subscribe([self.base_topic + '/#'])

	def onMQTTDisconnected(self):
		Domoticz.Debug("onMQTTDisconnected")

	def onMQTTSubscribed(self):
		Domoticz.Debug("onMQTTSubscribed")

	def onMQTTPublish(self, topic, message): # process incoming MQTT statuses

		if "/announce" in topic: # announce did not contain any information for us
			return False
		
		try:
			topic = str(topic)
			original_message = message
			message = str(message)
		except:
			Domoticz.Debug("MQTT message is not a valid string!") #if message is not a real string, drop it
			return False
		
		Domoticz.Debug("MQTT message: " + topic + " " + str(message))
		
		mqttpath = topic.split('/')
		if (mqttpath[0] == self.base_topic):
			if self.alive: # if device heartbeat enabled
				if self._updatedevice(str(mqttpath[1])): # if update needed
					unitname = mqttpath[1]+"-online"
					iUnit = searchdevice(unitname)
					if iUnit<0:
						devparams = { "Name" : unitname, "Unit": iUnit, "TypeName" :"Switch", "Used":1, "DeviceID" : unitname}
						iUnit = adddevice(**devparams)
					if iUnit<0:
						return False
					try:
						Devices[iUnit].Update(nValue=1,sValue="On")
					except Exception as e:
						Domoticz.Debug(str(e))
			# Shelly Gen 2
			if self.getGen(mqttpath[1]) == self.SHELLY_GEN_2:
				return updateGen2Device(mqttpath, original_message, self.powerread, self.abspwr)
			# RELAY and EMETER type, not command->process (Shelly relays, EM & EM3)
			elif ( (len(mqttpath)>4) and (mqttpath[4] in ["power","energy"]) ) or ( (len(mqttpath)>3) and (mqttpath[2] in ["relay","emeter"]) and ("/command" not in topic) ):
				return updateRelayAndMeter(mqttpath, message, self.powerread, self.abspwr)
			# ROLLER type, not command->process
			elif ( len(mqttpath)>3) and (mqttpath[2] == "roller") and ("/command" not in topic):
				return updateRoller(mqttpath, message)
			# INPUT type, not command->process
			elif ( len(mqttpath)>3) and (mqttpath[2] == "input") and (mqttpath[len(mqttpath)-1]!="command"):
				return updateInput(mqttpath, message)
			# LONGPUSH type, not command->process
			elif ( len(mqttpath)>3) and (mqttpath[2] == "longpush") and (mqttpath[len(mqttpath)-1]!="command"):
				return updateLongPush(mqttpath, message)
			# ShellyGAS
			elif ( (len(mqttpath)>3) and ("shellygas" in mqttpath[1]) and (mqttpath[2] in ["sensor"]) ):
				return updateGas(mqttpath, original_message)
			# Button device
			elif( (len(mqttpath)>3) and "shellybutton" in mqttpath[1] and (mqttpath[2] == "input_event" or mqttpath[2] == "sensor" ) ):
				return updateButton(mqttpath, message)
			# Generic input_event
			elif( (len(mqttpath)>3) and (mqttpath[2] == "input_event") ):
				return updateInputEvent(mqttpath, message)
			# SENSOR type, not command->process ShellyFlood,Shelly Smoke, ShellyDW2 (temp and battery)
			elif( (len(mqttpath)>3) and (mqttpath[2] == "sensor") and (mqttpath[3] in ['temperature','battery']) and any( item in mqttpath[1] for item in ["shellyflood" , "shellysmoke", "shellydw2" ])):
				return updateSensorTempBattery(mqttpath, message)
			# SENSOR type, not command->process ShellySense and ShellyHT
			elif (len(mqttpath)>3) and (mqttpath[2] == "sensor") and (mqttpath[3] in ['temperature','humidity','battery']) and (("shellysense" in mqttpath[1]) or ("shellyht" in mqttpath[1])):
				return updateSensorTempHumBattery(mqttpath, message)
			# SENSOR type, not command->process - device inside temperature!
			elif (len(mqttpath)==3) and (mqttpath[2] == "temperature"):
				return updateTemperature(mqttpath, message)
			# SENSOR MOTION
			elif (len(mqttpath)==3) and (mqttpath[2] == "status"):
				return updateMotion(mqttpath, message)
			# Switch sensor type, ShellyFlood & ShellySmoke & ShellyMotion & ShellyDW
			elif (len(mqttpath)>3) and (mqttpath[2] == "sensor") and (mqttpath[3] in ['flood','smoke','motion','state']):
				return updateFloodSmokeMotionState(mqttpath, message)
			#  Switch sensor type, ShellyDW,ShellyDW2 sensors
			elif (
				len(mqttpath) > 3 and mqttpath[2] == "sensor" and
				mqttpath[3] in ["lux" , "tilt" , "vibration" , "illumination" , "act_reasons" ]
			):
				return updateVibrationIlluminationReasons(mqttpath, message)
			# SENSOR type, not command->process ShellyDW battery
			elif (len(mqttpath)>3) and (mqttpath[3] == "battery") and ("shellydw" in mqttpath[1]):
				return updateDWBattery(mqtpath, message)
			# RGB type, not command->process
			elif (len(mqttpath)>3) and (mqttpath[2] in ["color","white","light"]) and ("/command" not in topic) and ("/set" not in topic):
				return updateRGB(mqttpath, message)
			# SENSOR type, not command->process - device ext temperature!
			elif (len(mqttpath)==4) and (mqttpath[2] == "ext_temperature"):
				return updateExtTemperature(mqttpath, message)
			# SENSOR type, not command->process - device ext humidity!
			elif (len(mqttpath)==4) and (mqttpath[2] == "ext_humidity"):
				return updateExtHumidity(mqttpath, message)
			# SENSOR type, not command->process - ADC values
			elif (len(mqttpath)==4) and (mqttpath[2] == "adc"):
				return updateAdc(mqttpath, message)

global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
	global _plugin
	_plugin.onCommand(Unit, Command, Level, Color)

def onDeviceModified(Unit):
	global _plugin
	return

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def searchdevice(devname):
	devname = str(devname).strip()
	if "-" not in devname:
		return -1
	# Domoticz.Debug( ">>> Looking for device: " + str(devname) )
	unitID = -1
	
	for device in Devices:
		# Domoticz.Log( ">>> Check device: " + str(Devices[device].DeviceID.strip()) )
		try:
			if( Devices[device].DeviceID.strip() == devname ):
				unitID = device
				break
		except:
			pass

	Domoticz.Debug( ">>> Return unitID " + str(unitID) + " for device: " + str(devname) )
	return unitID
					
def adddevice(**kwargs):
	if str(Settings["AcceptNewHardware"])!="0":
		try:
			iUnit = len(Devices)+1
			# Looking for possible device ID
			for x in range(1,256):
				if x not in Devices:
					iUnit=x
					break
			kwargs["Unit"] = iUnit
			# Create device
			Domoticz.Log( "Adding device: " + str(kwargs["Name"]) + " parameters: " + str(kwargs))
			Domoticz.Device( **kwargs ).Create()
		except Exception as e:
			Domoticz.Error(str(e))
			return -1
		return iUnit
	else:
		return -1
		
def updateRelayAndMeter(mqttpath, message, powerReadSetting=0, absPowerSetting=0):
	unitname = mqttpath[1]+"-"+mqttpath[3]
	unitname = unitname.strip()
	devtype = 1
	funcid = -1
	try:
		funcid = int(mqttpath[3].strip())
		devtype=0 # regular relay
	except:
		devtype = 1 # Shelly2 power meter
	if len(mqttpath)==5 and devtype==0:
		devtype = 2 # indexed relays with power readings (Shelly EM/1PM/2.5/4Pro)
	
	subval=""
	if devtype==1:
		subval = mqttpath[3].strip()
	elif devtype==2:
		subval = mqttpath[4].strip()
	
	if subval=="power" or subval=="energy":
		if funcid in [0,1,2,3]:
			unitname=mqttpath[1]+"-"+str(funcid)+"-energy" # fix 2.5 and 4pro support (also 1PM,EM)
		else:
			unitname=mqttpath[1]+"-energy" # shelly2
	elif subval=="voltage":
		unitname=mqttpath[1]+"-"+str(funcid)+"-voltage" # Shelly EM voltage meter
	elif subval=="reactive_power" or subval=="returned_energy":
		if funcid in [0,1,2,3]:
			unitname=mqttpath[1]+"-"+str(funcid)+"-renergy" # EM
	elif subval=="total":
		if funcid in [0,1,2,3]:
			unitname=mqttpath[1]+"-"+str(funcid)+"-total" # EM
	elif subval=="total_returned":
		if funcid in [0,1,2,3]:
			unitname=mqttpath[1]+"-"+str(funcid)+"-rtotal" # EM
	elif subval=="current":
		unitname=mqttpath[1]+"-"+str(funcid)+"-current" # Shelly EM current meter
	elif subval=="pf":
		unitname=mqttpath[1]+"-"+str(funcid)+"-pf" # Shelly EM pf
	iUnit = searchdevice(unitname)
	
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:
			iUnit = 0
			for x in range(1,256):
				if x not in Devices:
					iUnit=x
					break
			if iUnit==0:
				iUnit=len(Devices)+1
			if devtype==0:
				Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Switch",Used=1,DeviceID=unitname).Create()
			elif subval=="voltage":
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=8,Used=1,DeviceID=unitname).Create()
			elif subval=="current":
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=23,Used=1,DeviceID=unitname).Create()
			elif subval=="pf":
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=31,Used=0,DeviceID=unitname).Create()
			elif powerReadSetting:
				if "energy" in subval or "power" in subval or "total" in subval:
					Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=29,Used=0,DeviceID=unitname).Create()
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	
	#
	if devtype==0:
		try:
			scmd = str(message).strip().lower()
			if (str(Devices[iUnit].sValue).lower() != scmd):
				if (scmd == "on"): # set device status if needed
					Devices[iUnit].Update(nValue=1,sValue="On")
				else:
					Devices[iUnit].Update(nValue=0,sValue="Off")
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	elif subval in ["voltage","current","pf"]:
		try:
			mval = float(str(message).strip())
		except:
			mval = str(message).strip()
		try:
			Devices[iUnit].Update(nValue=0,sValue=str(mval))
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	elif powerReadSetting:
		try:
			curval = Devices[iUnit].sValue
			prevdata = curval.split(";")
		except:
			prevdata = []
		if len(prevdata)<2:
			prevdata.append(0)
			prevdata.append(0)
		try:
			mval = float(str(message).strip())
			if absPowerSetting!=0: # activate ugly fix for solar cell negative input
				mval = abs(mval)
		except:
			mval = str(message).strip()
		
		sval = ""
		if "power" in subval and powerReadSetting==2:
			sval = str(mval)+";"+str(prevdata[1])
		elif "power" in subval and powerReadSetting==1:
			sval = str(mval)+";0"
		elif "total" in subval:
			try:
				sval = "0;"+str(float(mval))
			except:
				sval = "0;0"
		elif "energy" in subval and powerReadSetting==2:
			try:
				mval2 = round((mval*0.017),4) # 10*Wh? or Watt-min??
			except:
				mval2 = str(mval)
			sval = str(prevdata[0])+";"+str(mval2)
		
		try:
			if sval!="":
				updated = 60
				Domoticz.Debug( "Device data: " + str(unitname) + " value: " + str( sval ) + " lastupdate:  " + str( Devices[iUnit].LastUpdate ) );
				try:
					format = '%Y-%m-%d %H:%M:%S'
					# WORKAROUND:
					# TypeError attribute of type 'NoneType' is not callable
					# Python bug workaround
					try:
						lastupdate = datetime.strptime( Devices[iUnit].LastUpdate , format)
					except TypeError:
						lastupdate = datetime(*(time.strptime( Devices[iUnit].LastUpdate , format)[0:6]))

					tdelta = datetime.now( ) - lastupdate
					updated = tdelta.seconds
					Domoticz.Debug( "Device update timedelta: " + str(updated) );
				except Exception as e:
					Domoticz.Error(str(e))

				if( updated > 10 ):
					Domoticz.Debug( "update: " + str(unitname) + " value: " + str( sval ) + " lastupdate:  " + str( Devices[iUnit].LastUpdate ) );
					Devices[iUnit].Update(nValue=0,sValue=str(sval))

		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	return True

def updateRoller(mqttpath, message):
	if mqttpath[len(mqttpath)-1]=="pos":
		unitname = mqttpath[1]+"-"+mqttpath[3]+"-pos"
	else:
		unitname = mqttpath[1]+"-"+mqttpath[3]+"-roller"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:
			iUnit = 0
			for x in range(1,256):
				if x not in Devices:
					iUnit=x
					break
			if iUnit==0:
				iUnit=len(Devices)+1
			if "-pos" in unitname:
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=244, Subtype=62, Switchtype=13,Used=1,DeviceID=unitname).Create() # create Blinds Percentage
			else:
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=244, Subtype=62, Switchtype=15,Used=1,DeviceID=unitname).Create() # create Venetian Blinds EU type
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	if "-pos" in unitname:
		try:
			if str(Parameters["Mode1"])!="1": # check if global inversion requested
				pval = int(str(message).strip())
			else:
				pval = 100-int(str(message).strip())
				if pval==101:
					pval=-1
			nval = 0
			if pval>0 and pval<100:
				nval = 2
			if pval>99:
				nval = 1
			try:
				p_pval = Devices[iUnit].sValue
				p_nval = Devices[iUnit].nValue
			except:
				p_pval = -1
				p_nval = -1
			if (str(p_pval).strip()!=str(pval).strip()) or (int(p_nval)!=int(nval)):
				Domoticz.Debug(str(p_nval)+":"+str(nval)+" "+str(p_pval)+":"+str(pval))
				Devices[iUnit].Update(nValue=int(nval),sValue=str(pval))
		except:
			Domoticz.Debug("MQTT message error " + str(topic) + ":"+ str(message))
	else:
		try:
			bcmd = str(message).strip().lower()
			if bcmd == "stop" and str(Devices[iUnit].sValue).lower() !="stop":
				Devices[iUnit].Update(nValue=17,sValue="Stop") # stop
				return True
			elif bcmd == "open" and str(Devices[iUnit].sValue).lower() !="off":
				Devices[iUnit].Update(nValue=0,sValue="Off") # open
				return True
			elif bcmd == "close" and str(Devices[iUnit].sValue).lower() !="on":
				Devices[iUnit].Update(nValue=1,sValue="On")  # close
				return True
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		
def updateInput(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]+"-input"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit<0: # if device does not exists in Domoticz, than create it

		imageId = 9 # Means 'Generic On/Off switch'
		if 'ShellyNGMQTT-Switch' in Images:
			imageId = Images["ShellyNGMQTT-Switch"].ID

		devparams = {
			"Name" : unitname+" BUTTON",
			"Unit": iUnit,
			"TypeName" :"Switch",
			"Used": 1, 
			"DeviceID" : unitname,
			"Image" : imageId
		}
		iUnit = adddevice(**devparams)
	if iUnit<0:
		return False
	try:
		if str(message).lower=="on" or str(message)=="1":
			scmd = "on"
		else:
			scmd = "off"
		if (str(Devices[iUnit].sValue).lower() != scmd):
			if (scmd == "on"): # set device status if needed
				Devices[iUnit].Update(nValue=1,sValue="On")
			else:
				Devices[iUnit].Update(nValue=0,sValue="Off")
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	return True

def updateLongPush(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]+"-lpush"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	
	if iUnit<0: # if device does not exists in Domoticz, than create it

		imageId = 9 # Means 'Generic On/Off switch'
		if 'ShellyNGMQTT-Switch' in Images:
			imageId = Images["ShellyNGMQTT-Switch"].ID

		devparams = {
			"Name": unitname+" LONGPUSH",
			"Unit": iUnit,
			"TypeName": "Switch",
			"Used": 0,
			"DeviceID" : unitname,
			"Image" : imageId
		}
		iUnit = adddevice(**devparams)
	
	if iUnit<0:
		return False
	
	try:
		if str(message).lower=="on" or str(message)=="1":
			scmd = "on"
		else:
			scmd = "off"
		if (str(Devices[iUnit].sValue).lower() != scmd):
			if (scmd == "on"): # set device status if needed
				Devices[iUnit].Update(nValue=1,sValue="On")
			else:
				Devices[iUnit].Update(nValue=0,sValue="Off")
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	return True

def updateGas(mqttpath, original_message):
	unitname = mqttpath[1]+"-"
	try:
		funcid = int(mqttpath[3].strip())
		unitname += str(funcid)+"-"+mqttpath[4]
	except:
		unitname += mqttpath[3]
		
	iUnit = searchdevice(unitname)
	if iUnit<0: # if device does not exists in Domoticz, than create it
		if "-operation" in unitname:
			devparams = {
				"Name" : unitname,
				"Unit" : iUnit,
				"TypeName" : "Selector Switch",
				"Used" : 1 ,
				"DeviceID" : unitname ,
				"Image" : 9,
				"Options" : {
					"LevelActions": "|||||",
					"LevelNames": "Off|unknown|warmup|normal|fault",
					"LevelOffHidden": "true",
					"SelectorStyle": "1"
				}	
			}
		elif "-gas" in unitname:
			devparams = { "Name" : unitname,
				"Unit" : iUnit,
				"TypeName" : "Selector Switch",
				"Used" : 1 , 
				"DeviceID" : unitname ,
				"Image" : 9,
				"Options" : {
					"LevelActions": "|||||",
					"LevelNames": "Off|unknown|none|mild|heavy|test",
					"LevelOffHidden": "true",
					"SelectorStyle": "1"
				}
			}
		elif "self_test" in unitname:
			devparams = {
				"Name" : unitname,
				"Unit" : iUnit,
				"TypeName" : "Selector Switch",
				"Used" : 1 ,
				"DeviceID" : unitname ,
				"Image" : 9,
				"Options" : {
					"LevelActions": "|||||",
					"LevelNames": "Off|not_completed|completed|running|pending",
					"LevelOffHidden": "true",
					"SelectorStyle": "1"
				}
			}
		elif "concentration" in unitname:
			devparams = {
				"Name" : unitname,
				"Unit" : iUnit,
				"Used" : 1 ,
				"DeviceID" : unitname ,
				"Type" : 243 ,
				"Subtype" : 31 ,
				"Options" : {
					"Gas concentration" : "1;ppm"
				}
			}
		try:
			iUnit = adddevice(**devparams)
			if( iUnit < 0 ):
				Domoticz.Status( "Error adding device: " + str(unitname) )
				return False
		except:
			return False

	if "concentration" in unitname:
		try:
			mval = float(message)
		except:
			mval = str(message).strip()
		try:
			Devices[iUnit].Update(nValue=0,sValue=str(mval))
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	else:
		if "-operation" in unitname:
			events = { "unknown" : 10 , "warmup" : 20 , "normal": 30 , "fault" : 40 }
		elif "-gas" in unitname:
			events = { "unknown" : 10 , "none" : 20 , "mild": 30 , "heavy" : 40 , "test" : 50 }
		elif "self_test" in unitname:
			events = { "not_completed" : 10 , "completed" : 20 , "running": 30 , "pending" : 40 }
		try:
			case = events.get(  str(message) , 0 )
			Domoticz.Debug("Update " + Devices[iUnit].Name + " selector to: " + str(case) )
			Devices[iUnit].Update(nValue=case,sValue=str(case))
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	# End of updateButton
	return True
		
def updateButton(mqttpath, message):
	unitname = str(mqttpath[1]).strip()
	Domoticz.Debug(">>>> Unit name: " + unitname )
	updatesensor = False
	if( mqttpath[2] == "sensor" ):
		if( mqttpath[3] != "battery" ):
			return True
		updatesensor = True
	#Looking for the device
	iUnit = searchdevice( unitname )
	# if device does not exists in Domoticz, than create it
	if iUnit < 0:
		if( updatesensor ):
			Domoticz.Debug(">>>> Device not exists, cannot update status: " + unitname )
			return False
		
		# Image = 9 means "Generic On/Off switch"
		devparams = {
			"Name" : unitname+"-button1",
			"Unit" : iUnit ,
			"TypeName" : "Selector Switch",
			"Used" : 1,
			"DeviceID" : unitname,
			"Image" : 9,
			"Options" : {
				"LevelActions": "|||||",
				"LevelNames": "Off|Single|Double|Triple|Long",
				"LevelOffHidden": "true",
				"SelectorStyle": "1"
			}
		}
		
		# Create the Domoticz device
		iUnit = adddevice( **devparams )
		if( iUnit < 0 ):
			Domoticz.Status( "Error adding device: " + str(unitname) )
			return False

	Domoticz.Debug(">>>> Device found: unit ID: " + str(iUnit) )
	
	# Device update
	try:
		if( updatesensor ):
			# Update battery level
			if( mqttpath[3] == "battery" ):
				if( int( message ) != int( Devices[iUnit].BatteryLevel ) ):
					Domoticz.Log("Update " + Devices[iUnit].Name + " battery level to: " + str(message) )
					Devices[iUnit].Update( nValue=Devices[iUnit].nValue,sValue=Devices[iUnit].sValue , BatteryLevel = int( message ) , SuppressTriggers = True )
		else:
			# Update button status
			Domoticz.Debug(">>>> Device action: " + str(message) )
			# 2020.08. button event types
			# {"event":"S","event_cnt":1}
			# {"event":"SS","event_cnt":2}
			# {"event":"SSS","event_cnt":3}
			# {"event":"L","event_cnt":4}
			payload =  json.loads( message.replace("'",'"').lower() )
			# Button push event
			if( "event" in payload ):
				# Convert event to selector switch strte
				events = { "s" : 10 , "ss" : 20 , "sss": 30 , "l" : 40 }
				case = events.get(  str(payload[ "event" ]) , 0 )
				Domoticz.Debug("Update " + Devices[iUnit].Name + " selector to: " + str(case) )
				Devices[iUnit].Update(nValue=case,sValue=str(case))
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	# End of updateButton
	return True

def updateInputEvent(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[2]+str(mqttpath[3])
	
	Domoticz.Debug(">>>> Unit name: " + unitname )
	
	#Looking for the device
	iUnit = searchdevice( unitname )
	# if device does not exists in Domoticz, than create it
	if iUnit < 0:

		imageId = 9 # Means 'Generic On/Off switch'
		if 'ShellyNGMQTT-Switch' in Images:
			imageId = Images["ShellyNGMQTT-Switch"].ID

		devparams = {
			"Name" : unitname,
			"Unit" : iUnit ,
			"TypeName": "Selector Switch",
			"Used": 0,
			"DeviceID" : unitname,
			"Image" : imageId,
			"Options": {
				"LevelActions": "|||||",
				"LevelNames": "Off|Single|Double|Triple|Long|Single+Long|Long+Single",
				"LevelOffHidden": "false",
				"SelectorStyle": "1"
			}
		}
		# Create the Domoticz device
		iUnit = adddevice( **devparams )
		if( iUnit < 0 ):
			Domoticz.Status( "Error adding device: " + str(unitname) )
			return False

	Domoticz.Debug(">>>> Device found: unit ID: " + str(iUnit) )

	# Device update
	try:
		# Update button status
		# Domoticz.Debug(">>>> Device action: " + str(message) )
		payload =  json.loads( message.replace("'",'"').lower() )
		# Button push event
		if ("event" in payload):
			# Convert event to selector switch state
			events = { "s" : 10 , "ss" : 20 , "sss": 30 , "l" : 40, "sl": 50, "ls" : 60 }
			case = events.get(  str(payload[ "event" ]) , 0 ) # get event type
			ncnt = str(payload[ "event_cnt" ]) # get last event ID
			try:
				cnt = int(Devices[iUnit].Description) # get old event ID if exist
			except Exception as e:
				cnt = -1
			try:
				ncnt = int(ncnt)
			except:
				ncnt = 0
			if (int(Devices[iUnit].nValue) != int(case)) or (ncnt != cnt): # update when type or counter changed
				Domoticz.Log("Update " + Devices[iUnit].Name + " selector to: " + str(case) )
				Devices[iUnit].Update(nValue=case,sValue=str(case),Description=str(ncnt))
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	# End of updateInputEvent
	return True

def updateSensorTempBattery(mqttpath, message):
	unitname = mqttpath[1]+"-temp"
	unitname = unitname.strip()
	iUnit = searchdevice( unitname )
	# Domoticz.Log( ">>> Device: " + str(unitname) + " UnitID: " + str( iUnit ) )
	if iUnit < 0:
		if( adddevice( Name=unitname, TypeName="Temperature", Used=1, DeviceID=unitname ) < 0 ):
			Domoticz.Log( "Error adding device: " + str(unitname) )
			return False
	stype = mqttpath[3].strip().lower()
	try:
		curval = Devices[iUnit].sValue
	except:
		curval = 0
	try:
		mval = float(message)
	except:
		mval = str(message).strip()

	if stype=="battery":
		try:
			if int(Devices[iUnit].BatteryLevel) != int(mval):
				Devices[iUnit].Update(nValue=0,sValue=str(curval),BatteryLevel=int(mval),SuppressTriggers = True)
		except Exception as e:
			Domoticz.Debug(str(e))
			return False

	elif stype=="temperature":
		try:
			Devices[iUnit].Update(nValue=0,sValue=str(mval))
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	# End of updateSensorTempBattery
	return True

def updateSensorTempHumBattery(mqttpath, message):
	unitname = mqttpath[1]+"-sensor"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)

	# if device does not exists in Domoticz, than create it
	if iUnit<0: 
			devparams = {
				"Name" : unitname,
				"Unit": iUnit,
				"TypeName" :"Temp+Hum",
				"Used":1,
				"DeviceID" : unitname
			}
			iUnit = adddevice(**devparams)
	
	if iUnit<0:
		return False
	
	stype = mqttpath[3].strip().lower()
	try:
		curval = Devices[iUnit].sValue
	except:
		curval = 0
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	if stype=="battery":
		try:
			if int(Devices[iUnit].BatteryLevel) != int(mval):
				Devices[iUnit].Update(nValue=0,sValue=str(curval),BatteryLevel=int(mval))
		except Exception as e:
			Domoticz.Debug(str(e))
	elif stype=="temperature":
		try:
			env = curval.split(";")
		except:
			env = [0,0]
		if len(env)<3:
			env.append(0)
			env.append(0)
			env.append(0)
		sval = str(mval)+";"+str(env[1])+";"+str(env[2])
		try:
			Devices[iUnit].Update(nValue=0,sValue=str(sval))
		except Exception as e:
			Domoticz.Debug(str(e))
	elif stype=="humidity":
		hstat = 0
		try:
			env = curval.split(";")
		except:
			env = [0,0]
		if len(env)<1:
			env.append(0)
		if int(mval)>= 50 and int(mval)<=70:
			hstat = 1
		elif int(mval)<40:
			hstat = 2
		elif int(mval)>70:
			hstat = 3
		sval = str(env[0]) + ";"+ str(mval)+";"+str(hstat)
		try:
			Devices[iUnit].Update(nValue=0,sValue=str(sval))
		except Exception as e:
			Domoticz.Debug(str(e))

def updateTemperature(mqttpath, message):
	
	unitname = mqttpath[1]+"-temp"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)

	if iUnit<0: # if device does not exists in Domoticz, than create it
		devparams = {
			"Name" : unitname,
			"Unit": iUnit,
			"TypeName" :"Temperature", 
			"Used":0,
			"DeviceID" : unitname
		}
		iUnit = adddevice(**devparams)
		if iUnit<0:
			return False
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	try:
			Devices[iUnit].Update(nValue=0,sValue=str(mval))
			return True
	except Exception as e:
			Domoticz.Debug(str(e))
			return False
	
def updateMotion(mqttpath, message):
	tmsg = str(message).strip()
	if "{" in tmsg:
		tmsg = tmsg.replace("'",'"').lower() # OMG replace single quotes and non-standard upper case letters
		try:
			jmsg = json.loads(tmsg)
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		
		if jmsg:
			if "motion" in jmsg:
					sensors = {
						# 246 Lux; 1 Lux : Illumination (sValue: "float")
						"lux" : {
							"Type" : 246 ,
							"Subtype" : 1
						} ,
						# 244 Light/Switch; Motion
						"motion": {
							"Type" : 244 ,
							"Subtype" : 73 ,
							"Switchtype" : 8
						},
						# 244 Light/Switch; 73 Switch; 2 Contact Statuses: Open: nValue = 1 Closed: nValue = 0
						"vibration": {
							"Type" : 244,
							"Subtype" : 73,
							"Switchtype" : 2
						},
						"active": {
							"Type" : 244,
							"Subtype" : 73,
							"Switchtype" : 2
						},
					}

					stypes = ["lux","motion", "vibration","active"]
					iUnit = -1
					for st in range(len(stypes)):
						unitname = mqttpath[1]+"-"+stypes[st]
						iUnit = searchdevice(unitname)
						if iUnit<0: # if device does not exists in Domoticz, than create it
							try:
								devparams = {  "Name" : unitname , "Unit" : iUnit , "Used" : 1 , "DeviceID" : unitname }
								devparams.update( **sensors[stypes[st]] )
								# Create the Domoticz device
								iUnit = adddevice( **devparams )
							except:
								Domoticz.Status( "Device " + str(unitname) + " unhandled sensor type: " + str(stypes[st]) )
								return False
						
						if iUnit>=0:
							if st > 0: #binary
								try:
									scmd = jmsg[stypes[st]]
									if scmd:
										scmd = "on"
									else:
										scmd = "off"
									if (str(Devices[iUnit].sValue).lower() != scmd): # set device status if changed
										if (scmd == "off"):
											Devices[iUnit].Update(nValue=0,sValue="Off",BatteryLevel=int(jmsg["bat"]))
										else:
											Devices[iUnit].Update(nValue=1,sValue="On",BatteryLevel=int(jmsg["bat"]))
								except Exception as e:
									Domoticz.Debug(str(e))
									return False
							else: #lux
								try:
									Devices[iUnit].Update(nValue=0,sValue=str(jmsg[stypes[st]]),BatteryLevel=int(jmsg["bat"]))
								except Exception as e:
									Domoticz.Debug(str(e))
									return False
	return True

def updateFloodSmokeMotionState(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]
	unitname = unitname.strip()
	iUnit = (unitname)
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:
			iUnit = 0
			for x in range(1,256):
				if x not in Devices:
					iUnit=x
					break
				if iUnit==0:
					iUnit=len(Devices)+1
				if (mqttpath[3]=="motion"):
					Domoticz.Device(Name=unitname, Unit=iUnit,Type=244,Subtype=62,Switchtype=8,Used=1,DeviceID=unitname).Create()
				elif (mqttpath[3]=="state"):
					Domoticz.Device(Name=unitname, Unit=iUnit,Type=244,Subtype=73,Switchtype=11,Used=1,DeviceID=unitname).Create()
				else:
					Domoticz.Device(Name=unitname, Unit=iUnit, TypeName="Switch",Used=1,DeviceID=unitname).Create() # create switch for Alert
				Devices[iUnit].Update(nValue=0,sValue="false")  # init value
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
			
	try:
		scmd = str(message).strip().lower()
		if scmd=="false" or scmd=="close":
			scmd = "off"
		else:
			scmd = "on"
		if (str(Devices[iUnit].sValue).lower() != scmd): # set device status if changed
			if (scmd == "off"):
				Devices[iUnit].Update(nValue=0,sValue="Off")
			else:
				Devices[iUnit].Update(nValue=1,sValue="On")
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	
def updateVibrationIlluminationReasons(mqttpath, message):
	# Every sensor type will be a separete device
	unitname = str(mqttpath[1]+"-"+mqttpath[3]).strip()
	# Sensor wakeup reason, just send to the log
	if( mqttpath[3] == "act_reasons" ):
		Domoticz.Log( "Device " + str(unitname) + " wakeup reason: " + str(message).strip(" []") )
		return True
	iUnit = searchdevice( unitname )
	# if device does not exists than create it
	if iUnit < 0:
		devparams = {  "Name" : unitname , "Unit" : iUnit , "Used" : 1 , "DeviceID" : unitname }
		sensors = {
			# 246 Lux; 1 Lux : Illumination (sValue: "float")
			"lux" : { "Type" : 246 , "Subtype" : 1 } ,
			
			# 243 General ; 31 Custom Sensor (nValue: 0, sValue: "floatValue"), Options: {'Custom': '1;<axisUnits>'}
			# FIXME: Options:: The axis label do not show in domoticz
			"tilt": {
				"Type" : 243,
				"Subtype" : 31,
				"Options" : {
					"Tilt" : "1;Degree"
				}
			} ,
			# 244 Light/Switch; 73 Switch; 2 Contact Statuses: Open: nValue = 1 Closed: nValue = 0
			"vibration": {
				"Type" : 244,
				"Subtype" : 73,
				"Switchtype" : 2
			},
			# Image 19 SUN
			"illumination":{
				"TypeName" : "Selector Switch",
				"Used" : 0,
				"Image" : 19,
				"Options" : {
					"LevelActions": "||||",
					"LevelNames": "Off|bright|twilight|dark|unknown",
					"LevelOffHidden": "true",
					"SelectorStyle": "1"
				}
			}
		}

		try:
			# Merge device specific parameters
			devparams.update( **sensors[mqttpath[3]] )
		except:
			Domoticz.Status( "Device " + str(unitname) + " unhandled sensor type: " + str(mqttpath[3]) )
			return False
		# Create the Domoticz device
		iUnit = adddevice( **devparams )
		if(  iUnit < 0 ):
			Domoticz.Status( "Error adding device: " + str(unitname) )
			return False
		try:
			if( mqttpath[3] == "vibration" ):
				value = 1 if int( message ) == 1 else 0;
				if( Devices[iUnit].nValue != value ):
					Devices[iUnit].Update(nValue = value ,sValue=""  )
					Domoticz.Debug("Update " + Devices[iUnit].Name + " to: " + str(value) )
			elif( mqttpath[3] == "illumination" ):
				state = { "bright" : 10 , "twilight" : 20 , "dark": 30 }
				case = state.get( str(message).strip() , 40 )
				if( Devices[iUnit].sValue != str(case) ):
					Domoticz.Debug("Update " + Devices[iUnit].Name + " selector to: " + str(case) )
					Devices[iUnit].Update(nValue=case,sValue=str(case))
			else:
				value = str(message).strip()
				if( Devices[iUnit].sValue != value ):
					Domoticz.Debug("Update " + Devices[iUnit].Name + " to: " + str(value) )
					Devices[iUnit].Update( nValue = 0, sValue = value )
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True

def updateDWBattery(mqttpath, message):
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	unitname = mqttpath[1]+"-state"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit>=0: # only update existing device
		try:
			curvaln = Devices[iUnit].nValue
			curvals = Devices[iUnit].sValue
		except:
			curvaln = 0
			curvals = ""
		try:
			if int(Devices[iUnit].BatteryLevel) != int(mval):
				Devices[iUnit].Update(nValue=int(curvaln),sValue=str(curvals),BatteryLevel=int(mval))
		except Exception as e:
			Domoticz.Debug(str(e))
	unitname = mqttpath[1]+"-lux"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit>=0: # only update existing device
		try:
			curval = Devices[iUnit].sValue
		except:
			curval = 0
		try:
			if int(Devices[iUnit].BatteryLevel) != int(mval):
				Devices[iUnit].Update(nValue=0,sValue=str(curval),BatteryLevel=int(mval))
		except Exception as e:
			Domoticz.Debug(str(e))

def updateRGB(mqttpath, message, powerReadSetting=0):
	unitname = mqttpath[1]+"-"+mqttpath[3]
	if (mqttpath[2] == "white"):
		unitname = unitname+"-w"
	elif (mqttpath[2] == 'light'):
		unitname = unitname+"-dimmer"
	else:
		unitname = unitname+"-rgb"
	unitname = unitname.strip()
	
	iUnit = searchdevice(unitname)
	
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:
			iUnit = 0
			for x in range(1,256):
				if x not in Devices:
					iUnit=x
					break
			if iUnit==0:
				iUnit=len(Devices)+1
			if "ShellyBulbDuo" in unitname:
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=241, Subtype=8, Switchtype=7, Used=1,DeviceID=unitname).Create() # create Cold White + Warm White device
			elif (mqttpath[2] in ["white","light"]) or ("2LED" in unitname):
				Domoticz.Device(Name=unitname, Unit=iUnit,Type=241, Subtype=3, Switchtype=7, Used=1,DeviceID=unitname).Create() # create Color White device
			else:
				if Parameters["Mode2"]!="1": # check if homebridge support is needed
					Domoticz.Device(Name=unitname, Unit=iUnit,Type=241, Subtype=6, Switchtype=7, Used=1,DeviceID=unitname).Create() # create RGBZW device
				else:
					Domoticz.Device(Name=unitname, Unit=iUnit,Type=241, Subtype=1, Switchtype=7, Used=1,DeviceID=unitname).Create() # create RGBW device
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		
	tmsg = str(message).strip()
	if "{" in tmsg:
		tmsg = tmsg.replace("'",'"').lower() # OMG replace single quotes and non-standard upper case letters
		try:
			jmsg = json.loads(tmsg)
		except Exception as e:
			Domoticz.Debug(str(e))
			jmsg = []
		if jmsg:
			status = 0
			if "ison" in jmsg:
				if str(jmsg["ison"])=="on" or str(jmsg["ison"])=="1" or jmsg["ison"]==True:
					status = 1
			elif "turn" in jmsg:
				if jmsg["turn"]=="on" or jmsg["turn"]=="1" or jmsg["turn"]==True:
					status = 1
			if "red" in jmsg: # rgbw
				color = {}
				color["m"] = 4
				color["t"] = 0
				color["ww"] = 0
				color["r"] = int(jmsg["red"])
				color["g"] = int(jmsg["green"])
				color["b"] = int(jmsg["blue"])
				color["cw"] = int(jmsg["white"])
				dimmer = str(jmsg["gain"])
				if (Devices[iUnit].nValue != status or Devices[iUnit].sValue != dimmer or json.loads(Devices[iUnit].Color) != color):
					jColor = json.dumps(color)
					Domoticz.Debug('Updating device #' + str(Devices[iUnit].ID))
					Domoticz.Debug('nValue: ' + str(Devices[iUnit].nValue) + ' -> ' + str(status))
					Domoticz.Debug('sValue: ' + Devices[iUnit].sValue + ' -> ' + dimmer)
					Domoticz.Debug('Color: ' + Devices[iUnit].Color + ' -> ' + jColor)
					Devices[iUnit].Update(nValue=status, sValue=dimmer, Color=jColor)
			elif "ShellyBulbDuo" in unitname: # BulbDuo, maybe other types in the future?
				color = {}
				color["m"] = 2
				color["t"] = int((100-int(jmsg["white"]))*2.55) # translate range 100 to range 255
				dimmer = str(jmsg["brightness"])
				changed = False
				try:
					if (int(json.loads(Devices[iUnit].Color)["t"]) != int(color["t"])):
						changed = True
				except:
					changed = True
				if (int(Devices[iUnit].nValue) != int(status)) or (int(Devices[iUnit].sValue) != int(dimmer)) or changed:
					jColor = json.dumps(color)
					Domoticz.Debug('Updating device #' + str(Devices[iUnit].ID))
					Domoticz.Debug('nValue: ' + str(Devices[iUnit].nValue) + ' -> ' + str(status))
					Domoticz.Debug('sValue: ' + Devices[iUnit].sValue + ' -> ' + dimmer)
					Domoticz.Debug('Color: ' + Devices[iUnit].Color + ' -> ' + jColor)
					Devices[iUnit].Update(nValue=status, sValue=dimmer, Color=jColor)
			else: # white
				dimmer = str(jmsg["brightness"])
				if (Devices[iUnit].nValue != status or Devices[iUnit].sValue != dimmer):
					Domoticz.Debug('Updating device #' + str(Devices[iUnit].ID))
					Domoticz.Debug('nValue: ' + str(Devices[iUnit].nValue) + ' -> ' + str(status))
					Domoticz.Debug('sValue: ' + Devices[iUnit].sValue + ' -> ' + dimmer)
					Devices[iUnit].Update(nValue=status, sValue=dimmer)
			if powerReadSetting: # decode power property if found
				if "power" in jmsg:
					unitname = mqttpath[1]+"-"+mqttpath[3]+"-power"
					iUnit = searchdevice(unitname)
					if iUnit<0: # if device does not exists in Domoticz, than create it
						devparams = { "Name" : unitname, "Unit": iUnit, "Type": 243, "Subtype": 29, "Used":0, "DeviceID" : unitname}
						iUnit = adddevice(**devparams)
					if iUnit<0:
						return False
					try:
						sval = str(jmsg["power"])+";0"
						Devices[iUnit].Update(nValue=0,sValue=str(sval)) # update power value
					except Exception as e:
						Domoticz.Debug(str(e))
						return False
					return True

#		
def updateExtTemperature(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]+"-temp"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit<0: # if device does not exists in Domoticz, than create it
		devparams = { "Name" : unitname, "Unit": iUnit, "TypeName" :"Temperature", "Used":0, "DeviceID" : unitname}
		iUnit = adddevice(**devparams)
	if iUnit<0:
		return False
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	try:
		Devices[iUnit].Update(nValue=0,sValue=str(mval))
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	return True

#
def updateExtHumidity(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]+"-hum"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit<0: # if device does not exists in Domoticz, than create it
		devparams = { "Name" : unitname, "Unit": iUnit, "TypeName" :"Humidity", "Used":0, "DeviceID" : unitname}
		iUnit = adddevice(**devparams)
	if iUnit<0:
		return False
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	try:
		Devices[iUnit].Update(nValue=int(mval),sValue=str(mval))
	except Exception as e:
		Domoticz.Debug(str(e))
		return False
	return True

#
def updateAdc(mqttpath, message):
	unitname = mqttpath[1]+"-"+mqttpath[3]+"-adc"
	unitname = unitname.strip()
	iUnit = searchdevice(unitname)
	if iUnit<0: # if device does not exists in Domoticz, than create it
		devparams = { "Name" : unitname, "Unit": iUnit, "Type": 243, "Subtype": 8, "Used":1, "DeviceID" : unitname}
		iUnit = adddevice(**devparams)
	if iUnit<0:
		return False
	try:
		mval = float(message)
	except:
		mval = str(message).strip()
	try:
		Devices[iUnit].Update(nValue=0,sValue=str(mval))
		return True
	except Exception as e:
		Domoticz.Debug(str(e))
	return True

###
#
def updateGen2Device(mqttpath, original_message, powerReadSetting=0, absPowerSetting=0):
	# Handle RPC status notifications over MQTT
	#
	if (len(mqttpath)==4) and (mqttpath[2] == "events") and (mqttpath[3] == "rpc"):
		# Check if we're dealing with a Shelly H&T
		#
		if original_message['method'] == 'NotifyFullStatus' and 'ht_ui' in original_message['params']:
			sensorName = mqttpath[1]+'-sensor'
			humidity = float(original_message['params']['humidity:0']['rh'])
			temperature = float(original_message['params']['temperature:0']['tC'])
			battery_percent = float(original_message['params']['devicepower:0']['battery']['percent'])
			updateGen2HandT(sensorName, humidity, temperature, battery_percent)
		##
		elif "params" in original_message:
			for param, paramValues in original_message['params'].items():
				Domoticz.Debug('Gen2:updateGen2Device :: Got param \'%s\' with values \'%s\' for path \'%s\'.' % (param, paramValues, mqttpath[1]))
				#
				if param.startswith('switch:'):
					for paramKey, paramValue in paramValues.items():
						
						switchName = mqttpath[1]+'-'+str(paramValues['id'])
						Domoticz.Debug('Gen2:updateGen2Device :: Got paramKey \'%s\' with paramValue \'%s\' (powerReadSetting: %s) for path \'%s\'.' % (paramKey, paramValue, powerReadSetting, mqttpath[1]))
					
						# Only continue for valid paramKeys
						if not paramKey in ['output', 'apower', 'current', 'pf', 'voltage', 'aenergy'] or ( paramKey == 'apower' and powerReadSetting == 0):
							continue
						
						if paramKey == 'apower' or paramKey == 'aenergy':
							switchName += '-total'
						elif paramKey == 'current':
							switchName += '-current'
						elif paramKey == 'pf':
							switchName += '-pf'
						elif paramKey == 'voltage':
							switchName += '-voltage'
						updateGen2Switch(switchName, paramKey, paramValue, powerReadSetting, absPowerSetting)

						if paramKey == 'apower':
							unitName = mqttpath[1]+'-'+str(paramValues['id'])+'-energy'
							updateGen2Switch(unitName, '_energy', paramValue, powerReadSetting, absPowerSetting)

				#
				elif param.startswith('input:'):
					for paramKey, paramValue in paramValues.items():

						if paramKey == 'state':
							inputName = mqttpath[1]+"-"+str(paramValues['id'])+'-input'
							updateGen2Input(inputName, paramKey, paramValue)

				#
				elif param == 'events':
					for event in paramValues:
						if 'component' in event and 'event' in event:
							if event['component'].startswith('input:'):
								if not event['event'] in ['single_push', 'double_push', 'triple_push', 'long_push']:
									continue
								
								inputName = mqttpath[1]+'-'+str(event['id'])+'-input_event'
								updateGen2Input(inputName, 'event', event['event'])

###
#
def updateGen2Switch(switchName, paramKey, paramValue, powerReadSetting, absPowerSetting):

	Domoticz.Debug('Gen2:updateGen2Switch :: Handle paramKey: \'%s\' with paramValue \'%s\' for switch \'%s\'' % (paramKey, paramValue, switchName))
	
	iUnit = searchdevice(switchName)
	if iUnit<0 and str(Settings['AcceptNewHardware'])!='0': # if device does not exists in Domoticz, than create it
		try:
			if paramKey == 'output':
				devparams = {
					'Name' : switchName,
					'TypeName' :'Switch',
					'Used':1,
					'DeviceID' : switchName
				}
				iUnit = adddevice(**devparams)
			elif paramKey in ['apower', 'aenergy']:
				
				imageId = 0
				if 'ShellyNGMQTT-kWhMeter' in Images:
					imageId = Images["ShellyNGMQTT-kWhMeter"].ID

				devparams = {
					'Name' : switchName,
					'Type': 243,
					'Subtype': 29,
					'Used': 0,
					'DeviceID': switchName,
					'Image': imageId
				}
				iUnit = adddevice(**devparams)
			elif paramKey == '_energy':
				devparams = {
					'Name': switchName,
					'Type': 248,
					'Subtype': 1,
					'Used': 1,
					'DeviceID' : switchName
				}
				iUnit = adddevice(**devparams)

			elif paramKey == 'current':
				devparams = {
					'Name' : switchName,
					'Type': 243,
					'Subtype': 23,
					'Used': 0,
					'DeviceID' : switchName
				}
				iUnit = adddevice(**devparams)
			elif paramKey == 'pf':
				devparams = {
					'Name' : switchName,
					'Type': 243,
					'Subtype': 31,
					'Used': 0,
					'DeviceID' : switchName
				}
				iUnit = adddevice(**devparams)
			elif paramKey == 'voltage':
				devparams = {
					'Name' : switchName,
					'Type': 243,
					'Subtype': 31,
					'Used': 0,
					'DeviceID' : switchName
				}
				iUnit = adddevice(**devparams)

		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	
	if iUnit<0:
		return False
	
	#
	if paramKey == 'output':
			
		try:
			paramValue = str(paramValue).strip().lower()

			if (paramValue == 'true'): # set device status if needed
				Domoticz.Debug('Gen2:updateGen2Switch :: Update switch \'%s\' - nValue: 1, sValue: \'%s\' - from paramKey \'%s\'' % (Devices[iUnit].Name, 'On', paramKey))
				Devices[iUnit].Update(nValue=1,sValue="On")
			else:
				Domoticz.Debug('Gen2:updateGen2Switch :: Update switch \'%s\' - nValue: 0, sValue: \'%s\' - from paramKey \'%s\'' % (Devices[iUnit].Name, 'Off', paramKey))
				Devices[iUnit].Update(nValue=0,sValue="Off")
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	
	elif paramKey in ['voltage','current','pf', '_energy']:
			
		try:
			mval = float(str(paramValue).strip())
		except:
			mval = str(paramValue).strip()

		sval = str(mval)
		try:
			if sval != '':

				updateValue = True

				if not sval.startswith('0'): 
					try:
						format = '%Y-%m-%d %H:%M:%S'
						# WORKAROUND:
						# TypeError attribute of type 'NoneType' is not callable
						# Python bug workaround
						try:
							lastupdate = datetime.strptime( Devices[iUnit].LastUpdate , format)
						except TypeError:
							lastupdate = datetime(*(time.strptime( Devices[iUnit].LastUpdate , format)[0:6]))

						tdelta = datetime.now( ) - lastupdate
						updated = tdelta.seconds
					except Exception as e:
						Domoticz.Error(str(e))

					if (updated < 10):
						updateValue = False
				#
				if updateValue:
					Domoticz.Debug('Gen2:updateGen2Switch :: Update sensor \'%s\' -  sValue: \'%s\ - from paramKey \'%s\'' % (Devices[iUnit].Name, mval, paramKey))
					Devices[iUnit].Update(nValue=0,sValue=sval)
			#
			return True
		#
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	
	elif paramKey in ['apower','aenergy']:
			
		try:
			curval = Devices[iUnit].sValue
			prevdata = curval.split(";")
		except:
			prevdata = []
		if len(prevdata)<2:
			prevdata.append(0)
			prevdata.append(0)

		try:
			mval1 = float(str(prevdata[0]))
		except:
			mval1 = 0

		try:
			mval2 = float(str(prevdata[1]))
		except:
			mval2 = 0

		if paramKey == 'apower':
			try:
				mval1 = float(str(paramValue).strip())
				if absPowerSetting != 0: # activate ugly fix for solar cell negative input
					mval1 = abs(mval1)
			except:
				mval1 = str(paramValue).strip()
		elif paramKey == 'aenergy' and 'total' in paramValue:
			try:
				mval2 = float(str(paramValue['total']).strip())
				if absPowerSetting != 0: # activate ugly fix for solar cell negative input
					mval2 = abs(mval2)
			except:
				mval2 = str(paramValue['total']).strip()

		sval = ""
		if paramKey == 'apower' and powerReadSetting == 2:
			sval = str(mval1)+';'+str(mval2)
		elif paramKey == 'apower' and powerReadSetting == 1:
			sval = str(mval1)+';0'
		elif paramKey == 'aenergy' and powerReadSetting == 2:
			#try:
			#	mval2 = round((mval*0.017),4) # 10*Wh? or Watt-min??
			#except:
			#	mval2 = str(mval)
			# sval = str(mval1)+';'+str(mval2)
			sval = str(mval1)+';'+str(mval2)

		try:
			if sval != '':

				updateValue = True

				if paramKey == 'apower' and not sval.startswith('0.0;'): 
					try:
						format = '%Y-%m-%d %H:%M:%S'
						# WORKAROUND:
						# TypeError attribute of type 'NoneType' is not callable
						# Python bug workaround
						try:
							lastupdate = datetime.strptime( Devices[iUnit].LastUpdate , format)
						except TypeError:
							lastupdate = datetime(*(time.strptime( Devices[iUnit].LastUpdate , format)[0:6]))

						tdelta = datetime.now( ) - lastupdate
						updated = tdelta.seconds
					except Exception as e:
						Domoticz.Error(str(e))

					if (updated < 10):
						updateValue = False
				#
				if updateValue:
					Domoticz.Debug('Gen2:updateGen2Switch :: Update sensor \'%s\' - sValue: \'%s\' - from paramKey \'%s\'' % (Devices[iUnit].Name, sval, paramKey))
					Devices[iUnit].Update(nValue=0,sValue=str(sval))
			#
			return True
		#
		except Exception as e:
			Domoticz.Debug(str(e))
			return False

	# End of Gen2 Switch Handling
	return False

###
#
def updateGen2Input(inputName, paramKey, paramValue):

	Domoticz.Debug('Gen2:updateGen2Input :: Handle paramKey: \'%s\' with paramValue \'%s\' for input \'%s\'' % (paramKey, paramValue, inputName))

	iUnit = searchdevice(inputName)
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:

			imageId = 9 # Means 'Generic On/Off switch'
			if 'ShellyNGMQTT-Switch' in Images:
				imageId = Images["ShellyNGMQTT-Switch"].ID

			if paramKey == "state":
				devparams = {
					'Name': inputName,
					'TypeName': 'Switch',
					'Used': 0,
					'DeviceID' : inputName,
					'Image': imageId
				}
				iUnit = adddevice(**devparams)

			elif paramKey == 'event':
				
				devparams = {
					'Name': inputName,
					'TypeName': 'Selector Switch',
					'Used': 1 ,
					'DeviceID': inputName,
					'Image': imageId,
					'Options': {
						'LevelActions': '|||',
						'LevelNames': 'Off|Single|Double|Triple|Long',
						'LevelOffHidden': 'true',
						'SelectorStyle': '0'
					}
				}
				# Create the Domoticz device
				iUnit = adddevice( **devparams )

		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	
	if iUnit<0:
		return False

	#
	if paramKey == "state":
		try:
			paramValue = str(paramValue).strip().lower()

			if (paramValue == "true"): # set device status if needed
				Domoticz.Debug('Gen2:updateGen2Input :: Update input \'%s\' - nValue: 1, sValue: \'%s\'' % (Devices[iUnit].Name, 'On'))
				Devices[iUnit].Update(nValue=1,sValue="On")
			else:
				Domoticz.Debug('Gen2:updateGen2Input :: Update input \'%s\' - nValue: 0, sValue: \'%s\'' % (Devices[iUnit].Name, 'Off'))
				Devices[iUnit].Update(nValue=0,sValue="Off")
		except Exception as e:
			Domoticz.Debug(str(e))
			return False
		return True
	
	elif paramKey == "event":
		# Convert event to selector switch state
		events = {"single_push": 10, "double_push": 20, "triple_push": 30, "long_push": 40}
		case = events.get(paramValue , 0 ) # get event type
		if (int(Devices[iUnit].nValue) != int(case)):
			Domoticz.Debug("Gen2:updateGen2Input :: Update inputEvent '" + Devices[iUnit].Name + "' to '" + str(case) + "' (based on event '" + paramValue + "')")
			Devices[iUnit].Update(nValue=case,sValue=str(case))

	# End of Gen2 Input Handling
	return False

def updateGen2HandT(sensorName, humidity, temperature, batteryPercentage):

	Domoticz.Debug('Gen2:updateGen2Input :: Handle humidity: \'%s\', temperature: \'%s\', batteryPercentage: \'%s\' for H&T sensor \'%s\'' % (humidity, temperature, batteryPercentage, sensorName))

	iUnit = searchdevice(sensorName)
	if iUnit<0 and str(Settings["AcceptNewHardware"])!="0": # if device does not exists in Domoticz, than create it
		try:
			devparams = {
				"Name" : sensorName,
				"TypeName" : "Temp+Hum",
				"Used" : 1 ,
				"DeviceID" : sensorName,
			}
			# Create the Domoticz device
			iUnit = adddevice( **devparams )

		except Exception as e:
			Domoticz.Debug(str(e))
			return False
	
	if iUnit<0:
		return False

	if int(humidity) >= 50 and int(humidity) <= 70:
		hstat = 1
	elif int(humidity) < 40:
		hstat = 2
	elif int(humidity) > 70:
		hstat = 3
	sval = str(temperature) + ";" + str(humidity) + ";" + str(hstat)

	try:
		Devices[iUnit].Update(nValue=0, sValue=str(sval), BatteryLevel=int(batteryPercentage))
		return True
	except Exception as e:
		Domoticz.Debug(str(e))

	# End of Gen2 Input Handling
	return False

###
#
def getGen2DeviceCommand(unitName, src, command, level, color):
	Domoticz.Debug("Gen2:controlGen2Device :: Create command for unitName '" + str(unitName) + "' -  command '" + str(command) + "' - level '" + str(level) + "' - Color '" + str(color) + "'")

	unitNameParts = unitName.split('-')
	try:
		switchId = int(unitNameParts[2].strip()) # get channel if applicable
	except:
		switchId = -1

	command = str(command).strip().lower()
		
	# Check if is it a normal relay
	#
	if switchId in range(0,4) and len(unitNameParts)==3: 
		if command == "on" or command == "off":
			return {
				"id": 1,
				"source": src,
				"method": "Switch.Set",
				"params": {
					"id": switchId,
					"on": (command == "on")
				}
			}

	return None