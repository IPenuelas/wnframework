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
		this.meta = wn.model.get('DocType', doctype);
		this.doc = wn.model.get(doctype, name);
		this.make_page();
		this.make_form();
	},
	make_page: function() {
		var page_name = wn.get_route_str();
		this.page = wn.container.add_page(page_name);
		wn.ui.make_app_page({parent:this.page});
		wn.container.change_to(page_name);
		this.wrapper = $(this.page).find('.layout-main-section');
	},
	make_form: function() {
		// form
		var me = this;
		this.$form = $('<form class="form-horizontal">').appendTo(this.wrapper);
		
		if(this.meta.get('DocField', {})[0].get('fieldtype')!='Section Break') {
			me.make_fieldset('_first_section');
		}

		// fieldsets
		this.meta.each('DocField', {fieldtype:'Section Break'}, function(df) {
			me.make_fieldset(df.get('fieldname'), df.get('label'));
		});
		
		// controls
		var fieldset = '_first_section';
		this.meta.each('DocField', function(df) {

			// change section
			if(df.get('fieldtype')=='Section Break') {
				fieldset = df.get('fieldname');
			} else {
				// make control 
				wn.ui.make_control({
					docfield: df.fields,
					parent: me.$form.find('fieldset[data-name="'+fieldset+'"]')
				});		
			}
		})
	},
	make_fieldset: function(name, legend) {
		var $fset = $('<fieldset data-name="'+name+'"></fieldset>').appendTo(this.$form);
		if(legend) {
			$('<legend>').text(legend).appendTo($fset);
		}
	}
});

wn.ui.make_control = function(opts) {
	control_map = {
		'Data': wn.ui.Control,
		'Check': wn.ui.CheckControl,
		'Text': wn.ui.TextControl,
		'Select': wn.ui.SelectControl,
		'Table': wn.ui.GridControl
	}
	if(control_map[opts.docfield.fieldtype]) {
		new control_map[opts.docfield.fieldtype](opts);
	}
}

wn.ui.Control = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.make_body();
		this.make_input();
		this.$w.find('.control-label').text(this.docfield.label);
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

wn.ui.GridControl = Class.extend({
	init: function(opts) {
		wn.lib.import_slickgrid();
		
		var width = $(opts.parent).parent('form:first').width();
		this.$w = $('<div style="height: 300px; border: 1px solid grey;"></div>')
			.appendTo(opts.parent)
			.css('width', width);
			
		var columns = $.map(wn.model.get('DocType', opts.docfield.options).get({doctype:'DocField'}), 
			function(d) {
				return {
					id: d.get('fieldname'),
					field: d.get('fieldname'),
					name: d.get('label'),
					width: 100
				}
			}
		);
		columns = [{id:'idx', field:'idx', name:'Sr', width: 40}].concat(columns);

		var options = {
			enableCellNavigation: true,
			enableColumnReorder: false
		};
		
		var grid = new Slick.Grid(this.$w.get(0), [], 
			columns, options);
	}
})
