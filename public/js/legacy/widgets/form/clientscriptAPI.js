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

// Client Side Scripting API
// ======================================================================================

$c_get_values = function(args, doc, dt, dn, user_callback) {
	var call_back = function(r,rt) {
		if(!r.message)return;
		if(user_callback) user_callback(r.message);
		
		var fl = args.fields.split(',');
		for(var i in fl) {
			locals[dt][dn][fl[i]] = r.message[fl[i]]; // set value
			if(args.table_field)
				refresh_field(fl[i], dn, args.table_field);
			else
				refresh_field(fl[i]);
		}
	}
	$c('webnotes.widgets.form.utils.get_fields',args,call_back);
}

get_server_fields = function(method, arg, table_field, doc, dt, dn, allow_edit, call_back) {
	if(!allow_edit)freeze('Fetching Data...');
	$c('runserverobj', args={'method':method, 'docs':compress_doclist(make_doclist(doc.doctype, doc.name)), 'arg':arg},
	function(r, rt) {
		if (r.message)  {
			var d = locals[dt][dn];
			var field_dict = r.message;
			for(var key in field_dict) {
				d[key] = field_dict[key];
				if (table_field) refresh_field(key, d.name, table_field);
				else refresh_field(key);
			}
		}
		if(call_back){
			doc = locals[doc.doctype][doc.name];
			call_back(doc, dt, dn);
		}
		if(!allow_edit)unfreeze();
    }
  );
}

set_multiple = function (dt, dn, dict, table_field) {
	var d = locals[dt][dn];
	
	// set value
	for(var key in dict) {
		d[key] = dict[key];
		if(!table_field) refresh_field(key);	
	}

	// refresh table
	if(table_field) {
		refresh_field(table_field);
		return;	
	}
	
}


set_field_tip = function(n,txt) {
	var df = wn.meta.get_docfield(cur_frm.doctype, n, cur_frm.docname);
	if(df)df.description = txt;

	if(cur_frm && cur_frm.fields_dict) {
		if(cur_frm.fields_dict[n])
			cur_frm.fields_dict[n].comment_area.innerHTML = replace_newlines(txt);
		else
			console.log('[set_field_tip] Unable to set field tip: ' + n);
	}
}

var refresh_field = function(n, docname, table_field) {
	// multiple
	if(table_field) {
		cur_frm.fields_dict[table_field].refresh_data();
	} else {
		if(typeof n=="string") n = [n];
		$.each(n, function(i, v) { cur_frm.refresh_field(v); });
	}
}
var refresh_many = refresh_field;

set_field_options = function(n, txt) {
	cur_frm.set_df_property(n, 'options', txt)
}

set_field_permlevel = function(n, level) {
	cur_frm.set_df_property(n, 'permlevel', level)
}

toggle_field = function(n, hidden) {
	var df = Meta.get_field(cur_frm.doctype, n, cur_frm.docname);
	if(df) {
		df.hidden = hidden;
		refresh_field(n);
	}
	else {
		console.log((hidden ? "hide_field" : "unhide_field") + " cannot find field " + n);
	}
}

hide_field = function(n) {
	if(cur_frm) {
		if(n.substr) toggle_field(n, 1);
		else { for(var i in n) toggle_field(n[i], 1) }
	}
}

unhide_field = function(n) {
	if(cur_frm) {
		if(n.substr) toggle_field(n, 0);
		else { for(var i in n) toggle_field(n[i], 0) }
	}
}

get_field_obj = function(fn) {
	return cur_frm.fields_dict[fn];
}

// set missing values in given doc
set_missing_values = function(doc, dict) {
	// dict contains fieldname as key and "default value" as value
	var fields_to_set = {};
	
	$.each(dict, function(i, v) { if (!doc[i]) { fields_to_set[i] = v; } });
	
	if (fields_to_set) { set_multiple(doc.doctype, doc.name, fields_to_set); }
}