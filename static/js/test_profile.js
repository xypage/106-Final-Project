if (!user.is_current) {
    // If this isn't the current user, manage the follow/unfollow buttons
	const follow_button = document.getElementById("follow_button");
	const unfollow_button = document.getElementById("unfollow_button");

	follow_button.onclick = (e) => {
		var xhttp = new XMLHttpRequest();
		xhttp.open("POST", "/follow_user/" + user.user_id, true);
		xhttp.onreadystatechange = function () {
			console.log(this);
			if (this.readyState == 4 && this.status == 200) {
				console.log("Followed");
			} else if (this.readyState == 4 && this.status != 200) {
				console.log("Error: " + this.responseText);
			}
		};
		xhttp.send();

		follow_button.classList.add("hidden");
		unfollow_button.classList.remove("hidden");
	};

	unfollow_button.onclick = (e) => {
		var xhttp = new XMLHttpRequest();
		xhttp.open("POST", "/unfollow_user/" + user.user_id, true);
		xhttp.onreadystatechange = function () {
			console.log(this);
			if (this.readyState == 4 && this.status == 200) {
				console.log("Unfollowed");
			} else if (this.readyState == 4 && this.status != 200) {
				console.log("Error: " + this.responseText);
			}
		};
		xhttp.send();

		follow_button.classList.remove("hidden");
		unfollow_button.classList.add("hidden");
	};
} else {
    // and if it is, manage the edit bio button
	const edit_bio_button = document.getElementById("edit_bio");

	edit_bio_button.onclick = (e) => {
		let new_bio_text = prompt("Enter your new bio", user.bio);

		var xhttp = new XMLHttpRequest();
		xhttp.open("POST", "/edit_bio");
		xhttp.setRequestHeader("Content-Type", "application/json");
		xhttp.onload = function () {
			if(this.readyState == 4 && this.status == 200) {
                document.querySelector(".bio").innerText = new_bio_text;
            }
		};
		const body = { new_bio: new_bio_text };
		xhttp.send(JSON.stringify(body));
	};
}
