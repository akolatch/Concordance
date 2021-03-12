from flask import session
from controllers import render_index
from models import Journal, User, Invite, Member


# /send_invite POST --> /invites/send POST
def send(recipient_name, journal_id, sender):

    # Check if user exists
    recipient = User.find({'username': recipient_name})
    if not recipient:
        return render_index("The user you are trying to share with could not be found")

    recipient_id = recipient[0]["id"]
    journal_name = Journal.find({'id': journal_id}, ['name'])[0]["name"]

    # if the user is not already in the journal
    journal_check = Member.find(
        {'user_id': recipient_id, 'journal_id': journal_id})
    if journal_check:
        return render_index(f"{recipient_name} is all ready a member of {journal_name}")

    # check if user already has a pending invite
    invite_check = Invite.find(
        {'user_id': recipient_id, 'journal_id': journal_id})

    if not invite_check:
        Invite.create({'user_id': recipient_id, 'journal_id': journal_id,
                       'sender': sender, ' journal_name': journal_name})

    return render_index("Invite Sent")


# /accept_invite POST --> /invites/journals POST
# /decline_invite --> /invites/members POST
def respond(journal_id, answer=True):
    """accept an invite"""

    user = session["user_id"]

    # add journal members
    if answer:
        Member.create({'journal_id': journal_id, 'user_id': user})

    # Remove invite from db
    Invite.delete({'journal_id': journal_id, 'user_id': user})

    # redirect back to homepage
    return render_index()
