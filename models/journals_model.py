import models

table='journals'

def new_journal(user_id, name):
  
  models.create(table, )
  db.execute("INSERT INTO journals (name, creator_id) VALUES (:name, :creator_id)",
            name=name, creator_id=user_id)
  new_journal = db.execute("SELECT id FROM journals WHERE name = :name AND creator_id = :creator_id",
                          name=name, creator_id=user_id)
  db.execute("INSERT INTO journal_members (journal_id, user_id) VALUES (:journal_id, :user_id)",
            journal_id=new_journal[0]["id"], user_id=user_id)