"""build and sync schema from doctypes"""

std_columns = ({
	'fieldname': 'name',
	'fieldtype': 'data',
	'reqd': 1
},)
std_columns_main = ({
		'fieldname': 'updated_on',
		'fieldtype': 'timestamp',
	},
	{
		'fieldname': 'created_by',
		'fieldtype': 'link',
		'options': 'Profile'
	},
	{
		'fieldname': 'created_on',
		'fieldtype': 'timestamp',
	},
	{
		'fieldname': 'updated_by',
		'fieldtype': 'link',
		'options': 'Profile'
	},
	{
		'fieldname': 'docstatus',
		'fieldtype': 'int',
	},
	{
		'fieldname': '_data',
		'fieldtype': 'text',
	})

	
std_columns_table = ({
		'fieldname': 'parent',
		'fieldtype': 'data',
	},
	{
		'fieldname': 'parenttype',
		'fieldtype': 'Link',
		'options': 'DocType'	
	},
	{
		'fieldname': 'parentfield',
		'fieldtype': 'Link'
	},
	{
		'fieldname': 'idx',
		'fieldtype': 'Integer',
		'length': 5
	})
	
type_map = {
	'currency':		('decimal', '18,6')
	,'int':		('int', '11')
	,'float':		('decimal', '18,6')
	,'check':		('int', '1')
	,'small text':	('smalltext', '')
	,'long text':	('longtext', '')
	,'code':		('text', '')
	,'text editor':	('text', '')
	,'date':		('date', '')
	,'time':		('time', '')
	,'timestamp':	('timestamp', '')
	,'text':		('text', '')
	,'data':		('varchar', '180')
	,'link':		('varchar', '180')
	,'password':	('varchar', '180')
	,'select':		('varchar', '180')
	,'read only':	('varchar', '180')
	,'blob':		('longblob', '')
}
	
def create_table(conn, doclistobj):
	"""make table based on given info"""
	
	template = """create table `%s` (%s) ENGINE=InnoDB CHARACTER SET=utf8"""

	columns, constraints = [], []

	# add std columns
	for d in std_columns:
		make_col_definition(d, columns, constraints)

	# is table
	for d in (doclistobj.get('istable') and std_columns_table or std_columns_main):
		make_col_definition(d, columns, constraints)

	# fields
	for d in doclistobj.get({"doctype":"DocField"}):
		make_col_definition(d, columns, constraints)
	
	query = template % (doclistobj.get('name'), ',\n'.join(columns + constraints))
	#print query
	
	conn.sql("""set foreign_key_checks=0""")	
	conn.sql(query)
	conn.sql("""set foreign_key_checks=1""")	

def remake_table(conn, doclistobj):
	"""drop table and remake it, backing up the data first"""
	import utils, os
	
	name = doclistobj.get('name')
	data = conn.sql("""select * from `%s`""" % name, as_dict=1)
	fname = utils.random_string(15) + '.txt'
	with open(fname, 'w') as tmpfile:
		tmpfile.write(str(data))
		
	conn.sql("""set foreign_key_checks=0""")	
	conn.sql("""drop table `%s`""" % name)
	
	make_table(doclistobj)
	conn.sql("""set foreign_key_checks=0""")	
	
	with open(fname, 'r') as tmpfile:
		mega_list = eval(tmpfile.read())
	
	for m in mega_list:
		conn.begin()
		conn.insert(m)
		conn.commit()
	
	conn.sql("""set foreign_key_checks=1""")
	os.remove(fname)
	

def make_col_definition(d, columns, constraints):
	"""make col definition from docfield"""
	
	if not d.get('fieldtype').lower() in type_map:
		return
	
	db_type, db_length = type_map[d.get("fieldtype").lower()]
	if db_length or d.get("length"):
		db_length = '(%s)' % str(db_length or d.get("length"))
	
	if d.get('fieldtype').lower() in ('int', 'float', 'currency', 'check') and d.get('default')==None:
		d['default'] = 0
		
	args = {
		"fieldtype": db_type,
		"length": db_length,
		"fieldname": d.get('fieldname'),
		"default": d.get("default")!=None and (' not null default "%s"' %\
		 	str(d.get('default')).replace('"', '\"')) or '',
		"keys": d.get('fieldname')=='name' and ' primary key' or '',
		"not_null": d.get('reqd') and ' not null' or ''
	}
	
	columns.append('`%(fieldname)s` %(fieldtype)s%(length)s%(not_null)s%(default)s%(keys)s' % args)
	
	# constraints
	if d.get('fieldtype')=='Link':
		constraints.append('constraint foreign key `%s`(`%s`) references `%s`(name)' % \
			(d.get('fieldname'), d.get('fieldname'), d.get('options')))
		
	if d.get('index'):
		constraints.append('index `%s`(`%s`)' % (d.get('fieldname'), d.get('fieldname')))

