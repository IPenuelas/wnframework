class FilesBackend:
	def doc_path(self, doctype_name, name):
		"""get docpath"""
		import wn, os
		start = os.path.join(wn.root_path, 'documents')
		return os.path.join(start, wn.code_style(doctype_name), wn.code_style(name) + '.json')
				
	def strip_values(self, doclist):
		"""reduce fields before writing in document file"""
		for d in doclist:
			remove_keys = ()
			remove_values = (None, 0)

			key_list = d.keys()
			for key in key_list:
				if key in remove_keys:
					del d[key]
					continue

				if d[key] in remove_values:
					del d[key]
						
	def insert_doclist(self, doclist):
		import json
		self.strip_values(doclist)
		with open(self.doc_path(doclist[0]['doctype'], doclist[0]['name']), 'w') as jsonfile:
			jsonfile.write(json.dumps(doclist, indent=1))
	
	def update_doclist(self, doclist):
		self.insert_doclists(doclist)
		
	def get(self, doctype_name, name):
		"""get doclist"""
		import json, os
		fpath = self.doc_path(doctype_name, name)
		if os.path.exists(fpath):
			with open(fpath, 'r') as jsonfile:
				return json.loads(jsonfile.read())
		else:
			return []
			
	def get_doclist(self, filters):
		"""get multiple doclists"""
		# TODO
		return []
	
	def get_value(self, doctype_name, name, key, default=None):
		"""get a particular value"""
		doclist = self.get(doctype_name, name)
		return doclist and doclist[0].get(key, default) or default
	
	def remove(self, doctype_name, name):
		import os
		fpath = self.doc_path(doctype_name, name)
		if os.path.exists(fpath):
			os.remove(fpath)