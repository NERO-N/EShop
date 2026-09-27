// slides script
const slidesInputs = document.querySelectorAll('[name="hero_image"]');
const length=slidesInputs.length
let count = 0;


 setInterval(changeslide,5000);

function changeslide()
{	
	slidesInputs[count].checked=true;
	count++;
	if(count==length)
		count=0;
}


// reveal animation script 
window.addEventListener('scroll', reveal);

function reveal (){
	const divToReveal = document.getElementsByClassName('toReveal');
	let windowHeight = window.innerHeight;  // a modifier
	let revealPoint = 200;

	for(let i=0; i<divToReveal.length ; i++){
		if (!divToReveal[i].classList.contains('active'))
		{
			let revealTop = divToReveal[i].getBoundingClientRect().top;
			if( revealPoint < windowHeight - revealTop){
				divToReveal[i].classList.add('active');
			}
		}
	}
}


