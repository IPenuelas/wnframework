import wn, wn.model, wn.backends

install_docs = [
	{"doctype": "Role", "name": "Administrator"},
	{"doctype": "Role", "name": "Guest"},
	{"doctype": "Role", "name": "All"},
	{"doctype": "User", "name": "Administrator", "password":"admin", "email":"admin@localhost"}
]

def execute():
	wn.backends.get('mysql').begin()
	for d in install_docs:
		wn.model.new(d).insert()
	wn.backends.get('mysql').commit()