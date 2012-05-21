// jquery extensions
(function($) {
	$.fn.add_options = function(options_list) {
		// create options
		for(var i=0; i<options_list.length; i++) {
			var v = options_list[i];
			value = v.value || v;
			label = v.label || v;
			$('<option>').html(label).attr('value', value).appendTo(this);
		}
		// select the first option
		$(this).val(options_list[0].value || options_list[0]);
	}
	$.fn.set_working = function() {
		var ele = this.get(0);
		$(ele).attr('disabled', 'disabled');
		if(ele.loading_img) { 
			$(ele.loading_img).toggle(true);
		} else {
			ele.loading_img = $('<img src="images/lib/ui/button-load.gif" \
				style="margin-left: 4px; margin-bottom: -2px; display: inline;" />')
				.insertAfter(ele);
		}		
	}
	$.fn.done_working = function() {
		var ele = this.get(0);
		$(ele).attr('disabled', null);
		if(typeof ele.loading_img != 'undefined') { 
			$(ele.loading_img).toggle(false); 
		};
	}
})(jQuery);


// underscore extensions
$.extend(_, {
	get_or_set: function(obj, key, val) {
		if(typeof obj[key] === 'undefined')
			obj[key] = val;
		return obj[key];
	}
});
