/* JavaScript scripts for Concordance web app

Table of content:
    -universal
    -register.html
    -Index.html
    -Page.html

*/

/********
UNIVERSAL
********/
/*******
REGISTER
********/


// Check for basic user name an password requirments displaying the requirment until it is met and enabling the next form
// Continuasly check if the username being entered is between 6 and 30 charachters long
document.querySelector('#username').onkeyup = function() {

    // Set a variable to represent the username
    let username = document.querySelector('#username').value;

    // If username is too short or long
    if (username.length < 6 || username.length > 30) {

        // Display username instructions
        document.querySelector('#username_instructions').style.display = "block";

        // Disable password form bar
        document.querySelector('#password').disabled = true;
    }

    // The username is a valid length
    else {

        // Turn off username instructions
        document.querySelector('#password').disabled = false;

        // Enable password form bar
        document.querySelector('#username_instructions').style.display = "none";
    }
};


// Continuasly check if the password being entered is between 8 and 30 characters long
document.querySelector('#password').onkeyup = function() {

    // Set a variable to represent the password
    let password = document.querySelector('#password').value;

    // If pasword length is too short or long
    if (password.length < 8 || password.length > 30) {

        // Display password instructions
        document.querySelector('#password_instructions').style.display = "block";

        // Disable confirm passwor form
        document.querySelector('#confirm').disabled = true;
    }

    // The password is a valid length
    else {

        // Turn off password instructions
        document.querySelector('#password_instructions').style.display = "none";

        // Enable confim password bar
        document.querySelector('#confirm').disabled = false;
    }
};

// Continuasly check if the password and confirm password match perfectly
document.querySelector('#confirm').onkeyup = function() {

    // If the passwords match
    if (document.querySelector('#confirm').value === document.querySelector('#password').value) {

        // Turn off confim instructions
        document.querySelector('#confirm_instructions').style.display = "none";

        // Enable the Submit button
        document.querySelector('#register_submit').disabled = false;
    }

    // While they dont match
    else {

        // Display confim instructions
        document.querySelector('#confirm_instructions').style.display = "block";

        // Disable register_submit button
        document.querySelector('#register_submit').disabled = true;
    }
};

/****
Page
****/

/*
The save function for page.html didnt work when added to scripts.js
it is therefor in a <script> element starting on line 50

        // Pass valuse from the text editor to a form so they can be Posted
        document.querySelector("#save").onclick = function() {
                    document.querySelector("#new-title").value = document.querySelector("#page-title").innerText;
                    document.querySelector("#page-text").value = document.querySelector("#page-content").innerHTML;
                };
*/

// edit button
function edit() {
    if (document.querySelector("#page-title").contentEditable === false) {
        document.querySelector("#page-title").contentEditable = true;
        document.querySelector("#page-content").contentEditable = true;
    }
    else {
        document.querySelector("#page-title").contentEditable = false;
        document.querySelector("#page-content").contentEditable = false;
    }
}

// Text formating bar
function format(command, value) {
    document.execCommand(command, false, value);
}



// Set url
function setUrl() {
	if (document.querySelector("#url").style.display === "none") {
	    document.querySelector("#url").style.display = "inline-block";
	}
	else {
		let url = document.querySelector("#url").value;
		let link_text = document.getSelection();
		document.execCommand('insertHTML', false, '<a href="http://' + url + '" target="_blank">' + link_text + '</a>');
		document.querySelector("#url").value = "";
	    document.querySelector("#url").style.display = "none";
    }
}

