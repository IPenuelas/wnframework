user = None

from webob import Request, Response
import wsgiref.handlers
import wn, wn.model

def application(environ, start_response):
	"""wsgi application method"""
	wn.request = Request(environ)
	wn.response = AppResponse()
	try:
		handle()
		wn.response.make()
	except Exception, e:
		wn.response.body = wn.traceback()

	return wn.response(environ, start_response)

class AppResponse(Response):
	"""attach set json, csv response types"""
	json = {}
	messages = []
	errors = []
	logs = []
	def error(self, txt): self.errors.append(txt)
	def message(self, txt): self.messages.append(txt)
	def log(self, txt): self.logs.append(txt)

	def make(self):
		"""make response body"""
		if self.messages:
			self.json['messages'] = self.messages
		if self.errors:
			self.json['errors'] = self.errors
		if self.logs:
			self.json['logs'] = self.logs
		if self.json:
			import json
			self.body = json.dumps(self.json, default=json_type_handler)
			
def handle():
	"""handle method"""
	load_session()
	if '_method' in wn.request.params:
		try:
			m = wn.request.params['_method'].split('.')
			method = getattr(__import__('.'.join(m[:-1]), fromlist=True), m[-1])
		except Exception, e:
			wn.response.error('method not found')
		if not method in whitelisted:
			wn.response.error('method not allowed')
		else:
			method()
	else:
		wn.response.error('no method')	

def load_session():
	"""load session from cookie or parameter"""
	wn.sid = wn.request.cookies.get('sid') or wn.request.params.get('sid') or 'guest'
	wn.session = wn.model.get('Session', wn.sid) or wn.model.DocList([{'user':'Guest'}])

whitelisted = []
guest_methods = []
def whitelist(allow_guest=False, allow_roles=[]):
	"""
	decorator for whitelisting a function @wn.app.whitelist()
	
	Note: if the function is allowed to be accessed by a guest user,
	it must explicitly be marked as allow_guest=True
	
	for specific roles, set allow_roles = ['Administrator'] etc.
	"""
	def innerfn(fn):
		global whitelisted, guest_methods
		whitelisted.append(fn)

		if allow_guest:
			guest_methods.append(fn)

		if allow_roles:
			if not (set(allow_roles) & set(wn.user.roles())):
				raise PermissionError, "Method not allowed"

		return fn

	return innerfn

def json_type_handler(obj):
	"""convert datetime objects to string"""
	if hasattr(obj, 'strftime'):
		return str(obj)
		
	
