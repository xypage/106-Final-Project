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
        };
    }
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
        };
    }
    xhttp.send();

    follow_button.classList.remove("hidden");
    unfollow_button.classList.add("hidden");
};

console.log(user);