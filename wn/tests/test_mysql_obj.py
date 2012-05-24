import unittest, sys

sys.path.append('controllers')
sys.path.append('lib')

import wn
import wn.backends, wn.model
import conf

class TestMySQLObj(unittest.TestCase):
	def setUp(self):
		self.conn = wn.backends.get('mysql_obj', user='root', password=conf.db_root_password)
		self.conn.create_user_and_database('test1', 'test1')
		self.conn.create_table(wn.model.get('DocType', '_statement'))

	def tearDown(self):
		self.conn.sql("drop database test1")
		self.conn.close()
		
	def test_insert(self):
		rec = {"doctype":"Test", "name":"r1", "test_data":"hello"}
		self.conn.insert(rec)
 		#print self.conn.sql("""select * from _statement""")
		self.assertEquals(self.conn.get("Test", "r1").get("test_data"), rec.get("test_data"))		
		
if __name__=='__main__':
	unittest.main()
