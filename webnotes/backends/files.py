class FilesBackend:
	def doc_path(self, doctype_name, name):
		"""get docpath"""
		import webnotes, os
		start = os.path.join(webnotes.root_path, 'documents')
		if doctype_name=='DocType' and (name in webnotes.core_doctypes)\
			or doctype_name=='Page' and (name in webnotes.core_pages):
			start = os.path.join(webnotes.root_path, 'lib', 'documents')

		return os.path.join(start, webnotes.scrub(doctype_name), webnotes.scrub(name) + '.json')
				
	def strip_values(doclist):
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
		strip_values(doclist)
		with open(self.doc_path(doclist[0]['doctype'], doclist[0]['name']), 'w') as jsonfile:
			jsonfile.write(json.dumps(doclist, indent=1))
	
	def update_doclist(self, doclist):
		self.insert_doclists(doclist)
		
	def get_doclist(self, doctype_name, name):
		import json
		with open(doc_path(doctype_name, name), 'r') as jsonfile:
			return json.loads(jsonfile.read())