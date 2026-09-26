let images = document.getElementsByClassName("image");
let activeImages = document.getElementsByClassName("active");

for(let i=0; i<images.length ;i++ ){
	images[i].addEventListener('mouseover',function(){

		if(activeImages.length>0){
			activeImages[0].classList.remove("active");
		}

		this.classList.add("active")
		document.getElementById("featured").src = this.src
	})
}