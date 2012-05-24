"""
Backends must

Methods:

get
insert
update
remove

optionally sql
"""

connections = {}

def get(backend_type, **args):
	backend_type = backend_type.lower()
	global connections
	if not connections.get(backend_type):
		if backend_type=='mysql':
			import mysql
			connections['mysql'] = mysql.MySQLBackend(**args)
		
		elif backend_type=='mysql_obj':
			import mysql_obj
			connections['mysql_obj'] = mysql_obj.MySQLObjectBackend(**args)
		
		elif backend_type.lower()=='files':
			import files
			connections['files'] = files.FilesBackend()

	return connections[backend_type]

def get_for(doctype):
	if doctype=='DocType':
		return get('files')
	else:
		return get('mysql')