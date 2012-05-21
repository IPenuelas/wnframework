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

// opts { width, height, title, fields (like docfields) }

wn.ui.FieldGroup = function() {
	this.first_button = false;
	this.make_fields = function(body, fl) {	
		$(this.body).css('padding', '11px');
		this.fields_dict = {}; // reset
		for(var i=0; i<fl.length; i++) {
			var df = fl[i];
			var div = $('<div style="margin: 6px 0px">').appendTo(body);
			
			f = wn.ui.make_control({
				docfield: df,
				parent: div
			})
			
			this.fields_dict[df.fieldname] = f
			
			// first button primary ?
			if(df.fieldtype=='Button' && !this.first_button) {
				$(f.input).addClass('btn-info');
				this.first_button = true;
			}
		}
	}
	
	/* get values */
	this.get_values = function() {
		var ret = {};
		var errors = [];
		for(var key in this.fields_dict) {
			var f = this.fields_dict[key];
			var v = f.get_value ? f.get_value() : null;

			if(f.df.reqd && !v) 
				errors.push(f.df.label + ' is mandatory');

			if(v) ret[f.df.fieldname] = v;
		}
		if(errors.length) {
			msgprint('<b>Please check the following Errors</b>\n' + errors.join('\n'));
			return null;
		}
		return ret;
	}
	
	/* set field value */
	this.set_value = function(key, val){
		var f = this.fields_dict[key];
		if(f) {
			f.set_input(val);
			f.refresh_mandatory();
		}		
	}

	/* set values from a dict */
	this.set_values = function(dict) {	
		for(var key in dict) {
			if(this.fields_dict[key]) {
				this.set_value(key, dict[key]);
			}
		}
	}
	
	this.clear = function() {
		for(key in this.fields_dict) {
			var f = this.fields_dict[key];
			if(f) {
				f.set_input(f.df['default'] || '');				
			}
		}
	}
}

wn.ui.Dialog = function(opts) {
	
	this.opts = opts;
	this.display = false;
	
	this.make = function(opts) {
		if(opts) 
			this.opts = opts;
		if(!this.opts.width) this.opts.width = 480;
		
		if(!$('#dialog-container').length) {
			$('<div id="dialog-container">').appendTo('body');
		}
		
		this.wrapper = $('<div class="dialog_wrapper">').appendTo('#dialog-container').get(0);

		if(this.opts.width)
			this.wrapper.style.width = this.opts.width + 'px';

		this.make_head();
		this.body = $('<div class="dialog_body">').appendTo(this.wrapper).get(0);
		
		if(this.opts.fields)
			this.make_fields(this.body, this.opts.fields);
	}
	
	this.make_head = function() {
		var me = this;
		this.appframe = new wn.ui.AppFrame(this.wrapper);
		this.appframe.$titlebar.find('.close').unbind('click').click(function() {
			if(me.oncancel)me.oncancel(); me.hide();
		});
		this.set_title(this.opts.title);
	}
	
	this.set_title = function(t) {
		this.appframe.$titlebar.find('.appframe-title').html(t || '');
	}
	
	this.set_postion = function() {
		// place it at the center
		this.wrapper.style.left  = (($(window).width() - parseInt(this.wrapper.style.width))/2) + 'px';
        this.wrapper.style.top = ($(window).scrollTop() + 60) + 'px';

		// place it on top
		top_index++;
		$(this.wrapper).css('z-index', top_index);	
	}
	
	/** show the dialog */
	this.show = function() {
		// already live, do nothing
		if(this.display) return;

		// set position
		this.set_postion()

		// show it
		$(this.wrapper).toggle(true);

		// hide background
		freeze();

		this.display = true;
		wn.ui.cur_dialog = this;

		// call onshow
		if(this.onshow)this.onshow();
	}

	this.hide = function() {
		// call onhide
		if(this.onhide) this.onhide();

		// hide
		unfreeze();
		$(this.wrapper).toggle(false);

		// flags
		this.display = false;
		wn.ui.cur_dialog = null;
	}
		
	this.no_cancel = function() {
		this.appframe.$titlebar.find('.close').toggle(false);
	}

	if(opts) this.make();

}

wn.ui.Dialog.prototype = new wn.ui.FieldGroup();
wn.ui.cur_dialog = null;

// close open dialogs on ESC
$(document).bind('keydown', function(e) {
	if(wn.ui.cur_dialog && !wn.ui.cur_dialog.no_cancel_flag && e.which==27) {
		wn.ui.cur_dialog.hide();
	}
});