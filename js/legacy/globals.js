wn.provide('wn.widgets.form');
wn.provide('wn.widgets.report');
wn.provide('wn.utils');
wn.provide('wn.model');
wn.provide('wn.profile');
wn.provide('wn.session');
wn.provide('_f');
wn.provide('_p');
wn.provide('_r');
wn.provide('_c');
wn.provide('_e');
wn.provide('_startup_data')

// setup custom binding for history
wn.settings.no_history = 1;

// constants
var NEWLINE = '\n';

// user
var profile=null;
var user=null;
var user_defaults=null;
var user_roles=null;
var user_fullname=null;
var user_email=null;
var user_img = {};

var pscript = {};
var selector=null; 

// Name Spaces
// ============

// form
var _f = {};

// print
var _p = {};

// email
var _e = {};

// report buidler
var _r = {};
var FILTER_SEP = '\1';

// API globals
var frms={};
var cur_frm=null;
var pscript = {};
var validated = true;
var validation_message = '';
var tinymce_loaded = null;