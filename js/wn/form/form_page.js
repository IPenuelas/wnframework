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

// form in a page

wn.views.FormPage = Class.extend({
	init: function(doctype, name) {
		this.doctype = doctype;
		this.name = name;
		this.doclist = wn.model.get(doctype, name);
		this.make_page();
		this.set_breadcrumbs(doctype, name);
		this.form = wn.ui.new_form({
			doclist: this.doclist,
			doc: this.doclist.doc,
			parent: this.$w,
			appframe: this.page.appframe
		});
		this.make_toolbar(doctype, name);
		wn.ui.toolbar.recent.add(doctype, name, true);
	},
	set_breadcrumbs: function(doctype, name) {
		wn.views.breadcrumbs(this.page.appframe, 
			wn.model.get_value('DocType', doctype, 'module'), doctype, name);
	},
	make_page: function() {
		var page_name = wn.get_route_str();
		this.page = wn.container.add_page(page_name);
		wn.ui.make_app_page({parent:this.page});
		wn.container.change_to(page_name);
		this.$w = $(this.page).find('.layout-main-section');
		this.$sidebar = $(this.page).find('.layout-side-section');
	},
	make_toolbar: function() {
		this.make_save_btn();
		
		if(!this.doclist.doc.get('__islocal')) {
			this.make_action_buttons();
			this.assign_to = new wn.ui.AssignTo({form_page: this});
			this.comments = new wn.ui.Comments({form_page: this});
			this.tags = new wn.ui.TagEditor({form_page: this});	
		}

		this.make_help_buttons();
	},
	make_save_btn: function() {
		var me = this;
		this.save_btn = this.page.appframe.add_button('Save', function() { 
			wn.freeze();
			me.doclist.save(function(r) {
				wn.unfreeze();
				if(!r.exc) {
					var doc = me.doclist.doc;
					if(doc.get('name') != wn.get_route()[2]) {
						wn.re_route[window.location.hash] = 
							wn.make_route_str(['Form', doc.get('doctype'), doc.get('name')])
						wn.set_route('Form', doc.get('doctype'), doc.get('name'));
					}				
				}
			}, me.save_btn);
		});
		
		$(this.save_btn).data('progress_html', 'Saving...')
		
		this.doclist.on('change', function() {
			me.save_btn.addClass('btn-warning').attr('title', 'Not Saved');
		});
		
		this.doclist.on('reset', function() {
			me.save_btn.removeClass('btn-warning').attr('title', 'Saved');
		});			
	},

	make_action_buttons: function() {
		this.action_btn_group = $('<div class="btn-group">\
		<button class="btn dropdown-toggle btn-small" data-toggle="dropdown">\
			Actions\
			<span class="caret"></span>\
		</button>\
		<ul class="dropdown-menu">\
			<li><a href="#" class="action-new"><i class="icon icon-plus"></i> New</a></li>\
			<li><a href="#" class="action-print"><i class="icon icon-print"></i> Print...</a></li>\
			<li><a href="#" class="action-email"><i class="icon icon-envelope"></i> Email...</a></li>\
			<li><a href="#" class="action-copy"><i class="icon icon-file"></i> Copy</a></li>\
			<li><a href="#" class="action-refresh"><i class="icon icon-refresh"></i> Refresh</a></li>\
			<li><a href="#" class="action-delete"><i class="icon icon-remove"></i> Delete</a></li>\
		</ul>\
		</div>').appendTo(this.page.appframe.$w.find('.appframe-toolbar'));
		this.action_btn_group.find('.dropdown-toggle').dropdown();
		
		var me = this;

		this.action_btn_group.find('.action-new').click(function() {
			var new_doclist = wn.model.create(me.doctype);
			wn.set_route('Form', me.doctype, new_doclist.doc.get('name'));
			return false;
		});

		this.action_btn_group.find('.action-copy').click(function() {
			var new_doclist = me.doclist.copy();
			wn.set_route('Form', me.doctype, new_doclist.doc.get('name'));
			return false;
		});
		
	},
	make_help_buttons: function() {
		var meta = this.form.meta.doc;
		var me = this;
		if(meta.get('description')) {
			this.page.appframe.add_help_button(meta.get('description'));			
		}
		
		// doctype button
		this.doctype_btn = this.page.appframe.add_button(meta.get('name'), function() {
			wn.set_route('List', meta.get('name'));
		}).addClass('btn-inverse');
		this.doctype_btn.parent().css('float', 'right');
	}
});

