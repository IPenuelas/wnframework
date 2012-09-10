# Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
# 
# MIT License (MIT)
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

# called from wnf.py
# lib/wnf.py --install [rootpassword] [dbname] [source]

import os,sys

class Installer:
	def __init__(self, root_login, root_password=None):

		import webnotes
		import webnotes.db
		from webnotes.sessions import Session
		self.session = Session(None, None, 'Administrator')
	
		if root_login and not root_password:
			import getpass
			root_password = getpass.getpass("MySQL root password: ")
			
		self.root_password = root_password
		from webnotes.model.db_schema import DbManager
		
		self.conn = webnotes.db.Database(user=root_login, password=root_password)			
		self.session._db = self.conn
		self.session.user = "Administrator"
		self.dbman = DbManager(self.session)

	def import_from_db(self, target, source_path='', password = 'admin', verbose=0):
		"""
		a very simplified version, just for the time being..will eventually be deprecated once the framework stabilizes.
		"""
		import conf
		import webnotes
		
		# delete user (if exists)
		self.dbman.delete_user(target)

		# create user and db
		self.dbman.create_user(target, 
			hasattr(conf, 'db_password') and conf.db_password or password)
			
		if verbose: print "Created user %s" % target
	
		# create a database
		self.dbman.create_database(target)
		if verbose: print "Created database %s" % target
		
		# grant privileges to user
		self.dbman.grant_all_privileges(target,target)
		if verbose: print "Granted privileges to user %s and database %s" % (target, target)

		# flush user privileges
		self.dbman.flush_privileges()

		self.conn.use(target)
		
		# import in target
		if verbose: print "Starting database import..."

		# get the path of the sql file to import
		source_given = True
		if not source_path:
			source_given = False
			source_path = os.path.join(os.path.sep.join(os.path.abspath(webnotes.__file__).split(os.path.sep)[:-3]), 'conf', 'Framework.sql')

		self.dbman.restore_database(target, source_path, self.root_password)
		if verbose: print "Imported from database %s" % source_path


		# framework cleanups
		self.framework_cleanups(target)
		if verbose: print "Ran framework startups on %s" % target
		
		# fresh app
		if 'Framework.sql' in source_path:
			from webnotes.model.sync import sync_install
			print "Building tables from all module..."
			sync_install(self.session)

		# set administrator password
		self.set_admin_password()
		
		self.conn.close()
		
		return target	

	def framework_cleanups(self, target):
		"""create framework internal tables"""
		self.create_sessions_table()
		self.create_scheduler_log()
		self.create_session_cache()
		self.create_cache_item()
		self.create_auth_table()

	def set_admin_password(self):
		# set the basic passwords
		self.conn.begin()
		self.conn.sql("""insert into __Auth (user, `password`)
			values ('Administrator', password('admin'))
			on duplicate key update `password`=password('admin')""")
		self.conn.commit()

	def create_sessions_table(self):
		"""create sessions table"""
		self.dbman.drop_table('tabSessions')
		self.conn.sql("""CREATE TABLE `tabSessions` (
		  `user` varchar(40) DEFAULT NULL,
		  `sid` varchar(120) DEFAULT NULL,
		  `sessiondata` longtext,
		  `ipaddress` varchar(16) DEFAULT NULL,
		  `lastupdate` datetime DEFAULT NULL,
		  `status` varchar(20) DEFAULT NULL,
		  KEY `sid` (`sid`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8""")
	
	def create_scheduler_log(self):
		self.dbman.drop_table('__SchedulerLog')
		self.conn.sql("""create table __SchedulerLog (
			`timestamp` timestamp,
			method varchar(200),
			error text
		) ENGINE=MyISAM DEFAULT CHARSET=utf8""")
	
	def create_session_cache(self):
		self.dbman.drop_table('__SessionCache')
		self.conn.sql("""create table `__SessionCache` ( 
			user VARCHAR(180), 
			country VARCHAR(180), 
			cache LONGTEXT) ENGINE=InnoDB""")

	def create_cache_item(self):
		self.dbman.drop_table('__CacheItem')
		self.conn.sql("""create table __CacheItem (
			`key` VARCHAR(180) NOT NULL PRIMARY KEY,
			`value` LONGTEXT
			) ENGINE=InnoDB DEFAULT CHARSET=utf8""")
			
	def create_auth_table(self):
		self.conn.sql("""create table if not exists __Auth (
			`user` VARCHAR(180) NOT NULL PRIMARY KEY,
			`password` VARCHAR(180) NOT NULL
			) ENGINE=InnoDB DEFAULT CHARSET=utf8""")
