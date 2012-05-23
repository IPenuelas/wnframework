"""
Backends must

Methods:

get
insert
update
remove

optionally sql
"""

def get(backend_type, **args):
	if backend_type.lower()=='mysql':
		import mysql
		return mysql.MySQLBackend(**args)
		
	if backend_type.lower()=='files':
		import files
		return files.FilesBackend()