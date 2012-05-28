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

import wn, wn.model
class DocType(wn.model.DocList):
	def setup(self):
		"""make table"""
		wn.backends.get(self.get('backend', 'mysql')).setup(self)

	def scrub_field_names(self):
		"""add underscore to fieldnames based on label"""
		for d in self.doclist:
			if d.parent and d.fieldtype:
				if (not d.fieldname):
					if d.label:
						d.fieldname = d.label.strip().lower().replace(' ','_')
					else:
						webnotes.msgprint('Fieldname is required for row: ' + str(d.idx), 
							raise_exception=1)
					
	
	def validate_fields(self):
		"validates fields for incorrect properties and double entries"
		fieldnames = {}
		illegal = ['.', ',', ' ', '-', '&', '%', '=', '"', "'", '*', '$']
		for d in self.doclist:
			if not d.permlevel: d.permlevel = 0
			if d.parent and d.fieldtype and d.parent == self.doc.name:
				# check if not double
				if d.fieldname:
					if fieldnames.get(d.fieldname):
						webnotes.msgprint("""Fieldname <b>%s</b> appears twice (rows %s and %s). 
							Please rectify""" % (d.fieldname, str(d.idx + 1), str(fieldnames[d.fieldname] + 1)), 
							raise_exception=1)
					fieldnames[d.fieldname] = d.idx
					
					# check bad characters
					for c in illegal:
						if c in d.fieldname:
							webnotes.msgprint('"%s" not allowed in fieldname' % c)
				
				else:
					webnotes.msgprint("Fieldname is mandatory in row %s" % str(d.idx+1), 
						raise_exception=1)
				
				# check illegal mandatory
				if d.fieldtype in ('HTML', 'Button', 'Section Break', 'Column Break') and d.reqd:
					webnotes.msgprint('%(lable)s [%(fieldtype)s] cannot be mandatory', 
						raise_exception=1)
		
		
	def validate(self):
		self.scrub_field_names()
		self.validate_fields()

	def on_update(self):
		"""pass"""
		pass