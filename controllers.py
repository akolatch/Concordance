from flask import redirect, render_template, request, session, Markup

from models import Page_Model, Journal_Model, User_Model, Invite_Model, Members_Model
from helpers import concordance_list, concordance_search


Page = Page_Model()
Journal = Journal_Model()
User = User_Model()
Invite = Invite_Model()

# / GET --> / GET
# Replace:
# def index(warning=""):
#     """Show all of users content"""

#     # no search
#     search = False

#     # handle Warning
#     display_warning = "block"
#     if warning == "":
#         display_warning = "none"

#     # Select all pages the user has access to
#     pages = db.execute("SELECT id, pages.journal_id, title FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC",
#                       user_id=session["user_id"])

#     # Select all journals a user has access to
#     journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
#                           user_id=session["user_id"])

#     username = db.execute("SELECT username FROM users WHERE id = :user_id",
#                           user_id=session["user_id"])
#     user_journal = db.execute("SELECT id FROM journals WHERE name = :username",
#                               username=username[0]["username"])

#     num_journals = len(journals)
#     # new user check
#     if not pages and num_journals == 1:
#         new_user = True

#         # load new_user index
#         return render_template("index.html", search=search, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals)
#     else:
#         new_user = False

#     # check for invites
#     invites = db.execute("SELECT journal_id, sender FROM  journal_invites WHERE user_id = :user_id", user_id=session["user_id"])

#     # load index
#     return render_template("index.html", search=search, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals, pages=pages)
# / GET --> / GET


def render_index(warning="", search=False, search_results=[]):
    # handle Warning
    user = session["user_id"]

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
    invites = Invite.find({'user_id': user}, ['journal_id', 'sender'])

    # load index
    if search:
        return render_template("index.html", search=search, results=search_results, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=False, journals=journals, pages=pages)

    return render_template("index.html", search=search, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=False, journals=journals, pages=pages)


# /move_page POST --> /journals/pages POST (/PUT)

# /new_journal POST --> /journals POST

# /delete_journal POST --> /journals/delete POST (/journal DELETE)

# /send_invite POST --> /journals/invites POST

# /accept_invite POST --> /journals/members POST

# /decline_invite --> combine with /journals/members POST
