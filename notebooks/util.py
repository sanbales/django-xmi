import urllib.request
import xmltodict
import re


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(camel_str):
    s1 = first_cap_re.sub(r'\1_\2', camel_str)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


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


def get_spec(url):
    with urllib.request.urlopen(url) as response:
        xml = response.read()

    return DotDict(xmltodict.parse(xml.decode()))


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

    def __init__(self, inp=None, parent=None):
        #self.__id = uuid4()
        clean_input = {} if inp is None else self._clean(inp)

        for key, value in clean_input.items():
            if hasattr(value, 'keys'):
                value = DotDict(value, self)
            elif isinstance(value, list) and all(LIST_TO_DICT_KEY in item for item in value):
                value = DotDict({item[LIST_TO_DICT_KEY]: item for item in value}, self)

            self[key] = value
    
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