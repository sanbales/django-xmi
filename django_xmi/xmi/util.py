from re import compile as re_compile


STRING_REPLACEMENTS = {'__': [':'],
                       '': ['@', '#']}
KEY_PREFIXES_TO_REMOVE = {'xmi', 'uml', 'oslc', 'rdf'}

# Determine which terms will not be allowed
RESERVED_TERMS = set(['False', 'class', 'finally', 'is', 'return', 'None', 'continue', 'for', 'lambda', 'try',
                      'True', 'def', 'from', 'nonlocal', 'while', 'and', 'del', 'global', 'not', 'with', 'as',
                      'elif', 'if', 'or', 'yield', 'assert', 'else', 'import', 'pass', 'break', 'except', 'in',
                      'raise'] + __builtins__.__dir__())
RESERVED_TERMS = tuple(term for term in RESERVED_TERMS if '_' != term[0])

# Declare regular expressions
first_cap_re = re_compile(r'(.)([A-Z][a-z]+)')
all_cap_re = re_compile(r'([a-z0-9])([A-Z])')


def camel_to_snake(camel_str):
    """
    Convert CamelCase to snake_case.

    :param camel_str: input string that should be in CamelCase form
    :return: string in snake_case form

    """
    s1 = first_cap_re.sub(r'\1_\2', camel_str)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_to_camel(snake_str, upper=True):
    """
    Convert snake_case to UpperCamelCase or lowerCamelCase.

    :param snake_str: input string that should be in snake_case form
    :param upper: flag to use UpperCamelCase vs lowerCamelCase
    :return: string in camel case form

    """
    components = snake_str.split('_')
    if upper:
        return "".join(x.title() for x in components)
    else:
        return components[0] + "".join(x.title() for x in components[1:])


def make_name_safe(name):
    name = camel_to_snake(name)
    if name in RESERVED_TERMS:
        # PEP-8's recommends adding an '_' after the name, but that is not allowed in Django
        name = 'has_' + name
    name = name.replace('__', '_')
    return name


class DotDict(dict):
    """
    A dictionary that supports dot notation as well as dictionary access notation.

    .. usage::
        d = DotDict() or d = DotDict({'val1': 'first'})
        set attributes: d.val2 = 'second' or d['val2'] = 'second'
        get attributes: d.val2 or d['val2']

    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, input_=None, list_to_dict_key='name'):
        clean_input = {} if input_ is None else self._clean(input_)

        if hasattr(clean_input, 'keys'):
            for key, value in clean_input.items():
                if hasattr(value, 'keys'):
                    value = DotDict(value)
                elif isinstance(value, (list, tuple)) and all(list_to_dict_key in item for item in value):
                    value = DotDict({item[list_to_dict_key]: item for item in value})

                self[key] = value
        elif isinstance(clean_input, (list, tuple)) and all(list_to_dict_key in item for item in clean_input):
            for item in clean_input:
                if list_to_dict_key in item:
                    self[item[list_to_dict_key]] = DotDict(item)
        super().__init__()

    def _clean(self, input_):
        if hasattr(input_, 'keys'):
            new = {}
            for key, value in input_.items():
                new_key = key
                new_value = self._clean(value)

                for new_char, bad_chars in STRING_REPLACEMENTS.items():
                    for bad_char in bad_chars:
                        new_key = new_key.replace(bad_char, new_char)

                for ns in KEY_PREFIXES_TO_REMOVE:
                    new_key = new_key.replace('{}__'.format(ns), '')

                new[new_key] = new_value
        elif isinstance(input_, (list, tuple)):
            new = [None] * len(input_)
            for i, item in enumerate(input_):
                new[i] = self._clean(item)
        else:
            return input_
        return new

    def __dir__(self):
        return list(self.keys())
