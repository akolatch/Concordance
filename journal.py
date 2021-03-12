from flask import session
from controllers import render_index
from models import Page, Journal, Member


# /new_journal POST --> /journals POST
def create(journal_name):
    """Create a Journal"""

    user = session["user_id"]

    # Journal name already exists check
    name_check = Journal.find({'creator_id': user}, ['name'])
    for name in name_check:
        if journal_name.lower() == name["name"].lower():
            return render_index("The journal you are trying to create already exists")

    # create new journal
    new_id = Journal.create({'name': journal_name, 'creator_id': user})
    Member.create({'journal_id': new_id, 'user_id': user})

    return render_index()


# /delete_journal POST --> /journals/delete POST (/journal DELETE)
def remove(journal_id):
    """delete a journal"""

    user = session["user_id"]

    checker = Journal.find(
        {'id': journal_id, 'creator_id': user}, ['creator_id'])
    if not checker:
        Member.delete({'journal_id': journal_id, 'user_id': user})
        return render_index("You have left the journal")

    Journal.delete({'id': journal_id})
    Page.delete({'journal_id': journal_id})
    Member.delete({'journal_id': journal_id})

    return render_index("Journal Deleted")
