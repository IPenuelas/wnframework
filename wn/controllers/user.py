import wn.model

class User(wn.model.DocList):
	def autoname(self):
		if not self.get('name'):
			self.set('name', self.get('email'))
