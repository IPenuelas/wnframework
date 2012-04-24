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

// build a form from a set of fields
wn.ui.Form = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
	},
	make_form: function() {
		// form
		var me = this;
		this.$form = $('<form class="form-horizontal">').appendTo(this.$w);
		
		if(this.fields[0].fieldtype!='Section Break') {
			me.make_fieldset('_first_section');
		}
		
		// controls
		$.each(this.fields, function(i, df) {
			// change section
			if(df.fieldtype=='Section Break') {
				me.make_fieldset(df.fieldname, df.label);
			} else {
				// make control 
				me.controls[df.fieldname] = wn.ui.make_control({
					docfield: df,
					parent: me.last_fieldset,
					doctype: me.doctype,
					docname: me.name
				});
			}
		});
	},
	make_fieldset: function(name, legend) {
		var $fset = $('<fieldset data-name="'+name+'"></fieldset>').appendTo(this.$form);
		if(legend) {
			$('<legend>').text(legend).appendTo($fset);
		}
		this.last_fieldset = $fset;
	},
	// listen for changes in model
	listen: function() {
		var me = this;
		if(this.doctype && this.name) {
			$(document).bind(wn.model.event_name(this.doctype, this.name), function(ev, key, val) {
				if(me.controls[key]) me.controls[key].set_input(val);
			});
		}
	}
});

wn.views.FormView = wn.ui.Form.extend({
	init: function(doctype, name) {
		this.doctype = doctype;
		this.name = name;
		this.meta = wn.model.get('DocType', doctype);
		this.doc = wn.model.get(doctype, name);
		this.controls = {};
		this.fields = $.map(this.meta.get('DocField', {}), function(d) { return d.fields; });
		this.make_page();
		this.make_form();
		this.listen();
	},
	make_page: function() {
		var page_name = wn.get_route_str();
		this.page = wn.container.add_page(page_name);
		wn.ui.make_app_page({parent:this.page});
		wn.container.change_to(page_name);
		this.$w = $(this.page).find('.layout-main-section');
	}
});

wn.ui.make_control = function(opts) {
	control_map = {
		'Check': wn.ui.CheckControl,
		'Data': wn.ui.Control,
		'Link': wn.ui.LinkControl,
		'Select': wn.ui.SelectControl,
		'Table': wn.ui.GridControl,
		'Text': wn.ui.TextControl
	}
	if(control_map[opts.docfield.fieldtype]) {
		return new control_map[opts.docfield.fieldtype](opts);
	} else {
		return null;		
	}
}

wn.ui.Control = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.make_body();
		this.make_input();
		this.$w.find('.control-label').text(this.docfield.label);
		this.set_init_value();
		if(this.no_label) {
			this.$w.find('.control-label').toggle(false);
		}
	},
	set_init_value: function() {
		if(this.doctype && this.docname) {
			this.set_input(wn.model.get_value(this.doctype, this.docname, this.docfield.fieldname));
		}
	},
	set_input: function(val) {
		this.$input.val(val);
	},
	set: function(val) {
		if(this.doctype && this.docname) {
			wn.model.set_value(this.doctype, this.docname, this.docfield.fieldname, val);
		} else {
			this.set_input(val);
		}		
	},
	get: function() {
		return this.$input.val();
	},
	make_input: function() {
		this.$input = $('<input type="text">').appendTo(this.$w.find('.controls'));
	},
	make_body: function() {
		this.$w = $('<div class="control-group">\
			<label class="control-label"></label>\
			<div class="controls">\
			</div>\
			</div>').appendTo(this.parent);
	},
	help_block: function(text) {
		if(!this.$w.find('.help-block').length) {
			this.$w.find('.controls').append('<div class="help-block">');
		}
		this.$w.find('.help-block').text(text);
	}
});

wn.ui.CheckControl = wn.ui.Control.extend({
	make_input: function() {
		this.$label = $('<label class="checkbox">').appendTo(this.$w.find('.controls'))
		this.$input = $('<input type="checkbox">').appendTo(this.$label);
	}
});

wn.ui.TextControl = wn.ui.Control.extend({
	make_input: function() {
		this.$input = $('<textarea type="text" rows="5">').appendTo(this.$w.find('.controls'));		
	}
});

wn.ui.SelectControl = wn.ui.Control.extend({
	make_input: function() {
		this.$input = $('<select>').appendTo(this.$w.find('.controls'));
		this.$input.add_options(this.docfield.options.split('\n'));
	}
});

wn.ui.LinkControl = wn.ui.Control.extend({
	make_input: function() {
		var me = this;
		this.$input_wrap = $('<div class="input-append">').appendTo(this.$w.find('.controls'));
		this.$input = $('<input type="text" />').appendTo(this.$input_wrap);
		$('<button class="btn"><i class="icon-search"></i></button>')
			.appendTo(this.$input_wrap)
			.click(function() {
				new wn.ui.Search({
					doctype: me.docfield.options,
					callback: function(val) {
						me.set(val);
					}
				});
			});
	}
});

wn.ui.GridControl = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.tabletype = this.docfield.options;
		wn.lib.import_slickgrid();
		this.make();
		this.set();
	},
	make: function() {
		var width = $(this.parent).parent('form:first').width();
		this.$w = $('<div style="height: 300px; border: 1px solid grey;"></div>')
			.appendTo(this.parent)
			.css('width', width);
			

		var options = {
			enableCellNavigation: true,
			enableColumnReorder: false
		};
		
		this.grid = new Slick.Grid(this.$w.get(0), [], 
			this.get_columns(), options);
		
	},
	get_columns: function() {
		var columns = $.map(wn.model.get('DocType', this.tabletype).get({doctype:'DocField'}), 
			function(d) {
				return {
					id: d.get('fieldname'),
					field: d.get('fieldname'),
					name: d.get('label'),
					width: 100
				}
			}
		);
		return [{id:'idx', field:'idx', name:'Sr', width: 40}].concat(columns);
	},
	set: function(val) {
		// refresh values from doclist
		var rows = wn.model.get(this.docfield.parenttype, this.docname)
			.get({parentfield:this.docfield.fieldname});
			
		this.grid.setData($.map(rows, 
			function(d) { return d.fields; }));
		this.grid.render();
	}
})
