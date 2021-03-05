# application to searve the concordane web apps

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, page_loader, new_journal, concordance_search

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///concordance.db")


@app.route("/")
@login_required
def index(warning=""):
    """Show all of users content"""

    # no search
    search = False

    # handle Warning
    display_warning = "block"
    if warning == "":
        display_warning = "none"

    # Select all pages the user has access to
    pages = db.execute("SELECT id, pages.journal_id, title FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC",
                       user_id=session["user_id"])

    # Select all journals a user has access to
    journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
                          user_id=session["user_id"])

    username = db.execute("SELECT username FROM users WHERE id = :user_id",
                          user_id=session["user_id"])
    user_journal = db.execute("SELECT id FROM journals WHERE name = :username",
                              username=username[0]["username"])

    num_journals = len(journals)
    # new user check
    if not pages and num_journals == 1:
        new_user = True

        # load new_user index
        return render_template("index.html", search=search, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals)
    else:
        new_user = False

    # check for invites
    invites = db.execute("SELECT journal_id, sender FROM  journal_invites WHERE user_id = :user_id", user_id=session["user_id"])

    # load index
    return render_template("index.html", search=search, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals, pages=pages)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            login_fail_display = "block"
            return render_template("login.html", login_fail_display=login_fail_display)

        # Ensure password was submitted
        elif not request.form.get("password"):
            login_fail_display = "block"
            return render_template("login.html", login_fail_display=login_fail_display)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            login_fail_display = "block"
            return render_template("login.html", login_fail_display=login_fail_display)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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

    # Username requirment text
    username_instructions = "Your username must be between 6 and 30 characters long."

    # Username requirment display setting
    username_instructions_display = "none"

    # Password requirment text
    password_instructions = "Passwords must be at least 8 characters long."

    # Password requirment display setting
    password_instructions_display = "none"

    # Password form disabled status
    password_form = "disabled"

    # On GET request render regiser.html with base instructions
    if request.method == "GET":
        return render_template("register.html", password_form=password_form, username=username, username_instructions=username_instructions, password_instructions=password_instructions, username_instructions_display=username_instructions_display, password_instructions_display=password_instructions_display)

    # On POST request check to confirm all username and password requirments were met.
    else:

        # set variables for usernam, password
        username = request.form.get("username")
        password = request.form.get("password")

        # Confirm the username doesnt already exsist
        if db.execute("SELECT username FROM users WHERE username = ?", username):

            # Reset username to blank
            username = ""

            # Set new username requirment text and display setting
            username_instructions = "Sorry, that useusername is taken. Try another."
            username_instructions_display = "block"
            return render_template("register.html", password_form=password_form, username=username, username_instructions=username_instructions, password_instructions=password_instructions, username_instructions_display=username_instructions_display, password_instructions_display=password_instructions_display)

        # Confirm the password contains at least one capitalized letter
        if password.islower():

            # Set new password requirment text and display setting
            password_instructions = "Your password must contain at least one character that is capitalized."
            password_instructions_display = "block"
            password_form = ""
            return render_template("register.html", password_form=password_form, username=username, username_instructions=username_instructions, password_instructions=password_instructions, username_instructions_display=username_instructions_display, password_instructions_display=password_instructions_display)

        # Confirm the password contains a combination of both letters and numbers
        if password.isnumeric() or password.isalpha():

            # Set new password requirment text and display setting
            password_instructions = "Your password must contain a combination of both numbers and letters."
            password_instructions_display = "block"
            password_form = ""
            return render_template("register.html", password_form=password_form, username=username, username_instructions=username_instructions, password_instructions=password_instructions, username_instructions_display=username_instructions_display, password_instructions_display=password_instructions_display)

        # Username and password are good

        # Hash the password
        pass_hash = generate_password_hash(password)

        # Store password and hash in the users db
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :pass_hash)", username=username, pass_hash=pass_hash)

        # set up new user db
        new_user = db.execute("SELECT id FROM users WHERE username = :username", username=username)
        user_id = new_user[0]["id"]
        new_journal(user_id, username)

        # Redirect user to login
        return redirect("login")


@app.route("/new_journal", methods=["POST"])
@login_required
def new_journals():
    """Create a Journal"""

    journal_name = request.form.get("journal_name")
    journal_name = journal_name.strip()

    if journal_name == "":
        return index("You must give a Title to your new journal")

    # Journal name taken check
    name_check = db.execute("SELECT name FROM journals WHERE creator_id = :creator",
                            creator=session["user_id"])

    for name in name_check:
        if journal_name.lower() == name["name"].lower():
            return index("The journal you are trying to create alread exsists")

    # creat new journal
    new_journal(session["user_id"], journal_name)

    return redirect("/")


@app.route("/search", methods=["POST"])
@login_required
def search():
    """execute a search"""

    # clean and check search term
    search_term = request.form.get("search-term")
    search_term = search_term.strip()

    if search_term == "":
        return index("You must include a search term to search")

    temp_results = db.execute( "SELECT title, id, pages.journal_id FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE title = :search_term ORDER BY title ASC",
                               search_term=search_term)

    search_results = concordance_search(search_term, session["user_id"])

    # Combine results
    temp_results += search_results

    if temp_results == []:
        return index("No Results Found!")
    if len(temp_results) == 1:
        return page_loader(temp_results[0]["id"], -1)

    results = []
    for page in temp_results:
        if page not in results:
            results.append(page)

    # Sett warning
    warning = ""
    display_warning = "none"

    # Select all pages the user has access to
    pages = db.execute("SELECT id, pages.journal_id, title FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC",
                       user_id=session["user_id"])

    # Select all journals a user has access to
    journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
                          user_id=session["user_id"])

    username = db.execute("SELECT username FROM users WHERE id = :user_id",
                          user_id=session["user_id"])
    user_journal = db.execute("SELECT id FROM journals WHERE name = :username",
                              username=username[0]["username"])

    num_journals = len(journals)
    # new user check
    if not pages and num_journals == 1:
        new_user = True

        # load new_user index
        return render_template("index.html", display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals)
    else:
        new_user = False

    # check for invites
    invites = db.execute("SELECT journal_id, sender FROM  journal_invites WHERE user_id = :user_id", user_id=session["user_id"])

    search = True

    # load index
    return render_template("index.html", search=search, results=results, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals, pages=pages)


@app.route("/new_page", methods=["POST"])
@login_required
def new_journal_page():
    """open a new page"""

    page_name = request.form.get("page_name")
    journal_id = request.form.get("journal_id")

    # strip ac
    page_name = page_name.strip()
    if page_name == "":
        return index("You must give a Title to your new page")

    name_check = db.execute("SELECT title FROM pages where journal_id = :journal_id",
                            journal_id=journal_id)

    for name in name_check:
        if page_name.lower() == name["title"].lower():
            return index("The page you are trying to create alread exsists")

    db.execute("INSERT INTO pages (title, journal_id) VALUES (:title, :journal_id)",
               title=page_name, journal_id=journal_id)
    new_page_id = db.execute("SELECT id FROM pages WHERE title = :title AND journal_id = :journal_id",
                             title=page_name, journal_id=journal_id)

    page_id = new_page_id[0]["id"]

    return page_loader(page_id, -1)


@app.route("/load_page", methods=["POST"])
@login_required
def load_page():
    """open a saved page"""

    # Load page from id
    page_id = request.form.get("page_id")
    return page_loader(page_id, -1)


@app.route("/concordance", methods=["POST"])
@login_required
def concordance():
    """append concordance onto a page"""

    # Load page from id
    concordance_id = request.form.get("concordance_id")
    page_id = request.form.get("page_id")
    return page_loader(page_id, concordance_id)


@app.route("/move_page", methods=["POST"])
@login_required
def move_page():
    """move a page to a differnt journal"""

    page_id = request.form.get("page_id")
    old_journal = request.form.get("old_journal_id")
    new_journal = request.form.get("new_journal_id")

    # Check to make sure this is your journal to move pages out of
    admin_checker = db.execute("SELECT creator_id FROM journals WHERE id = :old_journal AND creator_id = :user_id",
                               old_journal=old_journal, user_id=session["user_id"])
    if not admin_checker:
        return page_loader(page_id, -1, "You cannot move pages from journals you did not create.")

    # Check to make sure the page name doesnt already exsist in the journal
    page_title = db.execute("SELECT title FROM pages WHERE id = :page_id",
                            page_id=page_id)
    name_check = db.execute("SELECT title FROM pages WHERE journal_id = :journal_id",
                            journal_id=new_journal)
    for name in name_check:
        if name["title"].lower() == page_title[0]["title"].lower():
            return page_loader(page_id, -1, "There is already a page with this title in the journal.")

    db.execute("UPDATE pages SET journal_id = :new_journal WHERE id = :page_id",
               new_journal=new_journal, page_id=page_id)
    return page_loader(page_id, -1, "page moved")


@app.route("/save_page", methods=["POST"])
@login_required
def save_page():
    """Save a Page"""

    title = request.form.get("title")
    page_id = request.form.get("page_id")
    text = request.form.get("page_text")

    title = title.strip()

    checker = db.execute("SELECT title, journal_id FROM pages WHERE id = :page_id", page_id=page_id)

    if title == checker[0]["title"]:
        db.execute("UPDATE pages SET content = :text WHERE id = :page_id", text=text, page_id=page_id)
        return page_loader(page_id, -1, "saved")
    temp_titles = db.execute("SELECT * FROM pages WHERE journal_id = :journal_id", journal_id=checker[0]["journal_id"])

    for name in temp_titles:
        if title == name["title"]:
            db.execute("UPDATE pages SET content = :text WHERE id = :page_id", text=text, page_id=page_id)
            return page_loader(page_id, -1, "The new title of this page already exsits. The page was save under its old name.")

    db.execute("UPDATE pages SET (title, content) = (:title, :text)  WHERE id = :page_id", title=title, text=text, page_id=page_id)
    return page_loader(page_id, -1, "saved")


@app.route("/delete_page", methods=["POST"])
@login_required
def delete_page():
    """Delete a page"""

    page_id = request.form.get("page_id")

    checker = db.execute("SELECT creator_id FROM journals JOIN pages ON journals.id = pages.journal_id WHERE pages.id = :page_id AND creator_id = :user_id",
                         page_id=page_id, user_id=session["user_id"])

    if not checker:
        return index("You cannot delete a page in journal if you are not an admin")

    db.execute("DELETE FROM pages WHERE id = :page_id", page_id=page_id)
    return index("Page Deleted")


@app.route("/delete_journal", methods=["POST"])
@login_required
def delete_journal():
    """delete a journal"""

    journal_id = request.form.get("journal_id")

    checker = db.execute("SELECT creator_id FROM journals WHERE id = :journal_id AND creator_id = :user_id",
                         journal_id=journal_id, user_id=session["user_id"])

    if not checker:
        db.execute("DELETE FROM journal_members WHERE journal_id = :journal_id AND user_id = :user_id",
                   journal_id=journal_id, user_id=session["user_id"])
        return index("You have left the journal")

    db.execute("DELETE FROM pages WHERE journal_id = :journal_id", journal_id=journal_id)
    db.execute("DELETE FROM journals WHERE id = :journal_id", journal_id=journal_id)
    db.execute("DELETE FROM journal_members WHERE journal_id = :journal_id", journal_id=journal_id)

    return index("Journal Deleted")


@app.route("/send_invite", methods=["POST"])
@login_required
def send_invite():
    """Send  journal share invite to user"""

    recipient_name = request.form.get("username")
    recipient = db.execute("SELECT * FROM users WHERE username = :username", username=recipient_name)

    # Check if user exsists
    if not recipient:
        return index("The user you are trying to share with could not be found")

    journal_id = request.form.get("journal_id")

    jounal_check = db.execute("SELECT * FROM journal_members WHERE user_id = :user_id AND journal_id = :journal_id",
                              user_id=recipient[0]["id"], journal_id=journal_id)

    # if the user is not already in the journal
    if not jounal_check:
        sender = request.form.get("sender")
        temp_name = db.execute("SELECT name FROM journals WHERE id = :journal_id", journal_id=journal_id)
        db.execute("INSERT INTO journal_invites (user_id, journal_id, sender, journal_name) VALUES (:user_id, :journal_id, :sender, :journal_name)",
                   user_id=recipient[0]["id"], journal_id=journal_id, sender=sender, journal_name=temp_name[0]["name"])

    return index("Invite Sent")


@app.route("/accept_invite", methods=["POST"])
@login_required
def accept_invite():
    """accept an invite"""

    journal_id = request.form.get("journal_id")

    # update journal members
    db.execute("INSERT INTO journal_members (journal_id, user_id) VALUES (:journal_id, :user_id)",
               journal_id=journal_id, user_id=session["user_id"])
    # Remove invite from db
    db.execute("DELETE FROM journal_invites WHERE journal_id = :journal_id AND user_id = :user_id",
               journal_id=journal_id, user_id=session["user_id"])

    # redirect back to homepage
    return redirect("/")


@app.route("/decline_invite", methods=["POST"])
@login_required
def decline_invite():
    """decline an invite"""

    # Remove invite from db
    journal_id = request.form.get("journal_id")
    db.execute("DELETE FROM journal_invites WHERE journal_id = :journal_id AND user_id = :user_id",
               journal_id=journal_id, user_id=session["user_id"])

    # redirect back to homepage
    return redirect("/")


@app.route("/acount", methods=["GET", "POST"])
@login_required
def acount():
    """manage acount activity"""
    if request == "GET":
        user = db.execute("SELECT name, id FROM users WHERE id = :user_id", user_id=session["user_id"])

        # Select all journals a user has access to
        journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
                          user_id=session["user_id"])



        return render_template("acount.html", user=user, journals=journals)

    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)