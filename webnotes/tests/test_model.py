# models
# database
# 	- schema
# 	- 

import unittest, sys

sys.path.append('controllers')
sys.path.append('lib')

import webnotes
webnotes.connect()

import os, json

class TestModel(unittest.TestCase):
	def test_read(self):
		return
		from webnotes.model.utils import read_doclist
		doclist = read_doclist('DocType', 'DocType')
		self.assertTrue(doclist[0]['name'] == 'DocType')
	
	def test_doclistobj_get(self):
		from webnotes.model.utils import read_doclist
		from webnotes.model.doclist import DocList
		
		doctype = DocList(read_doclist('DocType', 'DocType'))
		
		self.assertTrue(doctype.get('name')=='DocType')
		self.assertTrue(len(doctype.get({'doctype':'DocField'})) > 10)
		self.assertTrue(len(doctype.get({'doctype':'DocField', 'fieldname':'autoname'})) == 1)
		self.assertTrue(doctype.get({'doctype':'DocField', 'fieldname':'autoname'})[0]['fieldname']=='autoname')
	
	def test_schema(self):
		from webnotes.model.utils import read_doclist
		from webnotes.schema import make_table
		from webnotes.model.doclist import DocList
		
		make_table(DocList(read_doclist('DocType', 'DocType')))
			

			
if __name__=='__main__':
	unittest.main()