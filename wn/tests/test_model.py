import unittest, sys

sys.path.append('controllers')
sys.path.append('lib')

import wn, wn.model
import wn.backends
import conf

class TestModels(unittest.TestCase):
	def setUp(self):
		self.files = wn.backends.get('files')

		self.files.insert_doclist([{"doctype":"DocType", "name":"Test", 
			"controller":"wn.tests.test_controller.Test", "backend":"mysql"},
		{"doctype":"DocField", "fieldtype":"Data", "fieldname":"test_data", "reqd":1},
		{"doctype":"DocField", "fieldtype":"Date", "fieldname":"test_date"},
		{"doctype":"DocField", "fieldtype":"Text", "fieldname":"test_text"},
		{"doctype":"DocField", "fieldtype":"Int", "fieldname":"test_int"},
		{"doctype":"DocField", "fieldtype":"Float", "fieldname":"test_float"},
		{"doctype":"DocField", "fieldtype":"Currency", "fieldname":"test_currency"},
		])
		
		
		self.conn = wn.backends.get('mysql', user='root', password=conf.db_root_password)
		self.conn.create_user_and_database('test1', 'test1')
		self.conn.create_table(wn.model.get('DocType', 'Test'))
	
	def test_get(self):
		wn.model.DocList([{"name":"r1", "test_data":"hello", "doctype":"Test"}]).insert()
		obj = wn.model.get('Test', 'r1')
		self.assertTrue(obj.test_property)
		self.assertTrue(obj.get('test_data')=='hello')
		
	def test_fail(self):
		self.assertRaises(wn.NotFoundError, wn.model.get, 'Test', 'r2')
		
	def test_duplicate(self):
		wn.model.DocList([{"name":"r1", "test_data":"hello", "doctype":"Test"}]).insert()
		self.assertRaises(Exception, wn.model.DocList([{"name":"r1", "test_data":"hello", 
			"doctype":"Test"}]).insert, None)
			
	def test_update(self):
		doclist = wn.model.DocList([{"name":"r1", "test_data":"hello", "doctype":"Test"}])
		doclist.insert()
		doclist.set('test_data', 'world')
		doclist.update()
		self.assertEquals(wn.model.get_value('Test', 'r1', 'test_data'), 'world')
		
	def tearDown(self):
		self.files.remove('DocType', 'files')
		self.conn.sql("drop database test1")
		self.conn.close()
		
if __name__=='__main__':
	unittest.main()
