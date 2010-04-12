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
import gtk.glade
import gconf


class PreferencesEditor :
	""" Userland Dbus Event Listener : Preferences Application """
	
	def __init__(self,parent,gconf):
		self.parent = parent
		
		self.builder = gtk.Builder()
		self.builder.add_from_file("preferences/editor.glade")

		self.editor = self.builder.get_object("userland-dbus-event-manager-preferences")
		#self.editor.connect_signals( self )
		
		self.AppHeader = self.builder.get_object("Preferences_Main_Header_Label")
		self.AppHeader.set_text(self.parent.info["name"])

		self.ObjectsList_GenerateWidgets()
		
		print "Preferences Application Ready"
		self.editor.show_all()

#
## User Interface : Content Generators
### generate widgets based on current config settings, things like a list of objects or action-groups
	def ObjectsList_getNames(self):
		output = []
		for object in self.parent.config['objects'] :
			output.append(object)
			
		return output
		
	def ObjectsList_GenerateWidgets (self):
		""" Function doc """
		objects = self.parent.config["objects"]
		self.Objects_List = {
			"Session" : {
				"Area" 		: self.builder.get_object("Objects_Session_List_Scroller"),
				"Tree"		: None,
				"Column"	: gtk.TreeViewColumn('Name'),
				"Store"		: gtk.TreeStore(str),
				"Cell"		: gtk.CellRendererText(),
			},
			"System" : {
				"Area"	: self.builder.get_object("Objects_System_List_Scroller"),
				"Tree"	: None,
				"Column"	: gtk.TreeViewColumn('Name'),
				"Store"	: gtk.TreeStore(str),
				"Cell"		: gtk.CellRendererText(),
			}
		}

		for bus_group in objects :
			# So far this holds : System & Session. Created for possible future types of DBUS buses
			Page = self.Objects_List[bus_group]
			
			for object in objects[bus_group] :
				Row = Page["Store"].append(None, ['%s' % object])

			Page["Tree"] = gtk.TreeView(Page["Store"]) #ObjectsList_View
			Page["Tree"].append_column(Page["Column"])
			Page["Column"].pack_start(Page["Cell"], True)
			Page["Column"].add_attribute(Page["Cell"], 'text', 0)
			Page["Tree"].set_search_column(0)
			Page["Column"].set_sort_column_id(0)
			Page["Tree"].set_reorderable(True)
			Page["Area"].add(Page["Tree"])
		

#
## User Interface : Control Handlers
	def ui_close(self):
		"""
		Called when the cancel/close button is clicked.
		"""
		self.editor.quit()
		
	def ui_save_changes(self) :
		"""
		Called when the 'apply' button is clicked.
		"""

	def ui_help(self,key) :
		"""
		Called when a 'help' button is clicked.
		Each help button will pass a key which relates to a section in the help file.
		"""
