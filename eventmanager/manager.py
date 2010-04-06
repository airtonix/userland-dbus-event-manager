#!/usr/bin/env python
"""
Userland Dbus Event Manager v0.01
Zenobius Jiricek, airtonix > ubuntuforums.org

 Description :
  A userland dbus event watcher that runs scripts for registered DBUS hook events.
  The important distinction here is that :
		+ scripts or commands are run as the user not root.
		+ the user navigates the dbus tree and selects DBUS signals (elements to hook and register)
		+ multiple scripts/commands can be assigned to each signal
 
 Dependancies : 
   pynotify, notify-osd, notifcation-daemon
      sudo apt-get install python-notify notify-osd notification-daemon

 Installation :
	Run setup.py
"""

import pygtk
pygtk.require('2.0')
import gtk
import pynotify
import os
import sys
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
from string import Template

from trayicon.ui import TrayIcon
from preferences.ui import userland_dbus_manager_preferences
from eventmanager import   APP_NAME, APP_DESCRIPTION, APP_VERSION, APP_AUTHORS, APP_HOMEPAGE, APP_LICENSE


class userland_dbus_manager:

	def __init__(self):
		
		self.name = APP_NAME
		self.notifications = True
		self.notification_queue = ()
		
		self.loop = gobject.MainLoop()
		self.bus = dbus.SystemBus()
		self.State="Initialising"
		
		self.dbusObjects = {
			"Laptop Lid" : {
				"Path"				: None,																	# REQUIRED : None means search for it
				"DBUS_Search"	: {
					"key"			: "info.product",
					"value"		:	"lidswitch"
				},
				"Interface"		: "org.freedesktop.Hal.Device",					# REQUIRED : 
				"Signals"			:	"*",
				"ACPI"				: "/proc/acpi/button/lid/LID0/state",
				"States"			:	{
					"Connect"			: "Open",
					"Disconnect"	: "Close"
				},
				"Scripts"		: {																				# move this into a config database sometime.
					"Open" : {
						"exists": 0,
						"path": "%s/laptop-lid-opened.sh" % sys.path[0]
					},
					"Close" : {
						"exists": 0,
						"path": "%s/laptop-lid-closed.sh" % sys.path[0]
					}		
				}
			},
			"Storage Devices" : {
				"hooked"		: False,
				"Interface"		: "org.freedesktop.DeviceKit.Disks",
				"Path"				: "/org/freedesktop/DeviceKit/Disks",
				"Signals"			: ("DeviceAdded","DeviceRemoved"),
				"States"			:	{
					"Connect"			: "Added",
					"Disconnect"	: "Removed"
				},
				"Scripts"		: {																				# move this into a config database sometime.
					"Open" : {
						"exists": 0,
						"path": "%s/generic-event.sh" % sys.path[0]
					},
					"Close" : {
						"exists": 0,
						"path": "%s/generic-event.sh" % sys.path[0]
					}		
				}
			}
		}

		self.MessageQue={}
		self.HookedObjects = {}
		self.Strings = {
			"NoEventScript" : {
				"icon"	: gtk.STOCK_DIALOG_WARNING,
				"title" : "No Event Script", 
				"body" : "${object} has ${event}, you need to specify/create an event script for this." # "<object-name> has <event>(ed)"
			},
			"ObjectEvent" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "${object} : ${event}",																				# <object-name> <event>(ed)
				"body" : "${object} : ${event}, executing user event script : %s"				# <object-name> <event> <script-path>
			},
			"HalObjectFound" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "${object} Hal Address",																# <object-name>
				"body" : "found ${object} @ ${path} "																	# <object-name> <object-hal-address>
			},
			"HalObjectNotFound" : {
				"icon"	: gtk.STOCK_DIALOG_WARNING,
				"title" : "No ${object} HAL entry",															# <object-name>
				"body" : "Could not find the hal-dbus address of ${object}."			# <object-name>
			},
			"AddingDbusHook" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "Adding DBUS Listener",
				"body" : "Listening for events from : ${object} @ ${path}"																	# <object-name> <object-hal-address>
			},
			"Paused" : {
				"icon"	: gtk.STOCK_MEDIA_PAUSE,
				"title" : self.name,
				"body" : "Event listening paused\n\t(${reason}).\nLeft click tray icon again to resume."
			},
			"Quitting" : {
				"icon"	: gtk.STOCK_QUIT,
				"title" : "Quitting",
				"body"	: "Dbus Event Listener is shutting down. ${reason}"
			},
			"Listening" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title"	: "Listening",
				"body"	: "waiting for DBUS events..."
			},
			"Test" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title"	: "Testing ${reason}",
				"body"	: "testing for : ${reason}..."
			}
		}

		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.ui_render()
		self.sniff_start()
		gtk.main()
		
	def ui_render(self) :
		self.notification_tray = TrayIcon(self)
		self.preferences_application = userland_dbus_manager_preferences(self)
		
	def sniff_start(self) :
		print "sniff_start"
		objects = self.dbusObjects.keys()
		objects.sort()
		for name in objects:
			self.add_dbus_hook(name, self.dbusObjects[name])

		if len(self.HookedObjects) > 0 :
			self.resume()
		else :
			self.pause({"reason" : "No listeners registered."})
		
	def sniff_stop(self):
		""" TODO :
			iterate over registered hooks and 'unhook' them.
		"""
		self.loop.quit()

	def add_dbus_hook(self,name,object) :
		if "DBUS_Search" in object :
			object["Path"] = self.find_dbus_object(name, object["DBUS_Search"]["key"], object["DBUS_Search"]["value"])

		if object["Path"] != None :
			self.message("AddingDbusHook", {"object": name, "path" : object["Path"]} )
			try :
				hook = self.bus.add_signal_receiver(
					self.callback_event_proxy,
					dbus_interface=object["Interface"],
					path=object["Path"],
					name=name)
					
				self.HookedObjects.push({
					"Name"			: name,
					"Object"		: object,
					"Listener"	: hook
				})
			except :
				print "Error hooking dbus object"

				
	def callback_event_proxy(self, message, sender=None, name=None):
		object = self.Objects[Object]
		ObjectStateFile = open(object["ACPI"], 'r').read()
		ObjectScripts = object["Scripts"]
		ObjectStates = object["States"]
		
		if ObjectStateFile.count( ObjectStates["Connect"].lower() ) > 0 :
			Script = ObjectScripts[ObjectStates["Connect"]]
			self.message("ObjectEvent", {"object":Name, "path":Script["path"]} )
			os.system('sh %s' % Script["path"])
		elif ObjectStateFile.count( ObjectStates["Disconnect"].lower() ) > 0 :
			Script = ObjectScripts[ObjectStates["Disconnect"]]
			self.message("ObjectDisconnect",{"object":Name, "path":Script["path"]} )
			os.system('sh %s' % Script["path"])
	
	def find_dbus_object(self, name, key, value) :
		print "Looking for %s : %s=%s" % (name,key,value)
		obj = self.bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
		iface = dbus.Interface(obj, "org.freedesktop.Hal.Manager")
		output= iface.FindDeviceStringMatch(key, value)
		
		if len(output) > 0:
			self.message("HalObjectFound", {"object":name, "path":output[0]} )
			return output[0]
		else :
			self.message("HalObjectNotFound",{"object":name} )
			return None
						
	def pause(self,reason):
			self.State = "Paused"
			self.message("Paused",{"reason":reason})
			self.notification_tray.update()
			self.sniff_stop()
		
	def resume(self):
		print "%s waking up" % self
		try:
			self.State = "Listening"
			self.notification_tray.update()
			self.message("Listening")
			self.loop.run()
		except KeyboardInterrupt:
			self.quit("Keyboard Interupt")
			
	def quit(self,reason=None):
		if reason!=None:
			reason = "\n Reason : %s " % reason
		else :
			reason = ""
			
		self.message("Quitting", {"reason" : reason})
		self.sniff_stop()
		sys.exit(0)

	def get_config(self,key) : 
		return self.Preferences[key]["Value"]

	def set_config(self,key,value) : 
		output = ""
		self.Preferences[key]["OnBeforeChange"](self)
		self.Preferences[key]["Value"] = value
		self.Preferences[key]["OnAfterChange"](self)
		
	def message(self, key, template_data=None) :
		try : 
			locale_string = self.Strings[key]
			if template_data!=None :
				title = Template(locale_string["title"]).substitute(template_data)
				body = Template(locale_string["body"]).substitute(template_data)
			else :
				title = locale_string["title"]
				body = locale_string["body"]

			return self.notification(locale_string["icon"], title, body) 
		except :
			print "Error : Can't find self.String : %s" % key
			
	def notification(self, icon=None, title=None, message=None):
		if self.notifications == True and pynotify.init("Images Test") :
			helper = gtk.Button()
			bubble = pynotify.Notification(title,message)
			if(icon != None) :
				bubble.set_icon_from_pixbuf(helper.render_icon(icon, gtk.ICON_SIZE_DIALOG))
		else:
			self.notifications = False
			
		try :
			bubble.show()
			print "%s : %s << %s >>"  % (self.name, title, message)
			#self.notification_queue[len(self.notification_queue)] = bubble
			return bubble
		except : 
			print "%s : Failed to send notification" % self.name
		
		
	def help(self,keyword=None):
		print self.name 
		print """ """

if __name__ == "__main__":
	import userland_dbus_manager_trayicon
	import userland_dbus_manager_preferences
	userland_dbus_manager()

