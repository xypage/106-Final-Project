var globalFeed = true;

// ajax, proceed with whatever is in the funciton as soon as the document is ready
$(document).ready(function () {
	// Submit a new form using AJAX when the "submit" button is clicked
	console.log("ready");
	// call function to load all posts
	load_all_posts();
	$("#new_post_form").submit(function (event) {
		console.log("we are in the submit function");
		event.preventDefault();
		var xhttp = new XMLHttpRequest();
		xhttp.open("POST", "/new_post", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		xhttp.onload = function () {
			if (this.status == 200) {
				clear_posts();
				if (globalFeed == true) {
					load_all_posts();
				} else {
					load_following_posts();
				}
				// Clear the form for new post entry
				document.getElementById("new_post_form").reset();
			} else {
				alert("Error: " + this.responseText);
			}
		};
		xhttp.onerror = function () {
			console.log("Error: " + this.responseText);
		};
		xhttp.send($(this).serialize());
	});

	$("#personal_feed").on("click", function () {
		console.log("personal_feed button was pressed");
		clear_posts();
		load_following_posts();
		globalFeed = false;
	});

	$("#global_feed").on("click", function () {
		console.log("global_feed button was pressed");
		clear_posts();
		load_all_posts();
		globalFeed = true;
	});
});

// function to clear posts currently in the feed before loading new ones
function clear_posts() {
	document.getElementById("feed_contents").innerHTML = "";
}

// function to load all posts (aka global feed)
function load_all_posts() {
	console.log("we are in the load_all_posts function");
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/get_all_posts", true);
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			var data = JSON.parse(this.responseText);
			document.getElementById("feed_label").innerText = "Global Feed";
    		displayPosts(data);
		} else if (this.readyState == 4 && this.status != 200) {
			console.log("Error: " + this.responseText);
		}
	};
	xhttp.send();
}

// function to load the posts of only the users the current user follows
function load_following_posts() {
	console.log("we are in the load_following_posts function");
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/get_following_posts", true);
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			var data = JSON.parse(this.responseText);
			document.getElementById("feed_label").innerText = "Personal Feed";
			displayPosts(data);
		} else if (this.readyState == 4 && this.status != 200) {
			console.log("Error: " + this.responseText);
		}
	};
	xhttp.send();
}

function displayPosts(data) {
    var user_feed = document.getElementById("feed_contents");
	for (var i = 0; i < data.length; i++) {
		var post = document.createElement("div");
		post.classList.add("post");

		var headerContainer = document.createElement("div");
		headerContainer.classList.add("headerContainer");

		var name = document.createElement("a");
		name.classList.add("name");
		name.innerText = `${data[i].name} (${data[i].username})`;
		name.href = `/user/${data[i].username}`;
		headerContainer.appendChild(name);

		var timestamp = document.createElement("p");
		timestamp.classList.add("timestamp");
		timestamp.innerText = data[i].timestamp;
		headerContainer.appendChild(timestamp);

		var content = document.createElement("p");
		content.classList.add("content");
		content.innerText = data[i].content;

		post.appendChild(headerContainer);
		post.appendChild(content);

		user_feed.appendChild(post);
	}
}

// buttons to see personal and global feed
const personalFeedBut = document.querySelector("#personal_feed");
const globalFeedBut = document.querySelector("#global_feed");

//change the button color once it's pressed but will change back once the other button is pressed

personalFeedBut.addEventListener("click", () => {
	personalFeedBut.style.backgroundColor = "rgb(192, 140, 164)";
	globalFeedBut.style.backgroundColor = "#fbeee0";
});

globalFeedBut.addEventListener("click", () => {
	personalFeedBut.style.backgroundColor = "#fbeee0";
	globalFeedBut.style.backgroundColor = "rgb(192, 140, 164)";
});
