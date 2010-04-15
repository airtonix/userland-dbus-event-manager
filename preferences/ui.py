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

		general_tree = MultiDataColumnList( self, self.parent.config.entries() )
		self.builder.get_object("General_Scroller").add( general_tree.render() )

		for page in self.parent.config.list_dirs() :
			page = self.key_name_from_path(page)
			page_name = page.capitalize()

			obj = self.builder.get_object( "%s_List_Scroller" % page_name )
			add_button = self.builder.get_object( "%s_List_Add" % page_name )
			remove_button = self.builder.get_object( "%s_List_Remove" % page_name )
			
			tree = FolderList( self, page, self.dir_to_dict(page) )

			# Set the add / remove actions for the lists
			add_button.connect('clicked', self.callback_list_add, (tree) )
			remove_button.connect('clicked', self.callback_list_add, (tree ) )

			print "Rendering : %s" % page
			obj.add( tree.render() )

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
#
## Callbacks
	def callback_list_add(self, widget, data) :
		""" Function Doc """
		target = data
		target.add_item().edit_item(new_item)
		
	def callback_list_remove(self, widget, data) :
		""" Function Doc """
		tree = data
		tree.remove_item()
		

class FolderList :
	
	def __init__(self, parent, name, data) :
		self.parent = parent
		self.name = name
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
		self.tree_view = gtk.TreeView(self.tree_store)

		tree_cell_render = gtk.CellRendererText()

		tree_column_name = gtk.TreeViewColumn('Name')
		tree_column_name.pack_start(tree_cell_render, True)
		tree_column_name.add_attribute(tree_cell_render, 'text', 0)
		tree_column_name.set_sort_column_id(0)

		self.tree_view.append_column(tree_column_name)
		self.tree_view.set_headers_visible(False)
		self.tree_view.set_search_column(0)
		self.tree_view.set_enable_search(True)

		self.tree_view.get_selection().set_select_function(self.callback_treeview_row_selected, (self.tree_view) )
		#tree_view.set_reorderable(True)
		
		return self.tree_view

	def add_item (self,data):
		""" Function doc """
		# need :
		# * the selected item <<< this will be the parent
		parent = data
		self.tree_store.append()
		return item

	def edit_item(self, item) :
		""" Function doc """
		
	def remove_item (self,data=None):
		""" Function doc """
		list = data
		if list == None :
			list = self.get_selection()
		for item in list :
			self.tree_store.remove(item)

	def get_selection(self):
		selected_items = []
		treeselection.selected_foreach(self.callback_get_selection_foreach, selected_items)
		model = sel.get_treeview().get_model()
		return (model, pathlist)
#
## CALLBACKS
	def callback_treeview_row_selected(self, *args):
		""" Called when a row is selected """
		print self.name, args
		
	def callback_get_selection_foreach(self, *args):
		""" helper callback for self.get_selection()"""
		print self.name, args

class MultiDataColumnList:
	def __init__(self, parent, data):
		self.data = data
		self.parent = parent
		
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
		self.text.set_property('editable', True)
		self.text.connect('edited', self.callback_CellRendererText, (list_store,1))
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.text, self.select_data)

		self.toggle = r = gtk.CellRendererToggle()
		self.toggle.set_property('activatable', True)
		self.toggle.connect('toggled', self.callback_CellRendererToggle, (list_store,1))
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.toggle, self.select_data)
		
		self.pixbuf = r = gtk.CellRendererPixbuf()
		self.column_value.pack_start(r, False)
		self.column_value.set_cell_data_func(self.pixbuf, self.select_data)
		#
		#
		
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
		else :
			self.text.props.visible=False
#
## Callbacks
	def callback_CellRendererToggle (self, cell, path, data) :
		""" Function doc """
		list_store, column = data
		list_store[path][column] = not list_store[path][column]
		return
		
	def callback_CellRendererText (self, cell, path, data) :
		""" Function doc """
		list_store, column = data
		list_store[path][column] = new_text
		return	
