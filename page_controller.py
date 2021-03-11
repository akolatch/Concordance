# check if req and red are needed
from flask import render_template, session, Markup, request, redirect
from models import Page_Model, Journal_Model
from controllers import render_index
from helpers import concordance_list, concordance_search

Page = Page_Model()
Journal = Journal_Model()

# /load_page POST --> /pages/load POST
#  replace page_loader(page_id, concordance_id, warning="")


def open_page(user, page_id, concordance_id=False, warning=""):
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
    #         return render_index("The page you are trying to create alread exsists")

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
        return render_index("The page you are trying to create alread exsists")

    page_id = Page.create({{'title': page_name, 'journal_id': journal_id}})

    return open_page(page_id)


# /save_page POST --> /pages/save POST
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

# /save_page POST --> /pages/save POST
def update_page(title, page_id, text):

    journal_id = Page.find({'id': page_id}, ['journal_id'])[0]["journal_id"]

    checker = Page.find(
        {'journal_id': journal_id, 'title': title}, ['id'])[0]['id']

    if checker and chacker != page_id:
        Page.update({'content': text}, {'id': page_id})
        return open_page(page_id, False, "The new title for this page already exsits. The page was save under its old title.")

    # if title == checker[0]["journal_id"]:
    #      title_taken = True

    Page.update({'title': title, 'content': text}, {'id': page_id})

    return page_loader(page_id, False, "saved")


# /delete_page POST --> /pages/delete POST (/page DELETE)
# Replace:
    #     checker = db.execute("SELECT creator_id FROM journals JOIN pages ON journals.id = pages.journal_id WHERE pages.id = :page_id AND creator_id = :user_id",
    #                          page_id=page_id, user_id=session["user_id"])

    #     if not checker:
    #         return render_index("You cannot delete a page in journal if you are not an admin")

    #     db.execute("DELETE FROM pages WHERE id = ?", page_id)
    #     return render_index("Page Deleted")


# /delete_page POST --> /pages/delete POST
def delete_page(user, page_id):
    """Delete a page"""

    checker = Journal.find_by_page_creater(user)

    if not checker:
        return "You cannot delete a page in journal if you are not an admin"

    Page.delete({'id': page_id})
    return "Page Deleted"

# Note: the rount should now return
#     message = delete_page(page_id)
#     return render_index(message)


# /concordance POST --> /pages/concordance POST
# ONLY CHANGE:
    # return open_page(page_id, concordance_id)


# /search Post --> /pages/search SET
# Replace:

    # temp_results = db.execute( "SELECT title, id, pages.journal_id FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE title = :search_term ORDER BY title ASC",
    #                           search_term=search_term)

    # search_results = concordance_search(search_term, session["user_id"])

    # # Combine results
    # temp_results += search_results

    # if temp_results == []:
    #     return render_index("No Results Found!")
    # if len(temp_results) == 1:
    #     return page_loader(temp_results[0]["id"], -1)

    # results = []
    # for page in temp_results:
    #     if page not in results:
    #         results.append(page)

    # # Sett warning
    # warning = ""
    # display_warning = "none"

    # # Select all pages the user has access to
    # pages = db.execute("SELECT id, pages.journal_id, title FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC",
    #                   user_id=session["user_id"])

    # # Select all journals a user has access to
    # journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
    #                       user_id=session["user_id"])

    # username = db.execute("SELECT username FROM users WHERE id = :user_id",
    #                       user_id=session["user_id"])
    # user_journal = db.execute("SELECT id FROM journals WHERE name = :username",
    #                           username=username[0]["username"])

    # num_journals = len(journals)
    # # new user check
    # if not pages and num_journals == 1:
    #     new_user = True

    #     # load new_user index
    #     return render_template("index.html", display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals)
    # else:
    #     new_user = False

    # # check for invites
    # invites = db.execute("SELECT journal_id, sender FROM  journal_invites WHERE user_id = :user_id", user_id=session["user_id"])

    # search = True

    # # load index
    # return render_template("index.html", search=search, results=results, invites=invites, display_warning=display_warning, warning=warning, username=username, user_journal=user_journal, new_user=new_user, journals=journals, pages=pages)


# /search Post --> /pages/search SET
def page_search(user, search_term):
    """execute a search"""

    search_results = Page.find_by_search_term(search_term)

    concordance_search_results = concordance_search(search_term, user)

    # Combine results
    search_results += concordance_search_results

    if search_results == []:
        return render_index("No Results Found!")
    if len(search_results) == 1:
        return page_loader(temp_results[0]["id"], -1)

    results = []
    for page in temp_results:
        if page not in results:
            results.append(page)

    return render_index('', True, results)
