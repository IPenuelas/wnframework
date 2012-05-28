import wn
import wn.backends

class DocList():
	def __init__(self, doclist=None, doctype_name=None):
		self.doclist = []			
		
		if isinstance(doclist, dict):
			name = [doclist]
		
		if isinstance(doclist, list):
			self.set_doclist(doclist)
			
		elif doctype_name and isinstance(doclist, basestring):
			self.load(doctype_name, doclist)
	
	def set_doclist(self, doclist):
		"""set `doc` and `doclist` properties"""
		self.doclist = doclist
		self.doc = doclist[0]
	
	def load(self, doctype_name, name):
		"""load from backend"""
		self.backend = wn.backends.get_for(doctype_name)
		doclist = self.backend.get(doctype_name, name)
		if not doclist:
			raise wn.NotFoundError, "%s, %s" % (doctype_name, name)
			
		self.set_doclist(doclist)
		
	def get(self, name, default=None):
		"""get a value from the main doc, or a list of child docs based on filters"""
		if isinstance(name, basestring):
			return self.doc.get(name, default)
		
		elif isinstance(name, dict):
			return filter(lambda d: False not in map(lambda key: d.get(key)==name[key], name.keys()), 
				self.doclist) or default
		else:
			raise Exception, 'unable to identify %s' % str(name)
	
	def set(self, name, value):
		"""set local value in main doc"""
		self.doc[name] = value
	
	def insert(self):
		"""insert the doclist"""
		self.trigger('autoname')
		self.trigger('before_insert')
		wn.backends.get_for(self.get('doctype')).insert_doclist(self.doclist)
		self.trigger('after_insert')

	def update(self):
		"""update the doclist"""
		self.trigger('before_update')
		wn.backends.get_for(self.get('doctype')).update_doclist(self.doclist)
		self.trigger('after_update')
	
	def trigger(self, method):
		hasattr(self, method) and getattr(self, method)()
	
	def autoname(self): 
		"""name the record"""
		pass
	
def get(doctype_name, name):
	"""get a doclist object of the give doctype, name"""
	if isinstance(doctype_name, basestring):
		return get_doctype_object(doctype_name)(name, doctype_name)

	elif isinstance(doctype_name, list):
		return get_doctype_object(doctype_name[0].get('doctype'))(doctype_name)
		
	else:
		raise Exception, "must pass doctype as string or doclist"

def import_object(txt):
	"""import a reference from a python module"""
	m = txt.split('.')	
	module = __import__('.'.join(m[:-1]), fromlist=True)
	return getattr(module, m[-1])

def get_controller_name(doctype_name):
	"""get controller module string for the doctype"""
	return wn.model.get_value('DocType', doctype_name, 'controller', 'wn.model.DocList')

def get_doctype_object(doctype_name):
	return import_object(get_controller_name(doctype_name))
	
def get_value(doctype_name, name, key, default=None):
	"""get a value"""
	return wn.backends.get_for(doctype_name).get_value(doctype_name, name, key, default)

def new(doctype_name):
	"""create a new instance of a doctype (pass name or doclist or maindoc)"""
	if isinstance(doctype_name, dict):
		newobj = get_doctype_object(doctype_name.get('doctype'))()
		doclist = [doctype_name]
	elif isinstance(doctype_name, list):
		newobj = get_doctype_object(doctype_name[0].get('doctype'))()
		doclist = doctype_name
	else:
		newobj = get_doctype_object(doctype_name)()
		doclist = [{"doctype":doctype_name}]
		
	newobj.set_doclist(doclist)
	return newobj