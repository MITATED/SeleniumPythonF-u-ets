# emacs-mode: -*- python-*-

def ru(text):
    txt = text.decode('utf-8')
    return txt



def mask(text):
    i = 0
    txt = []
    while (len(text) > i):
        txt[i:(i + 1)] = [text[i].decode('utf-8')]
        i = (i + 1)

    return txt



def codos(text):
    txt = text.encode('utf-8')
    return txt



# local variables:
# tab-width: 4
