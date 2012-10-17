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

import webnotes

@webnotes.whitelist()
def add_tag():
	"adds a new tag to a record, and creates the Tag master"	
	f = webnotes.form_dict
	DocTags(f.dt).add(f.dn, f.tag)

@webnotes.whitelist()
def remove_tag():
	"removes tag from the record"
	f = webnotes.form_dict
	DocTags(f.dt).remove(f.dn, f.tag)

def clear_tags(dt, dn):
	DocTags(dt).remove_all(dn)

class DocTags:
	"""Tags for a particular doctype"""
	def __init__(self, dt):
		self.dt = dt
		
	def get_tag_fields(self):
		"""returns tag_fields property"""
		return webnotes.conn.get_value('DocType', self.dt, 'tag_fields')
		
	def get_tags(self, dn):
		"""returns tag for a particular item"""
		return webnotes.conn.get_value(self.dt, dn, '_user_tags', ignore=1) or ''

	def create(self, tag):
		try:
			webnotes.conn.sql("insert into tabTag(name) values (%s) on duplicate key ignore", tag)
		except Exception, e:
			if e.args[0]==1147:
				self.setup_tag_master()
				self.create(tag)

	def add(self, dn, tag):
		"""add a new user tag"""
		self.create(tag)
		tl = self.get_tags(dn).split(',')
		if not tag in tl:
			tl.append(tag)
			self.update(dn, tl)

	def remove(self, dn, tag):
		"""remove a user tag"""
		tl = self.get_tags(dn).split(',')
		self.update(dn, filter(lambda x:x!=tag, tl))

	def remove_all(self, dn):
		"""remove all user tags (call before delete)"""
		tl = self.get_tags(dn).split(',')
		tl = filter(lambda x:x, tl)
		self.update(dn, [])

	def update(self, dn, tl):
		"""updates the _user_tag column in the table"""

		if not tl:
			tags = ''
		else:
			tl = list(set(filter(lambda x: x, tl)))
			tags = ',' + ','.join(tl)
		try:
			webnotes.conn.sql("update `tab%s` set _user_tags=%s where name=%s" % \
				(self.dt,'%s','%s'), (tags , dn))
		except Exception, e:
			if e.args[0]==1054: 
				if not tags:
					# no tags, nothing to do
					return
					
				self.setup()
				self.update(dn, tl)
			else: raise e

	def setup_tags(self):
		"""creates the tabTag table if not exists"""
		webnotes.conn.commit()
		from webnotes.modules import reload_doc
		reload_doc('core','doctype','tag')
		webnotes.conn.begin()
		
	def setup(self):
		"""adds the _user_tags column if not exists"""
		webnotes.conn.commit()
		webnotes.conn.sql("alter table `tab%s` add column `_user_tags` varchar(180)" % self.dt)
		webnotes.conn.begin()

