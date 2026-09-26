// hide/display header script
let header = document.getElementsByTagName("header");
let lastscroll = 0;

window.addEventListener('scroll', headerDisplay);

function headerDisplay (){
	let newscroll = window.scrollY;

	if (newscroll > lastscroll) {
		header[0].style.top = "-130px";
	}
	else
	{
		header[0].style.top = "0px";	
	}
	lastscroll = newscroll
}