import unittest, sys
sys.path.append('controllers')
sys.path.append('lib')

import wn, wn.model, wn.app
import wn.backends

class TestInstall(unittest.TestCase):
	def setUp(self):
		import wn.install
		wn.install.setup_db()
		wn.install.setup_doctypes()
		
	def test_add_user(self):
		wn.model.new([{"doctype":"User", "email":"test@erpnext.com", "first_name":"Test", 
			"password":"test13"}]).insert()
		self.assertEquals(wn.model.get('User', "test@erpnext.com").get('password'), 'test13')
		
		self.assertEquals(wn.app.test("/?_method=wn.app.login&user=test@erpnext.com&password=test13"), 
			{"info":["Logged In"]})
		
		
	def tearDown(self):
		import wn.install
		wn.install.remove()
		wn.backends.close()
		
if __name__=='__main__':
	unittest.main()