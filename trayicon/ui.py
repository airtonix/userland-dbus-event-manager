"""
 * ui.py
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
pygtk.require('2.0')

import gtk

class TrayIcon():
	
	def __init__(self,parent=None):
		self.parent = parent
		self.db = {
			"Icons" : {
				"Paused" 				: gtk.STOCK_MEDIA_PAUSE,
				"Listening"			:	gtk.STOCK_QUIT,
				"Initialising"	:	gtk.STOCK_REFRESH,
				"AddingHook"		: gtk.STOCK_QUIT,
				"CatchingEvent"	: gtk.STOCK_QUIT,
				"Orphan"				: gtk.STOCK_DIALOG_ERROR
			},
			"Menu" : {
				"items" : (
					( "pause",
						gtk.STOCK_MEDIA_PAUSE,
						self.menu_event,                
						"Toggle Monitoring"),
					( "preferences",
						gtk.STOCK_PREFERENCES,
						self.menu_event,                
						"Preferences" ),
					( "quit",
						gtk.STOCK_QUIT,    # name, icon, callback, accelerator
						self.menu_event,                
						"Quit" ),
					"-",
					( "help",
						gtk.STOCK_HELP,        
						self.menu_event,                
						"Help Documentation Viewer"),
					( "about",
						gtk.STOCK_ABOUT,
						self.menu_event,                
						"About" ),
					
				)
			}
		}
		self.tray = self.render()

	def quit(self,reason=None) :
		if self.parent :
			self.parent.quit(reason)
		else :
			gtk.main_quit()
		
## EVENTS
	def pause(self,reason=None) :
		"""
			Pause monitoring >> Trigger to parent
				reason : template data to mention why.
		"""
		if self.parent :
			print "parent found, interupting"
			self.parent.pause(reason)
		else :
			print "would pause, but no parent to interupt."
		
	def resume(self) :
		"""
			Pause monitoring >> Trigger to parent
		"""
		if self.parent :
			print "parent found, waking up"
			self.parent.resume()
		else :
			print "would resume, but no parent to wake up."
		
	def on_right_click(self, icon, event_button, event_time):
		self.popup_menu(event_button, event_time, icon)
			
	def on_left_click(self, *args):
		state = self.get_parent_state()
		if state == "Paused" :
			self.resume()
		elif state == "Listening" : 
			self.pause({"reason":"User Click"})
		else :
			print "Un-prepared parent state : %s " % state

	def menu_event(self, widget, event, data = None):
		print ("Notification Tray Menu Event")
		#print event
		getattr(self, "menu_item_%s" % widget.get_name(), None)()

## UI DRAWING
#
# Trayicon
	def render(self):
		icon = gtk.StatusIcon()
		icon.connect('popup-menu', self.on_right_click)
		icon.connect('activate', self.on_left_click)
		self.tray = icon
		
		self.update()
		print "Tray Icon Ready"
		return icon
		
	def update(self):
		icons = self.db["Icons"]
		self.tray.set_from_stock(icons[self.get_parent_state()])

	def get_parent_state(self) :
		if self.parent and self.parent.State :
			state = self.parent.State
		else :
			state = "Orphan"
		return state
		
#
# Trayicon Menu
	def popup_menu(self, event_button, event_time, icon):
		menu = gtk.Menu()
		db = self.db["Menu"]
		
		for item in db["items"] :
			if not item == "-" :
				print("%s \t: %s, %s") % (item[0], item[1], item[2])
				menuItem = gtk.ImageMenuItem(item[1])
				menuItem.set_name(item[0])
				menuItem.connect("button-press-event", item[2], icon)
			else :
				menuItem = gtk.SeparatorMenuItem()
				
			menuItem.show()
			menu.append(menuItem)

		menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)

#
# Trayicon Menu > About Window
	def  show_about_dialog(self, widget):
		if self.parent and self.parent.info :
			info = self.parent.info
			about_dialog = gtk.AboutDialog()
			about_dialog.set_destroy_with_parent (True)
			about_dialog.set_icon_name (info["name"])
			about_dialog.set_name(info["name"])
			about_dialog.set_version(info["version"])
			about_dialog.set_copyright(info["copyright"])
			about_dialog.set_website(info["homepage"])
			about_dialog.set_comments(info["comments"])
			about_dialog.set_authors(info["authors"])

			about_dialog.run()
			about_dialog.destroy()
		else:
			raise "Can't get parent info"
			 
	def show_preferences_dialog(self, *args):
		"""
			Render preferences dialog window :
				TODO :
					create :
							+ network interface selector
							+ colour selector
		"""
 		self.parent.show_preferences_dialog()
 		
## UI INTERFACE HANDLERS
#
# Trayicon Menu > About
	def menu_item_about(self):
		self.show_about_dialog(self.tray)
#
# Trayicon Menu > Quit
	def menu_item_quit(self):
		self.quit()
#
# Trayicon Menu > Pause
	def menu_item_pause(self):
		self.pause()
#
# Trayicon Menu > Preferences
	def menu_item_preferences(self):
		self.show_preferences_dialog(self.tray)
#
# Trayicon Menu > Help
	def menu_item_help(self):
		self.show_help_dialog()

if __name__ == "__main__":
	## This is here to provide the means to test this module.
	TrayIcon()
	gtk.main()
