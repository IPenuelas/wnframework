wn.ui.msgprint = function(message) {
	if(!wn.ui.msgprint_dialog) {
		wn.ui.msgprint_dialog = new wn.ui.Dialog({
			width: 500,
			title: 'Message'
		});
	}

	var d = wn.ui.msgprint_dialog;
	if(typeof(message)!='string')
		message = JSON.stringify(message);
		
	d.onhide = function() {
		$(d.body).empty();
	}
	
	if($(d.body).children().length) {
		$(d.body).append('<hr>');
	}
	$(d.body).append(message);
	
	d.show();
}

var msgprint = wn.ui.msgprint();