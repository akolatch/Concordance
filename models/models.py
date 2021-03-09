
def find(table_name, return_data, params, variables):
  query_string = f"SELECT {return_data} FROM {table_name} WHERE {params}"
  data = db.execute(query_string, *variables)
  return data

def create(table_name, params, place_holder, variables):
  query_string = f"INSERT INTO {table_name} ({params}) VALUES ({place_holder})"
  db.execute(query_string, *variables)

def delete(table_name, params, variables):
  query_string = f"DELETE FROM {table_name} WHERE {params}"
  db.execute(query_string, *variables)

def update(table_name, update_data, target):
  query_string = f"UPDATE {table_name} SET {update_data} WHERE {target}"
  db.execute(query_string, *variables)

def test():
  print('yep')