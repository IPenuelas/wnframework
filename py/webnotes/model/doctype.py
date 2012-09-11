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
Get metadata (main doctype with fields and permissions with all table doctypes)

- if exists in cache, get it from cache
- add custom fields
- override properties from PropertySetter
- sort based on prev_field
- optionally, post process (add js, css, select fields), or without

"""
# imports
import conf
import webnotes
import webnotes.model
import webnotes.model.doc
import webnotes.model.controller
import webnotes.model.doclist

doctype_cache = {}
docfield_types = None

def get(session, doctype, processed=False):
	"""return doclist"""

	# from database cache __CacheItem
	doclist = from_cache(session, doctype, processed)
	if doclist: return DocTypeDocList(doclist)
	
	load_docfield_types(session)
	
	# main doctype doclist
	doclist = get_doctype_doclist(session, doctype)

	# add doctypes of table fields
	table_types = [d.options for d in doclist \
		if d.doctype=='DocField' and d.fieldtype=='Table']
		
	for table_doctype in table_types:
		doclist += get_doctype_doclist(session, table_doctype)
		
	if processed: 
		add_code(session, doctype, doclist)
		expand_selects(session, doclist)
		add_print_formats(session, doclist)
		add_search_fields(session, doclist)
		update_language(session, doclist)

	# add validators
	add_validators(session, doctype, doclist)

	to_cache(session, doctype, processed, doclist)
		
	return DocTypeDocList(doclist)

def update_language(session, doclist):
	"""update language"""
	if session.non_english():
		from webnotes import _
		from webnotes.modules import get_doc_path

		# load languages for each doctype
		from webnotes.utils.translate import get_lang_data, update_lang_js
		_messages = {}

		for d in doclist:
			if d.doctype=='DocType':
				_messages.update(get_lang_data(get_doc_path(d.module, d.doctype, d.name), 
					session.lang, 'doc'))
				_messages.update(get_lang_data(get_doc_path(d.module, d.doctype, d.name), 
					session.lang, 'js'))

		doc = doclist[0]

		# attach translations to client
		doc["__messages"] = _messages

def load_docfield_types(session):
	global docfield_types
	docfield_types = dict(session.db.sql("""select fieldname, fieldtype from tabDocField
		where parent='DocField'"""))

def get_doctype_doclist(session, doctype):
	"""get doclist of single doctype"""
	doclist = webnotes.model.doclist.load(session, 'DocType', doctype)
	add_custom_fields(session, doctype, doclist)
	apply_property_setters(session, doctype, doclist)
	sort_fields(doclist)
	return doclist

def sort_fields(doclist):
	"""sort on basis of previous_field"""
	from webnotes.model.doclist import DocList
	newlist = DocList([])
	pending = filter(lambda d: d.doctype=='DocField', doclist)
	
	maxloops = 20
	while (pending and maxloops>0):
		maxloops -= 1
		for d in pending[:]:
			if d.previous_field:
				# field already added
				for n in newlist:
					if n.fieldname==d.previous_field:
						newlist.insert(newlist.index(n)+1, d)
						pending.remove(d)
						break
			else:
				newlist.append(d)
				pending.remove(d)
			
	# recurring at end	
	if pending:
		newlist += pending
		
	# renum
	idx = 1
	for d in newlist:
		d.idx = idx
		idx += 1

	doclist.get({"doctype":["!=", "DocField"]}).extend(newlist)
			
def apply_property_setters(session, doctype, doclist):		
	from webnotes.utils import cint
	for ps in session.db.sql("""select * from `tabProperty Setter` where
		doc_type=%s""", doctype, as_dict=1):
		if ps['doctype_or_field']=='DocType':
			doclist[0][ps['property']] = ps['value']
		else:
			docfield = filter(lambda d: d.doctype=="DocField" and d.fieldname==ps['field_name'], 
				doclist)
			if not docfield: continue
			if docfield_types.get(ps['property'], None) in ('Int', 'Check'):
				ps['value'] = cint(ps['value'])
				
			docfield[0][ps['property']] = ps['value']

def add_custom_fields(session, doctype, doclist):
	try:
		res = session.db.sql("""SELECT * FROM `tabCustom Field`
			WHERE dt = %s AND docstatus < 2""", doctype, as_dict=1)
	except Exception, e:
		if e.args[0]==1146:
			return doclist
		else:
			raise e

	for r in res:
		custom_field = webnotes.model.doc.Document(fielddata=r)
		
		# convert to DocField
		custom_field.update({
			'doctype': 'DocField',
			'parent': doctype,
			'parentfield': 'fields',
			'parenttype': 'DocType',
		})
		doclist.append(custom_field)

	return doclist
	
def from_cache(session, doctype, processed):
	""" load doclist from cache.
		sets flag __from_cache in first doc of doclist if loaded from cache"""
	global doctype_cache

	# from memory
	if not processed and doctype in doctype_cache:
		return doctype_cache[doctype]

	json_doclist = session.memc.get_value(cache_name(doctype, processed))
	if json_doclist:
		import json
		from webnotes.model.doclist import DocList
		doclist = DocList([webnotes.model.doc.Document(fielddata=d)
				for d in json.loads(json_doclist)])
		doclist[0].__from_cache = True
		return doclist

def to_cache(session, doctype, processed, doclist):
	global doctype_cache
	import json
	
	json_doclist = json.dumps([d for d in doclist], default=webnotes.json_handler)
	session.memc.set_value(cache_name(doctype, processed), json_doclist)

	if not processed:
		doctype_cache[doctype] = doclist

def cache_name(doctype, processed):
	"""returns cache key"""
	return "doctype:" + doctype + (not processed and ":Raw" or "")

def clear_cache(session, doctype):
	global doctype_cache
	session.memc.delete_value(cache_name(doctype, False))
	session.memc.delete_value(cache_name(doctype, True))

	if doctype in doctype_cache:
		del doctype_cache[doctype]
	
def add_code(session, doctype, doclist):
	import os, conf
	from webnotes.modules import scrub, get_module_path
	
	doc = doclist[0]
	
	path = os.path.join(get_module_path(doc.module), 'doctype', scrub(doc.name))

	def _add_code(fname, fieldname):
		fpath = os.path.join(path, fname)
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				doc[fieldname] = f.read()
		
	_add_code(scrub(doc.name) + '.js', '__js')
	_add_code(scrub(doc.name) + '.css', '__css')
	_add_code('%s_list.js' % scrub(doc.name), '__listjs')
	add_embedded_js(session, doc)
	
def add_embedded_js(session, doc):
	"""embed all require files"""

	import re, os, conf

	# custom script
	custom = session.db.get_value("Custom Script", {"dt": doc.name, "script_type": "Client"}) or ""
	doc['__js'] = (doc.get('__js') or '') + '\n' + custom	
	
	def _sub(match):
		fpath = os.path.join(os.path.dirname(conf.modules_path), \
			re.search('["\'][^"\']*["\']', match.group(0)).group(0)[1:-1])
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				return '\n' + f.read() + '\n'
		else:
			return '\n// no file "%s" found \n' % fpath
	
	if doc.get('__js'):
		doc['__js'] = re.sub('(wn.require\([^\)]*.)', _sub, doc['__js'])
		
def expand_selects(session, doclist):
	for d in filter(lambda d: d.fieldtype=='Select' and (d.options or '').startswith('link:'), doclist):
		doctype = d.options[5:]
		d.options = '\n'.join([''] + [o.name for o in session.db.sql("""select name from `tab%s` 
			where docstatus<2 order by name asc""" % doctype)])

def add_print_formats(session, doclist):
	# TODO: Process Print Formats for $import
	# to deprecate code in print_format.py
	# if this is implemented, clear CacheItem on saving print format
	print_formats = session.db.sql("""select * FROM `tabPrint Format`
		WHERE doc_type=%s AND docstatus<2""", doclist[0].get('name'), as_dict=1)
	for pf in print_formats:
		doclist.append(webnotes.model.doc.Document('Print Format', fielddata=pf))

def get_property(session, dt, prop, fieldname=None):
	"""get a doctype property"""
	doctypelist = get(session, dt)
	if fieldname:
		return doctypelist.getone({"fieldname":fieldname}).get(prop)
	else:
		return doctypelist[0].get(prop)
		
def get_link_fields(session, doctype):
	"""get docfields of links and selects with "link:" """
	doctypelist = get(session, doctype)
	
	return doctypelist.get({"fieldtype":"Link"}).extend(doctypelist.get({"fieldtype":"Select", 
		"options": "^link:"}))
		
def add_validators(session, doctype, doclist):
	for validator in session.db.sql("""select name from `tabDocType Validator` where
		for_doctype=%s""", doctype):
		doclist.extend(session.get_doclist('DocType Validator', validator.name))
		
def add_search_fields(session, doclist):
	"""add search fields found in the doctypes indicated by link fields' options"""
	for lf in doclist.get({"fieldtype": "Link"}):
		if lf.options:
			search_fields = get(session, lf.options)[0].search_fields
			if search_fields:
				lf.search_fields = map(lambda sf: sf.strip(), search_fields.split(","))

class DocTypeDocList(webnotes.model.doclist.DocList):
	def get_field(self, fieldname, parent=None, parentfield=None):
		filters = {"doctype":"DocField", "fieldname":fieldname}
		
		# if parentfield, get the name of the parent table
		if parentfield:
			parent = self.get_options(parentfield)

		if parent:
			filters["parent"] = parent
		
		return self.getone(filters)
		
	def get_fieldnames(self, filters=None):
		if not filters: filters = {}
		filters.update({"doctype": "DocField", "parent": self[0].name})
			
		return map(lambda df: df.fieldname, self.get(filters))
	
	def get_options(self, fieldname, parent=None, parentfield=None):
		return self.get_field(fieldname, parent, parentfield).options
		
	def get_label(self, fieldname, parent=None, parentfield=None):
		return self.get_field(fieldname, parent, parentfield).label
		
	def get_table_fields(self):
		return self.get({"doctype": "DocField", "fieldtype": "Table"})	
