from cs50 import SQL
db = SQL("sqlite:///concordance.db")


class Query_Model:
    def __init__(self, table):
        self.table = table

    # helper functions for converting inputs into properly formatted strings

    def param_formatter(self, param):
        return f'{" = ? AND ".join(param)} = ?'

    def gen_placeholder(self, data):
        return f'{"?," * (len(data) - 1)}?'

    def update_fields(self, data):
        if len(data) == 1:
            return self.param_formatter(data.keys())
        else:
            field_names = ', '.join(data.keys())
            placeholder = self.gen_placeholder(data)
            return f'({field_names}) = ({placeholder})'

    # core queries
    # SELECT query
    # args:
        # conditions: DICT where the keys = the fields name of the condition and the value is the value need to be matched
        #  fields: LIST <STRING> where each value is the field you wish to return, default is * (ALL)
    # return:
        # LIST<DICT> where each value is a dict representing a row of data that matched the query
            # in each dict the keys are the fields desired with the values being the data stored at that field
    def find(self, conditions, fields=['*']):
        fields_string = ', '.join(fields)
        condition_string = self.param_formatter(conditions.keys())
        values = conditions.values()
        query_string = f'SELECT {fields_string} FROM {self.table} WHERE {condition_string}'
        return db.execute(query_string, *values)

    # INSERT query
    # args:
        # data: DICT where the keys fields that are going to be created and the values are the data to be stores in those fields
    # Return:
        # NUMBER: the Id of the newly created data
    def create(self, data):
        fields = ', '.join(data.keys())
        placeholders = self.gen_placeholder(data)
        values = data.values()
        query_string = f'INSERT INTO {self.table} ({fields}) VALUES ({placeholders})'
        return db.execute(query_string, *values)

    # UPDATE query
    # args:
        # data: DICT where the keys fields that are going to be updated and the values is the data to for those updates
        # conditions: DICT where the keys = the fields name of the condition and the value is the value need to be matched
    # Return:
        # NUMBER: the number of fields updated
    def update(self, data, conditions):
        fields = self.update_fields(data)
        condition_string = self.param_formatter(conditions.keys())
        values = [*data.values(), *conditions.values()]
        query_string = f"UPDATE {self.table} SET {fields} WHERE {condition_string}"
        return db.execute(query_string, *values)

    def delete(self, conditions):
        condition_string = self.param_formatter(conditions.keys())
        values = conditions.values()
        query_string = f'DELETE FROM {self.table} WHERE {condition_string}'
        return db.execute(query_string, *values)
