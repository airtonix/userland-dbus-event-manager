"""
 * config.py
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
"""
	Object Data Structure Example
	=============================
		objects = {
			"Laptop Lid" : {
				"Bus"					: "System",										# REQUIRED : 
				"Interface"		: "org.freedesktop.Hal.Device",					# REQUIRED : 
				"Path"				: None,											# REQUIRED : None means search for it (some devices might have different locations per machine)
				"DBUS_Search"	: {
					"key"					: "info.product",
					"value"				:	"Lid Switch"
				},
				"ACPI"				: "/proc/acpi/button/lid/LID0/state",
				"States"			:	{
					"Connect"			: "Open",
					"Disconnect"	: "Close"
				},
				"Scripts"			: {												# move this into a config database sometime.
					"Open" 				: {
						"exists"			: 0,
						"path"				: "%s/laptop-lid-opened.sh" % sys.path[0]
					},
					"Close" 			: {
						"exists"			: 0,
						"path"				: "%s/laptop-lid-closed.sh" % sys.path[0]
					}		
				}
			}

		}
"""
	
 
import gconf
import types


class ConfigManager:
	def __init__( self, domain):
		self.domain = domain
		self.client = gconf.client_get_default ()
		
		if not self.client.dir_exists (self.domain):
			self.client.add_dir ( self.domain, gconf.CLIENT_PRELOAD_NONE )

	def get_entries( self,path=None):
		'''Wrapper method for gconf.Client.all_entries(...)'''
		
		return self.client.all_entries( "%s" % self.build_path(path) )

	def get_list( self , path=None):
		'''Wrapper method for gconf.Client.get_list(...)'''
		return self.client.get_list( "%s/list" % self.build_path(path) , gconf.VALUE_STRING )
                                                                                                                            
	def set_list( self, path, values ): # set_list( self, list )
		'''Wrapper method for gconf.Client.set_list(...)'''
		return self.client.set_list( "%s/list" % self.build_path(path), gconf.VALUE_STRING, values )

	def set_string( self, path, value ):
		'''Wrapper method for gconf.Client.set_string(...)'''
		return self.client.set_string ( "%s" % self.build_path(path), value )
                                                                                                                            
	def get_string( self, path=None ):
		'''Wrapper method for gconf.Client.get_string(...)'''
		return self.client.get_string( "%s" % self.build_path(path) )

	def set_int( self, path, value ):
		'''Wrapper method for gconf.Client.set_int(...)'''
		return self.client.set_int( "%s" % self.build_path(path) , value )

	def get_int( self, path=None ):
		'''Wrapper method for gconf.Client.get_int(...)'''
		return self.client.get_int( "%s" % self.build_path(path) )

	def set_bool( self, path, value ):
		'''Wrapper method for gconf.Client.set_bool(...)'''
		return self.client.set_bool( "%s" % self.build_path(path), value )

	def get_bool( self, path=None ):
		'''Wrapper method for gconf.Client.get_bool(...)'''
		return self.client.get_bool( "%s" % self.build_path(path) )

	def set_float( self, path, value ):
		'''Wrapper method for gconf.Client.set_float(...)'''
		return self.client.set_float( "%s" % self.build_path(path), value )

	def get_float( self, path=None ):
		'''Wrapper method for gconf.Client.get_float(...)'''
		return self.client.get_float( "%s" % self.build_path(path) )

	def unset( self, path ):
		'''Wrapper method for gconf.Client.unset(...)'''
		return self.client.unset( "%s" % self.build_path(path) )

	def list_dirs(self, path=None):
		'''Returns a tuple representing directories in the current domain + path gconf directory'''
		return self.client.all_dirs("%s" % self.build_path(path) )
		
	def remove_dir( self, path ):
		'''Wrapper method for gconf.Client.remove_dir(...)'''
		path = self.build_path(path)
		print "removing dir %s " % path
		''' If it doesn't exist, return false. '''
		if not self.client.dir_exists( "%s" % path ):
			print "remove_dir : can't find (%s)" % path
			return False
			
		''' Test if it has child values, recursively unset them if so '''
		children = self.get_entries(path)
		if len(children) > 0 :
			print "remove_dir : dir(%s) has children(%s)" % (path,children)
			return self.client.recursive_unset( "%s" % path , gconf.UNSET_INCLUDING_SCHEMA_NAMES)

		return self.client.remove_dir( "%s" % path )

	def get_real_value( self, value ): # value is of type gconf.Value
		'''Convenience method for transparently getting a value determined by its type'''
		if value.type == gconf.VALUE_INVALID:
			_value = None
		elif value.type == gconf.VALUE_STRING:
			_value = value.get_string()
		elif value.type == gconf.VALUE_INT:
			_value = value.get_int()
		elif value.type == gconf.VALUE_FLOAT:
			_value = value.get_float()
		elif value.type == gconf.VALUE_BOOL:
			_value = value.get_bool()
		elif value.type == gconf.VALUE_SCHEMA:
			_value = None # gconf.Value doesn't have a get_schema method
		elif value.type == gconf.VALUE_LIST:
			_value = value.get_list()
		return _value

	def set_real_value( self, path, value ):
		'''Convenience method for transparently setting a value determined by its type'''
		_type = type( value )
		path = self.build_path(path)
		
		if _type == types.StringType:
			self.set_string( path, value )
		elif _type == types.IntType:
			self.set_int( path, value )
		elif _type == types.FloatType:
			self.set_float( path, value )
		elif _type == types.BooleanType:
			self.set_bool( path, value )
		else:
			print "Error: Couldn't determine type for %s did not save value %s " % (path, value )
			
	def build_path (self, path=None):
		""" Function doc """
		search_path = self.domain
		if path != None and path.rfind(search_path) < 0 :
			search_path = search_path + "/" + path
		return search_path
		
class GconfManager( ConfigManager ) :
	def __init__( self, domain, dir=None) :
		ConfigManager.__init__( self, domain )

	def entries( self, path = None):
		'''Returns a dict representing values within our /prefs gconf directory'''
		entries_tmp = {}
		for entry in self.get_entries(path):
			key = entry.get_key()
			key = key[ key.rfind("/")+1 : ]
			if not entry.get_value():
				entries_tmp[key] = None
				continue
			value = self.get_real_value( entry.get_value() )
			entries_tmp[key] = value
		return entries_tmp

	def save_prefs( self, entries ):
		'''Saves key and value pairs found in the dict prefs to our /prefs gconf directory'''
		for key, value in entries.iteritems():
			self.set_real_value( key, value )
	
if __name__ == '__main__':
	#Examples
	"""
	myapp = GconfManager( "/apps" , "mytestapp")

	print myapp.set_string( "lol", "blah" )
	print myapp.entries()

	print myapp.unset("lol")

	print myapp.remove_dir("prefs")
	print myapp.remove_dir("")

	prefs = GconfManager( "/apps/mytestapp" , "prefs")
	print prefs.set_string( "foo", "blah" )
	print prefs.set_string( "bar", "blahblah" )
	print prefs.get_string( "foo" )

	print prefs.unset( "foo" )
	print prefs.entries()
	prefs.set_real_value( 'vte_scrollback_lines', 10000 )
	print prefs.entries()

	print prefs.get_entries()[0].get_key()
	print prefs.get_entries()[0].get_value()
	"""

