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

wn.provide('wn.login')

wn.pages.login.on('load', function() {
	var wrapper = this.wrapper;
	wrapper.appframe = new wn.ui.AppFrame($(wrapper).find('.appframe-area'));
	wrapper.appframe.title('Login');
	wrapper.appframe.$w.find('.close').toggle(false);

	$('#login_btn').click(wn.login.do)
		
	$('#password').keypress(function(ev){
		if(ev.which==13 && $('#password').val())
			wn.login.do();
	});
	$(document).trigger('login_rendered');	
});

// Login
wn.login.do = function(){

    var args = {};
    args['usr']=$("#login_id").val();
    args['pwd']=$("#password").val();
    if($('#remember_me').attr("checked")) 
      args['remember_me'] = 1;

	$('#login_btn').set_working();

	wn.call({
		method: 'login',
		args: args,
		callback: function(r) {
			$('#login_btn').done_working();
		    if(r.message=="Logged In"){
		        window.location.href='app.html';
		    } else {
		        $('#login_message').html('<span style="color: RED;">'+(r.message)+'</span>');
		    }			
		}
	})
}


wn.login.show_forgot_password = function(){
    // create dialog
	var d = new wn.ui.Dialog({
		title:"Forgot Password",
		fields: [
			{'label':'Email Id', 'fieldname':'email_id', 'fieldtype':'Data', 'reqd':true},
			{'label':'Email Me A New Password', 'fieldname':'run', 'fieldtype':'Button'}
		]
	});

	$(d.fields_dict.run.input).click(function() {
		var values = d.get_values();
		if(!values) return;
		wn.call({
			method:'reset_password',
			args: { user: values.email_id },
			callback: function() {
				d.hide();
			}
		})
	})
	d.show();
}
