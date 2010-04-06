#        Project Name : Userland Dbus Event Proxy
# Program Description : 
#         Designed By : Zenobius Jiricek
#          Created On : 2010-04-06
#          Created By : Zenobius Jiricek
#      Version Number :
#      Known Problems : 

import pygtk
pygtk.require('2.0')
import gtk

class userland_dbus_manager_preferences :
	""" Userland Dbus Event Listener : Preferences Application """
	def __init__(self,parent):
		print "Preferences Application Ready"
		self.parent = parent
