# Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
# 
# MIT License (MIT)
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from __future__ import unicode_literals
import sys, os
import webnotes
import webnotes.utils

sql = None
session = None
errdoc = ''
errdoctype = ''
errmethod = ''

@webnotes.whitelist(allow_guest=True)
def startup():
	import webnotes
	import webnotes.session_cache

	webnotes.response.update(webnotes.session_cache.get())

def cleanup_docs():
	from webnotes.model.doc import Document
	if webnotes.response.get('docs'):
		clean = []
		for d in webnotes.response['docs']:
			if isinstance(d, Document):
				clean.append(d.fields)
			else:
				clean.append(d)
		webnotes.response['docs'] = clean

@webnotes.whitelist()
def runserverobj(arg=None):
	import webnotes.widgets.form.run_method
	webnotes.widgets.form.run_method.runserverobj()

@webnotes.whitelist(allow_guest=True)
def logout():
	webnotes.login_manager.logout()

@webnotes.whitelist()
def dt_map():
	import webnotes
	import webnotes.model.utils
	from webnotes.model.code import get_obj
	from webnotes.model.doc import Document
	
	form = webnotes.form
	
	dt_list = webnotes.model.utils.expand(form.get('docs'))
	from_doctype = form.get('from_doctype')
	to_doctype = form.get('to_doctype')
	from_docname = form.get('from_docname')
	from_to_list = form.get('from_to_list')
	
	dm = get_obj('DocType Mapper', from_doctype +'-' + to_doctype)
	dl = dm.dt_map(from_doctype, to_doctype, from_docname, Document(fielddata = dt_list[0]), [], 
		from_to_list)
	
	webnotes.response['docs'] = dl

@webnotes.whitelist()
def load_month_events():
	import webnotes

	mm = webnotes.form.get('month')
	yy = webnotes.form.get('year')
	m_st = str(yy) + '-' + str(mm) + '-01'
	m_end = str(yy) + '-' + str(mm) + '-31'

	import webnotes.widgets.event
	webnotes.response['docs'] = webnotes.widgets.event.get_cal_events(m_st, m_end)

@webnotes.whitelist()
def uploadfile():
	import webnotes.utils
	import webnotes.utils.file_manager
	import json

	ret = []

	try:
		if webnotes.form.get('from_form'):
			webnotes.utils.file_manager.upload()
		else:
			if webnotes.form.get('method'):
				m = webnotes.form['method']
				modulename = '.'.join(m.split('.')[:-1])
				methodname = m.split('.')[-1]

				__import__(modulename)
				import sys
				moduleobj = sys.modules[modulename]
				ret = getattr(moduleobj, methodname)()
	except Exception, e:
		webnotes.msgprint(e)
		webnotes.errprint(webnotes.utils.getTraceback())

	webnotes.response['type'] = 'iframe'
	if not webnotes.response.get('result'):
		webnotes.response['result'] = """<script>
			window.parent.wn.upload.callback("%s", %s);
		</script>""" % (webnotes.form.get('_id'),
			json.dumps(ret, default=webnotes.json_handler))

@webnotes.whitelist(allow_guest=True)
def reset_password():
	from webnotes.model.code import get_obj
	
	user = webnotes.form.get('user', '')
	if webnotes.conn.sql("""select name from tabProfile where name=%s""", user):
		import profile
		user_profile = profile.Profile(user)
		pwd = user_profile.reset_password()
		user_profile.send_new_pwd(pwd)
		
		webnotes.msgprint("Password has been reset and sent to your email id.")
	else:
		webnotes.msgprint("No such user (%s)" % user)


def handle():
	"""handle request"""
	cmd = webnotes.form['cmd']

	if cmd!='login':
		# login executed in webnotes.auth
		try:
			execute_cmd(cmd)
		except webnotes.ValidationError, e:
			#webnotes.errprint(webnotes.utils.getTraceback())
			webnotes.errprint(e)
			webnotes.conn.rollback()
		except:
			webnotes.errprint(webnotes.utils.getTraceback())
			webnotes.conn and webnotes.conn.rollback()
				
	print_response()

	if webnotes.conn:
		webnotes.conn.close()

def execute_cmd(cmd):
	"""execute a request as python module"""
	validate_cmd(cmd)
	method = get_method(cmd)
	if not method in webnotes.whitelisted:
		webnotes.response['403'] = 1
		webnotes.msgprint('Not Allowed, %s' % str(method))
		raise Exception, 'Not Allowed, %s' % str(method)
		
	if not webnotes.conn.in_transaction:
		webnotes.conn.begin()

	if 'arg' in webnotes.form:
		# direct method call
		ret = method(webnotes.form.get('arg'))
	else:
		ret = method()

	# returns with a message
	if ret:
		webnotes.response['message'] = ret

	# update session
	webnotes.session_obj.update()

	if webnotes.conn.in_transaction:
		webnotes.conn.commit()

def get_method(cmd):
	"""get method object from cmd"""
	if '.' in cmd:
		cmd_parts = cmd.split('.')
		module_string = ".".join(cmd_parts[:-1])
		fn_string = cmd_parts[-1]
		module = __import__(module_string, fromlist=[module_string.split('.')[-1].encode('utf-8')])
		method = getattr(module, fn_string)
	else:
		method = globals()[cmd]
	return method
	
def validate_cmd(cmd):
	# check if there is no direct possibility of malicious script injection
	if cmd.startswith('webnotes.model.code'):
		raise Exception, 'Cannot call any methods from webnotes.model.code directly from the handler'

	if cmd.startswith('webnotes.model.db_schema'):
		raise Exception, 'Cannot call any methods from webnotes.model.db_schema directly from the handler'

	if cmd.startswith('webnotes.conn'):
		raise Exception, 'Cannot call database connection method directly from the handler'
		
def print_response():
	print_map = {
		'csv': print_csv,
		'iframe': print_iframe,
		'download': print_raw,
		'json': print_json,
		'page': print_page
	}
	
	print_map.get(webnotes.response.get('type'), print_json)()

def print_page():
	"""print web page"""
	from website.utils import render
	render(webnotes.response['page_name'])

def eprint(content):
	print content.encode('utf-8')

def print_json():	
	make_logs()
	cleanup_docs()
	add_cookies()

	eprint("Content-Type: text/html; charset: utf-8")
	print webnotes.cookies

	import json
	print_zip(json.dumps(webnotes.response, default=webnotes.json_handler))
		
def print_csv():
	eprint("Content-Type: text/csv; charset: utf-8")
	eprint("Content-Disposition: attachment; filename=%s.csv" % webnotes.response['doctype'].replace(' ', '_'))
	eprint("")
	eprint(webnotes.response['result'])

def print_iframe():
	eprint("Content-Type: text/html; charset: utf-8")
	eprint("")
	eprint(webnotes.response.get('result') or '')
	
	if webnotes.debug_log:
		import json
		eprint("""\
			<script>
				var messages = %(messages)s;
				if (messages.length) {
					for (var i in messages) {
						window.parent.msgprint(messages[i]);
					}
				}
				var errors = %(errors)s;
				if (errors.length) {
					for (var i in errors) {
						window.parent.console.log(errors[i]);
					}
				}
			</script>""" % {
				'messages': json.dumps(webnotes.message_log, default=webnotes.json_handler).replace(
					"'", "\\'"),
				'errors': json.dumps(webnotes.debug_log, default=webnotes.json_handler).replace("'", "\\'"),
			})

def print_raw():
	eprint("Content-Type: %s" % \
		mimetypes.guess_type(webnotes.response['filename'])[0] \
		or 'application/unknown'),
	eprint("Content-Disposition: filename=%s" % \
		webnotes.response['filename'].replace(' ', '_'))
	eprint("")
	eprint(webnotes.response['filecontent'])

def make_logs():
	"""make strings for msgprint and errprint"""
	import json
	from webnotes.utils import cstr
	if webnotes.debug_log:
		webnotes.response['exc'] = json.dumps("\n".join([cstr(d) for d in webnotes.debug_log]),
			default=webnotes.json_handler)

	if webnotes.message_log:
		webnotes.response['server_messages'] = json.dumps([cstr(d) for d in webnotes.message_log],
			default=webnotes.json_handler)

def add_cookies():
	"""if there ar additional cookies defined during the request, add them"""
	if webnotes.cookies or webnotes.add_cookies:
		for c in webnotes.add_cookies.keys():
			webnotes.cookies[c.encode('utf-8')] = \
				webnotes.add_cookies[c].encode('utf-8')

def print_zip(response):
	response = response.encode('utf-8')
	if accept_gzip() and len(response)>512:
		response = compressBuf(response)
		eprint("Content-Encoding: gzip")
		eprint("Content-Length: %d" % len(response))
	eprint("")
	print response

def accept_gzip():
	"""return true if client accepts gzip"""
	try:
		import string
		if string.find(os.environ["HTTP_ACCEPT_ENCODING"], "gzip") != -1:
			return True
		else:
			return False
	except:
		return False

def compressBuf(buf):
	import gzip, cStringIO
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf, compresslevel = 5)
	zfile.write(buf)
	zfile.close()
	return zbuf.getvalue()
