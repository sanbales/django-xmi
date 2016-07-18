from os import path
from re import compile as re_compile
import urllib.request
import xmltodict


LIST_TO_DICT_KEY = 'name'
REPLACEMENTS = {'__': [':'],
                '': ['@', '#']}
NS_TO_REMOVE_FROM_KEYS = {'xmi', 'uml', 'oslc', 'rdf'}
BASE_URL = 'https://raw.githubusercontent.com/axelreichwein/SysML2OSLCResourceShapes/master/SysMLProfileToOSLCResourceShapes/Resource%20Shapes/'
FIELDS_MAP = {'string': 'TextField',
              'integer': 'IntegerField',
              'boolean': 'BooleanField'}
FIELD = '    {name} = {kind}({model}help_text="{description}"{extra_attrs})'
BASE_DIR = 'c:/sandboxes/SysML2OSLCResourceShapes/SysMLProfileToOSLCResourceShapes/Resource Shapes/'
FIELDS_TO_SKIP = ('name', 'visibility', 'uri')

first_cap_re = re_compile(r'(.)([A-Z][a-z]+)')
all_cap_re = re_compile(r'([a-z0-9])([A-Z])')
url_re = re_compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def camel_to_snake(camel_str):
    s1 = first_cap_re.sub(r'\1_\2', camel_str)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def parse_xmi(xmi_loc):
    if url_re.match(xmi_loc):
        with urllib.request.urlopen(xmi_loc) as response:
            xmi = response.read()
    elif path.exists(xmi_loc):
        with open(xmi_loc, 'r') as file:
            xmi = file.readlines()

    xmi = DotDict(xmltodict.parse(xmi.decode()))

    if 'XMI' in xmi:
        return xmi.XMI

    return xmi


class DotDict(dict):
    """
    a dictionary that supports dot notation 
    as well as dictionary access notation 
    usage: d = DotDict() or d = DotDict({'val1':'first'})
    set attributes: d.val2 = 'second' or d['val2'] = 'second'
    get attributes: d.val2 or d['val2']
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, input_=None):
        clean_input = {} if inp is None else self._clean(input_)

        if hasattr(clean_input, 'keys'):
            for key, value in clean_input.items():
                if hasattr(value, 'keys'):
                    value = DotDict(value, self)
                elif isinstance(value, (list, tuple)) and all(LIST_TO_DICT_KEY in item for item in value):
                    value = DotDict({item[LIST_TO_DICT_KEY]: item for item in value}, self)

                self[key] = value
        elif isinstance(clean_input, (list, tuple)) and all(LIST_TO_DICT_KEY in item for item in clean_input):
            for item in clean_input:
                if LIST_TO_DICT_KEY in item:
                    self[item[LIST_TO_DICT_KEY]] = DotDict(item)

    def _clean(self, inp):
        if hasattr(inp, 'keys'):
            new = {}
            for key, value in inp.items():
                new_key = key
                new_value = self._clean(value)
                
                for new_char, bad_chars in REPLACEMENTS.items():
                    for bad_char in bad_chars:
                        new_key = new_key.replace(bad_char, new_char)

                for ns in NS_TO_REMOVE_FROM_KEYS:
                    new_key = new_key.replace('{}__'.format(ns), '')
                
                new[new_key] = new_value
        elif isinstance(inp, (list, tuple)):
            new = [None] * len(inp)
            for i, item in enumerate(inp):
                new[i] = self._clean(item)
        else:
            return inp
        return new

    def __dir__(self):
        return list(self.keys())


def get_generalization(element):
    if isinstance(element, str):
        return element.split('_')[-1]
    
    if hasattr(element, 'keys'):
        if 'generalization' in element:
            return get_generalization(element['generalization'])
        if 'general' in element:
            return get_generalization(element['general'])
        if 'idref' in element:
            # TODO: add feature to find the class name of this ref
            return get_generalization(element['idref'])
        if 'href' in element:
            return get_generalization(element['href'])

    if isinstance(element, (list, tuple)):
        generalizations = []
        for general in element:
            generalizations.append(get_generalization(general))
        return ', '.join(generalizations)
    
    if element is not None and 'type' in element:
        return element['type'].split(':')[-1]
    
    return element
