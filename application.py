from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import journal
import page
import invite
import user
from controllers import render_index
from helpers import apology, login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@login_required
def index():
    """Show all of users content"""
    return render_index()


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            login_fail_display = "block"
            return render_template("login.html", login_fail_display=login_fail_display)

        # Ensure password was submitted
        elif not password:
            login_fail_display = "block"
            return render_template("login.html", login_fail_display=login_fail_display)

        return user.login(username, password)

    else:
        login_fail_display = "none"
        return render_template("login.html", login_fail_display=login_fail_display)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Set username field to blank
    username = ""

    # Username requirement text
    username_instructions = "Your username must be between 6 and 30 characters long."

    # Username requirement display setting
    username_instructions_display = "none"

    # Password requirement text
    password_instructions = "Passwords must be at least 8 characters long."

    # Password requirement display setting
    password_instructions_display = "none"

    # Password form disabled status
    password_form = "disabled"

    # On GET request render register.html with base instructions
    if request.method == "GET":
        return render_template("register.html", password_form=password_form, username=username, username_instructions=username_instructions, password_instructions=password_instructions, username_instructions_display=username_instructions_display, password_instructions_display=password_instructions_display)

    # On POST request check to confirm all username and password requirements were met.
    else:

        # set variables for usernam, password
        username = request.form.get("username")
        password = request.form.get("password")

        return user.register(username, password)


@app.route("/new_journal", methods=["POST"])
@login_required
def new_journals():
    """Create a Journal"""

    journal_name = request.form.get("journal_name")
    journal_name = journal_name.strip()

    if journal_name == "":
        return render_index("You must give a Title to your new journal")

    return journal.create(session["user_id"], journal_name)


@app.route("/search", methods=["POST"])
@login_required
def search():
    """execute a search"""

    # clean and check search term
    search_term = request.form.get("search-term")
    search_term = search_term.strip()

    if search_term == "":
        return render_index("You must include a search term to search")

    return page.search(search_term)


@app.route("/new_page", methods=["POST"])
@login_required
def new_page():
    """open a new page"""

    page_name = request.form.get("page_name")
    journal_id = request.form.get("journal_id")

    if page_name == "":
        return render_index("You must give a Title to your new page")

    page_name = page_name.strip()

    return page.create(page_name, journal_id)


@app.route("/load_page", methods=["POST"])
@login_required
def load_page():
    """open a saved page"""

    # Load page from id
    page_id = request.form.get("page_id")
    return page.load(page_id)


@app.route("/concordance", methods=["POST"])
@login_required
def concordance():
    """append concordance onto a page"""

    # Load page from id
    concordance_id = request.form.get("concordance_id")
    page_id = request.form.get("page_id")
    return page.load(page_id, concordance_id)


@app.route("/move_page", methods=["POST"])
@login_required
def move_page():
    """move a page to a different journal"""

    page_id = request.form.get("page_id")
    old_journal = request.form.get("old_journal_id")
    new_journal = request.form.get("new_journal_id")

    return page.move(page_id, old_journal, new_journal)


@app.route("/save_page", methods=["POST"])
@login_required
def save_page():
    """Save a Page"""

    title = request.form.get("title")
    page_id = request.form.get("page_id")
    text = request.form.get("page_text")

    title = title.strip()
    return page.update(title, page_id, text)


@app.route("/delete_page", methods=["POST"])
@login_required
def delete_page():
    """Delete a page"""

    page_id = request.form.get("page_id")

    message = page.remove(page_id)

    return render_index(message)


@app.route("/delete_journal", methods=["POST"])
@login_required
def delete_journal():
    """delete a journal"""

    journal_id = request.form.get("journal_id")

    return journal.remove(journal_id)


@app.route("/send_invite", methods=["POST"])
@login_required
def send_invite():
    """Send  journal share invite to user"""

    recipient_name = request.form.get("username")
    journal_id = request.form.get("journal_id")
    sender = request.form.get("sender")

    return invite.send(recipient_name, journal_id, sender)


@app.route("/accept_invite", methods=["POST"])
@login_required
def accept_invite():
    """accept an invite"""

    journal_id = request.form.get("journal_id")

    return invite.respond(journal_id)


@app.route("/decline_invite", methods=["POST"])
@login_required
def decline_invite():
    """decline an invite"""

    journal_id = request.form.get("journal_id")

    return invite.respond(journal_id, False)

# TODO:


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """manage account activity"""
    if request == "GET":
        # user = db.execute("SELECT name, id FROM users WHERE id = :user_id", user_id=session["user_id"])

        # # Select all journals a user has access to
        # journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
        #                   user_id=session["user_id"])

        return render_template("account.html", user=user, journals=journals)

    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
