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

// assign to is lined to todo
// refresh - load todos
// create - new todo
// delete to do

wn.provide("wn.ui.form");

wn.ui.form.AssignTo = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		var me = this;
		this.wrapper = $('<div>\
			<div class="assignments"></div>\
		</div>').appendTo(this.parent);

		this.$list = this.wrapper.find(".assignments");
		
		this.parent.find(".btn").click(function() {
			me.add();
		});
	},
	refresh: function() {
		if(this.frm.doc.__islocal) {
			this.parent.toggle(false);
			return;
		}
		this.parent.toggle(true);

		var me = this;
		$c('webnotes.widgets.form.assign_to.get', {
			doctype: me.frm.doctype,
			name: me.frm.docname
		}, function(r,rt) {
			me.render(r.message)
		})
	},
	render: function(d) {
		var me = this;
		this.$list.empty();
		if(this.dialog) {
			this.dialog.hide();			
		}
		
		for(var i=0; i<d.length; i++) {	
			$.extend(d[i], wn.user_info(d[i].owner));
			
			$(repl('<div class="alert alert-info">\
				<span class="avatar avatar-small"><img src="%(image)s" /></span> %(fullname)s \
				<a class="close" href="#" style="top: 4px;"\
					data-owner="%(owner)s">&times;</a></div>', d[i]))
				.appendTo(this.$list);
		}

		// set remove
		this.$list.find('a.close').click(function() {
			$c('webnotes.widgets.form.assign_to.remove', {
				doctype: me.frm.doctype,
				name: me.frm.docname,
				assign_to: $(this).attr('data-owner')		
			}, function(r,rt) {me.render(r.message);});
			return false;
		});
	},
	add: function() {
		var me = this;
		if(!me.dialog) {
			me.dialog = new wn.ui.Dialog({
				title: 'Add to To Do',
				width: 350,
				fields: [
					{fieldtype:'Link', fieldname:'assign_to', options:'Profile', 
						label:'Assign To', 
						description:'Add to To Do List of', reqd:true},
					{fieldtype:'Data', fieldname:'description', label:'Comment'}, 
					{fieldtype:'Date', fieldname:'date', label:'Complete By'}, 
					{fieldtype:'Select', fieldname:'priority', label:'Priority',
						options:'Low\nMedium\nHigh', 'default':'Medium'},
					{fieldtype:'Check', fieldname:'notify', label:'Notify By Email'},
					{fieldtype:'Button', label:'Add', fieldname:'add_btn'}
				]
			});
			me.dialog.fields_dict.add_btn.input.onclick = function() {
				
				var assign_to = me.dialog.fields_dict.assign_to.get_value();
				if(assign_to) {
					$c('webnotes.widgets.form.assign_to.add', {
						doctype: me.frm.doctype,
						name: me.frm.docname,
						assign_to: assign_to,
						description: me.dialog.fields_dict.description.get_value(),
						priority: me.dialog.fields_dict.priority.get_value(),
						date: me.dialog.fields_dict.date.get_value(),
						notify: me.dialog.fields_dict.notify.get_value()
					}, function(r,rt) {me.render(r.message);});
				}
			}
		}
		me.dialog.clear();
		me.dialog.show();
	}
});

