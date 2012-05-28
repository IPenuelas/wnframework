import wn, wn.model

class Session(wn.model.DocList):
	def before_insert(self):
		"""create sid and boot"""
		import json
		self.set('name', wn.random_sha1())
		self.set('user', wn.request.params['user'])
		self.set('boot', json.dumps(self.get('boot', {})))
	
	def boot_user(self):
		"""boot non-guest user with roles and defaults"""
			