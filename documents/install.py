install_docs = [
	{'doctype':'Module Def', 'name': 'Core', 'module_name':'Core'},

	# roles
	{'doctype':'Role', 'role_name': 'Administrator', 'name': 'Administrator'},
	{'doctype':'Role', 'role_name': 'All', 'name': 'All'},
	{'doctype':'Role', 'role_name': 'System Manager', 'name': 'System Manager'},
	{'doctype':'Role', 'role_name': 'Report Manager', 'name': 'Report Manager'},
	{'doctype':'Role', 'role_name': 'Guest', 'name': 'Guest'},
	
	# profiles
	{'doctype':'Profile', 'name':'Administrator', 'first_name':'Administrator', 
		'email':'admin@localhost', 'enabled':1},
	{'doctype':'Profile', 'name':'Guest', 'first_name':'Guest',
		'email':'guest@localhost', 'enabled':1},
		
	# userroles
	{'doctype':'UserRole', 'parent': 'Administrator', 'role': 'Administrator', 
		'parenttype':'Profile', 'parentfield':'userroles'},
	{'doctype':'UserRole', 'parent': 'Guest', 'role': 'Guest', 
		'parenttype':'Profile', 'parentfield':'userroles'}
]