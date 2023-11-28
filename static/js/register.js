var countre=1;
function add_more_field(){
    countre+=1
    html=' <input type="text" placeholder="phone" name="phone'+countre+''"><br>\
		<input type="password" placeholder="password" name="password'+countre+'"><br>\
		<input type="text" placeholder="name" name="name'+countre+'"><br>\
        <button onclick="add_more_field()">Add more +</button>\
		<button type="submit">Register</button>'\
		var form = document.getElementById('contactForm')
		form.innerHtml+= html
}