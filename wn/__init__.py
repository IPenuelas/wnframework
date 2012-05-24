"""
wn server
"""
import os

root_path = os.path.join(os.sep, *os.path.abspath(os.path.dirname(__file__)).split(os.sep)[:-2])

def code_style(txt):
	"""return code friendly names"""
	txt = txt.replace(' ', '_')
	import re
	return re.sub("[^a-zA-Z0-9_]", '', txt)

def traceback():
	"""Returns the traceback of the Exception"""
	import sys, traceback, string
	type, value, tb = sys.exc_info()
	
	body = "Traceback (innermost last):\n"
	list = traceback.format_tb(tb, None) + traceback.format_exception_only(type, value)
	body = body + "%-20s %s" % (string.join(list[:-1], ""), list[-1])
	
	return body
	
def random_sha1():
	import hashlib, datetime
	return hashlib.sha1(str(datetime.datetime.now())).hexdigest()
	
# Errors
class ValidationError(Exception): pass

