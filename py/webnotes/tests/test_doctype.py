# Test Cases
import unittest, webnotes

import webnotes.model.doctype 

class DocTypeTest(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		webnotes.conn.sql("""delete from __CacheItem""")
		
	def tearDown(self):
		webnotes.conn.rollback()

	def test_profile(self):
		doclist = webnotes.model.doctype.get('Profile', processed=True)
		self.assertEquals(len(filter(lambda d: d.fieldname=='first_name' and d.doctype=='DocField', 
			doclist)), 1)
		self.assertEquals(len(filter(lambda d: d.name=='DefaultValue' and d.doctype=='DocType', 
			doclist)), 1)
		self.assertEquals(len(filter(lambda d: d.parent=='DefaultValue' and d.doctype=='DocField'
			and d.fieldname=='defkey', doclist)), 1)
		
		# js code added
		self.assertTrue(doclist[0].fields.get('__js'))
		self.assertTrue(doclist[0].fields.get('__listjs'))
		self.assertTrue(doclist[0].fields.get('__css'))
		
		# test embedded js code
		self.assertTrue('wn.RoleEditor = Class.extend({' in doclist[0].fields.get('__js'))
		
		# check if exists in cache
		self.assertTrue(webnotes.conn.sql("""select `key` from __CacheItem 
			where `key`='Profile'"""))
		return doclist
		
	def test_select_options(self):
		doctypelist = webnotes.model.doctype.get('Role', processed=True)
		self.assertTrue('System' in doctypelist.getone({"fieldname":"module"}).options.split())
		
	def test_print_format(self):
		doctypelist = webnotes.model.doctype.get("Sales Order", processed=True)
		self.assertEquals(len(doctypelist.get({"doctype":"Print Format"})), 3)

	def test_with_cache(self):
		self.assertFalse(getattr(self.test_profile()[0], '__from_cache', False))
		
		# second time with cache
		self.assertTrue(getattr(self.test_profile()[0], '__from_cache', False))

	def test_doctype_doctype(self):
		doclist = webnotes.model.doctype.get('DocType')
		
		self.assertEquals(len(doclist.get({"fieldname":'issingle', "doctype":'DocField'})), 1) 
		self.assertEquals(len(doclist.get({"name":'DocField', "doctype":'DocType'})), 1) 
		self.assertEquals(len(doclist.get({"parent":'DocField', "doctype":'DocField', 
			"fieldname":"fieldname"})), 1) 

		# test raw cache
		self.assertTrue(webnotes.conn.sql("""select `key` from __CacheItem 
			where `key`='DocType:Raw'"""))
			
	def test_property_setter(self):
		doclist = webnotes.model.doctype.get('Profile')
		self.assertEquals(len(filter(lambda d: d.fieldname=='first_name' 
			and (d.hidden or 0)==0, doclist)), 1)

		webnotes.conn.sql("""delete from __CacheItem""")
				
		from webnotes.model.doc import Document
		ps = Document("Property Setter")
		ps.fields.update({
			'name': 'test',
			'doc_type': "Profile",
			'field_name': 'first_name',
			'doctype_or_field': 'DocField',
			'property': 'hidden',
			'value': 1
		})
		ps.save()

		doclist = webnotes.model.doctype.get('Profile')
		self.assertEquals(len(filter(lambda d: d.fieldname=='first_name' 
			and (d.hidden or 0)==1, doclist)), 1)

	def test_previous_field(self):
		doclist = webnotes.model.doctype.get('Profile')
		first_name_idx = doclist.getone({"fieldname":"first_name"}).idx
		last_name_idx = doclist.getone({"fieldname":"last_name"}).idx
		
		self.assertTrue(first_name_idx < last_name_idx)

		webnotes.conn.sql("""delete from __CacheItem""")
				
		from webnotes.model.doc import Document
		ps = Document("Property Setter")
		ps.fields.update({
			'name': 'test',
			'doc_type': "Profile",
			'field_name': 'first_name',
			'doctype_or_field': 'DocField',
			'property': 'previous_field',
			'value': 'last_name'
		})
		ps.save()

		doclist = webnotes.model.doctype.get('Profile')
		first_name_idx = doclist.getone({"fieldname":"first_name"}).idx
		last_name_idx = doclist.getone({"fieldname":"last_name"}).idx
		self.assertEquals(last_name_idx+1, first_name_idx)
		
	def test_get_link_fields(self):
		# link type
		doctypelist = webnotes.model.doctype.get_link_fields("DocType")
		self.assertTrue(len(doctypelist.get({"fieldname":"module", "fieldtype":"Link"})), 1)

		# link: type selects
		doctypelist = webnotes.model.doctype.get_link_fields("Role")
		self.assertTrue(len(doctypelist.get({"fieldname":"module", "fieldtype":"Select"})), 1)
