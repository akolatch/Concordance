# check if req and red are needed
from flask import render_template, session, Markup, request, redirect
from models import Page_Model, Journal_Model
from controllers import render_index
from helpers import concordance_list, concordance_search

Page = Page_Model()
Journal = Journal_Model()


# /load_page POST --> /pages/load POST
def open_page(page_id, concordance_id=False, warning=""):
    """open page"""

    user = session["user_id"]

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
def create_page(page_name, journal_id):
    """create new page"""

    name_check = Page.find(
        {'title': page_name, 'journal_id': journal_id}, ['id'])

    if name_check:
        return render_index("The page you are trying to create alread exsists")

    page_id = Page.create({'title': page_name, 'journal_id': journal_id})

    return open_page(page_id)


# /save_page POST --> /pages/save POST
def update_page(title, page_id, text):

    journal_id = Page.find({'id': page_id}, ['journal_id'])[0]["journal_id"]

    checker = Page.find(
        {'journal_id': journal_id, 'title': title}, ['id'])[0]['id']

    if checker and checker != int(page_id):
        Page.update({'content': text}, {'id': page_id})
        return open_page(page_id, False, "The new title for this page already exsits. The page was save under its old title.")

    Page.update({'title': title, 'content': text}, {'id': page_id})

    return open_page(page_id, False, "saved")


# /delete_page POST --> /pages/delete POST
def remove_page(page_id):
    """Delete a page"""

    user = session["user_id"]

    checker = Journal.find_by_page_creator(page_id, user)

    if not checker:
        return "You cannot delete a page in journal if you are not an admin"

    Page.delete({'id': page_id})
    return "Page Deleted"


# /concordance POST --> /pages/concordance POST


# /search Post --> /pages/search SET
def page_search(search_term):
    """execute a search"""

    user = session["user_id"]

    search_results = Page.find_by_search_term(search_term)

    concordance_search_results = concordance_search(search_term, user)

    # Combine results
    search_results += concordance_search_results

    if search_results == []:
        return render_index("No Results Found!")
    if len(search_results) == 1:
        return open_page(search_results[0]["id"])

    results = []
    for page in search_results:
        if page not in results:
            results.append(page)

    return render_index('', True, results)
