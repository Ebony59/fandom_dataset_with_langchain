def is_empty(text):
    empty = False
    if text == None:
        empty = True
    elif type(text) == float:
        if str(text) == 'nan':
            empty = True
        elif text == np.nan:
            empty = True
    elif type(text) == str:
        if len(text) == 0:
            empty = True
    return empty