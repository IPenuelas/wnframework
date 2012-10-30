// Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
// 
// MIT License (MIT)
// 
// Permission is hereby granted, free of charge, to any person obtaining a 
// copy of this software and associated documentation files (the "Software"), 
// to deal in the Software without restriction, including without limitation 
// the rights to use, copy, modify, merge, publish, distribute, sublicense, 
// and/or sell copies of the Software, and to permit persons to whom the 
// Software is furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
// CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
// OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// 

wn.provide("wn.perm");
var READ = 0, WRITE = 1, CREATE = 2; 
var SUBMIT = 3, CANCEL = 4, AMEND = 5;

$.extend(wn.perm, {
	
	get_perm: function(doctype, dn, ignore_submit) {
		var perm = [[0,0],];
		if(in_list(user_roles, 'Administrator')) 
			perm[0][READ] = 1;		
		
		$.each(wn.meta.get("DocPerm", {parent:doctype}), function(i, p) {
			var pl = cint(p.permlevel?p.permlevel:0);
			// if user role
			if(in_list(user_roles, p.role)) {
				// if field match
				if(wn.perm.check_match(p, doctype, dn)) { // new style
					if(!perm[pl])
						perm[pl] = [];
						
					if(!perm[pl][READ]) {
						if(cint(p.read)) perm[pl][READ]=1; else perm[pl][READ]=0;
					}
					if(!perm[pl][WRITE]) { 
						if(cint(p.write)) { perm[pl][WRITE]=1; perm[pl][READ]=1; }
						else perm[pl][WRITE]=0;
					}
					if(!perm[pl][CREATE]) { 
						if(cint(p.create))perm[pl][CREATE]=1; else perm[pl][CREATE]=0;
					}
					if(!perm[pl][SUBMIT]) { 
						if(cint(p.submit))perm[pl][SUBMIT]=1; else perm[pl][SUBMIT]=0;
					}
					if(!perm[pl][CANCEL]) { 
						if(cint(p.cancel))perm[pl][CANCEL]=1; else perm[pl][CANCEL]=0;
					}
					if(!perm[pl][AMEND]) { 
						if(cint(p.amend)) perm[pl][AMEND]=1;  else perm[pl][AMEND]=0;
					}
				}
			}
		});

		return perm;
	},
	
	check_match: function(p, doctype, name) {
		if(!name) return true;
		var out =false;
		if(p.match) {
			if(user_defaults[p.match]) {
				for(var i=0;i<user_defaults[p.match].length;i++) {
					 // user must have match field in defaults
					if(user_defaults[p.match][i]==locals[doctype][name][p.match]) {
					    // must match document
			  			return true;
					}
				}
				return false;
			} else if(!locals[doctype][name][p.match]) { // blanks are true
				return true;
			} else {
				return false;
			}
		} else {
			return true;
		}
	},	
	
});