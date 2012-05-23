import unittest, sys

sys.path.append('controllers')
sys.path.append('lib')

import wn
import wn.backends
import conf
from wn.backends import mysql_schema

class TestMySQL(unittest.TestCase):
	def setUp(self):
		self.conn = wn.backends.get('mysql', user='root', password=conf.db_root_password)
		self.conn.create_user_and_database('test1', 'test1')

	def tearDown(self):
		self.conn.sql("drop database test1")
		self.conn.close()
	
	def test_create_table(self):
		from wn.model import DocList
		table_def = DocList([{"doctype":"DocType", "name":"Test"},
		{"doctype":"DocField", "fieldtype":"Data", "fieldname":"test_data", "reqd":1},
		{"doctype":"DocField", "fieldtype":"Date", "fieldname":"test_date"},
		{"doctype":"DocField", "fieldtype":"Text", "fieldname":"test_text"},
		{"doctype":"DocField", "fieldtype":"Int", "fieldname":"test_int"},
		{"doctype":"DocField", "fieldtype":"Float", "fieldname":"test_float"},
		{"doctype":"DocField", "fieldtype":"Currency", "fieldname":"test_currency"},
		])
		mysql_schema.create_table(self.conn, table_def)
		self.assertTrue("Test" in self.conn.get_tables())
	
	def test_insert(self):
		self.test_create_table()
		rec = {"doctype":"Test", "name":"r1", "test_data":"hello"}
		self.conn.insert(rec)
		self.assertEquals(self.conn.get("Test", "r1")[0].get("test_data"), rec.get("test_data"))
	
	def test_mandatory(self):
		self.test_create_table()
		rec = {"doctype":"Test", "name":"r1"}
		self.assertRaises(wn.ValidationError, self.conn.insert, (rec))
	
	def test_update(self):
		self.test_insert()
		rec = {"doctype":"Test", "name":"r1", "test_data":"hello sir"}
		self.conn.update(rec)
		self.assertEquals(self.conn.get("Test", "r1")[0].get("test_data"), rec.get("test_data"))
	

if __name__=='__main__':
	try:
		unittest.main()
	finally:
		if wn.messages:
			print wn.messages