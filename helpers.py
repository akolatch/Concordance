from cs50 import SQL
import os
import requests
import urllib.parse

from query_model import db
from flask import redirect, render_template, request, session, Markup
from functools import wraps
from models import Page


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


# strip html, punctuation, and excese " "
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

    # get all the content the user has access to
    check_contents = Page.find_by_user(
        user_id, ['id', 'title', 'pages.journal_id', 'content'])

    # Create a list of search results
    search_results = []
    for content in check_contents:
        stripped_content = search_format(content["content"])
        found = stripped_content.find(search_format(search_term))
        if found >= 0:
            search_results.append(content)

    # strip "content" from results
    for result in search_results:
        result.pop("content")

    return search_results


# Concordance algorithm
def concordance_list(page_id, user_id):
    """scan thepages text and get a list of all other pages mentioned in a given page"""

    # Get the page info and all the page titles available to the user
    text = Page.find({'id': page_id}, ['id', 'content', 'title'])
    # text = db.execute("SELECT id, content, title FROM pages WHERE id = :page_id", page_id=page_id)
    titles = Page.find_by_user(user_id, ['id', 'title', 'pages.journal_id'])
    # titles = db.execute(
    #     "SELECT title, id, pages.journal_id FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC", user_id=user_id)

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
