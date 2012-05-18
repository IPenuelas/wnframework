wn.provide('wn.views');
wn.views.breadcrumbs = function(parent, module, doctype, name) {
	$(parent).empty();
	var $bspan = $('<span class="breadcrumbs"></span>');

	if(name) {
		$bspan.append('<span class="appframe-title">' + name + '</span>');
	} else if(doctype) {
		$bspan.append('<span class="appframe-title">' + doctype + ' List </span>');
	} else if(module) {
		$bspan.append('<span class="appframe-title">' + module + '</span>');		
	}

	if(name && doctype && (!wn.model.get_value('DocType', doctype, 'issingle'))) {
		$bspan.append(repl(' in <a href="#!List/%(doctype)s">%(doctype)s List</a>',
			{doctype: doctype}))
	}
	
	if(doctype && module && wn.modules && wn.modules[module]) {
		$bspan.append(repl(' in <a href="#!%(module_page)s">%(module)s</a>',
			{module: module, module_page: wn.modules[module] }))
	}
	$bspan.appendTo(parent);
}
