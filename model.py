from query_model import Query_Model, db


class Journal_Model(Query_Model):
    def __init__(self):
        self.table = 'journals'

    def find_by_user(self, user_id):
        query_string = 'SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC'
        return db.execute(query_string, user_id=user_id)

    def find_by_page_creator(self, page_id, user_id):
        query_string = 'SELECT creator_id FROM journals JOIN pages ON journals.id = pages.journal_id WHERE pages.id = :page_id AND creator_id = :user_id'
        return db.execute(query_string, page_id=page_id, user_id=user_id)


class Page_Model(Query_Model):
    def __init__(self):
        self.table = 'pages'

    def find_by_user(self, user_id, fields=['*']):
        fields = ', '.join(fields)
        query_string = f'SELECT {fields} FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE user_id = :user_id ORDER BY title ASC'
        return db.execute(query_string, user_id=user_id)

    def find_by_search_term(self, search_term):
        query_string = 'SELECT title, id, pages.journal_id FROM pages JOIN journal_members ON pages.journal_id = journal_members.journal_id WHERE title = :search_term ORDER BY title ASC'
        return db.execute(query_string, search_term=search_term)


class User_Model(Query_Model):
    def __init__(self):
        self.table = 'users'


class Invite_Model(Query_Model):
    def __init__(self):
        self.table = 'journal_invites'


class Members_Model(Query_Model):
    def __init__(self):
        self.table = 'journal_members'


Page = Page_Model()
Journal = Journal_Model()
User = User_Model()
Invite = Invite_Model()
Member = Members_Model()
