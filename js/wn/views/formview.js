// render formview

wn.provide('wn.views.formview');

wn.views.formview = {
	show: function(dt, dn) {
		// show doctype
		wn.model.with_doctype(dt, function() {
			wn.model.with_doc(dt, dn, function(dn, r) {
				if(r && r['403']) return; // not permitted
				
				if(!(wn.model.get(dt, dn))) {
					wn.container.change_to('404');
					return;
				}
				
				new wn.views.FormView(dt, dn);
			});
		})
	},
	create: function(dt) {
		var new_name = LocalDB.create(dt);
		wn.set_route('Form', dt, new_name);
	}
}

wn.views.FormView = Class.extend({
	init: function(doctype, name) {
		this.doctype = doctype;
		this.name = name;
		this.make_page();	
	},
	make_page: function() {
		var page_name = wn.get_route_str();
		this.page = wn.container.add_page(page_name);
		wn.ui.make_app_page({parent:this.page});
		wn.container.change_to(page_name);
	},
});
