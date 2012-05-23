"""
wn server
"""
import os

messages = []
errors = []
root_path = os.path.join(os.sep, *os.path.abspath(os.path.dirname(__file__)).split(os.sep)[:-2])

def msgprint(txt): 
	"""add to messages"""
	messages.append(txt)

def code_style(txt):
	"""return code friendly names"""
	return txt.replace(' ','_').replace('-', '_').replace('/', '_').lower()

# Errors
class ValidationError(Exception): pass

