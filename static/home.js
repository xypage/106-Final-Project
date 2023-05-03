
var globalFeed = true;

// ajax, proceed with whatever is in the funciton as soon as the document is ready
$(document).ready(function() {
    // Submit a new form using AJAX when the "submit" button is clicked
    console.log("ready");
    // call function to load all posts
    load_all_posts();
    // call function to load unfollowed users
    load_unfollowed_users();
    // call function to load followed users
    load_followed_users();
    $("#new_post_form").submit(function(event) {
        console.log("we are in the submit function");
        event.preventDefault();
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/new_post", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.onload = function() {
            if (this.status == 200) {
                if (globalFeed == true){

                    // If succesful, append the new post to the page
                    var post = document.createElement("div");
                    post.classList.add("post");
                    var post_html = JSON.parse(this.responseText);
                    post.innerHTML = post_html;
                    document.getElementById('user_feed').appendChild(post);
                    // Clear the form for new post entry
                    document.getElementById("new_post_form").reset();
                }
            } else {
                alert("Error: " + this.responseText);
            }
        };
        xhttp.onerror = function() {
            console.log("Error: " + this.responseText);
        };
        xhttp.send($(this).serialize());
    });


    $("#personal_feed").on('click', function() {
        console.log("personal_feed button was pressed");
        load_following_posts();
        globalFeed = false;
    });

    $("#global_feed").on('click', function() {
        console.log("global_feed button was pressed");
        load_all_posts();
        globalFeed = true;
    });


});



// function to load all posts (aka global feed)
function load_all_posts() {
    console.log("we are in the load_all_posts function")
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_all_posts", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            var user_feed = document.getElementById("user_feed");
            user_feed.innerHTML = "<h3>Global Feed</h3>";
            // iterate through each post and append to the page
            for (var i = 0; i < data.length; i++){
                var post = document.createElement("div");
                post.classList.add("post");
                // post.innerHTML = '<p>${data[i].name} (${data[i].username})</p><p>${data[i].content}</p><p>${data[i].timestamp}</p>';
                post.innerHTML = `<p>${data[i].name} (${data[i].username})</p><p>${data[i].content}</p><p>${data[i].timestamp}</p>`;

                // append the post to the page within the user_feed div
                // document.getElementById('user_feed').appendChild(post);
                user_feed.appendChild(post);
            }
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}

// function to load the posts of only the users the current user follows
function load_following_posts() {
    console.log("we are in the load_following_posts function");
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_following_posts", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            var user_feed = document.getElementById("user_feed");
            user_feed.innerHTML = "<h3>Personal Feed</h3>";

            for (var i = 0; i < data.length; i++){
                var post = document.createElement("div");
                post.classList.add("post");

                post.innerHTML = `<p>${data[i].name} (${data[i].username})</p><p>${data[i].content}</p><p>${data[i].timestamp}</p>`;

                user_feed.appendChild(post);

            }
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}

function load_unfollowed_users(){
    console.log('inside load_unfollowed_users function');
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_unfollowed_users", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.responseText);
            var user_list = document.getElementById('user_list');
            user_list.innerHTML = "<h3>Unfollowed Users</h3>";
            for (var i = 0; i < data.length; i++){
                var user = document.createElement("div");
                user.innerHTML = `<p>${data[i].name} (${data[i].username})</p>`;
                var follow_button = document.createElement("button");
                follow_button.innerHTML = "Follow";
                // need to save i because of javascript cosure problem
                (function(user_id) {
                    follow_button.onclick = function() {
                        // call function to follow user with respective user_id
                        follow_user(user_id);
                    };
                })(data[i].id);
                user.appendChild(follow_button);
                user_list.appendChild(user);
            }
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}

function load_followed_users(){
    console.log('inside the function load_followed_users');
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_followed_users", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            var data = JSON.parse(this.response);
            var user_list = document.getElementById('following_list');
            user_list.innerHTML = "<h3>Followed users</h3>";
            for (var i = 0; i < data.length; i++){
                var user = document.createElement("div")
                user.innerHTML = `<p>${data[i].name} (${data[i].username})</p>`;
                var unfollow_button = document.createElement("button");
                unfollow_button.innerHTML = "Unfollow";
                // need to save i because of javascript closure problem
                (function(user_id) {
                    unfollow_button.onclick = function() {
                        // call function to unfollow user with respective user_id
                        unfollow_user(user_id);
                    };
                })(data[i].id);
                user.appendChild(unfollow_button);
                user_list.appendChild(user);
            }

        } else if (this.readyState == 4 & this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}

function unfollow_user(user_id){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/unfollow_user/" + user_id, true);
    xhttp.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200){
            // reload the data of the followed users (need to removed unfollowed user)
            load_followed_users();
            // reload the data of the unfollowed users  (need to add unfollowed user)
            load_unfollowed_users();
            if (globalFeed == false){
                load_following_posts();
            }
        }else if (this.readyState == 4 & this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send(); 
}


function follow_user(user_id){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/follow_user/" + user_id, true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            // Reload the unfollowed users list (need to remove the followed user)
            load_unfollowed_users();
            // Reload the followed user list (need to add the followed user)
            load_followed_users();
            if (globalFeed == false){
                load_following_posts();
            }
        } else if (this.readyState == 4 && this.status != 200){
            console.log("Error: " + this.responseText);
        };
    }
    xhttp.send();
}