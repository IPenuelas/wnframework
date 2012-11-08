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

from __future__ import unicode_literals
"""
DocListWrapper is a collection of doclist & controller and is used
to manage run client events like save, submit, cancel
"""
import webnotes
from webnotes.utils import cint
from webnotes.model.doc import Document
from webnotes.model.doclist import DocList

class ModelWrapper:
	"""Collection of Documents with one parent and multiple children"""
	def __init__(self, dt=None, dn=None):
		self.obj = None
		self.to_docstatus = 0
		if isinstance(dt, list):
			self.set_doclist(dt)
		elif dt and dn:
			self.load_from_db(dt, dn)

	def load_from_db(self, dt=None, dn=None, prefix='tab'):
		"""Load doclist from dt"""
		from webnotes.model.doc import Document, getchildren
		if not dt: dt = self.doc.doctype
		if not dn: dn = self.doc.name

		doc = Document(dt, dn, prefix=prefix)

		# get all children types
		tablefields = webnotes.model.meta.get_table_fields(dt)

		# load chilren
		doclist = [doc,]
		for t in tablefields:
			doclist += getchildren(doc.name, t[0], t[1], dt, prefix=prefix)

		self.set_doclist(doclist)

	def from_compressed(self, data):
		from webnotes.model.utils import expand
		self.set_doclist(expand(data))
		
	def set_doclist(self, doclist):
		for i, d in enumerate(doclist):
			if isinstance(d, dict):
				doclist[i] = Document(fielddata=d)
		
		self.doclist = DocList(doclist)
		self.doc = doclist[0]

		if self.obj:
			self.obj.doclist = self.doclist
			self.obj.doc = self.doc

	def make_obj(self):
		if self.obj: return self.obj

		from webnotes.model.controller import get_obj
		self.obj = get_obj(doc=self.doc, doclist=self.doclist)
		return self.obj
		

	def to_dict(self):
		return [d.fields for d in self.doclist]

	def save(self, check_links=1):
		"""Save the doclist and trigger events"""
		self.prepare_for_save(check_links)
		
		# pre save
		if self.doc.docstatus < 2:
			self.run_method('validate')

		# save
		self.save_main()
		self.save_children()
		
		# post save
		if self.doc.docstatus < 2:	
			self.run_method('on_update')

			if self.cur_docstatus==0 and self.doc.docstatus==1:
				self.run_method('on_submit')
				
			elif self.cur_docstatus==1 and self.doc.docstatus==1:
				self.run_method("on_update_after_submit")
		
		elif self.doc.docstatus==2:
			self.run_method('on_cancel')
			
		else:
			webnotes.msgprint("docstatus must be one of (0, 1, 2)")
				
	def submit(self):
		self.doc.docstatus = 1
		self.save()

	def cancel(self):
		self.doc.docstatus = 2
		self.save()

	def update_after_submit(self):
		if self.doc.docstatus != 1:
			msgprint("Only to called after submit", raise_exception=1)
		self.save()

	def prepare_for_save(self, check_links):
		self.check_docstatus()
		self.check_if_latest()
		self.check_permission()
		if check_links:
			self.check_links()
		self.update_timestamps_and_docstatus()
		self.update_parent_info()

	def check_if_latest(self):
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
		if not self.doc.check_perm(verbose=1):
			webnotes.msgprint("Not enough permission to save %s" % \
				self.doc.doctype, raise_exception=1)

	def check_links(self):
		ref, err_list = {}, []
		for d in self.doclist:
			if not ref.get(d.doctype):
				ref[d.doctype] = d.make_link_list()

			err_list += d.validate_links(ref[d.doctype])

		if err_list:
			webnotes.msgprint("""[Link Validation] Could not find the following values: %s.
			Please correct and resave. Document Not Saved.""" % ', '.join(err_list), raise_exception=1)

	def update_timestamps_and_docstatus(self):
		from webnotes.utils import now
		ts = now()
		user = webnotes.__dict__.get('session', {}).get('user') or 'Administrator'

		for d in self.doclist:
			if self.doc.fields.get('__islocal'):
				d.owner = user
				d.creation = ts

			d.modified_by = user
			d.modified = ts
			
			# docstatus same as parent docstats
			d.docstatus = self.doc.docstatus
			
	def update_parent_info(self):
		for i, d in enumerate(self.doclist[1:]):
			if d.parentfield:
				d.parenttype = self.doc.doctype
				d.parent = self.doc.name
			if not d.idx:
				d.idx = i + 1

	def check_docstatus(self):
		# if docstatus is None, it gets stored as 0
		self.doc.docstatus = cint(self.doc.docstatus)
		
		self.cur_docstatus = cint(webnotes.conn.get_value(self.doc.doctype, 
			self.doc.name, "docstatus"))
			
		if self.doc.docstatus==0 and self.cur_docstatus > 0:
			webnotes.msgprint("""Document cannot be coverted back to Draft, please cancel and amend.""",
				raise_exception=1)

		elif self.doc.docstatus==1 and self.cur_docstatus > 1:
			webnotes.msgprint("""Document cannot be coverted back to Submit, please amend.""",
				raise_exception=1)

		elif self.doc.docstatus==2 and self.cur_docstatus == 0:
			webnotes.msgprint("""Document cannot be directly Cancelled, please submit first.""",
				raise_exception=1)

	def run_method(self, method):
		"""Run a method and custom_method"""
		self.make_obj()
		if hasattr(self.obj, method):
			getattr(self.obj, method)()
		if hasattr(self.obj, 'custom_' + method):
			getattr(self.obj, 'custom_' + method)()

		trigger(method, self.obj.doc)
		
	def save_main(self):
		"""Save the main doc"""
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
		"""Save Children, with the new parent name"""
		child_map = {}
		for d in self.doclist[1:]:
			if (d.fields.has_key('parent') and d.fields.get('parent')) or \
					(d.fields.has_key("parentfield") and d.fields.get("parentfield")):
				# if d.parent:
				d.parent = self.doc.name # rename if reqd
				d.parenttype = self.doc.doctype
				
				d.save(new = cint(d.fields.get('__islocal')))
			
			child_map.setdefault(d.doctype, []).append(d.name)
		
		# delete all children in database that are not in the child_map
		
		# get all children types
		tablefields = webnotes.model.meta.get_table_fields(self.doc.doctype)
				
		for dt in tablefields:
			cnames = child_map.get(dt[0]) or []
			if cnames:
				webnotes.conn.sql("""delete from `tab%s` where parent=%s and parenttype=%s and
					name not in (%s)""" % (dt[0], '%s', '%s', ','.join(['%s'] * len(cnames))), 
						tuple([self.doc.name, self.doc.doctype] + cnames))
			else:
				webnotes.conn.sql("""delete from `tab%s` where parent=%s and parenttype=%s""" \
					% (dt[0], '%s', '%s'), (self.doc.name, self.doc.doctype))
		
def trigger(method, doc):
	"""trigger doctype events"""
	try:
		import startup.event_handlers
	except ImportError:
		return
		
	if hasattr(startup.event_handlers, method):
		getattr(startup.event_handlers, method)(doc)
		
	if hasattr(startup.event_handlers, 'doclist_all'):
		startup.event_handlers.doclist_all(doc, method)

	