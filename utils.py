from dateutil import parser


def is_integer(a):
    try:
        _ = int(a)
    except ValueError:
        return False
    return True


def convert_from_str(date):
    return parser.parse(date)
