import unittest, sys

sys.path.append('controllers')
sys.path.append('lib')

import wn, wn.model
import wn.backends
import conf

class TestModels(unittest.TestCase):
	def setUp(self):
		self.conn = wn.backends.get('files')
		self.conn.insert_doclist([{"doctype":"DocType", "name":"Test", 
			"controller":"wn.tests.test_controller.Test"},
		{"doctype":"DocField", "fieldtype":"Data", "fieldname":"test_data", "reqd":1},
		{"doctype":"DocField", "fieldtype":"Date", "fieldname":"test_date"},
		{"doctype":"DocField", "fieldtype":"Text", "fieldname":"test_text"},
		{"doctype":"DocField", "fieldtype":"Int", "fieldname":"test_int"},
		{"doctype":"DocField", "fieldtype":"Float", "fieldname":"test_float"},
		{"doctype":"DocField", "fieldtype":"Currency", "fieldname":"test_currency"},
		])
		
	def tearDown(self):
		self.conn.remove("DocType", "Test")
		
	def test_model_get(self):
		testobj = wn.model.get('DocType', 'Test')
		self.assertTrue(testobj.test_property)

if __name__=='__main__':
	try:
		unittest.main()
	finally:
		if wn.messages:
			print wn.messages