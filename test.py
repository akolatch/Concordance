
name = 'aharon'
word = 'hello'
thing = 'world'
t = [name, word, thing]

num = ['1']


def param_formater(params):
    return f'{" =? AND ".join(params)}=?'


print(', '.join(t))
