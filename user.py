from flask import redirect, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash

from controllers import render_index
from models import User
import journal

# /login POST --> /login POST


def login(username, password):

    # Query database for username
    rows = User.find({'username': username})

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        login_fail_display = "block"
        return render_template("login.html", login_fail_display=login_fail_display)

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # Redirect user to home page
    return render_index()


# /register POST --> /register POST
def register(username, password):
    """Register user"""doesn't

    # Confirm the username doesn't already exist
    if User.find({'username': username}, ['username']):

        # Set new username requirement text and display setting
        username_instructions = "Sorry, that useusername is taken. Try another."
        password_instructions = "Passwords must be at least 8 characters long."
        # username_instructions_display = "block"
        return render_template(
            "register.html",
            username="",
            username_instructions=username_instructions,
            username_instructions_display="block",
            password_form="disabled",
            password_instructions=password_instructions,
            password_instructions_display="none")

    password_is_invalid = False

    # Confirm the password contains at least one capitalized letter
    if password.islower():

        # Set new password requirement text and display setting
        password_instructions = "Your password must contain at least one character that is capitalized."
        password_is_invalid = True

    # Confirm the password contains a combination of both letters and numbers
    if password.isnumeric() or password.isalpha():

        # Set new password requirement text and display setting
        password_instructions = "Your password must contain a combination of both numbers and letters."
        password_is_invalid = True

    if password_is_invalid:
        return render_template(
            "register.html",
            username=username,
            username_instructions="",
            username_instructions_display="none",
            password_form="",
            password_instructions=password_instructions,
            password_instructions_display="block")

    # Hash the password
    pass_hash = generate_password_hash(password)

    # Store password and hash in the users db
    user_id = User.create({'username': username, 'hash':  pass_hash})

    # create(user, journal_name, new_user=False)
    journal.create(user_id, username, True)

    # Redirect user to login
    return redirect("login")
