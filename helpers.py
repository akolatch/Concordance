from cs50 import SQL
import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, Markup
from functools import wraps

# Give helper access to DB
db = SQL("sqlite:///concordance.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# strip html, punctuation, and excece " "
def search_format(text):

    # Strip punctuation and html
    for old, new in [('<div>', " "),  ('</div>', " "), ('</a>', " "), ('<li>', " "),
                     ('</li>', " "), ('<ul>', " "), ('</ul>', " "), ('<ol>', " "),
                     ('</ol>', " "), ('&nbsp', " "), ('<', " "), ('>', " "),
                     ('"',  " "), (';', " "), ('href', " "), ('=', " "),
                     ('_', " "), ('/', " "), (':', " "), ('-', " "),
                     (',', " "), ('!', " "), ('.', " "), ('(', " "),
                     (')', " "), ('@', " "), ('#', " "), ('$', " "),
                     ('%', " "), ('^', " "), ('&', " "), ('*', " "),
                     ('+', " "), ('{', " "), ('}', " "), ('[', " "),
                     (']', " "), ("'", " "), ('~', " "), ('`', " "),
                     ('|', " "), ('    ', " "), ('   ', " "), ('  ', " ")]:
        text = text.replace(old, new)
        text = text.lower()
        text = text.strip()
    return text


# search
def concordance_search(search_term, user_id):

    # get all the content the user has accses to
    check_contents = db.execute(
        "SELECT id, title, pages.journal_id, content FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC", user_id=user_id)

    # Creat a list of search results
    search_results = []
    for content in check_contents:
        stripped_content = search_format(content["content"])
        found = stripped_content.find(search_format(search_term))
        if found >= 0:
            search_results.append(content)

    # stip "content" from results
    for result in search_results:
        result.pop("content")

    return search_results


# Concordance algorithm
def concordance_list(page_id, user_id):
    """scan thepages text and get a list of all other pages mentioned in a given page"""

    # Get the page info and all the page titles availible to the user
    text = db.execute("SELECT id, content, title FROM pages WHERE id = :page_id", page_id=page_id)
    titles = db.execute(
        "SELECT title, id, pages.journal_id FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC", user_id=user_id)

    # Strip all html and punctuation from text
    stripped_text = search_format(text[0]["content"])

    # Produce a list of all titles in a given text
    temp_list = []
    for title in titles:
        if title["id"] != text[0]["id"]:
            found = stripped_text.find(search_format(title["title"]))
            if found >= 0:
               temp_list.append(title)

    search_results = concordance_search(text[0]["title"], user_id)

    # Remove the page itself from the search results
    for result in search_results:
        if result["id"] == page_id:
            search_results.remove(result)

    # Combine list items and remove duplicates
    temp_list += search_results
    concordance_list = []
    for item in temp_list:
        if item not in concordance_list:
            concordance_list.append(item)

    return concordance_list


# Load a page
def page_loader(page_id, concordance_id, warning=""):
    """Core page loading function """
    # check to see if this is a concordance load
    if concordance_id == -1:
        concordance_page = None
        concordance_content = ""
    else:
        concordance_page = db.execute("SELECT id, content, title FROM pages WHERE id = :concordance_id",
                                      concordance_id=concordance_id)
        concordance_content = Markup(concordance_page[0]["content"])

    # Check if there is a load warning
    display_warning = "block"
    if warning == "":
        display_warning = "none"

    # Select all pages the user has access to
    pages = db.execute("SELECT id, pages.journal_id, title FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC",
                       user_id=session["user_id"])

    # Select all journals a user has access to
    journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
                          user_id=session["user_id"])

    # Retrieve page from DB
    display_page = db.execute("SELECT * FROM pages WHERE id = :page_id", page_id=page_id)

    page_journal = db.execute("SELECT id, name FROM journals WHERE id = :journal_id", journal_id=display_page[0]["journal_id"])
    # Error Check
    if not display_page:
        return apology("page not found", 403)

    # genereate the concordance list
    concordance = concordance_list(page_id, session["user_id"])

    concordance_journals = []
    for page in concordance:
        if page["journal_id"] not in concordance_journals:
            concordance_journals.append(page["journal_id"])

    print(concordance_journals)
    # format text
    page_content = Markup(display_page[0]["content"])

    return render_template("page.html", concordance_page=concordance_page, concordance_content=concordance_content, concordance_journals=concordance_journals, concordance=concordance, display_warning=display_warning, warning=warning, display_page=display_page, page_content=page_content, page_journal=page_journal, pages=pages, journals=journals)


# Set up a new journal
def new_journal(user_id, name):

    db.execute("INSERT INTO journals (name, creator_id) VALUES (:name, :creator_id)",
               name=name, creator_id=user_id)
    new_journal = db.execute("SELECT id FROM journals WHERE name = :name AND creator_id = :creator_id",
                             name=name, creator_id=user_id)
    db.execute("INSERT INTO journal_members (journal_id, user_id) VALUES (:journal_id, :user_id)",
               journal_id=new_journal[0]["id"], user_id=user_id)