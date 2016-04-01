var username=false,password1=false,password2=false,email=false;
function zoomdisabler(){
	if(screen.width<600){
		document.getElementById("layout").setAttribute("content","width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no");
	}
}
function controllauser(){
	var textBox = document.getElementById("username");
	var textLength = textBox.value.length;
	var flag=0;
	var patt1=new RegExp(" ");
	if(patt1.test(textBox.value)==true){
		document.getElementById("checkuser").innerHTML='Inserire un username senza spazi';
		if(textLength==2) document.getElementById("checkuser").innerHTML+=' e di lunghezza almeno 2';
		username=false;
		flag=1;
	}
	else{
		document.getElementById("checkuser").innerHTML=''
		username=true;
		flag=0;
	}
	if(textLength<2){
		if(flag==0){
			document.getElementById("checkuser").innerHTML='Inserire un username di lunghezza almeno 2';
		}
		else document.getElementById("checkuser").innerHTML+=' e di lunghezza almeno 2';
		username=false;
	}
	else{
		if(flag==0){
			document.getElementById("checkuser").innerHTML='';
		}
		username=true;
	}
}

function controllapass(){
	var passw = /[a-zA-Z0-9]{8,20}/;
	var textBox = document.getElementById("password1");  
	if(textBox.value.match(passw)){ 
		document.getElementById("checkpass").innerHTML='';
		password1=true;
	}  
	else{   
		document.getElementById("checkpass").innerHTML='La password inserita non è corretta';
		password1=false;
	}
}
function controllapsw2(){
	var passBox = document.getElementById("password1");
	var textBox = document.getElementById("password2");
	if(textBox.value!=passBox.value || passBox.value==''){
		document.getElementById("checkconf").innerHTML='La conferma non corrisponde alla password';
		password2=false;
	}
	else{
		document.getElementById("checkconf").innerHTML='';
		password2=true;
	}
}
function controllamail(){
	var mail = document.getElementById("email");
    var filter = /[a-zA-Z0-9_.+-]+\@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9_.+-]+/;
    if (!filter.test(mail.value)){
    	document.getElementById("checkmail").innerHTML='Mail non valida';
    	email=false;
	}
	else{
		email=true;
		document.getElementById("checkmail").innerHTML='';
	}
}
function controllatuz(){
	controllauser();
	controllapass();
	controllapsw2();
	controllamail();
	if(!username || !password1 || !password2 || !email){
        return false;
	}
	else return true;
}
function controllarec(){
	controllamail();
	if(!email){
        return false;
	}
	else return true;
}