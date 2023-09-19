function likePost(post_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/like/" + post_id);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onload = function () {
    	if (this.readyState == 4 && this.status == 200) {
            console.log("Successfully liked")
    		// document.querySelector(".bio").innerText = new_bio_text;
            // set post to liked
    	}
    };
    xhttp.send();

}