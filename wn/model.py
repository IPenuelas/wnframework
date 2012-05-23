import wn
import wn.backends

class DocList():
	def __init__(self, name=None, doctype_name=None):
		self.doclist = []			
		
		if type(name) is list:
			self.doclist = name	
			self.doc = self.doclist[0]
			
		elif doctype_name and name:
			self.load(doctype_name, name)
	
	def load(self, doctype_name, name):
		"""load from backend"""
		self.backend = wn.backends.get_for(doctype_name)
		self.doclist = self.backend.get_doclist(doctype_name, name)
		self.doc = self.doclist[0]
		
	def get(self, name, default=None):
		"""get a value from the main doc, or a list of child docs based on filters"""
		if isinstance(name, basestring):
			return self.doc.get(name, default)
		
		elif isinstance(name, dict):
			return filter(lambda d: False not in map(lambda key: d.get(key)==name[key], name.keys()), 
				self.doclist) or default
		else:
			raise Exception, 'unable to identify %s' % str(name)
					
	def insert(self):
		"""insert the doclist"""
		self.backend = wn.backends.get_for(doctype_name)
		self.backend.insert_doclist(self.doclist)

	def update(self):
		"""update the doclist"""
		self.backend = wn.backends.get_for(doctype_name)
		self.backend.update_doclist(self.doclist)

def import_object(txt):
	"""import a reference from a python module"""
	m = txt.split('.')	
	module = __import__('.'.join(m[:-1]), fromlist=True)
	return getattr(module, m[-1])

def get_controller_name(doctype_name):
	"""get controller module string for the doctype"""
	return wn.model.get_value('DocType', doctype_name, 'controller', 'wn.model.DocList')
	
def get(doctype_name, name):
	"""get a doclist object of the give doctype, name"""
	if isinstance(doctype_name, basestring):
		return import_object(get_controller_name(doctype_name))(name, doctype_name)

	elif isinstance(doctype_name, list):
		return import_object(get_controller_name(doctype_name.get('doctype')))(doctype_name)
		
	else:
		raise Exception, "must pass doctype as string or doclist"

def get_value(doctype_name, name, key, default):
	"""get a value"""
	return wn.backends.get_for(doctype_name).get_value(doctype_name, name, key, default)
		