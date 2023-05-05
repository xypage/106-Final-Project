const body = document.querySelector("body");
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
			if (this.readyState == 4 && this.status == 200) {
				document.querySelector(".bio").innerText = new_bio_text;
			}
		};
		const body = { new_bio: new_bio_text };
		xhttp.send(JSON.stringify(body));
	};
}

const following_button = document.getElementById("following_button");
console.log(following_button);
following_button.onclick = () => {
	console.log("Following button pressed");
	let screen_cover = document.createElement("div");
	screen_cover.classList.add("screen_cover");
	screen_cover.onclick = (e) => {
		if (e.target != screen_cover) {
			// avoids doing this when you click on a child element, like the unfollow buttons
			return;
		}
		body.removeChild(screen_cover);
	};

	let following_popup = document.createElement("div");
	following_popup.classList.add("popup");

	fetch(`/user/${user.username}/following`, {
		method: "GET",
	})
		.then((response) => response.json())
		.then((following_users) => {
			if (following_users.length == 0) {
				let no_followed = document.createElement("h1");
				no_followed.innerText = "Not following anyone";
				following_popup.appendChild(no_followed);
			} else {
				let following_table = document.createElement("table");
				following_table.classList.add("follow_table");
				following_users.forEach((followed) => {
					let row = document.createElement("tr");
					row.classList.add("row");

					let user_label = document.createElement("td");
					let user_link = document.createElement("a");
					user_link.innerText = `${followed.name} (${followed.username})`;
					user_link.href = `/user/${followed.username}`;
					user_label.appendChild(user_link);
					row.appendChild(user_label);

					// only let them unfollow if it's their profile
					if (user.is_current) {
						let unfollow_block = document.createElement("td");
						let unfollow_button = document.createElement("button");
						unfollow_button.innerText = "Unfollow " + followed.name;
						unfollow_button.classList.add("unfollow_button");
						unfollow_button.onclick = () => {
							fetch(`/unfollow_user/${followed.id}`, { method: "POST" })
								.then((response) => {
									following_table.removeChild(row);
								})
								.catch((error) => {
									console.log("Error unfollowing " + followed.username, error);
								});
						};
						unfollow_block.appendChild(unfollow_button);
						row.appendChild(unfollow_block);
					}

					following_table.appendChild(row);
				});
				following_popup.appendChild(following_table);
			}
		})
		.catch((error) => {
			alert("Error getting following");
		});

	screen_cover.appendChild(following_popup);
	// body.insertBefore(following_popup, body.firstChild);
	body.appendChild(screen_cover);
};
const followers_button = document.getElementById("followers_button");
followers_button.onclick = () => {
	console.log("Followers button pressed");
	let screen_cover = document.createElement("div");
	screen_cover.classList.add("screen_cover");
	screen_cover.onclick = (e) => {
		if (e.target != screen_cover) {
			// avoids doing this when you click on a child element, like the unfollow buttons
			return;
		}
		body.removeChild(screen_cover);
	};

	let followers_popup = document.createElement("div");
	followers_popup.classList.add("popup");

	fetch(`/user/${user.username}/followed_by`, {
		method: "GET",
	})
		.then((response) => {
			console.log(response);
			return response.json();
		})
		.then((followers) => {
			if (followers.length == 0) {
				let no_followers = document.createElement("h1");
				no_followers.innerText = "No followers";
				followers_popup.appendChild(no_followers);
			} else {
				let followers_table = document.createElement("table");
				followers_table.classList.add("follow_table");
				followers.forEach((follower) => {
					let row = document.createElement("tr");
					row.classList.add("row");

					let user_label = document.createElement("td");
					let user_link = document.createElement("a");
					user_link.innerText = `${follower.name} (${follower.username})`;
					user_link.href = `/user/${follower.username}`;
					user_label.appendChild(user_link);
					row.appendChild(user_label);

					// Only let them remove followers if it's the current user
					if (user.is_current) {
						let unfollow_block = document.createElement("td");
						let unfollow_button = document.createElement("button");
						unfollow_button.innerText =
							"Stop " + follower.name + " from following";
						unfollow_button.classList.add("unfollow_button");
						unfollow_button.onclick = () => {
							fetch(`/remove_follower/${follower.id}`, { method: "POST" })
								.then((response) => {
									followers_table.removeChild(row);
								})
								.catch((error) => {
									console.log(
										"Error making " + follower.username + " unfollow",
										error
									);
								});
						};
						unfollow_block.appendChild(unfollow_button);
						row.appendChild(unfollow_block);
					}

					followers_table.appendChild(row);
				});
				followers_popup.appendChild(followers_table);
			}
		})
		.catch((error) => {
			alert("Error getting followers", error);
		});

	screen_cover.appendChild(followers_popup);
	// body.insertBefore(following_popup, body.firstChild);
	body.appendChild(screen_cover);
};
