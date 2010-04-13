"""
 * manager.py
 * This file is part of Userland-Dbus-Event-Manager
 *
 * Copyright (C) 2010 - Zenobius Jiricek
 *
 * Userland-Dbus-Event-Manager is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Userland-Dbus-Event-Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Userland-Dbus-Event-Manager; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, 
 * Boston, MA  02110-1301  USA
"""

import pygtk
pygtk.require( '2.0' )
import gtk
import pynotify
import os
import sys
import dbus
import gobject
import gconf
from dbus.mainloop.glib import DBusGMainLoop
from string import Template

from trayicon.ui import TrayIcon
from preferences.config import ConfigManager, GconfManager
from preferences.ui import PreferencesEditor

from eventmanager import   APP_NAME, APP_NAME_SHORT, APP_DESCRIPTION, APP_VERSION, APP_AUTHORS, APP_HOMEPAGE, APP_LICENSE


class userland_dbus_manager:

	def __init__( self, settings = None ):

		self.State = "Initialising"
		self.info = {
			"name"				: APP_NAME,
			"short-name"	: APP_NAME_SHORT,
			"version"			: APP_VERSION,
			"copyright"		: APP_LICENSE,
			"comments"		: APP_DESCRIPTION,
			"homepage"		: APP_HOMEPAGE,
			"authors"			: APP_AUTHORS,
		}

		self.gconf_schema = {
			"use_notify_send"	: False,
			"send_signals_over_network" : False,
			"actions" : {
				"actions" : {
					"lid-opened"			: "bin/laptop-lid-opened.sh",			# paths are relative to $HOME
					"lid-closed"			: "bin/laptop-lid-closed.sh",
				},
				"groups" : {
					"lid-is-opened"		: ["lid-opened"],
				}
			},
			"objects" : {
				"session" : {},
				"system" : {
					"laptop_lid" : {
						"name"	: "Laptop Lid Open/Close",
						"interface" : "org.freedesktop.PowerKit",
						"dbus_path"	: "org/freedesktop/PowerKit",
						"object"		: "",
						"signals"		: {
							"open"	: {
								"name"	: "laptop lid opened",
								"requires" : "LAPTOP LID OPENED",
								"actions"	: ["lid-opened"],
							},
							"close"	: {
								"name"	: "laptop lid closed",
								"requires" : "LAPTOP LID CLOSED",
								"actions"	: ["lid-closed"],
							}
							
						}
					} 
				}
			}
		}
		self.Strings = {
			"NoEventScript" : {
				"icon"	: gtk.STOCK_DIALOG_WARNING,
				"title" : "No Event Script",
				"body" : "${object} has ${event}, you need to specify/create an event script for this." # "<object-name> has <event>(ed)"
			},
			"ObjectEvent" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "${object} : ${event}", 																				# <object-name> <event>(ed)
				"body" : "${object} : ${event}, executing user event script : %s"				# <object-name> <event> <script-path>
			},
			"HalObjectFound" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "${object} Hal Address", 																# <object-name>
				"body" : "found ${object} @ ${path} "																	# <object-name> <object-hal-address>
			},
			"HalObjectNotFound" : {
				"icon"	: gtk.STOCK_DIALOG_WARNING,
				"title" : "No ${object} HAL entry", 															# <object-name>
				"body" : "Could not find the hal-dbus address of ${object}."			# <object-name>
			},
			"AddingDbusHook" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "Adding DBUS Listener",
				"body" : "Listening for events from : ${object} @ ${path}"																	# <object-name> <object-hal-address>
			},
			"RemovingDbusHook" : {
				"icon"	: gtk.STOCK_DIALOG_INFO,
				"title" : "Removing DBUS Listener",
				"body" : "Stopped listening for events from : ${object} @ ${path}"																	# <object-name> <object-hal-address>
			},
			"Paused" : {
				"icon"	: gtk.STOCK_MEDIA_PAUSE,
				"title" : "Paused",
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
		self.dbusObjects = {}
		self.notification_queue = []
		self.MessageQue = []
		self.HookedObjects = []

		self.loop = gobject.MainLoop()
		self.notification_tray = TrayIcon( self )

		self.initialise_config()
		
		self.sniff_start()
		gtk.main()

	def initialise_config(self):

		self.config = GconfManager( "/apps/%s" % self.info['short-name'])

		print self.config.list_dirs()

		if not self.config.get_bool("use_notify_send") :
			self.config.set_bool("use_notify_send", True)

		if not "system" in self.config.list_dirs() :
			self.config.set_int("objects/system/count", 0)

		if not "session" in self.config.list_dirs() :
			self.config.set_int("objects/session/count", 0)
			
		if not "actions" in self.config.list_dirs("actions") :
			self.config.set_int("actions/actions/count", 0)

		if not "groups" in self.config.list_dirs("actions") :
			self.config.set_int("actions/groups/count", 0)

		print self.config.entries()
		
	def show_preferences_dialog (self):
		""" Function doc """
		self.config_editor = PreferencesEditor(self,gconf)
		
	def sniff_start( self ) :
		"""
			Starts the sniffing/listening process by stepping through the list of desired objects and registering them
		"""
		print "sniff_start"
		objects = self.dbusObjects.keys()
		objects.sort()

		for name in objects:
			self.add_dbus_hook( name, self.dbusObjects[name] )

		if len( self.HookedObjects ) > 0 :
			self.resume()
		else :
			self.pause( {"reason" : "No listeners registered."} )

	def sniff_stop( self ):
		"""
			Stops the listening process by unregistering any registered signals
		"""
		for name in self.HookedObjects :
			self.del_dbus_hook( name )
			self.HookedObjects.remove( name )

		self.loop.quit()

	def add_dbus_hook( self, name, object ) :
		"""
			Registers an object hook
				name		: name of the thing to listen for, as known by the user
				object	: dictionary of key/values that specify the details of the thing to listen for
					object["Bus"]				: [REQUIRED] use the system or session bus
					object["Interface"] : [REQUIRED] dbus interface name
					object["Path"]			: [REQUIRED] dbus path
					object["Signal"]		: dbus signal to specifically listen for, if left out all signals will trigger the callback
		"""

		bus = self.bus[object["Bus"]]
		if "DBUS_Search" in object :
			object["Path"] = self.find_dbus_object( bus, name, object["DBUS_Search"]["key"], object["DBUS_Search"]["value"] )

		if object["Path"] != None :
			self.message( "AddingDbusHook", {"object": name, "path" : object["Path"]} )
			try :
				bus.add_signal_receiver( 
					self.callback_event_proxy,
					dbus_interface = object["Interface"],
					path = object["Path"] )
				self.HookedObjects.append( name )
			except AttributeError as error :
				self.ErrorMessage( "DBUS register : %s" % error )

	def del_dbus_hook( self, name ) :
		object = self.dbusObjects[name]
		self.bus[object["Bus"]]
		self.message( "RemovingDbusHook", {"object": name, "path" : object["Path"]} )
		try :
			bus.remove_signal_receiver( 
				self.callback_event_proxy,
				dbus_interface = object["Interface"],
				path = object["Path"] )
		except AttributeError as error :
			self.ErrorMessage( "DBUS unregister : %s" % error )

	def find_dbus_object( self, bus, name, key, value ) :
		print bus
		print "Looking for %s : %s=%s" % ( name, key, value )
		obj = bus.get_object( "org.freedesktop.Hal", "/org/freedesktop/Hal/Manager" )
		iface = dbus.Interface( obj, "org.freedesktop.Hal.Manager" )
		output = iface.FindDeviceStringMatch( key, value )
		print output

		if len( output ) > 0:
			self.message( "HalObjectFound", {"object":name, "path":output[0]} )
			return output[0]
		else :
			self.message( "HalObjectNotFound", {"object":name} )
			return None

	def callback_event_proxy( self, message, sender = None, name = None ):
		object = self.Objects[Object]
		ObjectStateFile = open( object["ACPI"], 'r' ).read()
		ObjectScripts = object["Scripts"]
		ObjectStates = object["States"]

		if ObjectStateFile.count( ObjectStates["Connect"].lower() ) > 0 :
			Script = ObjectScripts[ObjectStates["Connect"]]
			self.message( "ObjectEvent", {"object":Name, "path":Script["path"]} )
			os.system( 'sh %s' % Script["path"] )
		elif ObjectStateFile.count( ObjectStates["Disconnect"].lower() ) > 0 :
			Script = ObjectScripts[ObjectStates["Disconnect"]]
			self.message( "ObjectDisconnect", {"object":Name, "path":Script["path"]} )
			os.system( 'sh %s' % Script["path"] )

	def pause( self, reason ):
			self.State = "Paused"
			self.message( "Paused", {"reason":reason} )
			self.notification_tray.update()
			self.sniff_stop()

	def resume( self ):
		print "%s waking up" % self
		try:
			self.State = "Listening"
			self.notification_tray.update()
			self.message( "Listening" )
			self.sniff_start()
		except KeyboardInterrupt:
			self.quit( "Keyboard Interupt" )

	def quit( self, reason = None ):
		if reason != None:
			reason = "\n Reason : %s " % reason
		else :
			reason = ""

		self.message( "Quitting", {"reason" : reason} )
		self.sniff_stop()
		sys.exit( 0 )

	def message( self, key, template_data = None ) :
		try :
			if self.Strings and self.Strings[key] :
				locale_string = self.Strings[key]
				if template_data != None :
					title = Template( locale_string["title"] ).substitute( template_data )
					body = Template( locale_string["body"] ).substitute( template_data )
				else :
					title = locale_string["title"]
					body = locale_string["body"]
				self.notification( locale_string["icon"], title, body )
			else :
				self.ErrorMessage( "self.Strings['%s'] not found." % key )
		except AttributeError as error :
			self.ErrorMessage( "Message Templating : %s\n%s" % ( key, error ) )

	def notification( self, icon = None, title = None, message = None ):
		if not self.config.get_bool("use_libNotify") and pynotify.init( "Images Test" ) :
			helper = gtk.Button()
			bubble = pynotify.Notification( title, message )

			if( icon != None ) :
				bubble.set_icon_from_pixbuf( helper.render_icon( icon, gtk.ICON_SIZE_DIALOG ) )

			try :
				bubble.show()
				#self.notification_queue[len(self.notification_queue)] = bubble
				return bubble
			except AttributeError as error :
				self.ErrorMessage( "libNotify : %s\n%s" % ( key, error ) )

		else :
			print "%s : %s << %s >>" % ( self.info["name"], title, message )

	def ErrorMessage( self, msg ):
		print "%s [Error] : %s" % ( self.info["name"], msg )

	def help( self, keyword = None ):
		print self.info["name"]
		print """ """
	
if __name__ == "__main__":
	print "This script can't be run by itself.'"
