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
"""
	Execute Patch Files

	Patch files usually lie in the "patches" module specified by "modules_path" in defs.py

	To run directly
	
	python lib/wnf.py patch patch1, patch2 etc
	python lib/wnf.py patch -f patch1, patch2 etc
	
	where patch1, patch2 is module name
"""
from __future__ import unicode_literals
import webnotes
import webnotes.utils

def run_all(patch_dict=None):
	"""run all pending patches"""
	import patches.patch_list
	patch_dict = patch_dict or patches.patch_list.patch_dict
	
	# special patch: version 00_00 executed first
	if patch_dict.get('00_00'):
		executed = get_executed_patches()
		run_single_version('00_00', patch_dict['00_00'], executed)
		
	# execute pending patches
	executed = get_executed_patches()
	for version in sorted(patch_dict):
		if version >= webnotes.conn.get_default('patch_version'):
			ret = run_single_version(version, patch_dict[version], executed)
			if ret == 'error': return
			
	
def run_single_version(version, patch_list, executed):
	for p in patch_list:
		pn = 'patches.' + version + '.' + p
		if pn not in executed:
			if not run_single(patchmodule = pn):
				log(pn + ': failed: STOPPED')
				return 'error'
	if version != '00_00':
		webnotes.conn.set_default('patch_version', version)	
	
def reload_doc(args):
	"""relaod a doc args {module, doctype, docname}"""	
	import webnotes.modules
	run_single(method = webnotes.modules.reload_doc, methodargs = args)

def run_single(patchmodule=None, method=None, methodargs=None, force=False):
	"""run a single patch"""
	import conf
	
	# don't write txt files
	conf.developer_mode = 0
	
	if force or method or not get_executed_patches(patchmodule):
		return execute_patch(patchmodule, method, methodargs)
	else:
		return True
		
def execute_patch(patchmodule, method=None, methodargs=None):
	"""execute the patch"""
	success = False
	block_user(True)
	webnotes.conn.begin()
	log('Executing %s in %s' % (patchmodule or str(methodargs), webnotes.conn.cur_db_name))
	try:
		if patchmodule:
			patch = __import__(patchmodule, fromlist=[patchmodule.split(".")[-1]])
			getattr(patch, 'execute')()
			update_patch_log(patchmodule)
			log('Success')
		elif method:
			method(**methodargs)
			
		webnotes.conn.commit()
		success = True
	except Exception, e:
		webnotes.conn.rollback()
		global has_errors
		has_errors = True
		tb = webnotes.utils.getTraceback()
		log(tb)
		import os
		if os.environ.get('HTTP_HOST'):
			add_to_patch_log(tb)

	block_user(False)
	return success

def add_to_patch_log(tb):
	"""add error log to patches/patch.log"""
	import conf, os
	with open(os.path.join(conf.modules_path,'erpnext','patches','patch.log'),'a') as patchlog:
		patchlog.write('\n\n' + tb)
	
def update_patch_log(patchmodule):
	"""update patch_file in patch log"""
	webnotes.conn.sql("""INSERT INTO `__PatchLog` VALUES (%s, now())""", \
		patchmodule)

def get_executed_patches(patchmodule=None):
	"""return True if is executed"""
	if patchmodule:
		p = webnotes.conn.sql("""select patch from __PatchLog where patch=%s""", patchmodule)
		if p:
			print "Patch %s already executed in %s" % (patchmodule, webnotes.conn.cur_db_name)
		return p
	else:
		return [p.patch for p in webnotes.conn.sql("""select distinct patch from __PatchLog""")]
	
def block_user(block):
	"""stop/start execution till patch is run"""
	webnotes.conn.begin()
	msg = "Patches are being executed in the system. Please try again in a few moments."
	webnotes.conn.set_global('__session_status', block and 'stop' or None)
	webnotes.conn.set_global('__session_status_message', block and msg or None)
	webnotes.conn.commit()

log_list = []
has_errors = False
def log(msg):
	log_list.append(msg)
