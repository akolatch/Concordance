from flask import redirect, render_template, request, session, Markup
from models import Page, Journal, User, Invite


# / GET --> / GET
def render_index(warning="", search=False, search_results=[]):

    user = session["user_id"]

    # handle Warning
    display_warning = "block"
    if not warning:
        display_warning = "none"

    # Select all pages the user has access to
    pages = Page.find_by_user(user, ['id', 'pages.journal_id', 'title'])

    # Select all journals a user has access to
    journals = Journal.find_by_user(user)
    username = User.find({'id': user}, ['username'])

    # new user check
    if not pages and len(journals) == 1:

        # load new_user index
        return render_template("index.html", search=search, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=True, journals=journals)

    # not new user
    user_journal = Journal.find({'name': username[0]["username"]}, ['id'])

    # check for invites
    invites = Invite.find({'user_id': user}, [
                          'journal_id', 'sender', '	journal_name'])

    # load index
    if search:
        return render_template("index.html", search=search, results=search_results, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=False, journals=journals, pages=pages)

    return render_template("index.html", search=search, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=False, journals=journals, pages=pages)
