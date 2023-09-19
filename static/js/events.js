function unattend(event_id) {
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/unattend/" + event_id);
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.onload = function () {
		if (this.readyState == 4 && this.status == 200) {
			console.log("Successfully unattended");
		}
	};
	xhttp.send();
	const calling_button = document.getElementById("toggle_for_" + event_id);
	calling_button.innerText = "RSVP";
	calling_button.onclick = () => {
		attend(event_id);
	};
}
function attend(event_id) {
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/attend/" + event_id);
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.onload = function () {
		if (this.readyState == 4 && this.status == 200) {
			console.log("Successfully attended");
		}
	};
	xhttp.send();
	const calling_button = document.getElementById("toggle_for_" + event_id);
	calling_button.innerText = "Cancel RSVP";
	calling_button.onclick = () => {
		unattend(event_id);
	};
}

const upcoming_button = document.getElementById("upcoming_button");
upcoming_button.onclick = () => {
	document.querySelector(".current-tab").classList.remove("current-tab");
	upcoming_button.classList.add("current-tab");
	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/load_events");
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.onload = function () {
		if (this.readyState == 4 && this.status == 200) {
			document.querySelector(".content-body").innerHTML = this.response;
		}
	};
	xhttp.send();
};

const rsvpd_button = document.getElementById("rsvpd_button");
rsvpd_button.onclick = () => {
	document.querySelector(".current-tab").classList.remove("current-tab");
	rsvpd_button.classList.add("current-tab");
	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/attending_events");
	xhttp.setRequestHeader("Content-Type", "application/json");
	xhttp.onload = function () {
		if (this.readyState == 4 && this.status == 200) {
			document.querySelector(".content-body").innerHTML = this.response;
		}
	};
	xhttp.send();
};

const create_button = document.getElementById("create_button");
create_button.onclick = () => {
	document.querySelector(".current-tab").classList.remove("current-tab");
	create_button.classList.add("current-tab");

	const container = document.querySelector(".content-body");
	let new_event = document.createElement("div");
	new_event.classList.add("new_event");

	let new_event_form = document.createElement("form");
	new_event_form.id = "new_event_form";
	new_event_form.action = "/new_event";
	new_event_form.method = "POST";
	new_event_form.onsubmit = "return false";
	new_event.append(new_event_form);

	let event_title_textarea = document.createElement("textarea");
	event_title_textarea.id = "event_title_textarea";
	event_title_textarea.name = "event_title_textarea";
	event_title_textarea.placeholder = "Enter the event title here";
	new_event_form.append(event_title_textarea);

	let event_description_textarea = document.createElement("textarea");
	event_description_textarea.id = "event_description_textarea";
	event_description_textarea.name = "event_description_textarea";
	event_description_textarea.placeholder = "Enter the event description here";
	new_event_form.append(event_description_textarea);

	let event_time_label = document.createElement("label");
	event_time_label.for = "event_time_picker";
	event_time_label.innerText = "Pick the time of the event";
	new_event_form.append(event_time_label);

	let event_time_picker = document.createElement("input");
	event_time_picker.type = "datetime-local";
	event_time_picker.id = "event_time_picker";
	event_time_picker.name = "event_time_picker";
	new_event_form.append(event_time_picker);

	let submit = document.createElement("input");
	submit.type = "submit";
	submit.value = "Submit";
	submit.onclick = (e) => {
		e.preventDefault();

		var xhttp = new XMLHttpRequest();
		xhttp.open("POST", "/new_event");
		xhttp.setRequestHeader("Content-Type", "application/json");
		xhttp.onload = function () {
			console.log(this.responseText);
		};
		const body = {
			title: event_title_textarea.value,
			description: event_description_textarea.value,
			date: event_time_picker.value,
		};
		xhttp.send(JSON.stringify(body));
	};
	new_event_form.append(submit);

	container.innerHTML = "";
	container.append(new_event);
};

function delete_event(event_id) {
	var xhttp = new XMLHttpRequest();
	xhttp.open("DELETE", "/delete_event/" + event_id);
	xhttp.onload = function () {
		if (this.status == 200) {
			let this_event = document.getElementById("event_" + event_id);
            let parent = document.querySelector(".content-body");
            parent.removeChild(this_event);
		}
	};
	xhttp.send();
    upcoming_button.click();
}
