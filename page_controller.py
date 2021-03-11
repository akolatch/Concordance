from flask import redirect, render_template, request, session, Markup

from models import Page_Model, Journal_Model, User_Model, Invite_Model, Members_Model
from helpers import concordance_list


Page = Page_Model()
Journal = Journal_Model()
user = session["user_id"]

# /load_page POST --> /pages GET
#  replace page_loader(page_id, concordance_id, warning="")


def open_page(page_id, concordance_id=False, warning=""):
    """open page"""

    concordance_page = None
    concordance_content = ""

    # check to see if this is a concordance load
    if concordance_id:
        concordance_page = Page.find({'id': concordance_id}, [
                                     'id', 'content', 'title'])
        concordance_content = (concordance_page[0]["content"])

    # Check if there is a load warning
    display_warning = "block"
    if not warning:
        display_warning = "none"

    # Select all pages the user has access to
    pages = Page.find_by_user(user, ['id', 'pages.journal_id', 'title'])

    # Select all journals a user has access to
    journals = Journal.find_by_user(user)

    # Retrieve page from DB
    display_page = Page.find({'id': page_id})

    # Error Check
    if not display_page:
        return apology("page not found", 403)

    page_journal = Journal.find(
        {'id': display_page[0]["journal_id"]}, ['id', 'name'])

    concordance = concordance_list(page_id, user)

    concordance_journals = []
    for page in concordance:
        if page["journal_id"] not in concordance_journals:
            concordance_journals.append(page["journal_id"])

    page_content = Markup(display_page[0]["content"])

    return render_template("page.html", concordance_page=concordance_page, concordance_content=concordance_content, concordance_journals=concordance_journals, concordance=concordance, display_warning=display_warning, warning=warning, display_page=display_page, page_content=page_content, page_journal=page_journal, pages=pages, journals=journals)


# /new_page POST --> /pages POST
# Replace:

    # name_check = db.execute("SELECT title FROM pages where journal_id = :journal_id",
    #                         journal_id=journal_id)

    # for name in name_check:
    #     if page_name.lower() == name["title"].lower():
    #         return index("The page you are trying to create alread exsists")

    # db.execute("INSERT INTO pages (title, journal_id) VALUES (:title, :journal_id)",
    #           title=page_name, journal_id=journal_id)
    # new_page_id = db.execute("SELECT id FROM pages WHERE title = :title AND journal_id = :journal_id",
    #                          title=page_name, journal_id=journal_id)

    # page_id = new_page_id[0]["id"]

# /new_page POST --> /pages POST
def create_page(page_name, journal_id):
    """create new page"""

    name_check = Page.find(
        {'title': page_name, 'journal_id': journal_id}, ['id'])

    if name_check:
        return index("The page you are trying to create alread exsists")

    page_id = Page.create({{'title': page_name, 'journal_id': journal_id}})

    return open_page(page_id)


# /save_page POST --> /pages/save POST (/page PUT)
# Replace:

    #     checker = db.execute("SELECT title, journal_id FROM pages WHERE id = :page_id", page_id=page_id)

    #     if title == checker[0]["title"]:
    #         db.execute("UPDATE pages SET content = :text WHERE id = :page_id", text=text, page_id=page_id)
    #         return page_loader(page_id, -1, "saved")
    #     temp_titles = db.execute("SELECT * FROM pages WHERE journal_id = :journal_id", journal_id=checker[0]["journal_id"])

    #     for name in temp_titles:
    #         if title == name["title"]:
    #             db.execute("UPDATE pages SET content = :text WHERE id = :page_id", text=text, page_id=page_id)
    #             return page_loader(page_id, -1, "The new title of this page already exsits. The page was save under its old name.")

    #     db.execute("UPDATE pages SET (title, content) = (:title, :text)  WHERE id = :page_id", title=title, text=text, page_id=page_id)
    #     return page_loader(page_id, -1, "saved")

# /save_page POST --> /pages/save POST (/page PUT)
def update_page(title, page_id, text):

    journal_id = Page.find({'id': page_id}, ['journal_id'])[0]["journal_id"]

    checker = Page.find(
        {'journal_id': journal_id, 'title': title}, ['id'])[0]['id']

    if checker AND chacker != page_id:
        Page.update({'content': text}, {'id': page_id})
        return open_page(page_id, False, "The new title for this page already exsits. The page was save under its old title.")

    if title == checker[0]["journal_id"]:
        title_taken = True

    Page.update({'title': title, 'content': text}, {'id': page_id})
    return page_loader(page_id, False, "saved")


# /delete_page POST --> /pages/delete POST (/page DELETE)
# Replace:
    #     checker = db.execute("SELECT creator_id FROM journals JOIN pages ON journals.id = pages.journal_id WHERE pages.id = :page_id AND creator_id = :user_id",
    #                          page_id=page_id, user_id=session["user_id"])

    #     if not checker:
    #         return index("You cannot delete a page in journal if you are not an admin")

    #     db.execute("DELETE FROM pages WHERE id = ?", page_id)
    #     return index("Page Deleted")


# /delete_page POST --> /pages/delete POST (/page DELETE)
def delete_page(page_id):
    """Delete a page"""

    checker = Journal.find_by_page_creater(user)

    if not checker:
        return "You cannot delete a page in journal if you are not an admin"

    Page.delete({'id': page_id})
    return "Page Deleted"

# Note: the rount should now return
#     message = delete_page(page_id)
#     return index(message)


# /concordance POST --> /pages/concordance GET
# ONLY CHANGE:
    # return open_page(page_id, concordance_id)
