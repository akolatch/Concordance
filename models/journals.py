# Set up a new journal
def new_journal(user_id, name):
  
  db.execute("INSERT INTO journals (name, creator_id) VALUES (:name, :creator_id)",
            name=name, creator_id=user_id)
  new_journal = db.execute("SELECT id FROM journals WHERE name = :name AND creator_id = :creator_id",
                          name=name, creator_id=user_id)
  db.execute("INSERT INTO journal_members (journal_id, user_id) VALUES (:journal_id, :user_id)",
            journal_id=new_journal[0]["id"], user_id=user_id)

# Select all journals a user has access to
def find_all_by_user(user_id):
  journals = db.execute("SELECT id, name FROM journals JOIN journal_members ON journals.id = journal_members.journal_id  WHERE user_id = :user_id ORDER BY name ASC",
                        user_id=session["user_id"])
  return journals


# Select all journals a user has created
def find_all_by_creator(username):
  user_journal = db.execute("SELECT id FROM journals WHERE name = :username",
                              username=username[0]["username"])
  return user_journal

def find_all_names(session):
  name_check = db.execute("SELECT name FROM journals WHERE creator_id = :creator",
                          creator=session["user_id"])
  return name_check

# Check to make sure this is your journal to move pages out of
def check()  
  admin_checker = db.execute("SELECT creator_id FROM journals WHERE id = :old_journal AND creator_id = :user_id",
                               old_journal=old_journal, user_id=session["user_id"])
# check to make sure aa given paage is in aa journal that was created by a given user
  checker = db.execute("SELECT creator_id FROM journals JOIN pages ON journals.id = pages.journal_id WHERE pages.id = :page_id AND creator_id = :user_id",
                         page_id=page_id, user_id=session["user_id"])
# delete journal
  db.execute("DELETE FROM journals WHERE id = :journal_id", journal_id=journal_id)


#
#  "SELECT creator_id FROM journals WHERE id = :old_journal AND creator_id = :user_id", old_journal=old_journal, user_id=session["user_id"]
#
#
def select_from(table_name, return_data, params, variables):
  query_string = f"SELECT {return_data} FROM {table_name} WHERE {params}"
  data = db.execute(query_string, *variables)
  return data

