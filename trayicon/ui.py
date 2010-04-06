#        Project Name : 
# Program Description : 
#         Designed By : Zenobius Jiricek
#          Created On : 2010-04-06
#          Created By : Zenobius Jiricek
#      Version Number :
#      Known Problems : 

import pygtk
pygtk.require('2.0')
import gtk

class userland_dbus_manager_trayicon :
	""" Userland Dbus Event Listener : Notification Tray """
	
	def __init__(self, parent) :
		self.parent = parent
		self.menu = {
			"items" : (
				( "quit", gtk.STOCK_QUIT,    # name, icon, callback, accelerator
					self.menu_event,                
					"Quit DBUS Event Listener" ),
				( "pause", gtk.STOCK_MEDIA_PAUSE,
					self.menu_event,                
					"Pause Event Listeners"),
				( "help", gtk.STOCK_HELP,        
					self.menu_event,                
					"Help Documentation Viewer"),
				( "about", None,
					self.menu_event,                
					"About" ),
				( "preferences", gtk.STOCK_PREFERENCES,
					self.menu_event,                
					"Preferences" )
			)
		}
		self.ui = gtk.UIManager()
		self.icon = self.render()
		
	def trayIcon_onRightClick(self, icon, event_button, event_time):
			self.popup_menu(event_button, event_time, icon)
			
	def trayIcon_onLeftClick(self, *args):
		IsPaused = self.parent.State == "Paused"
		if IsPaused :
			self.parent.resume()
		else : 
			self.parent.pause({"reason":"User Click"})
		
	def help (self,keyword=None):
		""" Function help
			self 	: object, this class
			keyword	: string, word to search for in the help documentation
			 
			opens help documentation, and searches for 'keyword' if supplied
		"""
		
	def preferences(self,key=None):
		self.parent.preferences_application.show(key)

	def icon_update(self):
		self.icon.set_from_stock(self.parent.Icons[self.parent.State])

	def quit(self):
		self.parent.quit("Requested by user")

	def menu_event(self, widget, event, data = None):
		print ("Notification Tray Menu Event")
		#print event
		getattr(self, widget.get_name(), None)()
		
	def popup_menu(self, event_button, event_time, icon):
		menu = gtk.Menu()

		for item in self.menu["items"] :
			print("%s \t: %s, %s") % (item[0], item[1], item[2])
			menuItem = gtk.ImageMenuItem(item[1])
			menuItem.show()
			menuItem.set_name(item[0])
			menuItem.connect("button-press-event", item[2], icon)
			menu.append(menuItem)

		menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)
		
	def render(self):
		icon = gtk.status_icon_new_from_stock(self.parent.Icons[self.parent.State])
		icon.connect('popup-menu', self.trayIcon_onRightClick)
		icon.connect('activate', self.trayIcon_onLeftClick)
		print "Tray Icon Ready"
		return icon

