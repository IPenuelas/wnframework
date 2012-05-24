import wn.model

class User(wn.model.DocList):
	def autoname(self):
		self.set('name', self.get('email'))
