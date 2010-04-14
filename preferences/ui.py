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
import types

class PreferencesEditor :
	""" Userland Dbus Event Listener : Preferences Application """
	
	def __init__(self,parent,gconf):
		self.parent = parent
		
		self.builder = gtk.Builder()
		self.builder.add_from_file("preferences/editor.glade")

		self.editor = self.builder.get_object("userland-dbus-event-manager-preferences")
		#self.editor.connect_signals( self )
		
		self.builder.get_object("Preferences_Main_Header_Label").set_text(self.parent.info["name"])
		self.builder.get_object("Preferences_Main_Header_Icon").set_from_file("./userland-dbus-event-manager.png")

		self.builder.get_object("General_Scroller").add( MultiDataColumnList(self.parent.config.entries()).render() )

		for page in self.parent.config.list_dirs() :
			page = self.key_name_from_path(page)

			obj = self.builder.get_object( "%s_List_Scroller" % page.capitalize() )

			tree = FolderList( self.dir_to_dict(page) ).render()

			print "Rendering : %s" % page
			obj.add( tree )

		print "Preferences Application Ready"
		self.editor.show_all()

	def dir_to_dict(self, path) :
		children = self.parent.config.list_dirs(path)
		print "Building tree data for : %s" % path
		print "\t%s children" % len(children)

		if len(children) > 0 :
			output = {}
			for branch in children:
				branch_name = self.key_name_from_path(branch)
				output[branch] = self.dir_to_dict(path +"/"+ branch_name )
		else :
			output = None
		
		return output

	def key_name_from_path (self,path):
		""" Function doc """
		return path[ path.rfind("/")+1 : ]
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

class FolderList :
	
	def __init__(self, data) :
		self.tree_store = gtk.TreeStore( types.StringType )
		self.walk_tree(self.tree_store, data, None)

	def trim_path (self,path):
		""" Function doc """
		return path[ path.rfind("/")+1 : ]

	def walk_tree(self, store, data, parent) :

		for item in data :
			name = self.trim_path( str(item) )
			row = store.append(None, [ name ] )
			if data[item] and len( data[item] ) > 0 :
				self.walk_tree(store, data[item], row)
		
	def render(self):
		""" Function doc """
		tree_view = gtk.TreeView(self.tree_store)

		tree_cell_render = gtk.CellRendererText()

		tree_column_name = gtk.TreeViewColumn('Name')
		tree_column_name.pack_start(tree_cell_render, True)
		tree_column_name.add_attribute(tree_cell_render, 'text', 0)
		tree_column_name.set_sort_column_id(0)

		tree_view.append_column(tree_column_name)

		tree_view.set_search_column(0)
		tree_view.set_enable_search(True)
		tree_view.set_reorderable(True)
		
		return tree_view


class MultiDataColumnList:
	def __init__(self, data):
		self.data = data
		
	def render(self):
		list_store = gtk.ListStore(types.StringType,object)
		for item in self.data :
			row = list_store.append([ item, self.data[item] ])

		self.tree_view = gtk.TreeView(list_store)


		self.column_name = gtk.TreeViewColumn('Name')
		self.column_name_render = gtk.CellRendererText()
		self.column_name.pack_start(self.column_name_render, True)
		self.column_name.add_attribute(self.column_name_render, 'text', 0)
		self.column_name.set_sort_column_id(0)

		self.tree_view.append_column(self.column_name)


		self.column_value = gtk.TreeViewColumn('Value')
		self.text = r = gtk.CellRendererText()
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.text, self.select_data)

		self.toggle = r = gtk.CellRendererToggle()
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.toggle, self.select_data)
		
		self.pixbuf = r = gtk.CellRendererPixbuf()
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.pixbuf, self.select_data)

		self.tree_view.append_column(self.column_value)
		
		return self.tree_view

	def trim_path (self,path):
		""" Function doc """
		return path[ path.rfind("/")+1 : ]

	def select_data(self, col, cell, model, iter):
		data = model[iter][1]
		#print "select_data : "
		#print data, col, cell, model ,iter

		if isinstance(data, bool):
			self.toggle.props.visible = True
			self.toggle.props.active = data
			self.toggle.set_property('activatable', True)
			self.toggle.connect('toggled', self.callback_CellRendererToggle, (model, 1))
		else :
			self.toggle.props.visible = False

		if isinstance(data, gtk.gdk.Pixbuf):
			self.pixbuf.props.visible = True
			self.pixbuf.props.pixbuf = data
		else :
			self.pixbuf.props.visible = False

		if isinstance(data, str):
			self.text.props.visible=True
			self.text.props.text = data
			self.text.set_property('editable', True)
			self.text.connect('edited', self.callback_CellRendererText, (model, 1))
		else :
			self.text.props.visible=False

	def callback_CellRendererToggle (self, cell, path, user_data):
		""" Function doc """
		model, column = user_data
		model[path][column] = not model[path][column]
		return
		
	def callback_CellRendererText (self, cell, path, user_data):
		""" Function doc """
		model, column = user_data
		model[path][column] = new_text
		return	
