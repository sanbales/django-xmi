from networkx import DiGraph, topological_sort
from copy import deepcopy
from os import path
from re import compile as re_compile, split as re_split
from textwrap import wrap
from warnings import warn
import urllib.request
import xmltodict
from .util import DotDict, snake_to_camel, camel_to_snake, make_name_safe


# Map types to Fields
FIELD_MAPPINGS = {'boolean': {'name': 'BooleanField', 'args': []},
                  'string': {'name': 'CharField', 'args': ['max_length=255']},
                  'real': {'name': 'FloatField', 'args': []},
                  'integer': {'name': 'IntegerField', 'args': []},
                  # TODO: figure out better field for `unlimited natural`
                  'unlimited_natural': {'name': 'IntegerField', 'args': []}}

url_re = re_compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
ignore_re = re_compile('^[aeAE]_')
ascii_fix_re = re_compile(r'[^\x00-\x7F]+')


class XmiParser(object):
    """Methods for parsing and storying XMI objects."""

    def __init__(self):
        self.elements = DotDict({})
        self.packages = DotDict({})
        self.literals = DotDict({})
        self.accessors = []
        self.field_mappings = deepcopy(FIELD_MAPPINGS)

    def parse(self, loc):
        """
        Parse an XMI file.

        :param loc: location of the xmi file to be parsed

        """
        if url_re.match(loc):
            with urllib.request.urlopen(loc) as response:
                xmi = response.read()
        elif path.exists(loc):
            with open(loc, 'r', encoding='utf-8') as file:
                xmi = ''.join([line.decode() if hasattr(line, 'decode') else line for line in file.readlines()])
        else:
            raise ValueError('Could not parse XMI from "{}"'.format(loc))

        if hasattr(xmi, 'decode'):
            xmi = xmi.decode()

        xmi = DotDict(xmltodict.parse(xmi))

        if 'XMI' in xmi:
            xmi = xmi.XMI
        else:
            warn('XMI not found')

        name = xmi.get('Profile', xmi.get('Package', {})).get('name', None)
        if name is None:
            warn("Could not get a name for the XMI at '{}'".format(loc))
            return xmi
        else:
            self.packages[name] = xmi

    def import_package(self, xmi):
        packages = {}
        for package in xmi.Profile.packageImport:
            if 'importedPackage' in package:
                packages[package['id']] = self.parse(package['importedPackage']['href'])
        return packages

    def parse_profile(self, source, key='Profile'):
        profile = source.get(key, {})
        for pkg in profile.get('packagedElement', {}).values():
            # Ignore deprecated packages
            if 'deprecated' in pkg.name.lower():
                warn("Ignoring '{}' Package because it appears to be deprecated".format(pkg.name))
                continue
            for elem in pkg.get('packagedElement', {}).values():
                if not isinstance(elem, dict) or "name" not in elem:
                    continue

                # Rename owned_____ keys, e.g., ownedAttributes
                for key in elem.keys():
                    if key.startswith('owned'):
                        value = elem[key]
                        # Fix in case the owned item is not a proper dictionary
                        if all(v in value for v in ('id', 'name', 'type')):
                            value = DotDict({value.name: value})
                        new_key = key.replace('owned', '').lower() + 's'
                        elem[new_key] = value
                        del elem[key]

                elem.update({'__profile__': profile.name,
                             '__package__': profile.name + '.' + pkg.name,
                             '__ignore__': bool(ignore_re.match(elem.name)),
                             '__modelclass__': self.get_generalization(elem) or 'models.Model',
                             '__docstring__': self._get_comment(elem),
                             '__is_abstract__': elem.get('isAbstract', False)})

                # We do not store the ignored elements, but we still process them
                if not elem.__ignore__:
                    key = camel_to_snake(elem.name)
                    if key in self.elements:
                        warn("Overwriting element '{}'".format(key))
                    self.elements[key] = elem

    def ordered_elements(self, base_type='element'):
        """
        Sort the elements based on their generalization dependencies to each other.

        :param base_type: the name of the element to use as the basic entity (snake_case)
        :type base_type: str
        """
        dep_graph = DiGraph()
        for name, elem in self.elements.items():
            sup_cls = elem.__modelclass__

            if name == base_type:
                elem.__modelclass__ = 'models.Model'
            elif ',' in sup_cls:
                for dep in sup_cls.split(','):
                    dep_graph.add_edge(name, camel_to_snake(dep.strip()))
            else:
                dep_graph.add_edge(name, camel_to_snake(sup_cls))

        sorted_elements = list(topological_sort(dep_graph))
        sorted_elements.reverse()
        return sorted_elements

    def process_literals(self):
        """Process all the literals declared in the package"""
        for element in self.elements.values():
            literals = element.get('literals', {})
            if literals:
                literals = {k: v for k, v in literals.items() if '_' != k[0]}
                # Determine if the long should be the description (i.e., comment)
                use_desc = all('ownedComment' in choice for choice in literals.values())
                iterator = literals.items() if use_desc else enumerate(literals)

                choices = []
                for short, long in iterator:
                    code = "'{}'" if use_desc else "{}"
                    long = long.ownedComment.body if use_desc else long
                    choice = ("(" + code + ", '{}')").format(short, long)
                    if len(choice) > 112:
                        ch_ind = ' ' * (10 + len(choice.split(',')[0]))
                        joint = " ' +\n" + ch_ind + "'"
                        choice = joint.join(wrap(choice, 112))
                        if len(choices) == 0:
                            choice = '\n' + ' ' * 8 + choice
                    choices += [choice]
                choices_var_name = camel_to_snake(element.name).upper() + '_CHOICES'
                choices = (',\n' + ' '*8).join(choices)

                choices = '    {} = ({})'.format(choices_var_name, choices)

                field = 'CharField' if use_desc else 'IntegerField'
                args = ['max_length=255'] if use_desc else []
                args += ['choices=' + choices_var_name]
                if element.name in self.literals:
                    warn("Overwriting literal for '{}'".format(element.name))
                self.literals[element.name] = DotDict({'field': field,
                                                       'args': args,
                                                       'choices': choices})

    def process_attributes(self):
        """
        Prepares the Django fields from the ownedAttributes.

        """
        for element in self.elements.values():
            for attr_name, attr in element.get('attributes', {}).items():
                attr_name = make_name_safe(attr_name)
                attr.name = attr_name

                # Check accessor to avoid conflicts with Django
                accessor = element.name + '.' + attr_name
                reverse_accessor = snake_to_camel(attr_name) + '.' + camel_to_snake(element.name)
                if reverse_accessor in self.accessors:
                    warn("Ignoring: {}".format(accessor))
                    continue
                else:
                    self.accessors.append(accessor)

                args = []
                attr.__print__ = DotDict({})
                attr.__field__ = None
                attr.__other__ = None

                # Identify Field Type
                if isinstance(attr.type, str):
                    attr.__field__ = 'ForeignKey'
                    attr.__other__ = attr.type
                elif isinstance(attr.type, dict):
                    if 'idref' in attr.type:
                        attr.__field__ = 'ForeignKey'
                        attr.__other__ = attr.type['idref'].split('_')[-1]
                    elif 'href' in attr.type:
                        href = attr.type['href'].split('#')[-1]
                        attr.__field__ = 'ForeignKey'
                        attr.__other__ = href
                        href = camel_to_snake(href)
                        if href in self.field_mappings:
                            attr.__field__ = self.field_mappings[href]['name']
                            attr.__other__ = None
                            args += self.field_mappings[href]['args']

                # If a reference to self, use 'self' for other
                if attr.__other__ == element.name:
                    attr.__other__ = 'self'

                # Check to see if field is not really an enum
                literal = self.literals.get(attr.__other__, None)
                if literal:
                    attr.__field__ = literal.field
                    attr.__other__ = None
                    attr.__choices__ = literal.choices
                    args += literal.args

                # TODO check to make sure the plus is necessary, add it back to the args line if so
                # added_plus = '+' if accessor in TROUBLE_ACCESSORS else ''
                if attr.__other__:
                    args += ["related_name='%(app_label)s_%(class)s_{}'".format(attr_name)]

                    # Define mutliplicities
                    if attr.get('upperValue', {}).get('value', None) == '*':
                        attr.__field__ = 'ManyToManyField'

                if 'lowerValue' in attr:
                    args += ['blank=True']

                if attr.__field__ not in ('ManyToManyField', 'BooleanField'):
                    # TODO: Check to see if this is necessary
                    args += ['null=True']

                # Get default
                default = attr.get('defaultValue', {}).get('instance', None)
                if default:
                    # TODO: must ensure the parsing of the default value coincides with the literals
                    if hasattr(default, 'keys'):
                        default = list(default.values())[0]
                    # TODO: find better way to reference these type of things (maybe a weakproxy dict of {id: proxyref}?
                    split_by = '-' if '-' in default else '_'
                    args += ["default='{}'".format(default.split(split_by)[-1])]

                attr.__print__ = DotDict({'field': '    {name} = models.{__field__}'.format(**attr)})
                if attr.__other__:
                    args = ["'{}'".format(attr.__other__)] + args

                help_text = attr.help_text = self._get_comment(attr)
                if help_text:
                    help_text = help_text.replace("'", '"')
                    help_str = "help_text='{}'".format(help_text)

                    # If the field declaration will be too long, wrap the help text
                    field_len = len(attr.__print__.field)
                    if field_len + len(', '.join(args)) + len(help_str) > 112:
                        help_ind = ' ' * (len(attr.__print__.field) + 1)
                        joint = " ' +\n" + help_ind + "'"
                        prepend = ('\n' + help_ind) if args else ''
                        attr.__print__.help_text = prepend + joint.join(wrap(help_str, 112 - field_len))
                attr.__print__.args = args

    @staticmethod
    def _get_comment(elem):
        return ascii_fix_re.sub("'", elem.get('comments', elem.get('ownedComment', {})).get('body', ''))

    def _parse_function(self, func, elem, prepend):
        _indent = ' ' * 4
        fn_name = camel_to_snake(func.name)
        lines = []

        if fn_name in elem.get('attributes', {}):
            fn_name = prepend + fn_name

        fn_name = make_name_safe(fn_name)
        func.name = fn_name

        comment = self._get_comment(func)
        # TODO: There may be a nicer way to do this
        ocl = (func.get('ownedRule', {})
               .get('specification', {})
               .get('body', '')) or func.get('specification', {}).get('body', '')
        lines += [_indent + 'def {}(self):'.format(fn_name)]
        if comment:
            lines += [_indent * 2 + '"""']
            for line in [(_indent + s) for s in wrap('{}\n'.format(comment), 104)]:
                lines += [_indent + line]
            if not ocl:
                lines += [_indent * 2 + '"""']

        method_body = '''raise NotImplementedError("Must manually implement this method!")'''
        if ocl:
            ocl = _indent * 3 + ocl.replace('\n\n', '\n').replace('\n', '\n' + _indent * 3)
            if comment:
                lines += ['']
            else:
                lines += [_indent * 2 + '"""']
            lines += [_indent * 2 + '.. ocl::']
            lines += ['{}'.format(ocl)]
            lines += [_indent * 2 + '"""']
            method_body = '''raise NotImplemented("Must manually translate OCL to Python: '{}'")'''.format(ocl.strip())
        lines += [_indent * 2 + method_body]
        return lines

    def process_operations_and_rules(self):
        for element in self.elements.values():
            for operation in element.get('operations', {}).values():
                operation.__print__ = self._parse_function(operation, element, 'get_')
            for rule in element.get('rules', {}).values():
                rule.__print__ = self._parse_function(rule, element, 'validate_')

    def process_meta(self):
        # TODO: this is currently not useful, figure out if we need to go back to abstract models or remove this
        _indent = ' ' * 4
        for elem in self.elements:
            if elem.__is_abstract__:
                elem.__print__ = ['\n' + _indent + 'class Meta:\n' + _indent * 2 + 'abstract = True\n']

    def get_generalization(self, element):
        if isinstance(element, str):
            return element.split('_')[-1]

        if hasattr(element, 'keys'):
            if 'generalization' in element:
                return self.get_generalization(element['generalization'])
            if 'general' in element:
                return self.get_generalization(element['general'])
            if 'idref' in element:
                # TODO: add feature to find the class name of this ref
                return self.get_generalization(element['idref'])
            if 'href' in element:
                return self.get_generalization(element['href'])

        if isinstance(element, (list, tuple)):
            generalizations = []
            for general in element:
                generalizations.append(self.get_generalization(general))
            return ', '.join(generalizations)

        if element is not None and 'type' in element:
            return element['type'].split(':')[-1]

        return element
