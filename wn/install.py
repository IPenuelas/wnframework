# install models

def setup_db():
	"""create database and install models"""
	import wn, wn.backends
	import conf
	
	conn = wn.backends.get('mysql', user='root')
	conn.create_user_and_database(user = getattr(conf, 'db_user', conf.db_name), 
		db_name = conf.db_name)
	conn.close()

def remove():
	"""drop conf db database (for test cases)"""
	import wn, wn.backends
	import conf
	
	conn = wn.backends.get('mysql', user='root')
	conn.sql("""drop database %s""" % conf.db_name)
	conn.close()
	
def setup_doctypes():
	import os
	import wn.model
	
	# make core tables
	for fname in os.listdir('lib/documents/doctype'):
		fname.endswith('.json') and wn.model.get('DocType', fname[:-5]).setup()

	# run install script
	import wn.controllers.install_script
	wn.controllers.install_script.execute()

	# make app tables
	for fname in os.listdir('documents/doctype'):
		fname.endswith('.json') and wn.model.get('DocType', fname[:-5]).setup()

	# run install script of the app if present
	try:
		import install_script
		install_script.execute()
	except ImportError, e:
		pass

def install():
	import wn.backends
	setup_db()
	setup_doctypes()
	wn.backends.close()
	
if __name__=='__main__':
	import sys
	sys.path.append('controllers')
	sys.path.append('lib')
	install()