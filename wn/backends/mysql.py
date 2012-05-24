import wn

class MySQLBackend():
	backend_type = 'mysql'
	in_transaction = False
	column_map = {}
	def __init__(self, host=None, user=None, password=None, db_name=None):
		"""create connection and use database if not root"""
		import MySQLdb, conf
		
		if not db_name:
			db_name = user or getattr(conf, 'db_name')
		
		self.conn = MySQLdb.connect(host=host or getattr(conf, 'db_host', 'localhost'), 
			user = user or db_name,
			passwd = password or getattr(conf, 'db_password'))
	
		self.conn.converter[246]=float
		self.conn.set_character_set('utf8')
		self.cursor = self.conn.cursor()
		
		if db_name!='root':
			self.use(db_name)
		
	def use(self, db_name):
		"""switch to database db_name"""
		self.conn.select_db(db_name)
		self.cur_db_name = db_name
		
	def sql(self, query, values=(), as_dict = 1, as_list = 0, debug=0, ignore_ddl=0):
		"""execute an sql statement"""
		# in transaction validations
		self.check_transaction_status(query)
			
		# execute
		try:
			if values!=():
				if debug: 
					if wn.response:
						wn.response.log(query % tuple(values))
					else:
						print query % tuple(values)
				self.cursor.execute(query, values)
				
			else:
				if debug: print query
				self.cursor.execute(query)
				
		except Exception, e:
			# ignore data definition errors
			if ignore_ddl and e.args[0] in (1146,1054,1091):
				pass
			else:
				raise e

		# scrub output if required
		if as_list:
			ret = self.fetch_as_list()
		elif as_dict:
			ret = self.fetch_as_dict()
		else:
			ret = self.cursor.fetchall()		

		return ret

			
	def check_transaction_status(self, query):
		"""update `in_transaction`, validate ddl is not called within a transaction and
		ensure too many write are not throttled in the system causing it to crash"""
		
		command = query and query.strip().split()[0].lower()
		
		if self.in_transaction and command in ('start', 'alter', 'drop', 'create'):
			raise Exception, 'This statement can cause implicit commit'

		if query and command=='start':
			self.in_transaction = True
			self.transaction_writes = 0
			
		if query and command in ('commit', 'rollback'):
			self.in_transaction = False

		if self.in_transaction and command in ('update', 'insert'):
			self.transaction_writes += 1
			if self.transaction_writes > 5000:
				if self.auto_commit_on_many_writes:
					self.commit()
					self.begin()
				else:
					wn.msgprint('A very long query was encountered. If you are trying to import data, please do so using smaller files')
					raise Exception, 'Bad Query!!! Too many writes'
	
	def begin(self):
		self.sql("start transaction")
		
	def commit(self):
		self.sql("commit")
	
	def rollback(self):
		self.sql("rollback")
	
	def fetch_as_dict(self):
		result = self.cursor.fetchall()
		ret = []
		for r in result:
			dict = {}
			for i in range(len(r)):
				dict[self.cursor.description[i][0]] = r[i]
			ret.append(dict)
		return ret
		
	def fetch_as_list(self):
		return [[c for c in r] for r in self.cursor.fetchall()]

	def filter_columns(self, obj):
		"""filter dict with valid table columns"""
		if not obj.get('doctype'):
			raise Exception, "doctype not set"
			
		columns = self.get_columns(obj.get('doctype'))
		ret = {}
		for c in columns:
			if obj.get(c) is not None:
				ret[c] = obj.get(c)
								
		return ret

	def get(self, doctype_name, name=None):
		"""get list of records from the backend, 
		   pass filters in a dict or using (`doctype_name`, `name`)
		   add the "doctype" property by default
		"""
		if isinstance(doctype_name, basestring):
			rec = self.sql("""select * from `%s` where name=%s""" % (doctype_name, '%s'), name)
			if rec: 
				rec[0]['doctype'] = doctype_name
				rec = rec + self.get_children(rec[0])
				return rec
		else:
			filters = doctype_name
			conditions, values = [], []
			for key in filters:
				if key=='doctype':
					doctype_name = filters[key]
				else:
					conditions.append('`'+key+'`=%s')
					values.append(filters[key])
								
			return [d.update('doctype', filters['doctype']) for d in \
				self.sql("""select * from `%s` where %s""" % (doctype_name,
				' and '.join(conditions)), values)]

	def insert(self, doc):
		"""insert dict like object in database where property `doctype` is the table"""
		import warnings
		with warnings.catch_warnings(record=True) as w:
			obj = self.filter_columns(doc)
			self.sql("""insert into `%s` (%s) values (%s)""" % (doc.get('doctype'), 
				', '.join(obj.keys()), (', %s' * len(obj.keys()))[2:]), obj.values())

			# raise exception if mandatory is not 
			if w and (str(w[0].message).endswith('default value')):
				raise wn.ValidationError, str(w[0].message)

	def update(self, doc):
		"""update dict like object in database where property `doctype` is the table"""
		obj = self.filter_columns(doc)
		self.sql("""update `%s` set %s where name=%s""" % (doc.get('doctype'),
			', '.join(["`%s`=%s" % (key, '%s') for key in obj.keys()]), '%s'), 
			obj.values() + [obj.get('name')])
	
	def remove(self, doctype_name, name):
		pass
	
	def insert_doclist(self, doclist):
		"""insert doclist"""
		map(self.insert, doclist)
		
	def update_doclist(self, doclist):
		"""update doclist"""
		map(self.update, doclist)
	
	def get_doclist(self, filters):
		"""get mulitple doclists"""
		main_list = self.get(filters)
		out = []
		for doc in main_list:
			out.append([doc].extend(self.get_children(doc)))
				
		return out

	def get_children(self, doc):
		"""get children of the given doc"""
		# TODO
		return []
	
	def get_value(self, doctype_name, name, key, default=None):
		"""get single value"""
		res = self.sql("""select `%s` from `%s` where name=%s""" % (key, doctype_name, '%s'), 
			name)
		return res and res[0].get(key, default) or default
	
	def get_columns(self, table):
		"""get table columns"""
		if not table in self.column_map:
			self.column_map[table] = [c[0] for c in self.sql("desc `%s`" % table, as_list=True)]

		return self.column_map[table]
	
	def get_tables(self):
		"""get list of tables"""
		return [c[0] for c in self.sql("show tables", as_list=True)]
	
	def create_user_and_database(self, db_name=None, password=None, user=None):
		"""create MySQL db with user and database as `db_name` and password as `db_password`"""
		import conf
		
		# default from conf
		if not db_name: db_name = conf.db_name
		if not password: password = conf.db_password
		if not user: user = getattr(conf, 'user', db_name)
		
		try:
			self.sql("drop user '%s'@'localhost';" % user)
		except Exception, e:
			if e.args[0]!=1396: raise e

		self.sql("create user %s@'localhost' identified by %s", (user, password))
		self.sql("create database if not exists `%s`" % db_name)
		self.sql("grant all privileges on `%s` . * to '%s'@'localhost'" % (user, db_name))
		self.sql("flush privileges")
		self.sql("use `%s`" % db_name)
	
	def create_table(self, doclist):
		"""create table"""
		from wn.backends import mysql_schema
		mysql_schema.create_table(self, doclist)
	
	def close(self):
		self.conn and self.conn.close()

		import wn.backends
		del wn.backends.connections[self.backend_type]