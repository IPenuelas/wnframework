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

import webnotes
import webnotes.model.doc
import webnotes.model.code

conn = webnotes.conn

class Page:
	"""
	   A page class helps in loading a Page in the system. On loading
	   
	   * Page will import Client Script from other pages where specified by `$import(page_name)`
	   * Execute dynamic HTML if the `content` starts with `#python`
	"""	
	def __init__(self, name):
		self.name = name

	def get_from_files(self, doc):
		"""
			Loads page info from files in module
		"""
		from webnotes.modules import get_module_path, scrub
		import os
		
		path = os.path.join(get_module_path(doc.module), 'page', scrub(doc.name))

		# script
		fpath = os.path.join(path, scrub(doc.name) + '.js')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				doc.fields['__script'] = f.read()

		# css
		fpath = os.path.join(path, scrub(doc.name) + '.css')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				doc.style = f.read()
		
		# html
		fpath = os.path.join(path, scrub(doc.name) + '.html')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				doc.content = f.read()
	
			
	def load(self):	
		"""
			Returns :term:`doclist` of the `Page`
		"""		
		doclist = webnotes.model.doc.get('Page', self.name)
		doc = doclist[0]

		# load from module
		if doc.module: 
			self.get_from_files(doc)

		# process
		self.process_content(doc)
		
		return doclist

@webnotes.whitelist()
def get(name):
	"""
	   Return the :term:`doclist` of the `Page` specified by `name`
	"""
	from webnotes.model.code import get_obj
	page = get_obj('Page', name)
	page.get_from_files()
	return page.doclist

@webnotes.whitelist(allow_guest=True)
def getpage():
	"""
	   Load the page from `webnotes.form` and send it via `webnotes.response`
	"""
	doclist = get(webnotes.form.getvalue('name'))
		
	# send
	webnotes.response['docs'] = doclist

def get_page_path(page_name, module):
	"""get path of the page html file"""
	import os
	import conf
	from webnotes.modules import scrub
	return os.path.join(conf.modules_path, 'erpnext', scrub(module), \
		'page', scrub(page_name), scrub(page_name) + '.html')
	
def get_page_html(page_name):
	"""get html of page, called from webnotes.cms.index"""
	p = webnotes.conn.sql("""select module, content from tabPage where name=%s""", \
		page_name, as_dict=1)

	if not p:
		return ''
	else:
		import os
		p=p[0]
		
		path = get_page_path(page_name, p['module'])
		if os.path.exists(path):
			with open(path, 'r') as f:
				return f.read()
		else:
			return p['content']
			
	
