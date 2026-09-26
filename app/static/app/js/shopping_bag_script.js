let updateButtons = document.getElementsByClassName("update_button");
for(let i=0; i<updateButtons.length; i++){
	updateButtons[i].addEventListener( 'click' , function(){
		this.style.display = "none"	
	})
}

