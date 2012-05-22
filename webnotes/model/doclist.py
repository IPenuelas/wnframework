# Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
# 
# MIT License (MIT)
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

"""
Transactions are defined as collection of classes, a DocList represents collection of Document
objects for a transaction with main and children.

Group actions like save, etc are performed on doclists
"""

import webnotes
from webnotes.utils import cint
from webnotes.model.doc import Document

class DocList:
	"""
	Collection of Documents with one parent and multiple children
	"""
	def __init__(self, doctype_name=None, doc_name=None):
		self.doclist = []
		self.obj = None
		self.to_docstatus = 0
		
		if type(doctype_name) is list:
			self.doclist = doctype_name
			if not isinstance(doctype_name[0], Document):
				self.doclist = [Document(d) for d in self.doclist]
	
			self.doc = self.doclist[0]
			
		elif doctype_name and doc_name:
			self.load_from_db(doctype_name, doc_name)


	def load_from_db(self, doctype_name, doc_name):
		"""
			Load doclist from dt
		"""
		from webnotes.model.doc import Document, getchildren

		doc = Document(doctype_name, doc_name)

		# get all children types
		tablefields = webnotes.model.meta.get_table_fields(doctype_name)

		# load chilren
		doclist = [doc,]
		for t in tablefields:
			doclist += getchildren(doc.name, t[0], t[1], doctype_name)

		self.doclist = doclist
		self.doc = doc
		self.run_method('onload')

	def __iter__(self):
		"""
			Make this iterable
		"""
		return self.doclist.__iter__()

	def get(self, name):
		"""get value, list"""
		if isinstance(name, basestring):
			return self.doc.get(name)
		
		# list of filtered record
		elif isinstance(name, dict):
			t = []
			for d in self.doclist:
				if not False in map(lambda key: d.get(key)==name[key], name.keys()):
					t.append(d)
			
			return t
			
		else:
			raise Exception, 'unable to identify %s' % str(name)

	def next(self):
		"""
			Next doc
		"""
		return self.doclist.next()

	def to_dict(self):
		"""
			return as a list of dictionaries
		"""
		return [d.fields for d in self.doclist]

	def check_conflict(self):
		"""
			Raises exception if the modified time is not the same as in the database
		"""
		from webnotes.model.meta import is_single

		if (not is_single(self.doc.doctype)) and (not cint(self.doc.fields.get('__islocal'))):
			tmp = webnotes.conn.sql("""
				SELECT modified FROM `tab%s` WHERE name="%s" for update"""
				% (self.doc.doctype, self.doc.name))

			if tmp and str(tmp[0][0]) != str(self.doc.modified):
				webnotes.msgprint("""
				Document has been modified after you have opened it.
				To maintain the integrity of the data, you will not be able to save your changes.
				Please refresh this document. [%s/%s]""" % (tmp[0][0], self.doc.modified), raise_exception=1)

	def check_permission(self):
		"""
			Raises exception if permission is not valid
		"""
		if not self.doc.check_perm(verbose=1):
			webnotes.msgprint("Not enough permission to save %s" % self.doc.doctype, raise_exception=1)

	def check_links(self):
		"""
			Checks integrity of links (throws exception if links are invalid)
		"""
		ref, err_list = {}, []
		for d in self.doclist:
			if not ref.get(d.doctype):
				ref[d.doctype] = d.make_link_list()

			err_list += d.validate_links(ref[d.doctype])

		if err_list:
			webnotes.msgprint("""[Link Validation] Could not find the following values: %s.
			Please correct and resave. Document Not Saved.""" % ', '.join(err_list), raise_exception=1)

	def update_timestamps_and_docstatus(self):
		"""
			Update owner, creation, modified_by, modified, docstatus
		"""
		from webnotes.utils import now
		ts = now()
		user = webnotes.__dict__.get('session', {}).get('user') or 'Administrator'

		for d in self.doclist:
			if self.doc.fields.get('__islocal'):
				d.owner = user
				d.creation = ts

			d.modified_by = user
			d.modified = ts
			if d.docstatus != 2: # don't update deleted
				d.docstatus = self.to_docstatus

	def prepare_for_save(self, check_links):
		"""
			Set owner, modified etc before saving
		"""
		self.check_conflict()
		self.check_permission()
		if check_links:
			self.check_links()
		self.update_timestamps_and_docstatus()

	def run_method(self, method):
		"""
		Run a method and custom_method
		"""
		if hasattr(self, method):
			getattr(self, method)()

	def save_main(self):
		"""
			Save the main doc
		"""
		try:
			self.doc.save(cint(self.doc.fields.get('__islocal')))
		except NameError, e:
			webnotes.msgprint('%s "%s" already exists' % (self.doc.doctype, self.doc.name))

			# prompt if cancelled
			if webnotes.conn.get_value(self.doc.doctype, self.doc.name, 'docstatus')==2:
				webnotes.msgprint('[%s "%s" has been cancelled]' % (self.doc.doctype, self.doc.name))
			webnotes.errprint(webnotes.utils.getTraceback())
			raise e

	def save_children(self):
		"""
			Save Children, with the new parent name
		"""
		for d in self.doclist[1:]:
			deleted, local = d.fields.get('__deleted',0), d.fields.get('__islocal',0)

			if cint(local) and cint(deleted):
				pass

			elif d.fields.has_key('parent'):
				if d.parent and (not d.parent.startswith('old_parent:')):
					d.parent = self.doc.name # rename if reqd
					d.parenttype = self.doc.doctype

				d.save(new = cint(local))

	def save(self, check_links=1):
		"""
			Save the list
		"""
		self.prepare_for_save(check_links)
		self.run_method('validate')
		self.save_main()
		self.save_children()
		self.run_method('on_update')

	def submit(self):
		"""
			Save & Submit - set docstatus = 1, run "on_submit"
		"""
		if self.doc.docstatus != 0:
			msgprint("Only draft can be submitted", raise_exception=1)
		self.to_docstatus = 1
		self.save()
		self.run_method('on_submit')

	def cancel(self):
		"""
			Cancel - set docstatus 2, run "on_cancel"
		"""
		if self.doc.docstatus != 1:
			msgprint("Only submitted can be cancelled", raise_exception=1)
		self.to_docstatus = 2
		self.prepare_for_save(1)
		self.save_main()
		self.save_children()
		self.run_method('on_cancel')

	def update_after_submit(self):
		"""
			Update after submit - some values changed after submit
		"""
		if self.doc.docstatus != 1:
			msgprint("Only to called after submit", raise_exception=1)
		self.to_docstatus = 1
		self.prepare_for_save(1)
		self.save_main()
		self.save_children()
		self.run_method('on_update_after_submit')

# clone

def clone(source_doclist):
	"""clone doclist"""
	from webnotes.model.doc import Document
	new_doclist = []
	new_parent = Document(source_doclist.doc.fields.copy())
	new_parent.name = 'Temp/001'
	new_parent.fields['__islocal'] = 1
	new_parent.fields['docstatus'] = 0

	if new_parent.fields.has_key('amended_from'):
		new_parent.fields['amended_from'] = None
		new_parent.fields['amendment_date'] = None

	new_parent.save(1)

	new_doclist.append(new_parent)

	for d in source_doclist.doclist[1:]:
		newd = Document(d.fields.copy())
		newd.name = None
		newd.fields['__islocal'] = 1
		newd.fields['docstatus'] = 0
		newd.parent = new_parent.name
		new_doclist.append(newd)
	
	doclistobj = DocList()
	doclistobj.docs = new_doclist
	doclistobj.doc = new_doclist[0]
	doclistobj.doclist = new_doclist
	doclistobj.children = new_doclist[1:]
	doclistobj.save()
	return doclistobj


# for bc
def getlist(doclist, parentfield):
	"""
		Return child records of a particular type
	"""
	import webnotes.model.utils
	return webnotes.model.utils.getlist(doclist, parentfield)

def copy_doclist(doclist, no_copy = []):
	"""
		Make a copy of the doclist
	"""
	import webnotes.model.utils
	return webnotes.model.utils.copy_doclist(doclist, no_copy)

def get_model_object(doclist):
	"""get the instace of DocList from modules"""
	
	doctype = doclist[0]['doctype']
	
	if doctype in webnotes.core_models:
		modulepackage = 'core.doctype.' + webnotes.scrub(doctype)
	else:
		modulepackage = scrub(webnotes.conn.get_value('DocType', doctype, 'model')) +\
			'.doctype.' + webnotes.scrub(doctype)

	__import__(modulepackage)

	# find subclass of "Model"
	modelclass = model_class(sys.modules[modulepackage])
	if modelclass: 
		return modelclass(obj)
	else:
		raise Exception, 'Model for %s not found' %  obj['type']

def model_class(moduleobj):
	"""find first subclass of model.Model"""
	for name in dir(moduleobj):
		attr = getattr(moduleobj, name)
		if isinstance(attr, type) and issubclass(attr, Model):
			return attr


@webnotes.whitelist()
def get(doctype=None, name=None):
	if not doctype or not name:
		doctype, name = webnotes.form_dict.get('doctype'), webnotes.form_dict.get('name')
	
	if webnotes.form_dict.get('cmd')=='webnotes.model.doclist.get':
		webnotes.response['docs'] = DocList(doctype, name).doclist
	else:
		return DocList(doctype, name)

@webnotes.whitelist()
def save():
	import json
	doclist = json.loads(webnotes.form_dict.get('docs'))
	
	
	