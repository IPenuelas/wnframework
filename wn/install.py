# install models
def install(**args):
	"""create database and install models"""
	import wn, wn.model, wn.backends
	from wn.backends import mysql_schema
	import os
	import conf
	
	msq = wn.backends.get('mysql', user='root', password= conf.db_root_password)
	msq.create_user_and_database(user = getattr(conf, 'db_user', conf.db_name), 
		db_name = conf.db_name)
	
	# create db schema
	for fname in os.listdir('documents/doctype'):
		if fname.endswith('.json'):
			print 'creating table ' + fname[:-5]
			msq.create_table(wn.model.get('DocType', fname[:-5]))
		
if __name__=='__main__':
	import sys
	sys.path.append('controllers')
	sys.path.append('lib')
	install()
	