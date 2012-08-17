# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import webnotes
import webnotes.model
from webnotes.model.controller import DocListController

class ToDoController(DocListController):
	def validate(self):
		"""create comment if assignment"""
		if self.doc.assigned_by:
			remove(self.doc.reference_type, self.doc.reference_name)
			webnotes.model.insert({
				'doctype':'Comment',
				'comment':'<a href="#Form/%s/%s">%s</a> has been assigned to you.' % (
					self.doc.reference_type, self.doc.reference_name, self.doc.reference_name),
				'owner': self.doc.owner,
				'comment_doctype': 'Message',
				'comment_by': webnotes.session['user']
			})
			
	def on_trash(self):
		"""if assigned, notify assigner that task is closed"""
		if self.doc.assigned_by:
			webnotes.model.insert({
				'doctype':'Comment',
				'comment':'<a href="#Form/%s/%s">%s</a> you had assigned has been closed.' % (
					self.doc.reference_type, self.doc.reference_name, self.doc.reference_name),
				'owner': self.doc.assigned_by,
				'comment_doctype': 'Message',
				'comment_by': webnotes.session['user']
			})

@webnotes.whitelist()
def remove_todo():
	remove(webnotes.form.reference_type, webnotes.form.reference_name)
	
def remove(reference_type, reference_name):
	"""remove any other assignment related to this reference"""
	for name in webnotes.conn.sql("""select name from tabToDo where reference_type=%s and 
		reference_name=%s""", (reference_type, reference_name)):
		webnotes.model.delete_doc('ToDo', name[0])