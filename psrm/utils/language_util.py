def convert_to_danish(s):
    d = {'&#198;': 'Æ', '&#248;': 'ø', '&#229;': 'å'}
    for key in d.keys():
        s = s.replace(key, d[key])
    return s
