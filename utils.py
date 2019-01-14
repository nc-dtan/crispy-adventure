def is_integer(a):
    try:
        _ = int(a)
    except ValueError:
        return False
    return True
