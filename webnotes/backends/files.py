class FilesBackend:
	def insert(self, doclist):
		pass

def doc_path(doctype, name):
	import webnotes, os
	start = os.path.join(webnotes.root_path, 'documents')
	if name in webnotes.core_models:
		start = os.path.join(webnotes.root_path, 'lib', 'documents')
	
	return os.path.join(start, webnotes.scrub(doctype), webnotes.scrub(name) + '.json')
		
def write_doclist(doclist):
	"""write doclist to models"""
	import webnotes	
	import json
	
	strip_values(doclist)
		
	with open(doc_path(doclist[0]['doctype'], doclist[0]['name']), 'w') as jsonfile:
		jsonfile.write(json.dumps(doclist, indent=1))

def strip_values(doclist):
	"""reduce fields before writing in document file"""
	for d in doclist:
		remove_keys = ('creation', 'modified', 'owner', 'modified_by', 'server_code_error',
			'_last_update', 'section_style', 'colour', 'default_print_format', 'oldfieldname', 
			'oldfieldtype')
		remove_values = (None, 0)
		
		key_list = d.keys()
		for key in key_list:
			if key in remove_keys:
				del d[key]
				continue
				
			if d[key] in remove_values:
				del d[key]
				
def read_doclist(doctype, name):
	import json
	with open(doc_path(doctype, name), 'r') as jsonfile:
		return json.loads(jsonfile.read())