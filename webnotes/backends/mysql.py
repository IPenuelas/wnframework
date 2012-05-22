class MySQLBackend():
	def __init__(self, host=None, user=None, password=None):
		import MySQLdb, conf
		
		db_name = user or getattr(conf, 'db_name')
		
		self.conn = MySQLdb.connect(host=host or getattr(conf, 'db_host', 'localhost'), 
			user = db_name
			passwd= password or getattr(conf, 'db_password'))
			
		self.conn.converter[246]=float
		self.conn.set_character_set('utf8')
		self.cursor = self.conn.cursor()
		
		if user!='root':
			self.use(db_name)
		
	def use(self, db_name):
		"""switch to database db_name"""
		self._conn.select_db(db_name)
		self.cur_db_name = db_name
		
	def sql(self, query, values=(), as_dict = 1, as_list = 0, debug=0, ignore_ddl=0):
		"""execute an sql statement"""
		# in transaction validations
		self.check_transaction_status(query)
			
		# execute
		try:
			if values!=():
				if debug: webnotes.msgprint(query % values)
				self.cursor.execute(query, values)
				
			else:
				if debug: webnotes.msgprint(query)
				self.cursor.execute(query)
				
		except Exception, e:
			# ignore data definition errors
			if ignore_ddl and e.args[0] in (1146,1054,1091):
				pass
			else:
				raise e

		# scrub output if required
		if as_dict:
			return self.fetch_as_dict()
		elif as_list:
			return self.fetch_as_list()
		else:
			return self.cursor.fetchall()
			
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
					webnotes.msgprint('A very long query was encountered. If you are trying to import data, please do so using smaller files')
					raise Exception, 'Bad Query!!! Too many writes'
					
	def fetch_as_dict(self):
		result = self.cursor.fetchall()
		ret = []
		for r in result:
			dict = {}
			for i in range(len(r)):
				dict[self.cursor.description[i][0]] = r[i]
			ret.append(dict)
		return ret
		
	def fetch_as_list(self, res):
		return [[c for c in r] for r in self.cursor.fetchall()]
		
	def get(self, doctype_name, doc_name):
		pass

	def insert(self, doc):
		pass
		
	def update(self, doc):
		pass

	def remove(self, doctype_name, doc_name):
		pass
		