from django.db import models


class Element(models.Model):
    """
    An Element is a constituent of a model. As such, it has the capability of owning other Elements.
    """

    __package__ = 'UML.CommonStructure'

    owned_comment = models.ManyToManyField('Comment', related_name='%(app_label)s_%(class)s_owned_comment', blank=True, 
                                           help_text='The Comments owned by this Element.')
    owned_element = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_owned_element', blank=True, 
                                           help_text='The Elements owned by this Element.')
    owner = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_owner', blank=True, null=True, 
                              help_text='The Element that owns this Element.')

    def all_owned_elements(self):
        """
        The query allOwnedElements() gives all of the direct and indirect ownedElements of an Element.

        .. ocl::
            result = (ownedElement->union(ownedElement->collect(e | e.allOwnedElements()))->asSet())
        """
        pass

    def has_owner(self):
        """
        Elements that must be owned must have an owner.

        .. ocl::
            mustBeOwned() implies owner->notEmpty()
        """
        pass

    def must_be_owned(self):
        """
        The query mustBeOwned() indicates whether Elements of this type must have an owner. Subclasses of
        Element that do not require an owner must override this operation.

        .. ocl::
            result = (true)
        """
        pass

    def not_own_self(self):
        """
        An element may not directly or indirectly own itself.

        .. ocl::
            not allOwnedElements()->includes(self)
        """
        pass

class TemplateableElement(models.Model):
    """
    A TemplateableElement is an Element that can optionally be defined as a template and bound to other
    templates.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owned_template_signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_owned_template_signature', blank=True, null=True, 
                                                 help_text='The optional TemplateSignature specifying the formal ' +
                                                 'TemplateParameters for this TemplateableElement. If a ' +
                                                 'TemplateableElement has a TemplateSignature, then it is a ' +
                                                 'template.')
    template_binding = models.ManyToManyField('TemplateBinding', related_name='%(app_label)s_%(class)s_template_binding', blank=True, 
                                              help_text='The optional TemplateBindings from this ' +
                                              'TemplateableElement to one or more templates.')

    def is_template(self):
        """
        The query isTemplate() returns whether this TemplateableElement is actually a template.

        .. ocl::
            result = (ownedTemplateSignature <> null)
        """
        pass

    def parameterable_elements(self):
        """
        The query parameterableElements() returns the set of ParameterableElements that may be used as the
        parameteredElements for a TemplateParameter of this TemplateableElement. By default, this set includes
        all the ownedElements. Subclasses may override this operation if they choose to restrict the set of
        ParameterableElements.

        .. ocl::
            result = (self.allOwnedElements()->select(oclIsKindOf(ParameterableElement)).oclAsType(ParameterableElement)->asSet())
        """
        pass

class NamedElement(models.Model):
    """
    A NamedElement is an Element in a model that may have a name. The name may be given directly and/or via the
    use of a StringExpression.
    """

    __package__ = 'UML.CommonStructure'

    client_dependency = models.ManyToManyField('Dependency', related_name='%(app_label)s_%(class)s_client_dependency', blank=True, 
                                               help_text='Indicates the Dependencies that reference this ' +
                                               'NamedElement as a client.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True, )
    name_expression = models.ForeignKey('StringExpression', related_name='%(app_label)s_%(class)s_name_expression', blank=True, null=True, 
                                        help_text='The StringExpression used to define the name of this ' +
                                        'NamedElement.')
    namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_namespace', blank=True, null=True, 
                                  help_text='Specifies the Namespace that owns the NamedElement.')
    qualified_name = models.CharField(max_length=255, blank=True, null=True, 
                                      help_text='A name that allows the NamedElement to be identified within a ' +
                                      'hierarchy of nested Namespaces. It is constructed from the names of the ' +
                                      'containing Namespaces starting at the root of the hierarchy and ending with ' +
                                      'the name of the NamedElement itself.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', blank=True, null=True, 
                                   help_text='Determines whether and how the NamedElement is visible outside its ' +
                                   'owning Namespace.')

    def all_namespaces(self):
        """
        The query allNamespaces() gives the sequence of Namespaces in which the NamedElement is nested, working
        outwards.

        .. ocl::
            result = (if owner.oclIsKindOf(TemplateParameter) and
              owner.oclAsType(TemplateParameter).signature.template.oclIsKindOf(Namespace) then
                let enclosingNamespace : Namespace =
                  owner.oclAsType(TemplateParameter).signature.template.oclAsType(Namespace) in
                    enclosingNamespace.allNamespaces()->prepend(enclosingNamespace)
            else
              if namespace->isEmpty()
                then OrderedSet{}
              else
                namespace.allNamespaces()->prepend(namespace)
              endif
            endif)
        """
        pass

    def all_owning_packages(self):
        """
        The query allOwningPackages() returns the set of all the enclosing Namespaces of this NamedElement,
        working outwards, that are Packages, up to but not including the first such Namespace that is not a
        Package.

        .. ocl::
            result = (if namespace.oclIsKindOf(Package)
            then
              let owningPackage : Package = namespace.oclAsType(Package) in
                owningPackage->union(owningPackage.allOwningPackages())
            else
              null
            endif)
        """
        pass

    def client_dependency(self):
        """
        .. ocl::
            result = (Dependency.allInstances()->select(d | d.client->includes(self)))
        """
        pass

    def has_no_qualified_name(self):
        """
        If there is no name, or one of the containing Namespaces has no name, there is no qualifiedName.

        .. ocl::
            name=null or allNamespaces()->select( ns | ns.name=null )->notEmpty() implies qualifiedName = null
        """
        pass

    def has_qualified_name(self):
        """
        When there is a name, and all of the containing Namespaces have a name, the qualifiedName is constructed
        from the name of the NamedElement and the names of the containing Namespaces.

        .. ocl::
            (name <> null and allNamespaces()->select(ns | ns.name = null)->isEmpty()) implies
              qualifiedName = allNamespaces()->iterate( ns : Namespace; agg: String = name | ns.name.concat(self.separator()).concat(agg))
        """
        pass

    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() determines whether two NamedElements may logically co-exist within a
        Namespace. By default, two named elements are distinguishable if (a) they have types neither of which is
        a kind of the other or (b) they have different names.

        .. ocl::
            result = ((self.oclIsKindOf(n.oclType()) or n.oclIsKindOf(self.oclType())) implies
                ns.getNamesOfMember(self)->intersection(ns.getNamesOfMember(n))->isEmpty()
            )
        """
        pass

    def qualified_name(self):
        """
        When a NamedElement has a name, and all of its containing Namespaces have a name, the qualifiedName is
        constructed from the name of the NamedElement and the names of the containing Namespaces.

        .. ocl::
            result = (if self.name <> null and self.allNamespaces()->select( ns | ns.name=null )->isEmpty()
            then 
                self.allNamespaces()->iterate( ns : Namespace; agg: String = self.name | ns.name.concat(self.separator()).concat(agg))
            else
               null
            endif)
        """
        pass

    def separator(self):
        """
        The query separator() gives the string that is used to separate names when constructing a qualifiedName.

        .. ocl::
            result = ('::')
        """
        pass

    def visibility_needs_ownership(self):
        """
        If a NamedElement is owned by something other than a Namespace, it does not have a visibility. One that
        is not owned by anything (and hence must be a Package, as this is the only kind of NamedElement that
        overrides mustBeOwned()) may have a visibility.

        .. ocl::
            (namespace = null and owner <> null) implies visibility = null
        """
        pass

class Namespace(models.Model):
    """
    A Namespace is an Element in a model that owns and/or imports a set of NamedElements that can be identified
    by name.
    """

    __package__ = 'UML.CommonStructure'

    element_import = models.ManyToManyField('ElementImport', related_name='%(app_label)s_%(class)s_element_import', blank=True, 
                                            help_text='References the ElementImports owned by the Namespace.')
    imported_member = models.ManyToManyField('PackageableElement', related_name='%(app_label)s_%(class)s_imported_member', blank=True, 
                                             help_text='References the PackageableElements that are members of ' +
                                             'this Namespace as a result of either PackageImports or ' +
                                             'ElementImports.')
    member = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_member', blank=True, 
                                    help_text='A collection of NamedElements identifiable within the Namespace, ' +
                                    'either by being owned or by being introduced by importing or inheritance.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    owned_member = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_owned_member', blank=True, 
                                          help_text='A collection of NamedElements owned by the Namespace.')
    owned_rule = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_owned_rule', blank=True, 
                                        help_text='Specifies a set of Constraints owned by this Namespace.')
    package_import = models.ManyToManyField('PackageImport', related_name='%(app_label)s_%(class)s_package_import', blank=True, 
                                            help_text='References the PackageImports owned by the Namespace.')

    def cannot_import_owned_members(self):
        """
        A Namespace cannot have an ElementImport to one of its ownedMembers.

        .. ocl::
            elementImport.importedElement.oclAsType(Element)->excludesAll(ownedMember)
        """
        pass

    def cannot_import_self(self):
        """
        A Namespace cannot have a PackageImport to itself.

        .. ocl::
            packageImport.importedPackage.oclAsType(Namespace)->excludes(self)
        """
        pass

    def exclude_collisions(self):
        """
        The query excludeCollisions() excludes from a set of PackageableElements any that would not be
        distinguishable from each other in this Namespace.

        .. ocl::
            result = (imps->reject(imp1  | imps->exists(imp2 | not imp1.isDistinguishableFrom(imp2, self))))
        """
        pass

    def get_names_of_member(self):
        """
        The query getNamesOfMember() gives a set of all of the names that a member would have in a Namespace,
        taking importing into account. In general a member can have multiple names in a Namespace if it is
        imported more than once with different aliases.

        .. ocl::
            result = (if self.ownedMember ->includes(element)
            then Set{element.name}
            else let elementImports : Set(ElementImport) = self.elementImport->select(ei | ei.importedElement = element) in
              if elementImports->notEmpty()
              then
                 elementImports->collect(el | el.getName())->asSet()
              else 
                 self.packageImport->select(pi | pi.importedPackage.visibleMembers().oclAsType(NamedElement)->includes(element))-> collect(pi | pi.importedPackage.getNamesOfMember(element))->asSet()
              endif
            endif)
        """
        pass

    def import_members(self):
        """
        The query importMembers() defines which of a set of PackageableElements are actually imported into the
        Namespace. This excludes hidden ones, i.e., those which have names that conflict with names of
        ownedMembers, and it also excludes PackageableElements that would have the indistinguishable names when
        imported.

        .. ocl::
            result = (self.excludeCollisions(imps)->select(imp | self.ownedMember->forAll(mem | imp.isDistinguishableFrom(mem, self))))
        """
        pass

    def imported_member(self):
        """
        The importedMember property is derived as the PackageableElements that are members of this Namespace as
        a result of either PackageImports or ElementImports.

        .. ocl::
            result = (self.importMembers(elementImport.importedElement->asSet()->union(packageImport.importedPackage->collect(p | p.visibleMembers()))->asSet()))
        """
        pass

    def members_are_distinguishable(self):
        """
        The Boolean query membersAreDistinguishable() determines whether all of the Namespace's members are
        distinguishable within it.

        .. ocl::
            result = (member->forAll( memb |
               member->excluding(memb)->forAll(other |
                   memb.isDistinguishableFrom(other, self))))
        """
        pass

    def members_distinguishable(self):
        """
        All the members of a Namespace are distinguishable within it.

        .. ocl::
            membersAreDistinguishable()
        """
        pass

class ParameterableElement(models.Model):
    """
    A ParameterableElement is an Element that can be exposed as a formal TemplateParameter for a template, or
    specified as an actual parameter in a binding of a template.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owning_template_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_owning_template_parameter', blank=True, null=True, 
                                                  help_text='The formal TemplateParameter that owns this ' +
                                                  'ParameterableElement.')
    template_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', blank=True, null=True, 
                                           help_text='The TemplateParameter that exposes this ' +
                                           'ParameterableElement as a formal parameter.')

    def is_compatible_with(self):
        """
        The query isCompatibleWith() determines if this ParameterableElement is compatible with the specified
        ParameterableElement. By default, this ParameterableElement is compatible with another
        ParameterableElement p if the kind of this ParameterableElement is the same as or a subtype of the kind
        of p. Subclasses of ParameterableElement should override this operation to specify different
        compatibility constraints.

        .. ocl::
            result = (self.oclIsKindOf(p.oclType()))
        """
        pass

    def is_template_parameter(self):
        """
        The query isTemplateParameter() determines if this ParameterableElement is exposed as a formal
        TemplateParameter.

        .. ocl::
            result = (templateParameter->notEmpty())
        """
        pass

class PackageableElement(models.Model):
    """
    A PackageableElement is a NamedElement that may be owned directly by a Package. A PackageableElement is also
    able to serve as the parameteredElement of a TemplateParameter.
    """

    __package__ = 'UML.CommonStructure'

    named_element = models.OneToOneField('NamedElement')
    parameterable_element = models.OneToOneField('ParameterableElement', on_delete=models.CASCADE, primary_key=True)
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', blank=True, null=True, default='public', 
                                   help_text='A PackageableElement must have a visibility specified if it is ' +
                                   'owned by a Namespace. The default visibility is public.')

    def namespace_needs_visibility(self):
        """
        A PackageableElement owned by a Namespace must have a visibility.

        .. ocl::
            visibility = null implies namespace = null
        """
        pass

class Type(models.Model):
    """
    A Type constrains the values represented by a TypedElement.
    """

    __package__ = 'UML.CommonStructure'

    package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_package', blank=True, null=True, 
                                help_text='Specifies the owning Package of this Type, if any.')
    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)

    def conforms_to(self):
        """
        The query conformsTo() gives true for a Type that conforms to another. By default, two Types do not
        conform to each other. This query is intended to be redefined for specific conformance situations.

        .. ocl::
            result = (false)
        """
        pass

class RedefinableElement(models.Model):
    """
    A RedefinableElement is an element that, when defined in the context of a Classifier, can be redefined more
    specifically or differently in the context of another Classifier that specializes (directly or indirectly)
    the context Classifier.
    """

    __package__ = 'UML.Classification'

    is_leaf = models.BooleanField(help_text='Indicates whether it is possible to further redefine a ' +
                                  'RedefinableElement. If the value is true, then it is not possible to further ' +
                                  'redefine the RedefinableElement.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    redefined_element = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_element', blank=True, 
                                               help_text='The RedefinableElement that is being redefined by this ' +
                                               'element.')
    redefinition_context = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', blank=True, 
                                                  help_text='The contexts that this element may be redefined ' +
                                                  'from.')

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two RedefinableElements in a context in which
        redefinition is possible, whether redefinition would be logically consistent. By default, this is false;
        this operation must be overridden for subclasses of RedefinableElement to define the consistency
        conditions.
        """
        pass

    def is_redefinition_context_valid(self):
        """
        The query isRedefinitionContextValid() specifies whether the redefinition contexts of this
        RedefinableElement are properly related to the redefinition contexts of the specified RedefinableElement
        to allow this element to redefine the other. By default at least one of the redefinition contexts of
        this element must be a specialization of at least one of the redefinition contexts of the specified
        element.

        .. ocl::
            result = (redefinitionContext->exists(c | c.allParents()->includesAll(redefinedElement.redefinitionContext)))
        """
        pass

    def non_leaf_redefinition(self):
        """
        A RedefinableElement can only redefine non-leaf RedefinableElements.

        .. ocl::
            redefinedElement->forAll(re | not re.isLeaf)
        """
        pass

    def redefinition_consistent(self):
        """
        A redefining element must be consistent with each redefined element.

        .. ocl::
            redefinedElement->forAll(re | re.isConsistentWith(self))
        """
        pass

    def redefinition_context_valid(self):
        """
        At least one of the redefinition contexts of the redefining element must be a specialization of at least
        one of the redefinition contexts for each redefined element.

        .. ocl::
            redefinedElement->forAll(re | self.isRedefinitionContextValid(re))
        """
        pass

class Classifier(models.Model):
    """
    A Classifier represents a classification of instances according to their Features.
    """

    __package__ = 'UML.Classification'

    attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_attribute', blank=True, 
                                       help_text='All of the Properties that are direct (i.e., not inherited or ' +
                                       'imported) attributes of the Classifier.')
    collaboration_use = models.ManyToManyField('CollaborationUse', related_name='%(app_label)s_%(class)s_collaboration_use', blank=True, 
                                               help_text='The CollaborationUses owned by the Classifier.')
    feature = models.ManyToManyField('Feature', related_name='%(app_label)s_%(class)s_feature', blank=True, 
                                     help_text='Specifies each Feature directly defined in the classifier. Note ' +
                                     'that there may be members of the Classifier that are of the type Feature but ' +
                                     'are not included, e.g., inherited features.')
    general = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_general', blank=True, 
                                     help_text='The generalizing Classifiers for this Classifier.')
    generalization = models.ManyToManyField('Generalization', related_name='%(app_label)s_%(class)s_generalization', blank=True, 
                                            help_text='The Generalization relationships for this Classifier. ' +
                                            'These Generalizations navigate to more general Classifiers in the ' +
                                            'generalization hierarchy.')
    inherited_member = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_inherited_member', blank=True, 
                                              help_text='All elements inherited by this Classifier from its ' +
                                              'general Classifiers.')
    is_abstract = models.BooleanField(help_text='If true, the Classifier can only be instantiated by ' +
                                      'instantiating one of its specializations. An abstract Classifier is ' +
                                      'intended to be used by other Classifiers e.g., as the target of ' +
                                      'Associations or Generalizations.')
    is_final_specialization = models.BooleanField()
    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    owned_template_signature = models.ForeignKey('RedefinableTemplateSignature', related_name='%(app_label)s_%(class)s_owned_template_signature', blank=True, null=True, 
                                                 help_text='The optional RedefinableTemplateSignature specifying ' +
                                                 'the formal template parameters.')
    owned_use_case = models.ManyToManyField('UseCase', related_name='%(app_label)s_%(class)s_owned_use_case', blank=True, 
                                            help_text='The UseCases owned by this classifier.')
    powertype_extent = models.ManyToManyField('GeneralizationSet', related_name='%(app_label)s_%(class)s_powertype_extent', blank=True, 
                                              help_text='The GeneralizationSet of which this Classifier is a ' +
                                              'power type.')
    redefinable_element = models.OneToOneField('RedefinableElement')
    redefined_classifier = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_classifier', blank=True, 
                                                  help_text='The Classifiers redefined by this Classifier.')
    representation = models.ForeignKey('CollaborationUse', related_name='%(app_label)s_%(class)s_representation', blank=True, null=True, 
                                       help_text='A CollaborationUse which indicates the Collaboration that ' +
                                       'represents this Classifier.')
    substitution = models.ManyToManyField('Substitution', related_name='%(app_label)s_%(class)s_substitution', blank=True, 
                                          help_text='The Substitutions owned by this Classifier.')
    template_parameter = models.ForeignKey('ClassifierTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', blank=True, null=True, 
                                           help_text='TheClassifierTemplateParameter that exposes this element as ' +
                                           'a formal parameter.')
    templateable_element = models.OneToOneField('TemplateableElement')
    type = models.OneToOneField('Type')
    use_case = models.ManyToManyField('UseCase', related_name='%(app_label)s_%(class)s_use_case', blank=True, 
                                      help_text='The set of UseCases for which this Classifier is the subject.')

    def all_attributes(self):
        """
        The query allAttributes gives an ordered set of all owned and inherited attributes of the Classifier.
        All owned attributes appear before any inherited attributes, and the attributes inherited from any more
        specific parent Classifier appear before those of any more general parent Classifier. However, if the
        Classifier has multiple immediate parents, then the relative ordering of the sets of attributes from
        those parents is not defined.

        .. ocl::
            result = (attribute->asSequence()->union(parents()->asSequence().allAttributes())->select(p | member->includes(p))->asOrderedSet())
        """
        pass

    def all_features(self):
        """
        The query allFeatures() gives all of the Features in the namespace of the Classifier. In general,
        through mechanisms such as inheritance, this will be a larger set than feature.

        .. ocl::
            result = (member->select(oclIsKindOf(Feature))->collect(oclAsType(Feature))->asSet())
        """
        pass

    def all_parents(self):
        """
        The query allParents() gives all of the direct and indirect ancestors of a generalized Classifier.

        .. ocl::
            result = (parents()->union(parents()->collect(allParents())->asSet()))
        """
        pass

    def all_realized_interfaces(self):
        """
        The Interfaces realized by this Classifier and all of its generalizations

        .. ocl::
            result = (directlyRealizedInterfaces()->union(self.allParents()->collect(directlyRealizedInterfaces()))->asSet())
        """
        pass

    def all_slottable_features(self):
        """
        All StructuralFeatures related to the Classifier that may have Slots, including direct attributes,
        inherited attributes, private attributes in generalizations, and memberEnds of Associations, but
        excluding redefined StructuralFeatures.

        .. ocl::
            result = (member->select(oclIsKindOf(StructuralFeature))->
              collect(oclAsType(StructuralFeature))->
               union(self.inherit(self.allParents()->collect(p | p.attribute)->asSet())->
                 collect(oclAsType(StructuralFeature)))->asSet())
        """
        pass

    def all_used_interfaces(self):
        """
        The Interfaces used by this Classifier and all of its generalizations

        .. ocl::
            result = (directlyUsedInterfaces()->union(self.allParents()->collect(directlyUsedInterfaces()))->asSet())
        """
        pass

    def conforms_to(self):
        """
        The query conformsTo() gives true for a Classifier that defines a type that conforms to another. This is
        used, for example, in the specification of signature conformance for operations.

        .. ocl::
            result = (if other.oclIsKindOf(Classifier) then
              let otherClassifier : Classifier = other.oclAsType(Classifier) in
                self = otherClassifier or allParents()->includes(otherClassifier)
            else
              false
            endif)
        """
        pass

    def directly_realized_interfaces(self):
        """
        The Interfaces directly realized by this Classifier

        .. ocl::
            result = ((clientDependency->
              select(oclIsKindOf(Realization) and supplier->forAll(oclIsKindOf(Interface))))->
                  collect(supplier.oclAsType(Interface))->asSet())
        """
        pass

    def directly_used_interfaces(self):
        """
        The Interfaces directly used by this Classifier

        .. ocl::
            result = ((supplierDependency->
              select(oclIsKindOf(Usage) and client->forAll(oclIsKindOf(Interface))))->
                collect(client.oclAsType(Interface))->asSet())
        """
        pass

    def get_general(self):
        """
        The general Classifiers are the ones referenced by the Generalization relationships.

        .. ocl::
            result = (parents())
        """
        pass

    def has_visibility_of(self):
        """
        The query hasVisibilityOf() determines whether a NamedElement is visible in the classifier. Non-private
        members are visible. It is only called when the argument is something owned by a parent.
        """
        pass

    def inherit(self):
        """
        The query inherit() defines how to inherit a set of elements passed as its argument.  It excludes
        redefined elements from the result.

        .. ocl::
            result = (inhs->reject(inh |
              inh.oclIsKindOf(RedefinableElement) and
              ownedMember->select(oclIsKindOf(RedefinableElement))->
                select(redefinedElement->includes(inh.oclAsType(RedefinableElement)))
                   ->notEmpty()))
        """
        pass

    def inheritable_members(self):
        """
        The query inheritableMembers() gives all of the members of a Classifier that may be inherited in one of
        its descendants, subject to whatever visibility restrictions apply.
        """
        pass

    def inherited_member(self):
        """
        The inheritedMember association is derived by inheriting the inheritable members of the parents.

        .. ocl::
            result = (inherit(parents()->collect(inheritableMembers(self))->asSet()))
        """
        pass

    def is_substitutable_for(self):
        """
        .. ocl::
            result = (substitution.contract->includes(contract))
        """
        pass

    def is_template(self):
        """
        The query isTemplate() returns whether this Classifier is actually a template.

        .. ocl::
            result = (ownedTemplateSignature <> null or general->exists(g | g.isTemplate()))
        """
        pass

    def maps_to_generalization_set(self):
        """
        The Classifier that maps to a GeneralizationSet may neither be a specific nor a general Classifier in
        any of the Generalization relationships defined for that GeneralizationSet. In other words, a power type
        may not be an instance of itself nor may its instances also be its subclasses.

        .. ocl::
            powertypeExtent->forAll( gs | 
              gs.generalization->forAll( gen | 
                not (gen.general = self) and not gen.general.allParents()->includes(self) and not (gen.specific = self) and not self.allParents()->includes(gen.specific) 
              ))
        """
        pass

    def may_specialize_type(self):
        """
        The query maySpecializeType() determines whether this classifier may have a generalization relationship
        to classifiers of the specified type. By default a classifier may specialize classifiers of the same or
        a more general type. It is intended to be redefined by classifiers that have different specialization
        constraints.

        .. ocl::
            result = (self.oclIsKindOf(c.oclType()))
        """
        pass

    def no_cycles_in_generalization(self):
        """
        Generalization hierarchies must be directed and acyclical. A Classifier can not be both a transitively
        general and transitively specific Classifier of the same Classifier.

        .. ocl::
            not allParents()->includes(self)
        """
        pass

    def non_final_parents(self):
        """
        The parents of a Classifier must be non-final.

        .. ocl::
            parents()->forAll(not isFinalSpecialization)
        """
        pass

    def parents(self):
        """
        The query parents() gives all of the immediate ancestors of a generalized Classifier.

        .. ocl::
            result = (generalization.general->asSet())
        """
        pass

    def specialize_type(self):
        """
        A Classifier may only specialize Classifiers of a valid type.

        .. ocl::
            parents()->forAll(c | self.maySpecializeType(c))
        """
        pass

class DataType(models.Model):
    """
    A DataType is a type whose instances are identified only by their value.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The attributes owned by the DataType.')
    owned_operation = models.ManyToManyField('Operation', related_name='%(app_label)s_%(class)s_owned_operation', blank=True, 
                                             help_text='The Operations owned by the DataType.')

class Enumeration(models.Model):
    """
    An Enumeration is a DataType whose values are enumerated in the model as EnumerationLiterals.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType', on_delete=models.CASCADE, primary_key=True)
    owned_literal = models.ManyToManyField('EnumerationLiteral', related_name='%(app_label)s_%(class)s_owned_literal', blank=True, 
                                           help_text='The ordered set of literals owned by this Enumeration.')

    def immutable(self):
        """
        .. ocl::
            ownedAttribute->forAll(isReadOnly)
        """
        pass

class TransitionKind(models.Model):
    """
    TransitionKind is an Enumeration type used to differentiate the various kinds of Transitions.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class TemplateParameter(models.Model):
    """
    A TemplateParameter exposes a ParameterableElement as a formal parameter of a template.
    """

    __package__ = 'UML.CommonStructure'

    default = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_default', blank=True, null=True, 
                                help_text='The ParameterableElement that is the default for this formal ' +
                                'TemplateParameter.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owned_default = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_default', blank=True, null=True, 
                                      help_text='The ParameterableElement that is owned by this TemplateParameter ' +
                                      'for the purpose of providing a default.')
    owned_parametered_element = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_parametered_element', blank=True, null=True, 
                                                  help_text='The ParameterableElement that is owned by this ' +
                                                  'TemplateParameter for the purpose of exposing it as the ' +
                                                  'parameteredElement.')
    parametered_element = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_parametered_element', null=True, 
                                            help_text='The ParameterableElement exposed by this ' +
                                            'TemplateParameter.')
    signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_signature', null=True, 
                                  help_text='The TemplateSignature that owns this TemplateParameter.')

    def must_be_compatible(self):
        """
        The default must be compatible with the formal TemplateParameter.

        .. ocl::
            default <> null implies default.isCompatibleWith(parameteredElement)
        """
        pass

class OperationTemplateParameter(models.Model):
    """
    An OperationTemplateParameter exposes an Operation as a formal parameter for a template.
    """

    __package__ = 'UML.Classification'

    parametered_element = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_parametered_element', null=True, 
                                            help_text='The Operation exposed by this OperationTemplateParameter.')
    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)

    def match_default_signature(self):
        """
        .. ocl::
            default->notEmpty() implies (default.oclIsKindOf(Operation) and (let defaultOp : Operation = default.oclAsType(Operation) in 
                defaultOp.ownedParameter->size() = parameteredElement.ownedParameter->size() and
                Sequence{1.. defaultOp.ownedParameter->size()}->forAll( ix | 
                    let p1: Parameter = defaultOp.ownedParameter->at(ix), p2 : Parameter = parameteredElement.ownedParameter->at(ix) in
                      p1.type = p2.type and p1.upper = p2.upper and p1.lower = p2.lower and p1.direction = p2.direction and p1.isOrdered = p2.isOrdered and p1.isUnique = p2.isUnique)))
        """
        pass

class ExtensionPoint(models.Model):
    """
    An ExtensionPoint identifies a point in the behavior of a UseCase where that behavior can be extended by the
    behavior of some other (extending) UseCase, as specified by an Extend relationship.
    """

    __package__ = 'UML.UseCases'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    use_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_use_case', null=True, 
                                 help_text='The UseCase that owns this ExtensionPoint.')

    def must_have_name(self):
        """
        An ExtensionPoint must have a name.

        .. ocl::
            name->notEmpty ()
        """
        pass

class StructuredClassifier(models.Model):
    """
    StructuredClassifiers may contain an internal structure of connected elements each of which plays a role in
    the overall Behavior modeled by the StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The Properties owned by the StructuredClassifier.')
    owned_connector = models.ManyToManyField('Connector', related_name='%(app_label)s_%(class)s_owned_connector', blank=True, 
                                             help_text='The connectors owned by the StructuredClassifier.')
    part = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_part', blank=True, 
                                  help_text='The Properties specifying instances that the StructuredClassifier ' +
                                  'owns by composition. This collection is derived, selecting those owned ' +
                                  'Properties where isComposite is true.')
    role = models.ManyToManyField('ConnectableElement', related_name='%(app_label)s_%(class)s_role', blank=True, 
                                  help_text='The roles that instances may play in this StructuredClassifier.')

    def all_roles(self):
        """
        All features of type ConnectableElement, equivalent to all direct and inherited roles.

        .. ocl::
            result = (allFeatures()->select(oclIsKindOf(ConnectableElement))->collect(oclAsType(ConnectableElement))->asSet())
        """
        pass

    def get_part(self):
        """
        Derivation for StructuredClassifier::/part

        .. ocl::
            result = (ownedAttribute->select(isComposite))
        """
        pass

class EncapsulatedClassifier(models.Model):
    """
    An EncapsulatedClassifier may own Ports to specify typed interaction points.
    """

    __package__ = 'UML.StructuredClassifiers'

    owned_port = models.ManyToManyField('Port', related_name='%(app_label)s_%(class)s_owned_port', blank=True, 
                                        help_text='The Ports owned by the EncapsulatedClassifier.')
    structured_classifier = models.OneToOneField('StructuredClassifier', on_delete=models.CASCADE, primary_key=True)

    def owned_port(self):
        """
        Derivation for EncapsulatedClassifier::/ownedPort : Port

        .. ocl::
            result = (ownedAttribute->select(oclIsKindOf(Port))->collect(oclAsType(Port))->asOrderedSet())
        """
        pass

class BehavioredClassifier(models.Model):
    """
    A BehavioredClassifier may have InterfaceRealizations, and owns a set of Behaviors one of which may specify
    the behavior of the BehavioredClassifier itself.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    classifier_behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_classifier_behavior', blank=True, null=True, 
                                            help_text='A Behavior that specifies the behavior of the ' +
                                            'BehavioredClassifier itself.')
    interface_realization = models.ManyToManyField('InterfaceRealization', related_name='%(app_label)s_%(class)s_interface_realization', blank=True, 
                                                   help_text='The set of InterfaceRealizations owned by the ' +
                                                   'BehavioredClassifier. Interface realizations reference the ' +
                                                   'Interfaces of which the BehavioredClassifier is an ' +
                                                   'implementation.')
    owned_behavior = models.ManyToManyField('Behavior', related_name='%(app_label)s_%(class)s_owned_behavior', blank=True, 
                                            help_text='Behaviors owned by a BehavioredClassifier.')

    def class_behavior(self):
        """
        If a behavior is classifier behavior, it does not have a specification.

        .. ocl::
            classifierBehavior->notEmpty() implies classifierBehavior.specification->isEmpty()
        """
        pass

class Class(models.Model):
    """
    A Class classifies a set of objects and specifies the features that characterize the structure and behavior
    of those objects.  A Class may have an internal structure and Ports.
    """

    __package__ = 'UML.StructuredClassifiers'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier', on_delete=models.CASCADE, primary_key=True)
    encapsulated_classifier = models.OneToOneField('EncapsulatedClassifier')
    extension = models.ManyToManyField('Extension', related_name='%(app_label)s_%(class)s_extension', blank=True, 
                                       help_text='This property is used when the Class is acting as a metaclass. ' +
                                       'It references the Extensions that specify additional properties of the ' +
                                       'metaclass. The property is derived from the Extensions whose memberEnds ' +
                                       'are typed by the Class.')
    is_abstract = models.BooleanField(help_text='If true, the Class does not provide a complete declaration and ' +
                                      'cannot be instantiated. An abstract Class is typically used as a target of ' +
                                      'Associations or Generalizations.')
    is_active = models.BooleanField(help_text='Determines whether an object specified by this Class is active or ' +
                                    'not. If true, then the owning Class is referred to as an active Class. If ' +
                                    'false, then such a Class is referred to as a passive Class.')
    nested_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_nested_classifier', blank=True, 
                                               help_text='The Classifiers owned by the Class that are not ' +
                                               'ownedBehaviors.')
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The attributes (i.e., the Properties) owned by the ' +
                                             'Class.')
    owned_operation = models.ManyToManyField('Operation', related_name='%(app_label)s_%(class)s_owned_operation', blank=True, 
                                             help_text='The Operations owned by the Class.')
    owned_reception = models.ManyToManyField('Reception', related_name='%(app_label)s_%(class)s_owned_reception', blank=True, 
                                             help_text='The Receptions owned by the Class.')
    super_class = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_super_class', blank=True, 
                                         help_text='The superclasses of a Class, derived from its ' +
                                         'Generalizations.')

    def get_extension(self):
        """
        Derivation for Class::/extension : Extension

        .. ocl::
            result = (Extension.allInstances()->select(ext | 
              let endTypes : Sequence(Classifier) = ext.memberEnd->collect(type.oclAsType(Classifier)) in
              endTypes->includes(self) or endTypes.allParents()->includes(self) ))
        """
        pass

    def passive_class(self):
        """
        Only an active Class may own Receptions and have a classifierBehavior.

        .. ocl::
            not isActive implies (ownedReception->isEmpty() and classifierBehavior = null)
        """
        pass

    def super_class(self):
        """
        Derivation for Class::/superClass : Class

        .. ocl::
            result = (self.general()->select(oclIsKindOf(Class))->collect(oclAsType(Class))->asSet())
        """
        pass

class Stereotype(models.Model):
    """
    A stereotype defines how an existing metaclass may be extended, and enables the use of platform or domain
    specific terminology or notation in place of, or in addition to, the ones used for the extended metaclass.
    """

    __package__ = 'UML.Packages'

    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    icon = models.ManyToManyField('Image', related_name='%(app_label)s_%(class)s_icon', blank=True, 
                                  help_text='Stereotype can change the graphical appearance of the extended model ' +
                                  'element by using attached icons. When this association is not null, it ' +
                                  'references the location of the icon content to be displayed within diagrams ' +
                                  'presenting the extended model elements.')
    profile = models.ForeignKey('Profile', related_name='%(app_label)s_%(class)s_profile', null=True, 
                                help_text='The profile that directly or indirectly contains this stereotype.')

    def association_end_ownership(self):
        """
        Where a stereotype's property is an association end for an association other than a kind of extension,
        and the other end is not a stereotype, the other end must be owned by the association itself.

        .. ocl::
            ownedAttribute
            ->select(association->notEmpty() and not association.oclIsKindOf(Extension) and not type.oclIsKindOf(Stereotype))
            ->forAll(opposite.owner = association)
        """
        pass

    def base_property_multiplicity_multiple_extension(self):
        """
        If a Stereotype extends more than one metaclass, the multiplicity of the corresponding base-properties
        shall be [0..1]. At any point in time, only one of these base-properties can contain a metaclass
        instance during runtime.
        """
        pass

    def base_property_multiplicity_single_extension(self):
        """
        If a Stereotype extends only one metaclass, the multiplicity of the corresponding base-property shall be
        1..1.
        """
        pass

    def base_property_upper_bound(self):
        """
        The upper bound of base-properties is exactly 1.
        """
        pass

    def binary_associations_only(self):
        """
        Stereotypes may only participate in binary associations.

        .. ocl::
            ownedAttribute.association->forAll(memberEnd->size()=2)
        """
        pass

    def containing_profile(self):
        """
        The query containingProfile returns the closest profile directly or indirectly containing this
        stereotype.

        .. ocl::
            result = (self.namespace.oclAsType(Package).containingProfile())
        """
        pass

    def generalize(self):
        """
        A Stereotype may only generalize or specialize another Stereotype.

        .. ocl::
            allParents()->forAll(oclIsKindOf(Stereotype)) 
            and Classifier.allInstances()->forAll(c | c.allParents()->exists(oclIsKindOf(Stereotype)) implies c.oclIsKindOf(Stereotype))
        """
        pass

    def name_not_clash(self):
        """
        Stereotype names should not clash with keyword names for the extended model element.
        """
        pass

    def get_profile(self):
        """
        A stereotype must be contained, directly or indirectly, in a profile.

        .. ocl::
            result = (self.containingProfile())
        """
        pass

class Package(models.Model):
    """
    A package can have one or more profile applications to indicate which profiles have been applied. Because a
    profile is a package, it is possible to apply a profile not only to packages, but also to profiles. Package
    specializes TemplateableElement and PackageableElement specializes ParameterableElement to specify that a
    package can be used as a template and a PackageableElement as a template parameter. A package is used to
    group elements, and provides a namespace for the grouped elements.
    """

    __package__ = 'UML.Packages'

    namespace = models.OneToOneField('Namespace')
    nested_package = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_nested_package', blank=True, 
                                            help_text='References the packaged elements that are Packages.')
    nesting_package = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_nesting_package', blank=True, null=True, 
                                        help_text='References the Package that owns this Package.')
    owned_stereotype = models.ManyToManyField('Stereotype', related_name='%(app_label)s_%(class)s_owned_stereotype', blank=True, 
                                              help_text='References the Stereotypes that are owned by the ' +
                                              'Package.')
    owned_type = models.ManyToManyField('Type', related_name='%(app_label)s_%(class)s_owned_type', blank=True, 
                                        help_text='References the packaged elements that are Types.')
    package_merge = models.ManyToManyField('PackageMerge', related_name='%(app_label)s_%(class)s_package_merge', blank=True, 
                                           help_text='References the PackageMerges that are owned by this ' +
                                           'Package.')
    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    packaged_element = models.ManyToManyField('PackageableElement', related_name='%(app_label)s_%(class)s_packaged_element', blank=True, 
                                              help_text='Specifies the packageable elements that are owned by ' +
                                              'this Package.')
    profile_application = models.ManyToManyField('ProfileApplication', related_name='%(app_label)s_%(class)s_profile_application', blank=True, 
                                                 help_text='References the ProfileApplications that indicate ' +
                                                 'which profiles have been applied to the Package.')
    templateable_element = models.OneToOneField('TemplateableElement')
    uri = models.CharField(max_length=255, blank=True, null=True, 
                           help_text='Provides an identifier for the package that can be used for many purposes. ' +
                           'A URI is the universally unique identification of the package following the IETF URI ' +
                           'specification, RFC 2396 http://www.ietf.org/rfc/rfc2396.txt and it must comply with ' +
                           'those syntax rules.')

    def all_applicable_stereotypes(self):
        """
        The query allApplicableStereotypes() returns all the directly or indirectly owned stereotypes, including
        stereotypes contained in sub-profiles.

        .. ocl::
            result = (let ownedPackages : Bag(Package) = ownedMember->select(oclIsKindOf(Package))->collect(oclAsType(Package)) in
             ownedStereotype->union(ownedPackages.allApplicableStereotypes())->flatten()->asSet()
            )
        """
        pass

    def containing_profile(self):
        """
        The query containingProfile() returns the closest profile directly or indirectly containing this package
        (or this package itself, if it is a profile).

        .. ocl::
            result = (if self.oclIsKindOf(Profile) then 
            	self.oclAsType(Profile)
            else
            	self.namespace.oclAsType(Package).containingProfile()
            endif)
        """
        pass

    def elements_public_or_private(self):
        """
        If an element that is owned by a package has visibility, it is public or private.

        .. ocl::
            packagedElement->forAll(e | e.visibility<> null implies e.visibility = VisibilityKind::public or e.visibility = VisibilityKind::private)
        """
        pass

    def makes_visible(self):
        """
        The query makesVisible() defines whether a Package makes an element visible outside itself. Elements
        with no visibility and elements with public visibility are made visible.
        """
        pass

    def must_be_owned(self):
        """
        The query mustBeOwned() indicates whether elements of this type must have an owner.

        .. ocl::
            result = (false)
        """
        pass

    def nested_package(self):
        """
        Derivation for Package::/nestedPackage

        .. ocl::
            result = (packagedElement->select(oclIsKindOf(Package))->collect(oclAsType(Package))->asSet())
        """
        pass

    def owned_stereotype(self):
        """
        Derivation for Package::/ownedStereotype

        .. ocl::
            result = (packagedElement->select(oclIsKindOf(Stereotype))->collect(oclAsType(Stereotype))->asSet())
        """
        pass

    def owned_type(self):
        """
        Derivation for Package::/ownedType

        .. ocl::
            result = (packagedElement->select(oclIsKindOf(Type))->collect(oclAsType(Type))->asSet())
        """
        pass

    def visible_members(self):
        """
        The query visibleMembers() defines which members of a Package can be accessed outside it.

        .. ocl::
            result = (member->select( m | m.oclIsKindOf(PackageableElement) and self.makesVisible(m))->collect(oclAsType(PackageableElement))->asSet())
        """
        pass

class ActivityNode(models.Model):
    """
    ActivityNode is an abstract class for points in the flow of an Activity connected by ActivityEdges.
    """

    __package__ = 'UML.Activities'

    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', blank=True, null=True, 
                                 help_text='The Activity containing the ActivityNode, if it is directly owned by ' +
                                 'an Activity.')
    in_group = models.ManyToManyField('ActivityGroup', related_name='%(app_label)s_%(class)s_in_group', blank=True, 
                                      help_text='ActivityGroups containing the ActivityNode.')
    in_interruptible_region = models.ManyToManyField('InterruptibleActivityRegion', related_name='%(app_label)s_%(class)s_in_interruptible_region', blank=True, 
                                                     help_text='InterruptibleActivityRegions containing the ' +
                                                     'ActivityNode.')
    in_partition = models.ManyToManyField('ActivityPartition', related_name='%(app_label)s_%(class)s_in_partition', blank=True, 
                                          help_text='ActivityPartitions containing the ActivityNode.')
    in_structured_node = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_in_structured_node', blank=True, null=True, 
                                           help_text='The StructuredActivityNode containing the ActvityNode, if ' +
                                           'it is directly owned by a StructuredActivityNode.')
    incoming = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_incoming', blank=True, 
                                      help_text='ActivityEdges that have the ActivityNode as their target.')
    outgoing = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_outgoing', blank=True, 
                                      help_text='ActivityEdges that have the ActivityNode as their source.')
    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    redefined_node = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_node', blank=True, 
                                            help_text='ActivityNodes from a generalization of the Activity ' +
                                            'containining this ActivityNode that are redefined by this ' +
                                            'ActivityNode.')

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityNode.

        .. ocl::
            result = (if inStructuredNode<>null then inStructuredNode.containingActivity()
            else activity
            endif)
        """
        pass

    def is_consistent_with(self):
        """
        .. ocl::
            result = (redefiningElement.oclIsKindOf(ActivityNode))
        """
        pass

class ControlNode(models.Model):
    """
    A ControlNode is an abstract ActivityNode that coordinates flows in an Activity.
    """

    __package__ = 'UML.Activities'

    activity_node = models.OneToOneField('ActivityNode', on_delete=models.CASCADE, primary_key=True)

class MergeNode(models.Model):
    """
    A merge node is a control node that brings together multiple alternate flows. It is not used to synchronize
    concurrent flows but to accept one among several alternate flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)

    def edges(self):
        """
        The ActivityEdges incoming to and outgoing from a MergeNode must be either all ObjectFlows or all
        ControlFlows.

        .. ocl::
            let allEdges : Set(ActivityEdge) = incoming->union(outgoing) in
            allEdges->forAll(oclIsKindOf(ControlFlow)) or allEdges->forAll(oclIsKindOf(ObjectFlow))
        """
        pass

    def one_outgoing_edge(self):
        """
        A MergeNode has one outgoing ActivityEdge.

        .. ocl::
            outgoing->size()=1
        """
        pass

class InteractionFragment(models.Model):
    """
    InteractionFragment is an abstract notion of the most general interaction unit. An InteractionFragment is a
    piece of an Interaction. Each InteractionFragment is conceptually like an Interaction by itself.
    """

    __package__ = 'UML.Interactions'

    covered = models.ManyToManyField('Lifeline', related_name='%(app_label)s_%(class)s_covered', blank=True, 
                                     help_text='References the Lifelines that the InteractionFragment involves.')
    enclosing_interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_enclosing_interaction', blank=True, null=True, 
                                              help_text='The Interaction enclosing this InteractionFragment.')
    enclosing_operand = models.ForeignKey('InteractionOperand', related_name='%(app_label)s_%(class)s_enclosing_operand', blank=True, null=True, 
                                          help_text='The operand enclosing this InteractionFragment (they may ' +
                                          'nest recursively).')
    general_ordering = models.ManyToManyField('GeneralOrdering', related_name='%(app_label)s_%(class)s_general_ordering', blank=True, 
                                              help_text='The general ordering relationships contained in this ' +
                                              'fragment.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

class CombinedFragment(models.Model):
    """
    A CombinedFragment defines an expression of InteractionFragments. A CombinedFragment is defined by an
    interaction operator and corresponding InteractionOperands. Through the use of CombinedFragments the user
    will be able to describe a number of traces in a compact and concise manner.
    """

    __package__ = 'UML.Interactions'

    cfragment_gate = models.ManyToManyField('Gate', related_name='%(app_label)s_%(class)s_cfragment_gate', blank=True, 
                                            help_text='Specifies the gates that form the interface between this ' +
                                            'CombinedFragment and its surroundings')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    interaction_operator = models.ForeignKey('InteractionOperatorKind', related_name='%(app_label)s_%(class)s_interaction_operator', null=True, default='seq', 
                                             help_text='Specifies the operation which defines the semantics of ' +
                                             'this combination of InteractionFragments.')
    operand = models.ManyToManyField('InteractionOperand', related_name='%(app_label)s_%(class)s_operand', 
                                     help_text='The set of operands of the combined fragment.')

    def has_break(self):
        """
        If the interactionOperator is break, the corresponding InteractionOperand must cover all Lifelines
        covered by the enclosing InteractionFragment.

        .. ocl::
            interactionOperator=InteractionOperatorKind::break  implies   
            enclosingInteraction.oclAsType(InteractionFragment)->asSet()->union(
               enclosingOperand.oclAsType(InteractionFragment)->asSet()).covered->asSet() = self.covered->asSet()
        """
        pass

    def consider_and_ignore(self):
        """
        The interaction operators 'consider' and 'ignore' can only be used for the ConsiderIgnoreFragment
        subtype of CombinedFragment

        .. ocl::
            ((interactionOperator = InteractionOperatorKind::consider) or (interactionOperator =  InteractionOperatorKind::ignore)) implies oclIsKindOf(ConsiderIgnoreFragment)
        """
        pass

    def opt_loop_break_neg(self):
        """
        If the interactionOperator is opt, loop, break, assert or neg, there must be exactly one operand.

        .. ocl::
            (interactionOperator =  InteractionOperatorKind::opt or interactionOperator = InteractionOperatorKind::loop or
            interactionOperator = InteractionOperatorKind::break or interactionOperator = InteractionOperatorKind::assert or
            interactionOperator = InteractionOperatorKind::neg)
            implies operand->size()=1
        """
        pass

class ExecutableNode(models.Model):
    """
    An ExecutableNode is an abstract class for ActivityNodes whose execution may be controlled using
    ControlFlows and to which ExceptionHandlers may be attached.
    """

    __package__ = 'UML.Activities'

    activity_node = models.OneToOneField('ActivityNode', on_delete=models.CASCADE, primary_key=True)
    handler = models.ManyToManyField('ExceptionHandler', related_name='%(app_label)s_%(class)s_handler', blank=True, 
                                     help_text='A set of ExceptionHandlers that are examined if an exception ' +
                                     'propagates out of the ExceptionNode.')

class Action(models.Model):
    """
    An Action is the fundamental unit of executable functionality. The execution of an Action represents some
    transformation or processing in the modeled system. Actions provide the ExecutableNodes within Activities
    and may also be used within Interactions.
    """

    __package__ = 'UML.Actions'

    context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_context', blank=True, null=True, 
                                help_text='The context Classifier of the Behavior that contains this Action, or ' +
                                'the Behavior itself if it has no context.')
    executable_node = models.OneToOneField('ExecutableNode', on_delete=models.CASCADE, primary_key=True)
    input = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_input', blank=True, 
                                   help_text='The ordered set of InputPins representing the inputs to the ' +
                                   'Action.')
    is_locally_reentrant = models.BooleanField(help_text='If true, the Action can begin a new, concurrent ' +
                                               'execution, even if there is already another execution of the ' +
                                               'Action ongoing. If false, the Action cannot begin a new execution ' +
                                               'until any previous execution has completed.')
    local_postcondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_local_postcondition', blank=True, 
                                                 help_text='A Constraint that must be satisfied when execution of ' +
                                                 'the Action is completed.')
    local_precondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_local_precondition', blank=True, 
                                                help_text='A Constraint that must be satisfied when execution of ' +
                                                'the Action is started.')
    output = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_output', blank=True, 
                                    help_text='The ordered set of OutputPins representing outputs from the ' +
                                    'Action.')

    def all_actions(self):
        """
        Return this Action and all Actions contained directly or indirectly in it. By default only the Action
        itself is returned, but the operation is overridden for StructuredActivityNodes.

        .. ocl::
            result = (self->asSet())
        """
        pass

    def all_owned_nodes(self):
        """
        Returns all the ActivityNodes directly or indirectly owned by this Action. This includes at least all
        the Pins of the Action.

        .. ocl::
            result = (input.oclAsType(Pin)->asSet()->union(output->asSet()))
        """
        pass

    def containing_behavior(self):
        """
        .. ocl::
            result = (if inStructuredNode<>null then inStructuredNode.containingBehavior() 
            else if activity<>null then activity
            else interaction 
            endif
            endif
            )
        """
        pass

    def get_context(self):
        """
        The derivation for the context property.

        .. ocl::
            result = (let behavior: Behavior = self.containingBehavior() in
            if behavior=null then null
            else if behavior._'context' = null then behavior
            else behavior._'context'
            endif
            endif)
        """
        pass

class ReadLinkObjectEndQualifierAction(models.Model):
    """
    A ReadLinkObjectEndQualifierAction is an Action that retrieves a qualifier end value from a link object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin from which the link object is obtained.')
    qualifier = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_qualifier', null=True, 
                                  help_text='The qualifier Property to be read.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin where the result value is placed.')

    def association_of_association(self):
        """
        The association of the Association end of the qualifier Property must be an AssociationClass.

        .. ocl::
            qualifier.associationEnd.association.oclIsKindOf(AssociationClass)
        """
        pass

    def ends_of_association(self):
        """
        The ends of the Association must not be static.

        .. ocl::
            qualifier.associationEnd.association.memberEnd->forAll(e | not e.isStatic)
        """
        pass

    def multiplicity_of_object(self):
        """
        The multiplicity of the object InputPin is 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def multiplicity_of_qualifier(self):
        """
        The multiplicity of the qualifier Property is 1..1.

        .. ocl::
            qualifier.is(1,1)
        """
        pass

    def multiplicity_of_result(self):
        """
        The multiplicity of the result OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def qualifier_attribute(self):
        """
        The qualifier Property must be a qualifier of an Association end.

        .. ocl::
            qualifier.associationEnd <> null
        """
        pass

    def same_type(self):
        """
        The type of the result OutputPin is the same as the type of the qualifier Property.

        .. ocl::
            result.type = qualifier.type
        """
        pass

    def type_of_object(self):
        """
        The type of the object InputPin is the AssociationClass that owns the Association end that has the given
        qualifier Property.

        .. ocl::
            object.type = qualifier.associationEnd.association
        """
        pass

class InteractionUse(models.Model):
    """
    An InteractionUse refers to an Interaction. The InteractionUse is a shorthand for copying the contents of
    the referenced Interaction where the InteractionUse is. To be accurate the copying must take into account
    substituting parameters with arguments and connect the formal Gates with the actual ones.
    """

    __package__ = 'UML.Interactions'

    actual_gate = models.ManyToManyField('Gate', related_name='%(app_label)s_%(class)s_actual_gate', blank=True, 
                                         help_text='The actual gates of the InteractionUse.')
    argument = models.ManyToManyField('ValueSpecification', related_name='%(app_label)s_%(class)s_argument', blank=True, 
                                      help_text='The actual arguments of the Interaction.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    refers_to = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_refers_to', null=True, 
                                  help_text='Refers to the Interaction that defines its meaning.')
    return_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_return_value', blank=True, null=True, 
                                     help_text='The value of the executed Interaction.')
    return_value_recipient = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_return_value_recipient', blank=True, null=True, 
                                               help_text='The recipient of the return value.')

    def all_lifelines(self):
        """
        The InteractionUse must cover all Lifelines of the enclosing Interaction that are common with the
        lifelines covered by the referred Interaction. Lifelines are common if they have the same selector and
        represents associationEnd values.

        .. ocl::
            let parentInteraction : Set(Interaction) = enclosingInteraction->asSet()->
            union(enclosingOperand.combinedFragment->closure(enclosingOperand.combinedFragment)->
            collect(enclosingInteraction).oclAsType(Interaction)->asSet()) in
            parentInteraction->size()=1 and let refInteraction : Interaction = refersTo in
            parentInteraction.covered-> forAll(intLifeline : Lifeline | refInteraction.covered->
            forAll( refLifeline : Lifeline | refLifeline.represents = intLifeline.represents and 
            (
            ( refLifeline.selector.oclIsKindOf(LiteralString) implies
              intLifeline.selector.oclIsKindOf(LiteralString) and 
              refLifeline.selector.oclAsType(LiteralString).value = intLifeline.selector.oclAsType(LiteralString).value ) and
            ( refLifeline.selector.oclIsKindOf(LiteralInteger) implies
              intLifeline.selector.oclIsKindOf(LiteralInteger) and 
              refLifeline.selector.oclAsType(LiteralInteger).value = intLifeline.selector.oclAsType(LiteralInteger).value )
            )
             implies self.covered->asSet()->includes(intLifeline)))
        """
        pass

    def arguments_are_constants(self):
        """
        The arguments must only be constants, parameters of the enclosing Interaction or attributes of the
        classifier owning the enclosing Interaction.
        """
        pass

    def arguments_correspond_to_parameters(self):
        """
        The arguments of the InteractionUse must correspond to parameters of the referred Interaction.
        """
        pass

    def gates_match(self):
        """
        Actual Gates of the InteractionUse must match Formal Gates of the referred Interaction. Gates match when
        their names are equal and their messages correspond.

        .. ocl::
            actualGate->notEmpty() implies 
            refersTo.formalGate->forAll( fg : Gate | self.actualGate->select(matches(fg))->size()=1) and
            self.actualGate->forAll(ag : Gate | refersTo.formalGate->select(matches(ag))->size()=1)
        """
        pass

    def return_value_recipient_coverage(self):
        """
        The returnValueRecipient must be a Property of a ConnectableElement that is represented by a Lifeline
        covered by this InteractionUse.

        .. ocl::
            returnValueRecipient->asSet()->notEmpty() implies
            let covCE : Set(ConnectableElement) = covered.represents->asSet() in 
            covCE->notEmpty() and let classes:Set(Classifier) = covCE.type.oclIsKindOf(Classifier).oclAsType(Classifier)->asSet() in 
            let allProps : Set(Property) = classes.attribute->union(classes.allParents().attribute)->asSet() in 
            allProps->includes(returnValueRecipient)
        """
        pass

    def return_value_type_recipient_correspondence(self):
        """
        The type of the returnValue must correspond to the type of the returnValueRecipient.

        .. ocl::
            returnValue.type->asSequence()->notEmpty() implies returnValue.type->asSequence()->first() = returnValueRecipient.type->asSequence()->first()
        """
        pass

class Relationship(models.Model):
    """
    Relationship is an abstract concept that specifies some kind of relationship between Elements.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    related_element = models.ManyToManyField('Element', related_name='%(app_label)s_%(class)s_related_element', 
                                             help_text='Specifies the elements related by the Relationship.')

class DirectedRelationship(models.Model):
    """
    A DirectedRelationship represents a relationship between a collection of source model Elements and a
    collection of target model Elements.
    """

    __package__ = 'UML.CommonStructure'

    relationship = models.OneToOneField('Relationship', on_delete=models.CASCADE, primary_key=True)
    source = models.ManyToManyField('Element', related_name='%(app_label)s_%(class)s_source', 
                                    help_text='Specifies the source Element(s) of the DirectedRelationship.')
    target = models.ManyToManyField('Element', related_name='%(app_label)s_%(class)s_target', 
                                    help_text='Specifies the target Element(s) of the DirectedRelationship.')

class Dependency(models.Model):
    """
    A Dependency is a Relationship that signifies that a single model Element or a set of model Elements
    requires other model Elements for their specification or implementation. This means that the complete
    semantics of the client Element(s) are either semantically or structurally dependent on the definition of
    the supplier Element(s).
    """

    __package__ = 'UML.CommonStructure'

    client = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_client', 
                                    help_text='The Element(s) dependent on the supplier Element(s). In some cases ' +
                                    '(such as a trace Abstraction) the assignment of direction (that is, the ' +
                                    'designation of the client Element) is at the discretion of the modeler and is ' +
                                    'a stipulation.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')
    supplier = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_supplier', 
                                      help_text='The Element(s) on which the client Element(s) depend in some ' +
                                      'respect. The modeler may stipulate a sense of Dependency direction suitable ' +
                                      'for their domain.')

class Abstraction(models.Model):
    """
    An Abstraction is a Relationship that relates two Elements or sets of Elements that represent the same
    concept at different levels of abstraction or from different viewpoints.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)
    mapping = models.ForeignKey('OpaqueExpression', related_name='%(app_label)s_%(class)s_mapping', blank=True, null=True, 
                                help_text='An OpaqueExpression that states the abstraction relationship between ' +
                                'the supplier(s) and the client(s). In some cases, such as derivation, it is ' +
                                'usually formal and unidirectional; in other cases, such as trace, it is usually ' +
                                'informal and bidirectional. The mapping expression is optional and may be omitted ' +
                                'if the precise relationship between the Elements is not specified.')

class Realization(models.Model):
    """
    Realization is a specialized Abstraction relationship between two sets of model Elements, one representing a
    specification (the supplier) and the other represents an implementation of the latter (the client).
    Realization can be used to model stepwise refinement, optimizations, transformations, templates, model
    synthesis, framework composition, etc.
    """

    __package__ = 'UML.CommonStructure'

    abstraction = models.OneToOneField('Abstraction', on_delete=models.CASCADE, primary_key=True)

class Substitution(models.Model):
    """
    A substitution is a relationship between two classifiers signifying that the substituting classifier
    complies with the contract specified by the contract classifier. This implies that instances of the
    substituting classifier are runtime substitutable where instances of the contract classifier are expected.
    """

    __package__ = 'UML.Classification'

    contract = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_contract', null=True, 
                                 help_text='The contract with which the substituting classifier complies.')
    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)
    substituting_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_substituting_classifier', null=True, 
                                                help_text='Instances of the substituting classifier are runtime ' +
                                                'substitutable where instances of the contract classifier are ' +
                                                'expected.')

class Observation(models.Model):
    """
    Observation specifies a value determined by observing an event or events that occur relative to other model
    Elements.
    """

    __package__ = 'UML.Values'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)

class Feature(models.Model):
    """
    A Feature declares a behavioral or structural characteristic of Classifiers.
    """

    __package__ = 'UML.Classification'

    featuring_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_featuring_classifier', blank=True, null=True, 
                                             help_text='The Classifiers that have this Feature as a feature.')
    is_static = models.BooleanField(help_text='Specifies whether this Feature characterizes individual instances ' +
                                    'classified by the Classifier (false) or the Classifier itself (true).')
    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)

class BehavioralFeature(models.Model):
    """
    A BehavioralFeature is a feature of a Classifier that specifies an aspect of the behavior of its instances.
    A BehavioralFeature is implemented (realized) by a Behavior. A BehavioralFeature specifies that a Classifier
    will respond to a designated request by invoking its implementing method.
    """

    __package__ = 'UML.Classification'

    concurrency = models.ForeignKey('CallConcurrencyKind', related_name='%(app_label)s_%(class)s_concurrency', null=True, default='sequential', 
                                    help_text='Specifies the semantics of concurrent calls to the same passive ' +
                                    'instance (i.e., an instance originating from a Class with isActive being ' +
                                    'false). Active instances control access to their own BehavioralFeatures.')
    feature = models.OneToOneField('Feature', on_delete=models.CASCADE, primary_key=True)
    is_abstract = models.BooleanField(help_text='If true, then the BehavioralFeature does not have an ' +
                                      'implementation, and one must be supplied by a more specific Classifier. If ' +
                                      'false, the BehavioralFeature must have an implementation in the Classifier ' +
                                      'or one must be inherited.')
    method = models.ManyToManyField('Behavior', related_name='%(app_label)s_%(class)s_method', blank=True, 
                                    help_text='A Behavior that implements the BehavioralFeature. There may be at ' +
                                    'most one Behavior for a particular pairing of a Classifier (as owner of the ' +
                                    'Behavior) and a BehavioralFeature (as specification of the Behavior).')
    namespace = models.OneToOneField('Namespace')
    owned_parameter = models.ManyToManyField('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', blank=True, 
                                             help_text='The ordered set of formal Parameters of this ' +
                                             'BehavioralFeature.')
    owned_parameter_set = models.ManyToManyField('ParameterSet', related_name='%(app_label)s_%(class)s_owned_parameter_set', blank=True, 
                                                 help_text='The ParameterSets owned by this BehavioralFeature.')
    raised_exception = models.ManyToManyField('Type', related_name='%(app_label)s_%(class)s_raised_exception', blank=True, 
                                              help_text='The Types representing exceptions that may be raised ' +
                                              'during an invocation of this BehavioralFeature.')

    def abstract_no_method(self):
        """
        When isAbstract is true there are no methods.

        .. ocl::
            isAbstract implies method->isEmpty()
        """
        pass

    def input_parameters(self):
        """
        The ownedParameters with direction in and inout.

        .. ocl::
            result = (ownedParameter->select(direction=ParameterDirectionKind::_'in' or direction=ParameterDirectionKind::inout))
        """
        pass

    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() determines whether two BehavioralFeatures may coexist in the same
        Namespace. It specifies that they must have different signatures.

        .. ocl::
            result = ((n.oclIsKindOf(BehavioralFeature) and ns.getNamesOfMember(self)->intersection(ns.getNamesOfMember(n))->notEmpty()) implies
              Set{self}->including(n.oclAsType(BehavioralFeature))->isUnique(ownedParameter->collect(p|
              Tuple { name=p.name, type=p.type,effect=p.effect,direction=p.direction,isException=p.isException,
                          isStream=p.isStream,isOrdered=p.isOrdered,isUnique=p.isUnique,lower=p.lower, upper=p.upper }))
              )
        """
        pass

    def output_parameters(self):
        """
        The ownedParameters with direction out, inout, or return.

        .. ocl::
            result = (ownedParameter->select(direction=ParameterDirectionKind::out or direction=ParameterDirectionKind::inout or direction=ParameterDirectionKind::return))
        """
        pass

class Operation(models.Model):
    """
    An Operation is a BehavioralFeature of a Classifier that specifies the name, type, parameters, and
    constraints for invoking an associated Behavior. An Operation may invoke both the execution of method
    behaviors as well as other behavioral responses. Operation specializes TemplateableElement in order to
    support specification of template operations and bound operations. Operation specializes
    ParameterableElement to specify that an operation can be exposed as a formal template parameter, and
    provided as an actual parameter in a binding of a template.
    """

    __package__ = 'UML.Classification'

    behavioral_feature = models.OneToOneField('BehavioralFeature')
    body_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_body_condition', blank=True, null=True, 
                                       help_text='An optional Constraint on the result values of an invocation of ' +
                                       'this Operation.')
    datatype = models.ForeignKey('DataType', related_name='%(app_label)s_%(class)s_datatype', blank=True, null=True, 
                                 help_text='The DataType that owns this Operation, if any.')
    has_class = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_has_class', blank=True, null=True, 
                                  help_text='The Class that owns this operation, if any.')
    interface = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_interface', blank=True, null=True, 
                                  help_text='The Interface that owns this Operation, if any.')
    is_ordered = models.BooleanField(help_text='Specifies whether the return parameter is ordered or not, if ' +
                                     'present.  This information is derived from the return result for this ' +
                                     'Operation.')
    is_query = models.BooleanField(help_text='Specifies whether an execution of the BehavioralFeature leaves the ' +
                                   'state of the system unchanged (isQuery=true) or whether side effects may occur ' +
                                   '(isQuery=false).')
    is_unique = models.BooleanField(help_text='Specifies whether the return parameter is unique or not, if ' +
                                    'present. This information is derived from the return result for this ' +
                                    'Operation.')
    lower = models.IntegerField(blank=True, null=True, 
                                help_text='Specifies the lower multiplicity of the return parameter, if present. ' +
                                'This information is derived from the return result for this Operation.')
    owned_parameter = models.ManyToManyField('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', blank=True, 
                                             help_text='The parameters owned by this Operation.')
    parameterable_element = models.OneToOneField('ParameterableElement')
    postcondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_postcondition', blank=True, 
                                           help_text='An optional set of Constraints specifying the state of the ' +
                                           'system when the Operation is completed.')
    precondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_precondition', blank=True, 
                                          help_text='An optional set of Constraints on the state of the system ' +
                                          'when the Operation is invoked.')
    raised_exception = models.ManyToManyField('Type', related_name='%(app_label)s_%(class)s_raised_exception', blank=True, 
                                              help_text='The Types representing exceptions that may be raised ' +
                                              'during an invocation of this operation.')
    redefined_operation = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_operation', blank=True, 
                                                 help_text='The Operations that are redefined by this Operation.')
    template_parameter = models.ForeignKey('OperationTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', blank=True, null=True, 
                                           help_text='The OperationTemplateParameter that exposes this element as ' +
                                           'a formal parameter.')
    templateable_element = models.OneToOneField('TemplateableElement', on_delete=models.CASCADE, primary_key=True)
    type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_type', blank=True, null=True, 
                             help_text='The return type of the operation, if present. This information is derived ' +
                             'from the return result for this Operation.')
    upper = models.IntegerField(blank=True, null=True, 
                                help_text='The upper multiplicity of the return parameter, if present. This ' +
                                'information is derived from the return result for this Operation.')

    def at_most_one_return(self):
        """
        An Operation can have at most one return parameter; i.e., an owned parameter with the direction set to
        'return.'

        .. ocl::
            self.ownedParameter->select(direction = ParameterDirectionKind::return)->size() <= 1
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two Operations in a context in which redefinition is
        possible, whether redefinition would be consistent. A redefining operation is consistent with a
        redefined operation if  it has the same number of owned parameters, and for each parameter the following
        holds:    - Direction, ordering and uniqueness are the same.  - The corresponding types are covariant,
        contravariant or invariant.  - The multiplicities are compatible, depending on the parameter direction.
        """
        pass

    def is_ordered(self):
        """
        If this operation has a return parameter, isOrdered equals the value of isOrdered for that parameter.
        Otherwise isOrdered is false.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()-> exists(isOrdered) else false endif)
        """
        pass

    def is_unique(self):
        """
        If this operation has a return parameter, isUnique equals the value of isUnique for that parameter.
        Otherwise isUnique is true.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()->exists(isUnique) else true endif)
        """
        pass

    def get_lower(self):
        """
        If this operation has a return parameter, lower equals the value of lower for that parameter. Otherwise
        lower has no value.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()->any(true).lower else null endif)
        """
        pass

    def only_body_for_query(self):
        """
        A bodyCondition can only be specified for a query Operation.

        .. ocl::
            bodyCondition <> null implies isQuery
        """
        pass

    def return_result(self):
        """
        The query returnResult() returns the set containing the return parameter of the Operation if one exists,
        otherwise, it returns an empty set

        .. ocl::
            result = (ownedParameter->select (direction = ParameterDirectionKind::return))
        """
        pass

    def get_type(self):
        """
        If this operation has a return parameter, type equals the value of type for that parameter. Otherwise
        type has no value.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()->any(true).type else null endif)
        """
        pass

    def get_upper(self):
        """
        If this operation has a return parameter, upper equals the value of upper for that parameter. Otherwise
        upper has no value.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()->any(true).upper else null endif)
        """
        pass

class Extend(models.Model):
    """
    A relationship from an extending UseCase to an extended UseCase that specifies how and when the behavior
    defined in the extending UseCase can be inserted into the behavior defined in the extended UseCase.
    """

    __package__ = 'UML.UseCases'

    condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_condition', blank=True, null=True, 
                                  help_text='References the condition that must hold when the first ' +
                                  'ExtensionPoint is reached for the extension to take place. If no constraint is ' +
                                  'associated with the Extend relationship, the extension is unconditional.')
    directed_relationship = models.OneToOneField('DirectedRelationship')
    extended_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_extended_case', null=True, 
                                      help_text='The UseCase that is being extended.')
    extension = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_extension', null=True, 
                                  help_text='The UseCase that represents the extension and owns the Extend ' +
                                  'relationship.')
    extension_location = models.ManyToManyField('ExtensionPoint', related_name='%(app_label)s_%(class)s_extension_location', 
                                                help_text='An ordered list of ExtensionPoints belonging to the ' +
                                                'extended UseCase, specifying where the respective behavioral ' +
                                                'fragments of the extending UseCase are to be inserted. The first ' +
                                                'fragment in the extending UseCase is associated with the first ' +
                                                'extension point in the list, the second fragment with the second ' +
                                                'point, and so on. Note that, in most practical cases, the ' +
                                                'extending UseCase has just a single behavior fragment, so that ' +
                                                'the list of ExtensionPoints is trivial.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

    def extension_points(self):
        """
        The ExtensionPoints referenced by the Extend relationship must belong to the UseCase that is being
        extended.

        .. ocl::
            extensionLocation->forAll (xp | extendedCase.extensionPoint->includes(xp))
        """
        pass

class TypedElement(models.Model):
    """
    A TypedElement is a NamedElement that may have a Type specified for it.
    """

    __package__ = 'UML.CommonStructure'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_type', blank=True, null=True, 
                             help_text='The type of the TypedElement.')

class ValueSpecification(models.Model):
    """
    A ValueSpecification is the specification of a (possibly empty) set of values. A ValueSpecification is a
    ParameterableElement that may be exposed as a formal TemplateParameter and provided as the actual parameter
    in the binding of a template.
    """

    __package__ = 'UML.Values'

    packageable_element = models.OneToOneField('PackageableElement')
    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)

    def boolean_value(self):
        """
        The query booleanValue() gives a single Boolean value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass

    def integer_value(self):
        """
        The query integerValue() gives a single Integer value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass

    def is_compatible_with(self):
        """
        The query isCompatibleWith() determines if this ValueSpecification is compatible with the specified
        ParameterableElement. This ValueSpecification is compatible with ParameterableElement p if the kind of
        this ValueSpecification is the same as or a subtype of the kind of p. Further, if p is a TypedElement,
        then the type of this ValueSpecification must be conformant with the type of p.

        .. ocl::
            result = (self.oclIsKindOf(p.oclType()) and (p.oclIsKindOf(TypedElement) implies 
            self.type.conformsTo(p.oclAsType(TypedElement).type)))
        """
        pass

    def is_computable(self):
        """
        The query isComputable() determines whether a value specification can be computed in a model. This
        operation cannot be fully defined in OCL. A conforming implementation is expected to deliver true for
        this operation for all ValueSpecifications that it can compute, and to compute all of those for which
        the operation is true. A conforming implementation is expected to be able to compute at least the value
        of all LiteralSpecifications.

        .. ocl::
            result = (false)
        """
        pass

    def is_null(self):
        """
        The query isNull() returns true when it can be computed that the value is null.

        .. ocl::
            result = (false)
        """
        pass

    def real_value(self):
        """
        The query realValue() gives a single Real value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass

    def string_value(self):
        """
        The query stringValue() gives a single String value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass

    def unlimited_value(self):
        """
        The query unlimitedValue() gives a single UnlimitedNatural value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass

class LiteralSpecification(models.Model):
    """
    A LiteralSpecification identifies a literal constant being modeled.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

class ForkNode(models.Model):
    """
    A ForkNode is a ControlNode that splits a flow into multiple concurrent flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)

    def edges(self):
        """
        The ActivityEdges incoming to and outgoing from a ForkNode must be either all ObjectFlows or all
        ControlFlows.

        .. ocl::
            let allEdges : Set(ActivityEdge) = incoming->union(outgoing) in
            allEdges->forAll(oclIsKindOf(ControlFlow)) or allEdges->forAll(oclIsKindOf(ObjectFlow))
        """
        pass

    def one_incoming_edge(self):
        """
        A ForkNode has one incoming ActivityEdge.

        .. ocl::
            incoming->size()=1
        """
        pass

class Constraint(models.Model):
    """
    A Constraint is a condition or restriction expressed in natural language text or in a machine readable
    language for the purpose of declaring some of the semantics of an Element or set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    constrained_element = models.ManyToManyField('Element', related_name='%(app_label)s_%(class)s_constrained_element', blank=True, 
                                                 help_text='The ordered set of Elements referenced by this ' +
                                                 'Constraint.')
    context = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_context', blank=True, null=True, 
                                help_text='Specifies the Namespace that owns the Constraint.')
    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    specification = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_specification', null=True, 
                                      help_text='A condition that must be true when evaluated in order for the ' +
                                      'Constraint to be satisfied.')

    def boolean_value(self):
        """
        The ValueSpecification for a Constraint must evaluate to a Boolean value.
        """
        pass

    def no_side_effects(self):
        """
        Evaluating the ValueSpecification for a Constraint must not have side effects.
        """
        pass

    def not_apply_to_self(self):
        """
        A Constraint cannot be applied to itself.

        .. ocl::
            not constrainedElement->includes(self)
        """
        pass

class IntervalConstraint(models.Model):
    """
    An IntervalConstraint is a Constraint that is specified by an Interval.
    """

    __package__ = 'UML.Values'

    constraint = models.OneToOneField('Constraint', on_delete=models.CASCADE, primary_key=True)
    specification = models.ForeignKey('Interval', related_name='%(app_label)s_%(class)s_specification', null=True, 
                                      help_text='The Interval that specifies the condition of the ' +
                                      'IntervalConstraint.')

class DurationConstraint(models.Model):
    """
    A DurationConstraint is a Constraint that refers to a DurationInterval.
    """

    __package__ = 'UML.Values'

    first_event = models.BooleanField(blank=True, 
                                      help_text='The value of firstEvent[i] is related to constrainedElement[i] ' +
                                      '(where i is 1 or 2). If firstEvent[i] is true, then the corresponding ' +
                                      'observation event is the first time instant the execution enters ' +
                                      'constrainedElement[i]. If firstEvent[i] is false, then the corresponding ' +
                                      'observation event is the last time instant the execution is within ' +
                                      'constrainedElement[i].')
    interval_constraint = models.OneToOneField('IntervalConstraint', on_delete=models.CASCADE, primary_key=True)
    specification = models.ForeignKey('DurationInterval', related_name='%(app_label)s_%(class)s_specification', null=True, 
                                      help_text='The DurationInterval constraining the duration.')

    def first_event_multiplicity(self):
        """
        The multiplicity of firstEvent must be 2 if the multiplicity of constrainedElement is 2. Otherwise the
        multiplicity of firstEvent is 0.

        .. ocl::
            if (constrainedElement->size() = 2)
              then (firstEvent->size() = 2) else (firstEvent->size() = 0) 
            endif
        """
        pass

    def has_one_or_two_constrained_elements(self):
        """
        A DurationConstraint has either one or two constrainedElements.

        .. ocl::
            constrainedElement->size() = 1 or constrainedElement->size()=2
        """
        pass

class ParameterDirectionKind(models.Model):
    """
    ParameterDirectionKind is an Enumeration that defines literals used to specify direction of parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class ActivityGroup(models.Model):
    """
    ActivityGroup is an abstract class for defining sets of ActivityNodes and ActivityEdges in an Activity.
    """

    __package__ = 'UML.Activities'

    contained_edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_contained_edge', blank=True, 
                                            help_text='ActivityEdges immediately contained in the ActivityGroup.')
    contained_node = models.ManyToManyField('ActivityNode', related_name='%(app_label)s_%(class)s_contained_node', blank=True, 
                                            help_text='ActivityNodes immediately contained in the ActivityGroup.')
    in_activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_in_activity', blank=True, null=True, 
                                    help_text='The Activity containing the ActivityGroup, if it is directly owned ' +
                                    'by an Activity.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    subgroup = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_subgroup', blank=True, 
                                      help_text='Other ActivityGroups immediately contained in this ' +
                                      'ActivityGroup.')
    super_group = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_super_group', blank=True, null=True, 
                                    help_text='The ActivityGroup immediately containing this ActivityGroup, if it ' +
                                    'is directly owned by another ActivityGroup.')

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityGroup.

        .. ocl::
            result = (if superGroup<>null then superGroup.containingActivity()
            else inActivity
            endif)
        """
        pass

    def nodes_and_edges(self):
        """
        All containedNodes and containeEdges of an ActivityGroup must be in the same Activity as the group.

        .. ocl::
            containedNode->forAll(activity = self.containingActivity()) and 
            containedEdge->forAll(activity = self.containingActivity())
        """
        pass

    def not_contained(self):
        """
        No containedNode or containedEdge of an ActivityGroup may be contained by its subgroups or its
        superGroups, transitively.

        .. ocl::
            subgroup->closure(subgroup).containedNode->excludesAll(containedNode) and
            superGroup->closure(superGroup).containedNode->excludesAll(containedNode) and 
            subgroup->closure(subgroup).containedEdge->excludesAll(containedEdge) and 
            superGroup->closure(superGroup).containedEdge->excludesAll(containedEdge)
        """
        pass

class StructuredActivityNode(models.Model):
    """
    A StructuredActivityNode is an Action that is also an ActivityGroup and whose behavior is specified by the
    ActivityNodes and ActivityEdges it so contains. Unlike other kinds of ActivityGroup, a
    StructuredActivityNode owns the ActivityNodes and ActivityEdges it contains, and so a node or edge can only
    be directly contained in one StructuredActivityNode, though StructuredActivityNodes may be nested.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action')
    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', blank=True, null=True, 
                                 help_text='The Activity immediately containing the StructuredActivityNode, if it ' +
                                 'is not contained in another StructuredActivityNode.')
    activity_group = models.OneToOneField('ActivityGroup')
    edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', blank=True, 
                                  help_text='The ActivityEdges immediately contained in the ' +
                                  'StructuredActivityNode.')
    must_isolate = models.BooleanField(help_text='If true, then any object used by an Action within the ' +
                                       'StructuredActivityNode cannot be accessed by any Action outside the node ' +
                                       'until the StructuredActivityNode as a whole completes. Any concurrent ' +
                                       'Actions that would result in accessing such objects are required to have ' +
                                       'their execution deferred until the completion of the ' +
                                       'StructuredActivityNode.')
    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    node = models.ManyToManyField('ActivityNode', related_name='%(app_label)s_%(class)s_node', blank=True, 
                                  help_text='The ActivityNodes immediately contained in the ' +
                                  'StructuredActivityNode.')
    structured_node_input = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_structured_node_input', blank=True, 
                                                   help_text='The InputPins owned by the StructuredActivityNode.')
    structured_node_output = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_structured_node_output', blank=True, 
                                                    help_text='The OutputPins owned by the ' +
                                                    'StructuredActivityNode.')
    variable = models.ManyToManyField('Variable', related_name='%(app_label)s_%(class)s_variable', blank=True, 
                                      help_text='The Variables defined in the scope of the ' +
                                      'StructuredActivityNode.')

    def all_actions(self):
        """
        Returns this StructuredActivityNode and all Actions contained in it.

        .. ocl::
            result = (node->select(oclIsKindOf(Action)).oclAsType(Action).allActions()->including(self)->asSet())
        """
        pass

    def all_owned_nodes(self):
        """
        Returns all the ActivityNodes contained directly or indirectly within this StructuredActivityNode, in
        addition to the Pins of the StructuredActivityNode.

        .. ocl::
            result = (self.Action::allOwnedNodes()->union(node)->union(node->select(oclIsKindOf(Action)).oclAsType(Action).allOwnedNodes())->asSet())
        """
        pass

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this StructuredActivityNode (considered as an Action).

        .. ocl::
            result = (self.Action::containingActivity())
        """
        pass

    def edges(self):
        """
        The edges of a StructuredActivityNode are all the ActivityEdges with source and target ActivityNodes
        contained directly or indirectly within the StructuredActivityNode and at least one of the source or
        target not contained in any more deeply nested StructuredActivityNode.

        .. ocl::
            edge=self.sourceNodes().outgoing->intersection(self.allOwnedNodes().incoming)->
            	union(self.targetNodes().incoming->intersection(self.allOwnedNodes().outgoing))->asSet()
        """
        pass

    def input_pin_edges(self):
        """
        The incoming ActivityEdges of an InputPin of a StructuredActivityNode must have sources that are not
        within the StructuredActivityNode.

        .. ocl::
            input.incoming.source->excludesAll(allOwnedNodes()-output)
        """
        pass

    def output_pin_edges(self):
        """
        The outgoing ActivityEdges of the OutputPins of a StructuredActivityNode must have targets that are not
        within the StructuredActivityNode.

        .. ocl::
            output.outgoing.target->excludesAll(allOwnedNodes()-input)
        """
        pass

    def source_nodes(self):
        """
        Return those ActivityNodes contained immediately within the StructuredActivityNode that may act as
        sources of edges owned by the StructuredActivityNode.

        .. ocl::
            result = (node->union(input.oclAsType(ActivityNode)->asSet())->
              union(node->select(oclIsKindOf(Action)).oclAsType(Action).output)->asSet())
        """
        pass

    def target_nodes(self):
        """
        Return those ActivityNodes contained immediately within the StructuredActivityNode that may act as
        targets of edges owned by the StructuredActivityNode.

        .. ocl::
            result = (node->union(output.oclAsType(ActivityNode)->asSet())->
              union(node->select(oclIsKindOf(Action)).oclAsType(Action).input)->asSet())
        """
        pass

class ConditionalNode(models.Model):
    """
    A ConditionalNode is a StructuredActivityNode that chooses one among some number of alternative collections
    of ExecutableNodes to execute.
    """

    __package__ = 'UML.Actions'

    clause = models.ManyToManyField('Clause', related_name='%(app_label)s_%(class)s_clause', 
                                    help_text='The set of Clauses composing the ConditionalNode.')
    is_assured = models.BooleanField(help_text='If true, the modeler asserts that the test for at least one ' +
                                     'Clause of the ConditionalNode will succeed.')
    is_determinate = models.BooleanField(help_text='If true, the modeler asserts that the test for at most one ' +
                                         'Clause of the ConditionalNode will succeed.')
    result = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, 
                                    help_text='The OutputPins that onto which are moved values from the ' +
                                    'bodyOutputs of the Clause selected for execution.')
    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)

    def all_actions(self):
        """
        Return only this ConditionalNode. This prevents Actions within the ConditionalNode from having their
        OutputPins used as bodyOutputs or decider Pins in containing LoopNodes or ConditionalNodes.

        .. ocl::
            result = (self->asSet())
        """
        pass

    def clause_no_predecessor(self):
        """
        No two clauses within a ConditionalNode may be predecessorClauses of each other, either directly or
        indirectly.

        .. ocl::
            clause->closure(predecessorClause)->intersection(clause)->isEmpty()
        """
        pass

    def executable_nodes(self):
        """
        The union of the ExecutableNodes in the test and body parts of all clauses must be the same as the
        subset of nodes contained in the ConditionalNode (considered as a StructuredActivityNode) that are
        ExecutableNodes.

        .. ocl::
            clause.test->union(clause._'body') = node->select(oclIsKindOf(ExecutableNode)).oclAsType(ExecutableNode)
        """
        pass

    def matching_output_pins(self):
        """
        Each clause of a ConditionalNode must have the same number of bodyOutput pins as the ConditionalNode has
        result OutputPins, and each clause bodyOutput Pin must be compatible with the corresponding result
        OutputPin (by positional order) in type, multiplicity, ordering, and uniqueness.

        .. ocl::
            clause->forAll(
            	bodyOutput->size()=self.result->size() and
            	Sequence{1..self.result->size()}->forAll(i |
            		bodyOutput->at(i).type.conformsTo(result->at(i).type) and
            		bodyOutput->at(i).isOrdered = result->at(i).isOrdered and
            		bodyOutput->at(i).isUnique = result->at(i).isUnique and
            		bodyOutput->at(i).compatibleWith(result->at(i))))
        """
        pass

    def no_input_pins(self):
        """
        A ConditionalNode has no InputPins.

        .. ocl::
            input->isEmpty()
        """
        pass

    def one_clause_with_executable_node(self):
        """
        No ExecutableNode in the ConditionNode may appear in the test or body part of more than one clause of a
        ConditionalNode.

        .. ocl::
            node->select(oclIsKindOf(ExecutableNode)).oclAsType(ExecutableNode)->forAll(n | 
            	self.clause->select(test->union(_'body')->includes(n))->size()=1)
        """
        pass

    def result_no_incoming(self):
        """
        The result OutputPins have no incoming edges.

        .. ocl::
            result.incoming->isEmpty()
        """
        pass

class VisibilityKind(models.Model):
    """
    VisibilityKind is an enumeration type that defines literals to determine the visibility of Elements in a
    model.
    """

    __package__ = 'UML.CommonStructure'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class DeploymentTarget(models.Model):
    """
    A deployment target is the location for a deployed artifact.
    """

    __package__ = 'UML.Deployments'

    deployed_element = models.ManyToManyField('PackageableElement', related_name='%(app_label)s_%(class)s_deployed_element', blank=True, 
                                              help_text='The set of elements that are manifested in an Artifact ' +
                                              'that is involved in Deployment to a DeploymentTarget.')
    deployment = models.ManyToManyField('Deployment', related_name='%(app_label)s_%(class)s_deployment', blank=True, 
                                        help_text='The set of Deployments for a DeploymentTarget.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

    def deployed_element(self):
        """
        Derivation for DeploymentTarget::/deployedElement

        .. ocl::
            result = (deployment.deployedArtifact->select(oclIsKindOf(Artifact))->collect(oclAsType(Artifact).manifestation)->collect(utilizedElement)->asSet())
        """
        pass

class Node(models.Model):
    """
    A Node is computational resource upon which artifacts may be deployed for execution. Nodes can be
    interconnected through communication paths to define network structures.
    """

    __package__ = 'UML.Deployments'

    deployment_target = models.OneToOneField('DeploymentTarget')
    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    nested_node = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_nested_node', blank=True, 
                                         help_text='The Nodes that are defined (nested) within the Node.')

    def internal_structure(self):
        """
        The internal structure of a Node (if defined) consists solely of parts of type Node.

        .. ocl::
            part->forAll(oclIsKindOf(Node))
        """
        pass

class ExecutionEnvironment(models.Model):
    """
    An execution environment is a node that offers an execution environment for specific types of components
    that are deployed on it in the form of executable artifacts.
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node', on_delete=models.CASCADE, primary_key=True)

class LiteralInteger(models.Model):
    """
    A LiteralInteger is a specification of an Integer value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.IntegerField(null=True, )

    def integer_value(self):
        """
        The query integerValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

class ObjectNode(models.Model):
    """
    An ObjectNode is an abstract ActivityNode that may hold tokens within the object flow in an Activity.
    ObjectNodes also support token selection, limitation on the number of tokens held, specification of the
    state required for tokens being held, and carrying control values.
    """

    __package__ = 'UML.Activities'

    activity_node = models.OneToOneField('ActivityNode')
    in_state = models.ManyToManyField('State', related_name='%(app_label)s_%(class)s_in_state', blank=True, 
                                      help_text='The States required to be associated with the values held by ' +
                                      'tokens on this ObjectNode.')
    is_control_type = models.BooleanField(help_text='Indicates whether the type of the ObjectNode is to be ' +
                                          'treated as representing control values that may traverse ControlFlows.')
    ordering = models.ForeignKey('ObjectNodeOrderingKind', related_name='%(app_label)s_%(class)s_ordering', null=True, default='FIFO', 
                                 help_text='Indicates how the tokens held by the ObjectNode are ordered for ' +
                                 'selection to traverse ActivityEdges outgoing from the ObjectNode.')
    selection = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_selection', blank=True, null=True, 
                                  help_text='A Behavior used to select tokens to be offered on outgoing ' +
                                  'ActivityEdges.')
    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)
    upper_bound = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_upper_bound', blank=True, null=True, 
                                    help_text='The maximum number of tokens that may be held by this ObjectNode. ' +
                                    'Tokens cannot flow into the ObjectNode if the upperBound is reached. If no ' +
                                    'upperBound is specified, then there is no limit on how many tokens the ' +
                                    'ObjectNode can hold.')

    def input_output_parameter(self):
        """
        A selection Behavior has one input Parameter and one output Parameter. The input Parameter must have the
        same type as  or a supertype of the type of ObjectNode, be non-unique, and have multiplicity 0..*. The
        output Parameter must be the same or a subtype of the type of ObjectNode. The Behavior cannot have side
        effects.

        .. ocl::
            selection<>null implies
            	selection.inputParameters()->size()=1 and
            	selection.inputParameters()->forAll(p | not p.isUnique and p.is(0,*) and self.type.conformsTo(p.type)) and
            	selection.outputParameters()->size()=1 and
            		selection.inputParameters()->forAll(p | self.type.conformsTo(p.type))
        """
        pass

    def object_flow_edges(self):
        """
        If isControlType=false, the ActivityEdges incoming to or outgoing from an ObjectNode must all be
        ObjectFlows.

        .. ocl::
            (not isControlType) implies incoming->union(outgoing)->forAll(oclIsKindOf(ObjectFlow))
        """
        pass

    def selection_behavior(self):
        """
        If an ObjectNode has a selection Behavior, then the ordering of the object node is ordered, and vice
        versa.

        .. ocl::
            (selection<>null) = (ordering=ObjectNodeOrderingKind::ordered)
        """
        pass

class CentralBufferNode(models.Model):
    """
    A CentralBufferNode is an ObjectNode for managing flows from multiple sources and targets.
    """

    __package__ = 'UML.Activities'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)

class ConsiderIgnoreFragment(models.Model):
    """
    A ConsiderIgnoreFragment is a kind of CombinedFragment that is used for the consider and ignore cases, which
    require lists of pertinent Messages to be specified.
    """

    __package__ = 'UML.Interactions'

    combined_fragment = models.OneToOneField('CombinedFragment', on_delete=models.CASCADE, primary_key=True)
    message = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_message', blank=True, 
                                     help_text='The set of messages that apply to this fragment.')

    def consider_or_ignore(self):
        """
        The interaction operator of a ConsiderIgnoreFragment must be either 'consider' or 'ignore'.

        .. ocl::
            (interactionOperator =  InteractionOperatorKind::consider) or (interactionOperator =  InteractionOperatorKind::ignore)
        """
        pass

    def type(self):
        """
        The NamedElements must be of a type of element that can be a signature for a message (i.e.., an
        Operation, or a Signal).

        .. ocl::
            message->forAll(m | m.oclIsKindOf(Operation) or m.oclIsKindOf(Signal))
        """
        pass

class Vertex(models.Model):
    """
    A Vertex is an abstraction of a node in a StateMachine graph. It can be the source or destination of any
    number of Transitions.
    """

    __package__ = 'UML.StateMachines'

    container = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_container', blank=True, null=True, 
                                  help_text='The Region that contains this Vertex.')
    incoming = models.ManyToManyField('Transition', related_name='%(app_label)s_%(class)s_incoming', blank=True, 
                                      help_text='Specifies the Transitions entering this Vertex.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    outgoing = models.ManyToManyField('Transition', related_name='%(app_label)s_%(class)s_outgoing', blank=True, 
                                      help_text='Specifies the Transitions departing from this Vertex.')

    def containing_state_machine(self):
        """
        The operation containingStateMachine() returns the StateMachine in which this Vertex is defined.

        .. ocl::
            result = (if container <> null
            then
            -- the container is a region
               container.containingStateMachine()
            else 
               if (self.oclIsKindOf(Pseudostate)) and ((self.oclAsType(Pseudostate).kind = PseudostateKind::entryPoint) or (self.oclAsType(Pseudostate).kind = PseudostateKind::exitPoint)) then
                  self.oclAsType(Pseudostate).stateMachine
               else 
                  if (self.oclIsKindOf(ConnectionPointReference)) then
                      self.oclAsType(ConnectionPointReference).state.containingStateMachine() -- no other valid cases possible
                  else 
                      null
                  endif
               endif
            endif
            )
        """
        pass

    def get_incoming(self):
        """
        Derivation for Vertex::/incoming.

        .. ocl::
            result = (Transition.allInstances()->select(target=self))
        """
        pass

    def is_contained_in_region(self):
        """
        This utility query returns true if the Vertex is contained in the Region r (input argument).

        .. ocl::
            result = (if (container = r) then
            	true
            else
            	if (r.state->isEmpty()) then
            		false
            	else
            		container.state.isContainedInRegion(r)
            	endif
            endif)
        """
        pass

    def is_contained_in_state(self):
        """
        This utility operation returns true if the Vertex is contained in the State s (input argument).

        .. ocl::
            result = (if not s.isComposite() or container->isEmpty() then
            	false
            else
            	if container.state = s then 
            		true
            	else
            		container.state.isContainedInState(s)
            	endif
            endif)
        """
        pass

    def get_outgoing(self):
        """
        Derivation for Vertex::/outgoing

        .. ocl::
            result = (Transition.allInstances()->select(source=self))
        """
        pass

class State(models.Model):
    """
    A State models a situation during which some (usually implicit) invariant condition holds.
    """

    __package__ = 'UML.StateMachines'

    connection = models.ManyToManyField('ConnectionPointReference', related_name='%(app_label)s_%(class)s_connection', blank=True, 
                                        help_text='The entry and exit connection points used in conjunction with ' +
                                        'this (submachine) State, i.e., as targets and sources, respectively, in ' +
                                        'the Region with the submachine State. A connection point reference ' +
                                        'references the corresponding definition of a connection point Pseudostate ' +
                                        'in the StateMachine referenced by the submachine State.')
    connection_point = models.ManyToManyField('Pseudostate', related_name='%(app_label)s_%(class)s_connection_point', blank=True, 
                                              help_text='The entry and exit Pseudostates of a composite State. ' +
                                              'These can only be entry or exit Pseudostates, and they must have ' +
                                              'different names. They can only be defined for composite States.')
    deferrable_trigger = models.ManyToManyField('Trigger', related_name='%(app_label)s_%(class)s_deferrable_trigger', blank=True, 
                                                help_text='A list of Triggers that are candidates to be retained ' +
                                                'by the StateMachine if they trigger no Transitions out of the ' +
                                                'State (not consumed). A deferred Trigger is retained until the ' +
                                                'StateMachine reaches a State configuration where it is no longer ' +
                                                'deferred.')
    do_activity = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_do_activity', blank=True, null=True, 
                                    help_text='An optional Behavior that is executed while being in the State. ' +
                                    'The execution starts when this State is entered, and ceases either by itself ' +
                                    'when done, or when the State is exited, whichever comes first.')
    entry = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_entry', blank=True, null=True, 
                              help_text='An optional Behavior that is executed whenever this State is entered ' +
                              'regardless of the Transition taken to reach the State. If defined, entry Behaviors ' +
                              'are always executed to completion prior to any internal Behavior or Transitions ' +
                              'performed within the State.')
    exit = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_exit', blank=True, null=True, 
                             help_text='An optional Behavior that is executed whenever this State is exited ' +
                             'regardless of which Transition was taken out of the State. If defined, exit ' +
                             'Behaviors are always executed to completion only after all internal and transition ' +
                             'Behaviors have completed execution.')
    is_composite = models.BooleanField(help_text='A state with isComposite=true is said to be a composite State. ' +
                                       'A composite State is a State that contains at least one Region.')
    is_orthogonal = models.BooleanField(help_text='A State with isOrthogonal=true is said to be an orthogonal ' +
                                        'composite State An orthogonal composite State contains two or more ' +
                                        'Regions.')
    is_simple = models.BooleanField(help_text='A State with isSimple=true is said to be a simple State A simple ' +
                                    'State does not have any Regions and it does not refer to any submachine ' +
                                    'StateMachine.')
    is_submachine_state = models.BooleanField(help_text='A State with isSubmachineState=true is said to be a ' +
                                              'submachine State Such a State refers to another ' +
                                              'StateMachine(submachine).')
    namespace = models.OneToOneField('Namespace')
    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    redefined_state = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_state', blank=True, null=True, 
                                        help_text='The State of which this State is a redefinition.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', null=True, 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    region = models.ManyToManyField('Region', related_name='%(app_label)s_%(class)s_region', blank=True, 
                                    help_text='The Regions owned directly by the State.')
    state_invariant = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_state_invariant', blank=True, null=True, 
                                        help_text='Specifies conditions that are always true when this State is ' +
                                        'the current State. In ProtocolStateMachines state invariants are ' +
                                        'additional conditions to the preconditions of the outgoing Transitions, ' +
                                        'and to the postcondition of the incoming Transitions.')
    submachine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_submachine', blank=True, null=True, 
                                   help_text='The StateMachine that is to be inserted in place of the ' +
                                   '(submachine) State.')
    vertex = models.OneToOneField('Vertex')

    def composite_states(self):
        """
        Only composite States can have entry or exit Pseudostates defined.

        .. ocl::
            connectionPoint->notEmpty() implies isComposite
        """
        pass

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the State either directly or
        transitively.

        .. ocl::
            result = (container.containingStateMachine())
        """
        pass

    def destinations_or_sources_of_transitions(self):
        """
        The connection point references used as destinations/sources of Transitions associated with a submachine
        State must be defined as entry/exit points in the submachine StateMachine.

        .. ocl::
            self.isSubmachineState implies (self.connection->forAll (cp |
              cp.entry->forAll (ps | ps.stateMachine = self.submachine) and
              cp.exit->forAll (ps | ps.stateMachine = self.submachine)))
        """
        pass

    def entry_or_exit(self):
        """
        Only entry or exit Pseudostates can serve as connection points.

        .. ocl::
            connectionPoint->forAll(kind = PseudostateKind::entryPoint or kind = PseudostateKind::exitPoint)
        """
        pass

    def is_composite(self):
        """
        A composite State is a State with at least one Region.

        .. ocl::
            result = (region->notEmpty())
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies that a redefining State is consistent with a redefined State
        provided that the redefining State is an extension of the redefined State A simple State can be
        redefined (extended) to become a composite State (by adding one or more Regions) and a composite State
        can be redefined (extended) by adding Regions and by adding Vertices, States, and Transitions to
        inherited Regions. All States may add or replace entry, exit, and 'doActivity' Behaviors.
        """
        pass

    def is_orthogonal(self):
        """
        An orthogonal State is a composite state with at least 2 regions.

        .. ocl::
            result = (region->size () > 1)
        """
        pass

    def is_redefinition_context_valid(self):
        """
        The query isRedefinitionContextValid() specifies whether the redefinition contexts of a State are
        properly related to the redefinition contexts of the specified State to allow this element to redefine
        the other. This means that the containing Region of a redefining State must redefine the containing
        Region of the redefined State.

        .. ocl::
            result = (if redefinedElement.oclIsKindOf(State) then
              let redefinedState : State = redefinedElement.oclAsType(State) in
                container.redefinedElement.oclAsType(Region)->exists(r:Region |
                  r.subvertex->includes(redefinedState))
            else
              false
            endif)
        """
        pass

    def is_simple(self):
        """
        A simple State is a State without any regions.

        .. ocl::
            result = ((region->isEmpty()) and not isSubmachineState())
        """
        pass

    def is_submachine_state(self):
        """
        Only submachine State references another StateMachine.

        .. ocl::
            result = (submachine <> null)
        """
        pass

    def redefinition_context(self):
        """
        The redefinition context of a State is the nearest containing StateMachine.

        .. ocl::
            result = (let sm : StateMachine = containingStateMachine() in
            if sm._'context' = null or sm.general->notEmpty() then
              sm
            else
              sm._'context'
            endif)
        """
        pass

    def submachine_or_regions(self):
        """
        A State is not allowed to have both a submachine and Regions.

        .. ocl::
            isComposite implies not isSubmachineState
        """
        pass

    def submachine_states(self):
        """
        Only submachine States can have connection point references.

        .. ocl::
            isSubmachineState implies connection->notEmpty( )
        """
        pass

class MultiplicityElement(models.Model):
    """
    A multiplicity is a definition of an inclusive interval of non-negative integers beginning with a lower
    bound and ending with a (possibly infinite) upper bound. A MultiplicityElement embeds this information to
    specify the allowable cardinalities for an instantiation of the Element.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    is_ordered = models.BooleanField(help_text='For a multivalued multiplicity, this attribute specifies whether ' +
                                     'the values in an instantiation of this MultiplicityElement are sequentially ' +
                                     'ordered.')
    is_unique = models.BooleanField(help_text='For a multivalued multiplicity, this attributes specifies whether ' +
                                    'the values in an instantiation of this MultiplicityElement are unique.')
    lower = models.IntegerField(null=True, )
    lower_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_lower_value', blank=True, null=True, 
                                    help_text='The specification of the lower bound for this multiplicity.')
    upper = models.IntegerField(null=True, )
    upper_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_upper_value', blank=True, null=True, 
                                    help_text='The specification of the upper bound for this multiplicity.')

    def compatible_with(self):
        """
        The operation compatibleWith takes another multiplicity as input. It returns true if the other
        multiplicity is wider than, or the same as, self.

        .. ocl::
            result = ((other.lowerBound() <= self.lowerBound()) and ((other.upperBound() = *) or (self.upperBound() <= other.upperBound())))
        """
        pass

    def includes_multiplicity(self):
        """
        The query includesMultiplicity() checks whether this multiplicity includes all the cardinalities allowed
        by the specified multiplicity.
        """
        pass

    def has_is(self):
        """
        The operation is determines if the upper and lower bound of the ranges are the ones given.

        .. ocl::
            result = (lowerbound = self.lowerBound() and upperbound = self.upperBound())
        """
        pass

    def is_multivalued(self):
        """
        The query isMultivalued() checks whether this multiplicity has an upper bound greater than one.
        """
        pass

    def get_lower(self):
        """
        The derived lower attribute must equal the lowerBound.

        .. ocl::
            result = (lowerBound())
        """
        pass

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an integer, which is the
        integerValue of lowerValue, if this is given, and 1 otherwise.

        .. ocl::
            result = (if (lowerValue=null or lowerValue.integerValue()=null) then 1 else lowerValue.integerValue() endif)
        """
        pass

    def lower_ge_0(self):
        """
        The lower bound must be a non-negative integer literal.

        .. ocl::
            lowerBound() >= 0
        """
        pass

    def lower_is_integer(self):
        """
        If it is not empty, then lowerValue must have an Integer value.

        .. ocl::
            lowerValue <> null implies lowerValue.integerValue() <> null
        """
        pass

    def get_upper(self):
        """
        The derived upper attribute must equal the upperBound.

        .. ocl::
            result = (upperBound())
        """
        pass

    def upper_bound(self):
        """
        The query upperBound() returns the upper bound of the multiplicity for a bounded multiplicity as an
        unlimited natural, which is the unlimitedNaturalValue of upperValue, if given, and 1, otherwise.

        .. ocl::
            result = (if (upperValue=null or upperValue.unlimitedValue()=null) then 1 else upperValue.unlimitedValue() endif)
        """
        pass

    def upper_ge_lower(self):
        """
        The upper bound must be greater than or equal to the lower bound.

        .. ocl::
            upperBound() >= lowerBound()
        """
        pass

    def upper_is_unlimited_natural(self):
        """
        If it is not empty, then upperValue must have an UnlimitedNatural value.

        .. ocl::
            upperValue <> null implies upperValue.unlimitedValue() <> null
        """
        pass

    def value_specification_constant(self):
        """
        If a non-literal ValueSpecification is used for lowerValue or upperValue, then that specification must
        be a constant expression.
        """
        pass

    def value_specification_no_side_effects(self):
        """
        If a non-literal ValueSpecification is used for lowerValue or upperValue, then evaluating that
        specification must not have side effects.
        """
        pass

class Pin(models.Model):
    """
    A Pin is an ObjectNode and MultiplicityElement that provides input values to an Action or accepts output
    values from an Action.
    """

    __package__ = 'UML.Actions'

    is_control = models.BooleanField(help_text='Indicates whether the Pin provides data to the Action or just ' +
                                     'controls how the Action executes.')
    multiplicity_element = models.OneToOneField('MultiplicityElement')
    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)

    def control_pins(self):
        """
        A control Pin has a control type.

        .. ocl::
            isControl implies isControlType
        """
        pass

    def not_unique(self):
        """
        Pin multiplicity is not unique.

        .. ocl::
            not isUnique
        """
        pass

class InputPin(models.Model):
    """
    An InputPin is a Pin that holds input values to be consumed by an Action.
    """

    __package__ = 'UML.Actions'

    pin = models.OneToOneField('Pin', on_delete=models.CASCADE, primary_key=True)

    def outgoing_edges_structured_only(self):
        """
        An InputPin may have outgoing ActivityEdges only when it is owned by a StructuredActivityNode, and these
        edges must target a node contained (directly or indirectly) in the owning StructuredActivityNode.

        .. ocl::
            outgoing->notEmpty() implies
            	action<>null and
            	action.oclIsKindOf(StructuredActivityNode) and
            	action.oclAsType(StructuredActivityNode).allOwnedNodes()->includesAll(outgoing.target)
        """
        pass

class LiteralString(models.Model):
    """
    A LiteralString is a specification of a String value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.CharField(max_length=255, blank=True, null=True, )

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

    def string_value(self):
        """
        The query stringValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass

class VariableAction(models.Model):
    """
    VariableAction is an abstract class for Actions that operate on a specified Variable.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    variable = models.ForeignKey('Variable', related_name='%(app_label)s_%(class)s_variable', null=True, 
                                 help_text='The Variable to be read or written.')

    def scope_of_variable(self):
        """
        The VariableAction must be in the scope of the variable.

        .. ocl::
            variable.isAccessibleBy(self)
        """
        pass

class WriteVariableAction(models.Model):
    """
    WriteVariableAction is an abstract class for VariableActions that change Variable values.
    """

    __package__ = 'UML.Actions'

    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', blank=True, null=True, 
                              help_text='The InputPin that gives the value to be added or removed from the ' +
                              'Variable.')
    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)

    def multiplicity(self):
        """
        The multiplicity of the value InputPin is 1..1.

        .. ocl::
            value<>null implies value.is(1,1)
        """
        pass

    def value_type(self):
        """
        The type of the value InputPin must conform to the type of the variable.

        .. ocl::
            value <> null implies value.type.conformsTo(variable.type)
        """
        pass

class LoopNode(models.Model):
    """
    A LoopNode is a StructuredActivityNode that represents an iterative loop with setup, test, and body
    sections.
    """

    __package__ = 'UML.Actions'

    body_output = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_body_output', blank=True, 
                                         help_text='The OutputPins on Actions within the bodyPart, the values of ' +
                                         'which are moved to the loopVariable OutputPins after the completion of ' +
                                         'each execution of the bodyPart, before the next iteration of the loop ' +
                                         'begins or before the loop exits.')
    body_part = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_body_part', blank=True, 
                                       help_text='The set of ExecutableNodes that perform the repetitive ' +
                                       'computations of the loop. The bodyPart is executed as long as the test ' +
                                       'section produces a true value.')
    decider = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_decider', null=True, 
                                help_text='An OutputPin on an Action in the test section whose Boolean value ' +
                                'determines whether to continue executing the loop bodyPart.')
    is_tested_first = models.BooleanField(help_text='If true, the test is performed before the first execution of ' +
                                          'the bodyPart. If false, the bodyPart is executed once before the test ' +
                                          'is performed.')
    loop_variable = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_loop_variable', blank=True, 
                                           help_text='A list of OutputPins that hold the values of the loop ' +
                                           'variables during an execution of the loop. When the test fails, the ' +
                                           'values are moved to the result OutputPins of the loop.')
    loop_variable_input = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_loop_variable_input', blank=True, 
                                                 help_text='A list of InputPins whose values are moved into the ' +
                                                 'loopVariable Pins before the first iteration of the loop.')
    result = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, 
                                    help_text='A list of OutputPins that receive the loopVariable values after ' +
                                    'the last iteration of the loop and constitute the output of the LoopNode.')
    setup_part = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_setup_part', blank=True, 
                                        help_text='The set of ExecutableNodes executed before the first iteration ' +
                                        'of the loop, in order to initialize values or perform other setup ' +
                                        'computations.')
    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)
    test = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_test', 
                                  help_text='The set of ExecutableNodes executed in order to provide the test ' +
                                  'result for the loop.')

    def all_actions(self):
        """
        Return only this LoopNode. This prevents Actions within the LoopNode from having their OutputPins used
        as bodyOutputs or decider Pins in containing LoopNodes or ConditionalNodes.

        .. ocl::
            result = (self->asSet())
        """
        pass

    def body_output_pins(self):
        """
        The bodyOutput pins are OutputPins on Actions in the body of the LoopNode.

        .. ocl::
            bodyPart.oclAsType(Action).allActions().output->includesAll(bodyOutput)
        """
        pass

    def executable_nodes(self):
        """
        The union of the ExecutableNodes in the setupPart, test and bodyPart of a LoopNode must be the same as
        the subset of nodes contained in the LoopNode (considered as a StructuredActivityNode) that are
        ExecutableNodes.

        .. ocl::
            setupPart->union(test)->union(bodyPart)=node->select(oclIsKindOf(ExecutableNode)).oclAsType(ExecutableNode)->asSet()
        """
        pass

    def input_edges(self):
        """
        The loopVariableInputs must not have outgoing edges.

        .. ocl::
            loopVariableInput.outgoing->isEmpty()
        """
        pass

    def loop_variable_outgoing(self):
        """
        All ActivityEdges outgoing from loopVariable OutputPins must have targets within the LoopNode.

        .. ocl::
            allOwnedNodes()->includesAll(loopVariable.outgoing.target)
        """
        pass

    def matching_loop_variables(self):
        """
        A LoopNode must have the same number of loopVariableInputs and loopVariables, and they must match in
        type, uniqueness and multiplicity.

        .. ocl::
            loopVariableInput->size()=loopVariable->size() and
            loopVariableInput.type=loopVariable.type and
            loopVariableInput.isUnique=loopVariable.isUnique and
            loopVariableInput.lower=loopVariable.lower and
            loopVariableInput.upper=loopVariable.upper
        """
        pass

    def matching_output_pins(self):
        """
        A LoopNode must have the same number of bodyOutput Pins as loopVariables, and each bodyOutput Pin must
        be compatible with the corresponding loopVariable (by positional order) in type, multiplicity, ordering
        and uniqueness.

        .. ocl::
            bodyOutput->size()=loopVariable->size() and
            Sequence{1..loopVariable->size()}->forAll(i |
            	bodyOutput->at(i).type.conformsTo(loopVariable->at(i).type) and
            	bodyOutput->at(i).isOrdered = loopVariable->at(i).isOrdered and
            	bodyOutput->at(i).isUnique = loopVariable->at(i).isUnique and
            	loopVariable->at(i).includesMultiplicity(bodyOutput->at(i)))
        """
        pass

    def matching_result_pins(self):
        """
        A LoopNode must have the same number of result OutputPins and loopVariables, and they must match in
        type, uniqueness and multiplicity.

        .. ocl::
            result->size()=loopVariable->size() and
            result.type=loopVariable.type and
            result.isUnique=loopVariable.isUnique and
            result.lower=loopVariable.lower and
            result.upper=loopVariable.upper
        """
        pass

    def result_no_incoming(self):
        """
        The result OutputPins have no incoming edges.

        .. ocl::
            result.incoming->isEmpty()
        """
        pass

    def setup_test_and_body(self):
        """
        The test and body parts of a ConditionalNode must be disjoint with each other.

        .. ocl::
            setupPart->intersection(test)->isEmpty() and
            setupPart->intersection(bodyPart)->isEmpty() and
            test->intersection(bodyPart)->isEmpty()
        """
        pass

    def source_nodes(self):
        """
        Return the loopVariable OutputPins in addition to other source nodes for the LoopNode as a
        StructuredActivityNode.

        .. ocl::
            result = (self.StructuredActivityNode::sourceNodes()->union(loopVariable))
        """
        pass

class Event(models.Model):
    """
    An Event is the specification of some occurrence that may potentially trigger effects by an object.
    """

    __package__ = 'UML.CommonBehavior'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)

class MessageEvent(models.Model):
    """
    A MessageEvent specifies the receipt by an object of either an Operation call or a Signal instance.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)

class Usage(models.Model):
    """
    A Usage is a Dependency in which the client Element requires the supplier Element (or set of Elements) for
    its full implementation or operation.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)

class InitialNode(models.Model):
    """
    An InitialNode is a ControlNode that offers a single control token when initially enabled.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)

    def control_edges(self):
        """
        All the outgoing ActivityEdges from an InitialNode must be ControlFlows.

        .. ocl::
            outgoing->forAll(oclIsKindOf(ControlFlow))
        """
        pass

    def no_incoming_edges(self):
        """
        An InitialNode has no incoming ActivityEdges.

        .. ocl::
            incoming->isEmpty()
        """
        pass

class Expression(models.Model):
    """
    An Expression represents a node in an expression tree, which may be non-terminal or terminal. It defines a
    symbol, and has a possibly empty sequence of operands that are ValueSpecifications. It denotes a (possibly
    empty) set of values when evaluated in a context.
    """

    __package__ = 'UML.Values'

    operand = models.ManyToManyField('ValueSpecification', related_name='%(app_label)s_%(class)s_operand', blank=True, 
                                     help_text='Specifies a sequence of operand ValueSpecifications.')
    symbol = models.CharField(max_length=255, blank=True, null=True, 
                              help_text='The symbol associated with this node in the expression tree.')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

class Interval(models.Model):
    """
    An Interval defines the range between two ValueSpecifications.
    """

    __package__ = 'UML.Values'

    max = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_max', null=True, 
                            help_text='Refers to the ValueSpecification denoting the maximum value of the range.')
    min = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_min', null=True, 
                            help_text='Refers to the ValueSpecification denoting the minimum value of the range.')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

class LinkAction(models.Model):
    """
    LinkAction is an abstract class for all Actions that identify the links to be acted on using LinkEndData.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    end_data = models.ManyToManyField('LinkEndData', related_name='%(app_label)s_%(class)s_end_data', blank=True, 
                                      help_text='The LinkEndData identifying the values on the ends of the links ' +
                                      'acting on by this LinkAction.')
    input_value = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_input_value', 
                                         help_text='InputPins used by the LinkEndData of the LinkAction.')

    def association(self):
        """
        Returns the Association acted on by this LinkAction.

        .. ocl::
            result = (endData->asSequence()->first().end.association)
        """
        pass

    def not_static(self):
        """
        The ends of the endData must not be static.

        .. ocl::
            endData->forAll(not end.isStatic)
        """
        pass

    def same_association(self):
        """
        The ends of the endData must all be from the same Association and include all and only the memberEnds of
        that association.

        .. ocl::
            endData.end = self.association().memberEnd->asBag()
        """
        pass

    def same_pins(self):
        """
        The inputValue InputPins is the same as the union of all the InputPins referenced by the endData.

        .. ocl::
            inputValue->asBag()=endData.allPins()
        """
        pass

class WriteLinkAction(models.Model):
    """
    WriteLinkAction is an abstract class for LinkActions that create and destroy links.
    """

    __package__ = 'UML.Actions'

    link_action = models.OneToOneField('LinkAction', on_delete=models.CASCADE, primary_key=True)

    def allow_access(self):
        """
        The visibility of at least one end must allow access from the context Classifier of the WriteLinkAction.

        .. ocl::
            endData.end->exists(end |
              end.type=_'context' or
              end.visibility=VisibilityKind::public or 
              end.visibility=VisibilityKind::protected and
              endData.end->exists(other | 
                other<>end and _'context'.conformsTo(other.type.oclAsType(Classifier))))
        """
        pass

class CreateLinkAction(models.Model):
    """
    A CreateLinkAction is a WriteLinkAction for creating links.
    """

    __package__ = 'UML.Actions'

    end_data = models.ManyToManyField('LinkEndCreationData', related_name='%(app_label)s_%(class)s_end_data', blank=True, 
                                      help_text='The LinkEndData that specifies the values to be placed on the ' +
                                      'Association ends for the new link.')
    write_link_action = models.OneToOneField('WriteLinkAction', on_delete=models.CASCADE, primary_key=True)

    def association_not_abstract(self):
        """
        The Association cannot be an abstract Classifier.

        .. ocl::
            not self.association().isAbstract
        """
        pass

class CreateLinkObjectAction(models.Model):
    """
    A CreateLinkObjectAction is a CreateLinkAction for creating link objects (AssociationClasse instances).
    """

    __package__ = 'UML.Actions'

    create_link_action = models.OneToOneField('CreateLinkAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The output pin on which the newly created link object is placed.')

    def association_class(self):
        """
        The Association must be an AssociationClass.

        .. ocl::
            self.association().oclIsKindOf(AssociationClass)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def type_of_result(self):
        """
        The type of the result OutputPin must be the same as the Association of the CreateLinkObjectAction.

        .. ocl::
            result.type = association()
        """
        pass

class InvocationAction(models.Model):
    """
    InvocationAction is an abstract class for the various actions that request Behavior invocation.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    argument = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_argument', blank=True, 
                                      help_text='The InputPins that provide the argument values passed in the ' +
                                      'invocation request.')
    on_port = models.ForeignKey('Port', related_name='%(app_label)s_%(class)s_on_port', blank=True, null=True, 
                                help_text='For CallOperationActions, SendSignalActions, and SendObjectActions, an ' +
                                'optional Port of the target object through which the invocation request is sent.')

class CallAction(models.Model):
    """
    CallAction is an abstract class for Actions that invoke a Behavior with given argument values and (if the
    invocation is synchronous) receive reply values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    is_synchronous = models.BooleanField(help_text='If true, the call is synchronous and the caller waits for ' +
                                         'completion of the invoked Behavior. If false, the call is asynchronous ' +
                                         'and the caller proceeds immediately and cannot receive return values.')
    result = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, 
                                    help_text='The OutputPins on which the reply values from the invocation are ' +
                                    'placed (if the call is synchronous).')

    def argument_pins(self):
        """
        The number of argument InputPins must be the same as the number of input (in and inout) ownedParameters
        of the called Behavior or Operation. The type, ordering and multiplicity of each argument InputPin must
        be consistent with the corresponding input Parameter.

        .. ocl::
            let parameter: OrderedSet(Parameter) = self.inputParameters() in
            argument->size() = parameter->size() and
            Sequence{1..argument->size()}->forAll(i | 
            	argument->at(i).type.conformsTo(parameter->at(i).type) and 
            	argument->at(i).isOrdered = parameter->at(i).isOrdered and
            	argument->at(i).compatibleWith(parameter->at(i)))
        """
        pass

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior or Operation being called. (This operation is
        abstract and should be overridden by subclasses of CallAction.)
        """
        pass

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior or Operation being called. (This
        operation is abstract and should be overridden by subclasses of CallAction.)
        """
        pass

    def result_pins(self):
        """
        The number of result OutputPins must be the same as the number of output (inout, out and return)
        ownedParameters of the called Behavior or Operation. The type, ordering and multiplicity of each result
        OutputPin must be consistent with the corresponding input Parameter.

        .. ocl::
            let parameter: OrderedSet(Parameter) = self.outputParameters() in
            result->size() = parameter->size() and
            Sequence{1..result->size()}->forAll(i | 
            	parameter->at(i).type.conformsTo(result->at(i).type) and 
            	parameter->at(i).isOrdered = result->at(i).isOrdered and
            	parameter->at(i).compatibleWith(result->at(i)))
        """
        pass

    def synchronous_call(self):
        """
        Only synchronous CallActions can have result OutputPins.

        .. ocl::
            result->notEmpty() implies isSynchronous
        """
        pass

class AcceptEventAction(models.Model):
    """
    An AcceptEventAction is an Action that waits for the occurrence of one or more specific Events.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    is_unmarshall = models.BooleanField(help_text='Indicates whether there is a single OutputPin for a ' +
                                        'SignalEvent occurrence, or multiple OutputPins for attribute values of ' +
                                        'the instance of the Signal associated with a SignalEvent occurrence.')
    result = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, 
                                    help_text='OutputPins holding the values received from an Event occurrence.')
    trigger = models.ManyToManyField('Trigger', related_name='%(app_label)s_%(class)s_trigger', 
                                     help_text='The Triggers specifying the Events of which the AcceptEventAction ' +
                                     'waits for occurrences.')

    def conforming_type(self):
        """
        If isUnmarshall=false and all the triggers are for SignalEvents, then the type of the single result
        OutputPin must either be null or all the signals must conform to it.

        .. ocl::
            not isUnmarshall implies 
            	result->isEmpty() or
            	let type: Type = result->first().type in
            	type=null or 
            		(trigger->forAll(event.oclIsKindOf(SignalEvent)) and 
            		 trigger.event.oclAsType(SignalEvent).signal->forAll(s | s.conformsTo(type)))
        """
        pass

    def no_input_pins(self):
        """
        AcceptEventActions may have no input pins.

        .. ocl::
            input->size() = 0
        """
        pass

    def no_output_pins(self):
        """
        There are no OutputPins if the trigger events are only ChangeEvents and/or CallEvents when this action
        is an instance of AcceptEventAction and not an instance of a descendant of AcceptEventAction (such as
        AcceptCallAction).

        .. ocl::
            (self.oclIsTypeOf(AcceptEventAction) and
               (trigger->forAll(event.oclIsKindOf(ChangeEvent) or  
                                         event.oclIsKindOf(CallEvent))))
            implies output->size() = 0
        """
        pass

    def one_output_pin(self):
        """
        If isUnmarshall=false and any of the triggers are for SignalEvents or TimeEvents, there must be exactly
        one result OutputPin with multiplicity 1..1.

        .. ocl::
            not isUnmarshall and trigger->exists(event.oclIsKindOf(SignalEvent) or event.oclIsKindOf(TimeEvent)) implies 
            	output->size() = 1 and output->first().is(1,1)
        """
        pass

    def unmarshall_signal_events(self):
        """
        If isUnmarshall is true (and this is not an AcceptCallAction), there must be exactly one trigger, which
        is for a SignalEvent. The number of result output pins must be the same as the number of attributes of
        the signal. The type and ordering of each result output pin must be the same as the corresponding
        attribute of the signal. The multiplicity of each result output pin must be compatible with the
        multiplicity of the corresponding attribute.

        .. ocl::
            isUnmarshall and self.oclIsTypeOf(AcceptEventAction) implies
            	trigger->size()=1 and
            	trigger->asSequence()->first().event.oclIsKindOf(SignalEvent) and
            	let attribute: OrderedSet(Property) = trigger->asSequence()->first().event.oclAsType(SignalEvent).signal.allAttributes() in
            	attribute->size()>0 and result->size() = attribute->size() and
            	Sequence{1..result->size()}->forAll(i | 
            		result->at(i).type = attribute->at(i).type and 
            		result->at(i).isOrdered = attribute->at(i).isOrdered and
            		result->at(i).includesMultiplicity(attribute->at(i)))
        """
        pass

class AcceptCallAction(models.Model):
    """
    An AcceptCallAction is an AcceptEventAction that handles the receipt of a synchronous call request. In
    addition to the values from the Operation input parameters, the Action produces an output that is needed
    later to supply the information to the ReplyAction necessary to return control to the caller. An
    AcceptCallAction is for synchronous calls. If it is used to handle an asynchronous call, execution of the
    subsequent ReplyAction will complete immediately with no effect.
    """

    __package__ = 'UML.Actions'

    accept_event_action = models.OneToOneField('AcceptEventAction', on_delete=models.CASCADE, primary_key=True)
    return_information = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_return_information', null=True, 
                                           help_text='An OutputPin where a value is placed containing sufficient ' +
                                           'information to perform a subsequent ReplyAction and return control to ' +
                                           'the caller. The contents of this value are opaque. It can be passed ' +
                                           'and copied but it cannot be manipulated by the model.')

    def result_pins(self):
        """
        The number of result OutputPins must be the same as the number of input (in and inout) ownedParameters
        of the Operation specified by the trigger Event. The type, ordering and multiplicity of each result
        OutputPin must be consistent with the corresponding input Parameter.

        .. ocl::
            let parameter: OrderedSet(Parameter) = trigger.event->asSequence()->first().oclAsType(CallEvent).operation.inputParameters() in
            result->size() = parameter->size() and
            Sequence{1..result->size()}->forAll(i | 
            	parameter->at(i).type.conformsTo(result->at(i).type) and 
            	parameter->at(i).isOrdered = result->at(i).isOrdered and
            	parameter->at(i).compatibleWith(result->at(i)))
        """
        pass

    def trigger_call_event(self):
        """
        The action must have exactly one trigger, which must be for a CallEvent.

        .. ocl::
            trigger->size()=1 and
            trigger->asSequence()->first().event.oclIsKindOf(CallEvent)
        """
        pass

    def unmarshall(self):
        """
        isUnmrashall must be true for an AcceptCallAction.

        .. ocl::
            isUnmarshall = true
        """
        pass

class StateInvariant(models.Model):
    """
    A StateInvariant is a runtime constraint on the participants of the Interaction. It may be used to specify a
    variety of different kinds of Constraints, such as values of Attributes or Variables, internal or external
    States, and so on. A StateInvariant is an InteractionFragment and it is placed on a Lifeline.
    """

    __package__ = 'UML.Interactions'

    covered = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_covered', null=True, 
                                help_text='References the Lifeline on which the StateInvariant appears.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    invariant = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_invariant', null=True, 
                                  help_text='A Constraint that should hold at runtime for this StateInvariant.')

class Behavior(models.Model):
    """
    Behavior is a specification of how its context BehavioredClassifier changes state over time. This
    specification may be either a definition of possible behavior execution or emergent behavior, or a selective
    illustration of an interesting subset of possible executions. The latter form is typically used for
    capturing examples, such as a trace of a particular execution.
    """

    __package__ = 'UML.CommonBehavior'

    context = models.ForeignKey('BehavioredClassifier', related_name='%(app_label)s_%(class)s_context', blank=True, null=True, 
                                help_text='The BehavioredClassifier that is the context for the execution of the ' +
                                'Behavior. A Behavior that is directly owned as a nestedClassifier does not have a ' +
                                'context. Otherwise, to determine the context of a Behavior, find the first ' +
                                'BehavioredClassifier reached by following the chain of owner relationships from ' +
                                'the Behavior, if any. If there is such a BehavioredClassifier, then it is the ' +
                                'context, unless it is itself a Behavior with a non-empty context, in which case ' +
                                'that is also the context for the original Behavior. For example, following this ' +
                                'algorithm, the context of an entry Behavior in a StateMachine is the ' +
                                'BehavioredClassifier that owns the StateMachine. The features of the context ' +
                                'BehavioredClassifier as well as the Elements visible to the context Classifier ' +
                                'are visible to the Behavior.')
    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    is_reentrant = models.BooleanField(help_text='Tells whether the Behavior can be invoked while it is still ' +
                                       'executing from a previous invocation.')
    owned_parameter = models.ManyToManyField('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', blank=True, 
                                             help_text='References a list of Parameters to the Behavior which ' +
                                             'describes the order and type of arguments that can be given when the ' +
                                             'Behavior is invoked and of the values which will be returned when ' +
                                             'the Behavior completes its execution.')
    owned_parameter_set = models.ManyToManyField('ParameterSet', related_name='%(app_label)s_%(class)s_owned_parameter_set', blank=True, 
                                                 help_text='The ParameterSets owned by this Behavior.')
    postcondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_postcondition', blank=True, 
                                           help_text='An optional set of Constraints specifying what is fulfilled ' +
                                           'after the execution of the Behavior is completed, if its precondition ' +
                                           'was fulfilled before its invocation.')
    precondition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_precondition', blank=True, 
                                          help_text='An optional set of Constraints specifying what must be ' +
                                          'fulfilled before the Behavior is invoked.')
    redefined_behavior = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_behavior', blank=True, 
                                                help_text='References the Behavior that this Behavior redefines. ' +
                                                'A subtype of Behavior may redefine any other subtype of Behavior. ' +
                                                'If the Behavior implements a BehavioralFeature, it replaces the ' +
                                                'redefined Behavior. If the Behavior is a classifierBehavior, it ' +
                                                'extends the redefined Behavior.')
    specification = models.ForeignKey('BehavioralFeature', related_name='%(app_label)s_%(class)s_specification', blank=True, null=True, 
                                      help_text='Designates a BehavioralFeature that the Behavior implements. The ' +
                                      'BehavioralFeature must be owned by the BehavioredClassifier that owns the ' +
                                      'Behavior or be inherited by it. The Parameters of the BehavioralFeature and ' +
                                      'the implementing Behavior must match. A Behavior does not need to have a ' +
                                      'specification, in which case it either is the classifierBehavior of a ' +
                                      'BehavioredClassifier or it can only be invoked by another Behavior of the ' +
                                      'Classifier.')

    def behaviored_classifier(self):
        """
        The first BehavioredClassifier reached by following the chain of owner relationships from the Behavior,
        if any.

        .. ocl::
            if from.oclIsKindOf(BehavioredClassifier) then
                from.oclAsType(BehavioredClassifier)
            else if from.owner = null then
                null
            else
                self.behavioredClassifier(from.owner)
            endif
            endif
        """
        pass

    def get_context(self):
        """
        A Behavior that is directly owned as a nestedClassifier does not have a context. Otherwise, to determine
        the context of a Behavior, find the first BehavioredClassifier reached by following the chain of owner
        relationships from the Behavior, if any. If there is such a BehavioredClassifier, then it is the
        context, unless it is itself a Behavior with a non-empty context, in which case that is also the context
        for the original Behavior.

        .. ocl::
            result = (if nestingClass <> null then
                null
            else
                let b:BehavioredClassifier = self.behavioredClassifier(self.owner) in
                if b.oclIsKindOf(Behavior) and b.oclAsType(Behavior)._'context' <> null then 
                    b.oclAsType(Behavior)._'context'
                else 
                    b 
                endif
            endif
                    )
        """
        pass

    def feature_of_context_classifier(self):
        """
        The specification BehavioralFeature must be a feature (possibly inherited) of the context
        BehavioredClassifier of the Behavior.

        .. ocl::
            _'context'.feature->includes(specification)
        """
        pass

    def input_parameters(self):
        """
        The in and inout ownedParameters of the Behavior.

        .. ocl::
            result = (ownedParameter->select(direction=ParameterDirectionKind::_'in' or direction=ParameterDirectionKind::inout))
        """
        pass

    def most_one_behavior(self):
        """
        There may be at most one Behavior for a given pairing of BehavioredClassifier (as owner of the Behavior)
        and BehavioralFeature (as specification of the Behavior).

        .. ocl::
            specification <> null implies _'context'.ownedBehavior->select(specification=self.specification)->size() = 1
        """
        pass

    def output_parameters(self):
        """
        The out, inout and return ownedParameters.

        .. ocl::
            result = (ownedParameter->select(direction=ParameterDirectionKind::out or direction=ParameterDirectionKind::inout or direction=ParameterDirectionKind::return))
        """
        pass

    def parameters_match(self):
        """
        If a Behavior has a specification BehavioralFeature, then it must have the same number of
        ownedParameters as its specification. The Behavior Parameters must also "match" the BehavioralParameter
        Parameters, but the exact requirements for this matching are not formalized.

        .. ocl::
            specification <> null implies ownedParameter->size() = specification.ownedParameter->size()
        """
        pass

class StateMachine(models.Model):
    """
    StateMachines can be used to express event-driven behaviors of parts of a system. Behavior is modeled as a
    traversal of a graph of Vertices interconnected by one or more joined Transition arcs that are triggered by
    the dispatching of successive Event occurrences. During this traversal, the StateMachine may execute a
    sequence of Behaviors associated with various elements of the StateMachine.
    """

    __package__ = 'UML.StateMachines'

    behavior = models.OneToOneField('Behavior', on_delete=models.CASCADE, primary_key=True)
    connection_point = models.ManyToManyField('Pseudostate', related_name='%(app_label)s_%(class)s_connection_point', blank=True, 
                                              help_text='The connection points defined for this StateMachine. ' +
                                              'They represent the interface of the StateMachine when used as part ' +
                                              'of submachine State')
    extended_state_machine = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_extended_state_machine', blank=True, 
                                                    help_text='The StateMachines of which this is an extension.')
    submachine_state = models.ManyToManyField('State', related_name='%(app_label)s_%(class)s_submachine_state', blank=True, 
                                              help_text='References the submachine(s) in case of a submachine ' +
                                              'State. Multiple machines are referenced in case of a concurrent ' +
                                              'State.')

    def lca(self):
        """
        The operation LCA(s1,s2) returns the Region that is the least common ancestor of Vertices s1 and s2,
        based on the StateMachine containment hierarchy.

        .. ocl::
            result = (if ancestor(s1, s2) then 
                s2.container
            else
            	if ancestor(s2, s1) then
            	    s1.container 
            	else 
            	    LCA(s1.container.state, s2.container.state)
            	endif
            endif)
        """
        pass

    def lca_state(self):
        """
        This utility funciton is like the LCA, except that it returns the nearest composite State that contains
        both input Vertices.

        .. ocl::
            result = (if v2.oclIsTypeOf(State) and ancestor(v1, v2) then
            	v2.oclAsType(State)
            else if v1.oclIsTypeOf(State) and ancestor(v2, v1) then
            	v1.oclAsType(State)
            else if (v1.container.state->isEmpty() or v2.container.state->isEmpty()) then 
            	null.oclAsType(State)
            else LCAState(v1.container.state, v2.container.state)
            endif endif endif)
        """
        pass

    def ancestor(self):
        """
        The query ancestor(s1, s2) checks whether Vertex s2 is an ancestor of Vertex s1.

        .. ocl::
            result = (if (s2 = s1) then 
            	true 
            else 
            	if s1.container.stateMachine->notEmpty() then 
            	    true
            	else 
            	    if s2.container.stateMachine->notEmpty() then 
            	        false
            	    else
            	        ancestor(s1, s2.container.state)
            	     endif
            	 endif
            endif  )
        """
        pass

    def classifier_context(self):
        """
        The Classifier context of a StateMachine cannot be an Interface.

        .. ocl::
            _'context' <> null implies not _'context'.oclIsKindOf(Interface)
        """
        pass

    def connection_points(self):
        """
        The connection points of a StateMachine are Pseudostates of kind entry point or exit point.

        .. ocl::
            connectionPoint->forAll (kind = PseudostateKind::entryPoint or kind = PseudostateKind::exitPoint)
        """
        pass

    def context_classifier(self):
        """
        The context Classifier of the method StateMachine of a BehavioralFeature must be the Classifier that
        owns the BehavioralFeature.

        .. ocl::
            specification <> null implies ( _'context' <> null and specification.featuringClassifier->exists(c | c = _'context'))
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies that a redefining StateMachine is consistent with a redefined
        StateMachine provided that the redefining StateMachine is an extension of the redefined StateMachine :
        Regions are inherited and Regions can be added, inherited Regions can be redefined. In case of multiple
        redefining StateMachine, extension implies that the redefining StateMachine gets orthogonal Regions for
        each of the redefined StateMachine.

        .. ocl::
            result = (-- the following is merely a default body; it is expected that the specific form of this constraint will be specified by profiles
            true)
        """
        pass

    def is_redefinition_context_valid(self):
        """
        The query isRedefinitionContextValid() specifies whether the redefinition context of a StateMachine is
        properly related to the redefinition contexts of the specified StateMachine to allow this element to
        redefine the other. The context Classifier of a redefining StateMachine must redefine the context
        Classifier of the redefined StateMachine.

        .. ocl::
            result = (if redefinedElement.oclIsKindOf(StateMachine) then
              let redefinedStateMachine : StateMachine = redefinedElement.oclAsType(StateMachine) in
                self._'context'().oclAsType(BehavioredClassifier).redefinedClassifier->
                  includes(redefinedStateMachine._'context'())
            else
              false
            endif)
        """
        pass

    def method(self):
        """
        A StateMachine as the method for a BehavioralFeature cannot have entry/exit connection points.

        .. ocl::
            specification <> null implies connectionPoint->isEmpty()
        """
        pass

class ProtocolStateMachine(models.Model):
    """
    A ProtocolStateMachine is always defined in the context of a Classifier. It specifies which
    BehavioralFeatures of the Classifier can be called in which State and under which conditions, thus
    specifying the allowed invocation sequences on the Classifier's BehavioralFeatures. A ProtocolStateMachine
    specifies the possible and permitted Transitions on the instances of its context Classifier, together with
    the BehavioralFeatures that carry the Transitions. In this manner, an instance lifecycle can be specified
    for a Classifier, by defining the order in which the BehavioralFeatures can be activated and the States
    through which an instance progresses during its existence.
    """

    __package__ = 'UML.StateMachines'

    conformance = models.ManyToManyField('ProtocolConformance', related_name='%(app_label)s_%(class)s_conformance', blank=True, 
                                         help_text='Conformance between ProtocolStateMachine')
    state_machine = models.OneToOneField('StateMachine', on_delete=models.CASCADE, primary_key=True)

    def classifier_context(self):
        """
        A ProtocolStateMachine must only have a Classifier context, not a BehavioralFeature context.

        .. ocl::
            _'context' <> null and specification = null
        """
        pass

    def deep_or_shallow_history(self):
        """
        ProtocolStateMachines cannot have deep or shallow history Pseudostates.

        .. ocl::
            region->forAll (r | r.subvertex->forAll (v | v.oclIsKindOf(Pseudostate) implies
            ((v.oclAsType(Pseudostate).kind <>  PseudostateKind::deepHistory) and (v.oclAsType(Pseudostate).kind <> PseudostateKind::shallowHistory))))
        """
        pass

    def entry_exit_do(self):
        """
        The states of a ProtocolStateMachine cannot have entry, exit, or do activity Behaviors.

        .. ocl::
            region->forAll(r | r.subvertex->forAll(v | v.oclIsKindOf(State) implies
            (v.oclAsType(State).entry->isEmpty() and v.oclAsType(State).exit->isEmpty() and v.oclAsType(State).doActivity->isEmpty())))
        """
        pass

    def protocol_transitions(self):
        """
        All Transitions of a ProtocolStateMachine must be ProtocolTransitions.

        .. ocl::
            region->forAll(r | r.transition->forAll(t | t.oclIsTypeOf(ProtocolTransition)))
        """
        pass

class AddVariableValueAction(models.Model):
    """
    An AddVariableValueAction is a WriteVariableAction for adding values to a Variable.
    """

    __package__ = 'UML.Actions'

    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', blank=True, null=True, 
                                  help_text='The InputPin that gives the position at which to insert a new value ' +
                                  'or move an existing value in ordered Variables. The type of the insertAt ' +
                                  'InputPin is UnlimitedNatural, but the value cannot be zero. It is omitted for ' +
                                  'unordered Variables.')
    is_replace_all = models.BooleanField(help_text='Specifies whether existing values of the Variable should be ' +
                                         'removed before adding the new value.')
    write_variable_action = models.OneToOneField('WriteVariableAction', on_delete=models.CASCADE, primary_key=True)

    def insert_at_pin(self):
        """
        AddVariableValueActions for ordered Variables must have a single InputPin for the insertion point with
        type UnlimtedNatural and multiplicity of 1..1 if isReplaceAll=false, otherwise the Action has no
        InputPin for the insertion point.

        .. ocl::
            if not variable.isOrdered then insertAt = null
            else 
              not isReplaceAll implies
              	insertAt<>null and 
              	insertAt->forAll(type=UnlimitedNatural and is(1,1.oclAsType(UnlimitedNatural)))
            endif
        """
        pass

    def required_value(self):
        """
        A value InputPin is required.

        .. ocl::
            value <> null
        """
        pass

class ConnectableElement(models.Model):
    """
    ConnectableElement is an abstract metaclass representing a set of instances that play roles of a
    StructuredClassifier. ConnectableElements may be joined by attached Connectors and specify configurations of
    linked instances to be created within an instance of the containing StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    end = models.ManyToManyField('ConnectorEnd', related_name='%(app_label)s_%(class)s_end', blank=True, 
                                 help_text='A set of ConnectorEnds that attach to this ConnectableElement.')
    parameterable_element = models.OneToOneField('ParameterableElement')
    template_parameter = models.ForeignKey('ConnectableElementTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', blank=True, null=True, 
                                           help_text='The ConnectableElementTemplateParameter for this ' +
                                           'ConnectableElement parameter.')
    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)

    def get_end(self):
        """
        Derivation for ConnectableElement::/end : ConnectorEnd

        .. ocl::
            result = (ConnectorEnd.allInstances()->select(role = self))
        """
        pass

class JoinNode(models.Model):
    """
    A JoinNode is a ControlNode that synchronizes multiple flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)
    is_combine_duplicate = models.BooleanField(help_text='Indicates whether incoming tokens having objects with ' +
                                               'the same identity are combined into one by the JoinNode.')
    join_spec = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_join_spec', blank=True, null=True, 
                                  help_text='A ValueSpecification giving the condition under which the JoinNode ' +
                                  'will offer a token on its outgoing ActivityEdge. If no joinSpec is specified, ' +
                                  'then the JoinNode will offer an outgoing token if tokens are offered on all of ' +
                                  'its incoming ActivityEdges (an "and" condition).')

    def incoming_object_flow(self):
        """
        If one of the incoming ActivityEdges of a JoinNode is an ObjectFlow, then its outgoing ActivityEdge must
        be an ObjectFlow. Otherwise its outgoing ActivityEdge must be a ControlFlow.

        .. ocl::
            if incoming->exists(oclIsKindOf(ObjectFlow)) then outgoing->forAll(oclIsKindOf(ObjectFlow))
            else outgoing->forAll(oclIsKindOf(ControlFlow))
            endif
        """
        pass

    def one_outgoing_edge(self):
        """
        A JoinNode has one outgoing ActivityEdge.

        .. ocl::
            outgoing->size() = 1
        """
        pass

class FinalNode(models.Model):
    """
    A FinalNode is an abstract ControlNode at which a flow in an Activity stops.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)

    def no_outgoing_edges(self):
        """
        A FinalNode has no outgoing ActivityEdges.

        .. ocl::
            outgoing->isEmpty()
        """
        pass

class FlowFinalNode(models.Model):
    """
    A FlowFinalNode is a FinalNode that terminates a flow by consuming the tokens offered to it.
    """

    __package__ = 'UML.Activities'

    final_node = models.OneToOneField('FinalNode', on_delete=models.CASCADE, primary_key=True)

class DeployedArtifact(models.Model):
    """
    A deployed artifact is an artifact or artifact instance that has been deployed to a deployment target.
    """

    __package__ = 'UML.Deployments'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

class Artifact(models.Model):
    """
    An artifact is the specification of a physical piece of information that is used or produced by a software
    development process, or by deployment and operation of a system. Examples of artifacts include model files,
    source files, scripts, and binary executable files, a table in a database system, a development deliverable,
    or a word-processing document, a mail message. An artifact is the source of a deployment to a node.
    """

    __package__ = 'UML.Deployments'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    deployed_artifact = models.OneToOneField('DeployedArtifact')
    file_name = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text='A concrete name that is used to refer to the Artifact in a physical ' +
                                 'context. Example: file system name, universal resource locator.')
    manifestation = models.ManyToManyField('Manifestation', related_name='%(app_label)s_%(class)s_manifestation', blank=True, 
                                           help_text='The set of model elements that are manifested in the ' +
                                           'Artifact. That is, these model elements are utilized in the ' +
                                           'construction (or generation) of the artifact.')
    nested_artifact = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_nested_artifact', blank=True, 
                                             help_text='The Artifacts that are defined (nested) within the ' +
                                             'Artifact. The association is a specialization of the ownedMember ' +
                                             'association from Namespace to NamedElement.')
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The attributes or association ends defined for the ' +
                                             'Artifact. The association is a specialization of the ownedMember ' +
                                             'association.')
    owned_operation = models.ManyToManyField('Operation', related_name='%(app_label)s_%(class)s_owned_operation', blank=True, 
                                             help_text='The Operations defined for the Artifact. The association ' +
                                             'is a specialization of the ownedMember association.')

class Association(models.Model):
    """
    A link is a tuple of values that refer to typed objects.  An Association classifies a set of links, each of
    which is an instance of the Association.  Each value in the link refers to an instance of the type of the
    corresponding end of the Association.
    """

    __package__ = 'UML.StructuredClassifiers'

    classifier = models.OneToOneField('Classifier')
    end_type = models.ManyToManyField('Type', related_name='%(app_label)s_%(class)s_end_type', 
                                      help_text='The Classifiers that are used as types of the ends of the ' +
                                      'Association.')
    is_derived = models.BooleanField(help_text='Specifies whether the Association is derived from other model ' +
                                     'elements such as other Associations.')
    member_end = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_member_end', blank=True, 
                                        help_text='Each end represents participation of instances of the ' +
                                        'Classifier connected to the end in links of the Association.')
    navigable_owned_end = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_navigable_owned_end', blank=True, 
                                                 help_text='The navigable ends that are owned by the Association ' +
                                                 'itself.')
    owned_end = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_end', blank=True, 
                                       help_text='The ends that are owned by the Association itself.')
    relationship = models.OneToOneField('Relationship', on_delete=models.CASCADE, primary_key=True)

    def association_ends(self):
        """
        Ends of Associations with more than two ends must be owned by the Association itself.

        .. ocl::
            memberEnd->size() > 2 implies ownedEnd->includesAll(memberEnd)
        """
        pass

    def binary_associations(self):
        """
        Only binary Associations can be aggregations.

        .. ocl::
            memberEnd->exists(aggregation <> AggregationKind::none) implies (memberEnd->size() = 2 and memberEnd->exists(aggregation = AggregationKind::none))
        """
        pass

    def end_type(self):
        """
        endType is derived from the types of the member ends.

        .. ocl::
            result = (memberEnd->collect(type)->asSet())
        """
        pass

    def ends_must_be_typed(self):
        """
        .. ocl::
            memberEnd->forAll(type->notEmpty())
        """
        pass

    def specialized_end_number(self):
        """
        An Association specializing another Association has the same number of ends as the other Association.

        .. ocl::
            parents()->select(oclIsKindOf(Association)).oclAsType(Association)->forAll(p | p.memberEnd->size() = self.memberEnd->size())
        """
        pass

    def specialized_end_types(self):
        """
        When an Association specializes another Association, every end of the specific Association corresponds
        to an end of the general Association, and the specific end reaches the same type or a subtype of the
        corresponding general end.

        .. ocl::
            Sequence{1..memberEnd->size()}->
            	forAll(i | general->select(oclIsKindOf(Association)).oclAsType(Association)->
            		forAll(ga | self.memberEnd->at(i).type.conformsTo(ga.memberEnd->at(i).type)))
        """
        pass

class AssociationClass(models.Model):
    """
    A model element that has both Association and Class properties. An AssociationClass can be seen as an
    Association that also has Class properties, or as a Class that also has Association properties. It not only
    connects a set of Classifiers but also defines a set of Features that belong to the Association itself and
    not to any of the associated Classifiers.
    """

    __package__ = 'UML.StructuredClassifiers'

    association = models.OneToOneField('Association')
    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)

    def cannot_be_defined(self):
        """
        An AssociationClass cannot be defined between itself and something else.

        .. ocl::
            self.endType()->excludes(self) and self.endType()->collect(et|et.oclAsType(Classifier).allParents())->flatten()->excludes(self)
        """
        pass

    def disjoint_attributes_ends(self):
        """
        The owned attributes and owned ends of an AssociationClass are disjoint.

        .. ocl::
            ownedAttribute->intersection(ownedEnd)->isEmpty()
        """
        pass

class ActivityParameterNode(models.Model):
    """
    An ActivityParameterNode is an ObjectNode for accepting values from the input Parameters or providing values
    to the output Parameters of an Activity.
    """

    __package__ = 'UML.Activities'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)
    parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_parameter', null=True, 
                                  help_text='The Parameter for which the ActivityParameterNode will be accepting ' +
                                  'or providing values.')

    def has_parameters(self):
        """
        The parameter of an ActivityParameterNode must be from the containing Activity.

        .. ocl::
            activity.ownedParameter->includes(parameter)
        """
        pass

    def no_edges(self):
        """
        An ActivityParameterNode may have all incoming ActivityEdges or all outgoing ActivityEdges, but it must
        not have both incoming and outgoing ActivityEdges.

        .. ocl::
            incoming->isEmpty() or outgoing->isEmpty()
        """
        pass

    def no_incoming_edges(self):
        """
        An ActivityParameterNode with no incoming ActivityEdges and one or more outgoing ActivityEdges must have
        a parameter with direction in or inout.

        .. ocl::
            (outgoing->notEmpty() and incoming->isEmpty()) implies 
            	(parameter.direction = ParameterDirectionKind::_'in' or 
            	 parameter.direction = ParameterDirectionKind::inout)
        """
        pass

    def no_outgoing_edges(self):
        """
        An ActivityParameterNode with no outgoing ActivityEdges and one or more incoming ActivityEdges must have
        a parameter with direction out, inout, or return.

        .. ocl::
            (incoming->notEmpty() and outgoing->isEmpty()) implies 
            	(parameter.direction = ParameterDirectionKind::out or 
            	 parameter.direction = ParameterDirectionKind::inout or 
            	 parameter.direction = ParameterDirectionKind::return)
        """
        pass

    def same_type(self):
        """
        The type of an ActivityParameterNode is the same as the type of its parameter.

        .. ocl::
            type = parameter.type
        """
        pass

class Activity(models.Model):
    """
    An Activity is the specification of parameterized Behavior as the coordinated sequencing of subordinate
    units.
    """

    __package__ = 'UML.Activities'

    behavior = models.OneToOneField('Behavior', on_delete=models.CASCADE, primary_key=True)
    edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', blank=True, 
                                  help_text='ActivityEdges expressing flow between the nodes of the Activity.')
    group = models.ManyToManyField('ActivityGroup', related_name='%(app_label)s_%(class)s_group', blank=True, 
                                   help_text='Top-level ActivityGroups in the Activity.')
    is_read_only = models.BooleanField(help_text='If true, this Activity must not make any changes to objects. ' +
                                       'The default is false (an Activity may make nonlocal changes). (This is an ' +
                                       'assertion, not an executable property. It may be used by an execution ' +
                                       'engine to optimize model execution. If the assertion is violated by the ' +
                                       'Activity, then the model is ill-formed.)')
    is_single_execution = models.BooleanField(help_text='If true, all invocations of the Activity are handled by ' +
                                              'the same execution.')
    node = models.ManyToManyField('ActivityNode', related_name='%(app_label)s_%(class)s_node', blank=True, 
                                  help_text='ActivityNodes coordinated by the Activity.')
    partition = models.ManyToManyField('ActivityPartition', related_name='%(app_label)s_%(class)s_partition', blank=True, 
                                       help_text='Top-level ActivityPartitions in the Activity.')
    structured_node = models.ManyToManyField('StructuredActivityNode', related_name='%(app_label)s_%(class)s_structured_node', blank=True, 
                                             help_text='Top-level StructuredActivityNodes in the Activity.')
    variable = models.ManyToManyField('Variable', related_name='%(app_label)s_%(class)s_variable', blank=True, 
                                      help_text='Top-level Variables defined by the Activity.')

    def maximum_one_parameter_node(self):
        """
        A Parameter with direction other than inout must have exactly one ActivityParameterNode in an Activity.

        .. ocl::
            ownedParameter->forAll(p | 
               p.direction <> ParameterDirectionKind::inout implies node->select(
                   oclIsKindOf(ActivityParameterNode) and oclAsType(ActivityParameterNode).parameter = p)->size()= 1)
        """
        pass

    def maximum_two_parameter_nodes(self):
        """
        A Parameter with direction inout must have exactly two ActivityParameterNodes in an Activity, at most
        one with incoming ActivityEdges and at most one with outgoing ActivityEdges.

        .. ocl::
            ownedParameter->forAll(p | 
            p.direction = ParameterDirectionKind::inout implies
            let associatedNodes : Set(ActivityNode) = node->select(
                   oclIsKindOf(ActivityParameterNode) and oclAsType(ActivityParameterNode).parameter = p) in 
              associatedNodes->size()=2 and
              associatedNodes->select(incoming->notEmpty())->size()<=1 and
              associatedNodes->select(outgoing->notEmpty())->size()<=1
            )
        """
        pass

class StructuralFeature(models.Model):
    """
    A StructuralFeature is a typed feature of a Classifier that specifies the structure of instances of the
    Classifier.
    """

    __package__ = 'UML.Classification'

    feature = models.OneToOneField('Feature')
    is_read_only = models.BooleanField(help_text='If isReadOnly is true, the StructuralFeature may not be written ' +
                                       'to after initialization.')
    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    typed_element = models.OneToOneField('TypedElement')

class DestroyLinkAction(models.Model):
    """
    A DestroyLinkAction is a WriteLinkAction that destroys links (including link objects).
    """

    __package__ = 'UML.Actions'

    end_data = models.ManyToManyField('LinkEndDestructionData', related_name='%(app_label)s_%(class)s_end_data', blank=True, 
                                      help_text='The LinkEndData that the values of the Association ends for the ' +
                                      'links to be destroyed.')
    write_link_action = models.OneToOneField('WriteLinkAction', on_delete=models.CASCADE, primary_key=True)

class TimeConstraint(models.Model):
    """
    A TimeConstraint is a Constraint that refers to a TimeInterval.
    """

    __package__ = 'UML.Values'

    first_event = models.BooleanField(blank=True, 
                                      help_text='The value of firstEvent is related to the constrainedElement. If ' +
                                      'firstEvent is true, then the corresponding observation event is the first ' +
                                      'time instant the execution enters the constrainedElement. If firstEvent is ' +
                                      'false, then the corresponding observation event is the last time instant ' +
                                      'the execution is within the constrainedElement.')
    interval_constraint = models.OneToOneField('IntervalConstraint', on_delete=models.CASCADE, primary_key=True)
    specification = models.ForeignKey('TimeInterval', related_name='%(app_label)s_%(class)s_specification', null=True, 
                                      help_text='TheTimeInterval constraining the duration.')

    def has_one_constrained_element(self):
        """
        A TimeConstraint has one constrainedElement.

        .. ocl::
            constrainedElement->size() = 1
        """
        pass

class ReadExtentAction(models.Model):
    """
    A ReadExtentAction is an Action that retrieves the current instances of a Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', null=True, 
                                   help_text='The Classifier whose instances are to be retrieved.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the Classifier instances are placed.')

    def multiplicity_of_result(self):
        """
        The multiplicity of the result OutputPin is 0..*.

        .. ocl::
            result.is(0,*)
        """
        pass

    def type_is_classifier(self):
        """
        The type of the result OutputPin is the classifier.

        .. ocl::
            result.type = classifier
        """
        pass

class Pseudostate(models.Model):
    """
    A Pseudostate is an abstraction that encompasses different types of transient Vertices in the StateMachine
    graph. A StateMachine instance never comes to rest in a Pseudostate, instead, it will exit and enter the
    Pseudostate within a single run-to-completion step.
    """

    __package__ = 'UML.StateMachines'

    kind = models.ForeignKey('PseudostateKind', related_name='%(app_label)s_%(class)s_kind', null=True, default='initial', 
                             help_text='Determines the precise type of the Pseudostate and can be one of: ' +
                             'entryPoint, exitPoint, initial, deepHistory, shallowHistory, join, fork, junction, ' +
                             'terminate or choice.')
    state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_state', blank=True, null=True, 
                              help_text='The State that owns this Pseudostate and in which it appears.')
    state_machine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_state_machine', blank=True, null=True, 
                                      help_text='The StateMachine in which this Pseudostate is defined. This only ' +
                                      'applies to Pseudostates of the kind entryPoint or exitPoint.')
    vertex = models.OneToOneField('Vertex', on_delete=models.CASCADE, primary_key=True)

    def choice_vertex(self):
        """
        In a complete statemachine, a choice Vertex must have at least one incoming and one outgoing Transition.

        .. ocl::
            (kind = PseudostateKind::choice) implies (incoming->size() >= 1 and outgoing->size() >= 1)
        """
        pass

    def fork_vertex(self):
        """
        In a complete StateMachine, a fork Vertex must have at least two outgoing Transitions and exactly one
        incoming Transition.

        .. ocl::
            (kind = PseudostateKind::fork) implies (incoming->size() = 1 and outgoing->size() >= 2)
        """
        pass

    def history_vertices(self):
        """
        History Vertices can have at most one outgoing Transition.

        .. ocl::
            ((kind = PseudostateKind::deepHistory) or (kind = PseudostateKind::shallowHistory)) implies (outgoing->size() <= 1)
        """
        pass

    def initial_vertex(self):
        """
        An initial Vertex can have at most one outgoing Transition.

        .. ocl::
            (kind = PseudostateKind::initial) implies (outgoing->size() <= 1)
        """
        pass

    def join_vertex(self):
        """
        In a complete StateMachine, a join Vertex must have at least two incoming Transitions and exactly one
        outgoing Transition.

        .. ocl::
            (kind = PseudostateKind::join) implies (outgoing->size() = 1 and incoming->size() >= 2)
        """
        pass

    def junction_vertex(self):
        """
        In a complete StateMachine, a junction Vertex must have at least one incoming and one outgoing
        Transition.

        .. ocl::
            (kind = PseudostateKind::junction) implies (incoming->size() >= 1 and outgoing->size() >= 1)
        """
        pass

    def outgoing_from_initial(self):
        """
        The outgoing Transition from an initial vertex may have a behavior, but not a trigger or a guard.

        .. ocl::
            (kind = PseudostateKind::initial) implies (outgoing.guard = null and outgoing.trigger->isEmpty())
        """
        pass

    def transitions_incoming(self):
        """
        All Transitions incoming a join Vertex must originate in different Regions of an orthogonal State.

        .. ocl::
            (kind = PseudostateKind::join) implies
            -- for any pair of incoming transitions there exists an orthogonal state which contains the source vetices of these transitions 
            -- such that these source vertices belong to different regions of that orthogonal state 
            incoming->forAll(t1:Transition, t2:Transition | let contState:State = containingStateMachine().LCAState(t1.source, t2.source) in
            	((contState <> null) and (contState.region
            		->exists(r1:Region, r2: Region | (r1 <> r2) and t1.source.isContainedInRegion(r1) and t2.source.isContainedInRegion(r2)))))
        """
        pass

    def transitions_outgoing(self):
        """
        All transitions outgoing a fork vertex must target states in different regions of an orthogonal state.

        .. ocl::
            (kind = PseudostateKind::fork) implies
            
            -- for any pair of outgoing transitions there exists an orthogonal state which contains the targets of these transitions 
            -- such that these targets belong to different regions of that orthogonal state 
            
            outgoing->forAll(t1:Transition, t2:Transition | let contState:State = containingStateMachine().LCAState(t1.target, t2.target) in
            	((contState <> null) and (contState.region
            		->exists(r1:Region, r2: Region | (r1 <> r2) and t1.target.isContainedInRegion(r1) and t2.target.isContainedInRegion(r2)))))
        """
        pass

class ReadSelfAction(models.Model):
    """
    A ReadSelfAction is an Action that retrieves the context object of the Behavior execution within which the
    ReadSelfAction execution is taking place.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the context object is placed.')

    def contained(self):
        """
        A ReadSelfAction must have a context Classifier.

        .. ocl::
            _'context' <> null
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the result OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def not_static(self):
        """
        If the ReadSelfAction is contained in an Behavior that is acting as a method, then the Operation of the
        method must not be static.

        .. ocl::
            let behavior: Behavior = self.containingBehavior() in
            behavior.specification<>null implies not behavior.specification.isStatic
        """
        pass

    def type(self):
        """
        The type of the result OutputPin is the context Classifier.

        .. ocl::
            result.type = _'context'
        """
        pass

class OpaqueAction(models.Model):
    """
    An OpaqueAction is an Action whose functionality is not specified within UML.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    body = models.CharField(max_length=255, blank=True, null=True, 
                            help_text='Provides a textual specification of the functionality of the Action, in ' +
                            'one or more languages other than UML.')
    input_value = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_input_value', blank=True, 
                                         help_text='The InputPins providing inputs to the OpaqueAction.')
    language = models.CharField(max_length=255, blank=True, null=True, 
                                help_text='If provided, a specification of the language used for each of the body ' +
                                'Strings.')
    output_value = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_output_value', blank=True, 
                                          help_text='The OutputPins on which the OpaqueAction provides outputs.')

    def language_body_size(self):
        """
        If the language attribute is not empty, then the size of the body and language lists must be the same.

        .. ocl::
            language->notEmpty() implies (_'body'->size() = language->size())
        """
        pass

class LiteralUnlimitedNatural(models.Model):
    """
    A LiteralUnlimitedNatural is a specification of an UnlimitedNatural number.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.IntegerField(null=True, )

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

    def unlimited_value(self):
        """
        The query unlimitedValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass

class ComponentRealization(models.Model):
    """
    Realization is specialized to (optionally) define the Classifiers that realize the contract offered by a
    Component in terms of its provided and required Interfaces. The Component forms an abstraction from these
    various Classifiers.
    """

    __package__ = 'UML.StructuredClassifiers'

    abstraction = models.ForeignKey('Component', related_name='%(app_label)s_%(class)s_abstraction', blank=True, null=True, 
                                    help_text='The Component that owns this ComponentRealization and which is ' +
                                    'implemented by its realizing Classifiers.')
    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)
    realizing_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_realizing_classifier', 
                                                  help_text='The Classifiers that are involved in the ' +
                                                  'implementation of the Component that owns this Realization.')

class StructuralFeatureAction(models.Model):
    """
    StructuralFeatureAction is an abstract class for all Actions that operate on StructuralFeatures.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin from which the object whose StructuralFeature is to be ' +
                               'read or written is obtained.')
    structural_feature = models.ForeignKey('StructuralFeature', related_name='%(app_label)s_%(class)s_structural_feature', null=True, 
                                           help_text='The StructuralFeature to be read or written.')

    def multiplicity(self):
        """
        The multiplicity of the object InputPin must be 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def not_static(self):
        """
        The structuralFeature must not be static.

        .. ocl::
            not structuralFeature.isStatic
        """
        pass

    def object_type(self):
        """
        The structuralFeature must either be an owned or inherited feature of the type of the object InputPin,
        or it must be an owned end of a binary Association whose opposite end had as a type to which the type of
        the object InputPin conforms.

        .. ocl::
            object.type.oclAsType(Classifier).allFeatures()->includes(structuralFeature) or
            	object.type.conformsTo(structuralFeature.oclAsType(Property).opposite.type)
        """
        pass

    def one_featuring_classifier(self):
        """
        The structuralFeature must have exactly one featuringClassifier.

        .. ocl::
            structuralFeature.featuringClassifier->size() = 1
        """
        pass

    def visibility(self):
        """
        The visibility of the structuralFeature must allow access from the object performing the
        ReadStructuralFeatureAction.

        .. ocl::
            structuralFeature.visibility = VisibilityKind::public or
            _'context'.allFeatures()->includes(structuralFeature) or
            structuralFeature.visibility=VisibilityKind::protected and
            _'context'.conformsTo(structuralFeature.oclAsType(Property).opposite.type.oclAsType(Classifier))
        """
        pass

class WriteStructuralFeatureAction(models.Model):
    """
    WriteStructuralFeatureAction is an abstract class for StructuralFeatureActions that change StructuralFeature
    values.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, null=True, 
                               help_text='The OutputPin on which is put the input object as modified by the ' +
                               'WriteStructuralFeatureAction.')
    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', blank=True, null=True, 
                              help_text='The InputPin that provides the value to be added or removed from the ' +
                              'StructuralFeature.')

    def multiplicity_of_result(self):
        """
        The multiplicity of the result OutputPin must be 1..1.

        .. ocl::
            result <> null implies result.is(1,1)
        """
        pass

    def multiplicity_of_value(self):
        """
        The multiplicity of the value InputPin is 1..1.

        .. ocl::
            value<>null implies value.is(1,1)
        """
        pass

    def type_of_result(self):
        """
        The type of the result OutputPin is the same as the type of the inherited object InputPin.

        .. ocl::
            result <> null implies result.type = object.type
        """
        pass

    def type_of_value(self):
        """
        The type of the value InputPin must conform to the type of the structuralFeature.

        .. ocl::
            value <> null implies value.type.conformsTo(structuralFeature.type)
        """
        pass

class CallOperationAction(models.Model):
    """
    A CallOperationAction is a CallAction that transmits an Operation call request to the target object, where
    it may cause the invocation of associated Behavior. The argument values of the CallOperationAction are
    passed on the input Parameters of the Operation. If call is synchronous, the execution of the
    CallOperationAction waits until the execution of the invoked Operation completes and the values of output
    Parameters of the Operation are placed on the result OutputPins. If the call is asynchronous, the
    CallOperationAction completes immediately and no results values can be provided.
    """

    __package__ = 'UML.Actions'

    call_action = models.OneToOneField('CallAction', on_delete=models.CASCADE, primary_key=True)
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation', null=True, 
                                  help_text='The Operation being invoked.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='The InputPin that provides the target object to which the Operation ' +
                               'call request is sent.')

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Operation being called.

        .. ocl::
            result = (operation.inputParameters())
        """
        pass

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Operation being called.

        .. ocl::
            result = (operation.outputParameters())
        """
        pass

    def type_target_pin(self):
        """
        If onPort has no value, the operation must be an owned or inherited feature of the type of the target
        InputPin, otherwise the Port given by onPort must be an owned or inherited feature of the type of the
        target InputPin, and the Port must have a required or provided Interface with the operation as an owned
        or inherited feature.

        .. ocl::
            if onPort=null then  target.type.oclAsType(Classifier).allFeatures()->includes(operation)
            else target.type.oclAsType(Classifier).allFeatures()->includes(onPort) and onPort.provided->union(onPort.required).allFeatures()->includes(operation)
            endif
        """
        pass

class ActivityEdge(models.Model):
    """
    An ActivityEdge is an abstract class for directed connections between two ActivityNodes.
    """

    __package__ = 'UML.Activities'

    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', blank=True, null=True, 
                                 help_text='The Activity containing the ActivityEdge, if it is directly owned by ' +
                                 'an Activity.')
    guard = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_guard', blank=True, null=True, 
                              help_text='A ValueSpecification that is evaluated to determine if a token can ' +
                              'traverse the ActivityEdge. If an ActivityEdge has no guard, then there is no ' +
                              'restriction on tokens traversing the edge.')
    in_group = models.ManyToManyField('ActivityGroup', related_name='%(app_label)s_%(class)s_in_group', blank=True, 
                                      help_text='ActivityGroups containing the ActivityEdge.')
    in_partition = models.ManyToManyField('ActivityPartition', related_name='%(app_label)s_%(class)s_in_partition', blank=True, 
                                          help_text='ActivityPartitions containing the ActivityEdge.')
    in_structured_node = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_in_structured_node', blank=True, null=True, 
                                           help_text='The StructuredActivityNode containing the ActivityEdge, if ' +
                                           'it is owned by a StructuredActivityNode.')
    interrupts = models.ForeignKey('InterruptibleActivityRegion', related_name='%(app_label)s_%(class)s_interrupts', blank=True, null=True, 
                                   help_text='The InterruptibleActivityRegion for which this ActivityEdge is an ' +
                                   'interruptingEdge.')
    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    redefined_edge = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_edge', blank=True, 
                                            help_text='ActivityEdges from a generalization of the Activity ' +
                                            'containing this ActivityEdge that are redefined by this ' +
                                            'ActivityEdge.')
    source = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_source', null=True, 
                               help_text='The ActivityNode from which tokens are taken when they traverse the ' +
                               'ActivityEdge.')
    target = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='The ActivityNode to which tokens are put when they traverse the ' +
                               'ActivityEdge.')
    weight = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_weight', blank=True, null=True, 
                               help_text='The minimum number of tokens that must traverse the ActivityEdge at the ' +
                               'same time. If no weight is specified, this is equivalent to specifying a constant ' +
                               'value of 1.')

    def is_consistent_with(self):
        """
        .. ocl::
            result = (redefiningElement.oclIsKindOf(ActivityEdge))
        """
        pass

    def source_and_target(self):
        """
        If an ActivityEdge is directly owned by an Activity, then its source and target must be directly or
        indirectly contained in the same Activity.

        .. ocl::
            activity<>null implies source.containingActivity() = activity and target.containingActivity() = activity
        """
        pass

class OpaqueBehavior(models.Model):
    """
    An OpaqueBehavior is a Behavior whose specification is given in a textual language other than UML.
    """

    __package__ = 'UML.CommonBehavior'

    behavior = models.OneToOneField('Behavior', on_delete=models.CASCADE, primary_key=True)
    body = models.CharField(max_length=255, blank=True, null=True, 
                            help_text='Specifies the behavior in one or more languages.')
    language = models.CharField(max_length=255, blank=True, null=True, 
                                help_text='Languages the body strings use in the same order as the body strings.')

class FunctionBehavior(models.Model):
    """
    A FunctionBehavior is an OpaqueBehavior that does not access or modify any objects or other external data.
    """

    __package__ = 'UML.CommonBehavior'

    opaque_behavior = models.OneToOneField('OpaqueBehavior', on_delete=models.CASCADE, primary_key=True)

    def has_all_data_type_attributes(self):
        """
        The hasAllDataTypeAttributes query tests whether the types of the attributes of the given DataType are
        all DataTypes, and similarly for all those DataTypes.

        .. ocl::
            result = (d.ownedAttribute->forAll(a |
                a.type.oclIsKindOf(DataType) and
                  hasAllDataTypeAttributes(a.type.oclAsType(DataType))))
        """
        pass

    def one_output_parameter(self):
        """
        A FunctionBehavior has at least one output Parameter.

        .. ocl::
            self.ownedParameter->
              select(p | p.direction = ParameterDirectionKind::out or p.direction= ParameterDirectionKind::inout or p.direction= ParameterDirectionKind::return)->size() >= 1
        """
        pass

    def types_of_parameters(self):
        """
        The types of the ownedParameters are all DataTypes, which may not nest anything but other DataTypes.

        .. ocl::
            ownedParameter->forAll(p | p.type <> null and
              p.type.oclIsTypeOf(DataType) and hasAllDataTypeAttributes(p.type.oclAsType(DataType)))
        """
        pass

class LiteralNull(models.Model):
    """
    A LiteralNull specifies the lack of a value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

    def is_null(self):
        """
        The query isNull() returns true.

        .. ocl::
            result = (true)
        """
        pass

class BroadcastSignalAction(models.Model):
    """
    A BroadcastSignalAction is an InvocationAction that transmits a Signal instance to all the potential target
    objects in the system. Values from the argument InputPins are used to provide values for the attributes of
    the Signal. The requestor continues execution immediately after the Signal instances are sent out and cannot
    receive reply values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal', null=True, 
                               help_text='The Signal whose instances are to be sent.')

    def no_onport(self):
        """
        A BroadcaseSignalAction may not specify onPort.

        .. ocl::
            onPort=null
        """
        pass

    def number_of_arguments(self):
        """
        The number of argument InputPins must be the same as the number of attributes in the signal.

        .. ocl::
            argument->size() = signal.allAttributes()->size()
        """
        pass

    def type_ordering_multiplicity(self):
        """
        The type, ordering, and multiplicity of an argument InputPin must be the same as the corresponding
        attribute of the signal.

        .. ocl::
            let attribute: OrderedSet(Property) = signal.allAttributes() in
            Sequence{1..argument->size()}->forAll(i | 
            	argument->at(i).type.conformsTo(attribute->at(i).type) and 
            	argument->at(i).isOrdered = attribute->at(i).isOrdered and
            	argument->at(i).compatibleWith(attribute->at(i)))
        """
        pass

class DurationInterval(models.Model):
    """
    A DurationInterval defines the range between two Durations.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval', on_delete=models.CASCADE, primary_key=True)
    max = models.ForeignKey('Duration', related_name='%(app_label)s_%(class)s_max', null=True, 
                            help_text='Refers to the Duration denoting the maximum value of the range.')
    min = models.ForeignKey('Duration', related_name='%(app_label)s_%(class)s_min', null=True, 
                            help_text='Refers to the Duration denoting the minimum value of the range.')

class ClearStructuralFeatureAction(models.Model):
    """
    A ClearStructuralFeatureAction is a StructuralFeatureAction that removes all values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', blank=True, null=True, 
                               help_text='The OutputPin on which is put the input object as modified by the ' +
                               'ClearStructuralFeatureAction.')
    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)

    def multiplicity_of_result(self):
        """
        The multiplicity of the result OutputPin must be 1..1.

        .. ocl::
            result<>null implies result.is(1,1)
        """
        pass

    def type_of_result(self):
        """
        The type of the result OutputPin is the same as the type of the inherited object InputPin.

        .. ocl::
            result<>null implies result.type = object.type
        """
        pass

class ExpansionRegion(models.Model):
    """
    An ExpansionRegion is a StructuredActivityNode that executes its content multiple times corresponding to
    elements of input collection(s).
    """

    __package__ = 'UML.Actions'

    input_element = models.ManyToManyField('ExpansionNode', related_name='%(app_label)s_%(class)s_input_element', 
                                           help_text='The ExpansionNodes that hold the input collections for the ' +
                                           'ExpansionRegion.')
    mode = models.ForeignKey('ExpansionKind', related_name='%(app_label)s_%(class)s_mode', null=True, default='iterative', 
                             help_text='The mode in which the ExpansionRegion executes its contents. If parallel, ' +
                             'executions are concurrent. If iterative, executions are sequential. If stream, a ' +
                             'stream of values flows into a single execution.')
    output_element = models.ManyToManyField('ExpansionNode', related_name='%(app_label)s_%(class)s_output_element', blank=True, 
                                            help_text='The ExpansionNodes that form the output collections of the ' +
                                            'ExpansionRegion.')
    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)

class ActionInputPin(models.Model):
    """
    An ActionInputPin is a kind of InputPin that executes an Action to determine the values to input to another
    Action.
    """

    __package__ = 'UML.Actions'

    from_action = models.ForeignKey('Action', related_name='%(app_label)s_%(class)s_from_action', null=True, 
                                    help_text='The Action used to provide the values of the ActionInputPin.')
    input_pin = models.OneToOneField('InputPin', on_delete=models.CASCADE, primary_key=True)

    def input_pin(self):
        """
        The fromAction of an ActionInputPin must only have ActionInputPins as InputPins.

        .. ocl::
            fromAction.input->forAll(oclIsKindOf(ActionInputPin))
        """
        pass

    def no_control_or_object_flow(self):
        """
        The fromAction of an ActionInputPin cannot have ActivityEdges coming into or out of it or its Pins.

        .. ocl::
            fromAction.incoming->union(outgoing)->isEmpty() and
            fromAction.input.incoming->isEmpty() and
            fromAction.output.outgoing->isEmpty()
        """
        pass

    def one_output_pin(self):
        """
        The fromAction of an ActionInputPin must have exactly one OutputPin.

        .. ocl::
            fromAction.output->size() = 1
        """
        pass

class Clause(models.Model):
    """
    A Clause is an Element that represents a single branch of a ConditionalNode, including a test and a body
    section. The body section is executed only if (but not necessarily if) the test section evaluates to true.
    """

    __package__ = 'UML.Actions'

    body = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_body', blank=True, 
                                  help_text='The set of ExecutableNodes that are executed if the test evaluates ' +
                                  'to true and the Clause is chosen over other Clauses within the ConditionalNode ' +
                                  'that also have tests that evaluate to true.')
    body_output = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_body_output', blank=True, 
                                         help_text='The OutputPins on Actions within the body section whose ' +
                                         'values are moved to the result OutputPins of the containing ' +
                                         'ConditionalNode after execution of the body.')
    decider = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_decider', null=True, 
                                help_text='An OutputPin on an Action in the test section whose Boolean value ' +
                                'determines the result of the test.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    predecessor_clause = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_predecessor_clause', blank=True, 
                                                help_text='A set of Clauses whose tests must all evaluate to ' +
                                                'false before this Clause can evaluate its test.')
    successor_clause = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_successor_clause', blank=True, 
                                              help_text='A set of Clauses that may not evaluate their tests ' +
                                              'unless the test for this Clause evaluates to false.')
    test = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_test', 
                                  help_text='The set of ExecutableNodes that are executed in order to provide a ' +
                                  'test result for the Clause.')

    def body_output_pins(self):
        """
        The bodyOutput Pins are OutputPins on Actions in the body of the Clause.

        .. ocl::
            _'body'.oclAsType(Action).allActions().output->includesAll(bodyOutput)
        """
        pass

    def decider_output(self):
        """
        The decider Pin must be on an Action in the test section of the Clause and must be of type Boolean with
        multiplicity 1..1.

        .. ocl::
            test.oclAsType(Action).allActions().output->includes(decider) and
            decider.type = Boolean and
            decider.is(1,1)
        """
        pass

    def test_and_body(self):
        """
        The test and body parts of a ConditionalNode must be disjoint with each other.

        .. ocl::
            test->intersection(_'body')->isEmpty()
        """
        pass

class DecisionNode(models.Model):
    """
    A DecisionNode is a ControlNode that chooses between outgoing ActivityEdges for the routing of tokens.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)
    decision_input = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_decision_input', blank=True, null=True, 
                                       help_text='A Behavior that is executed to provide an input to guard ' +
                                       'ValueSpecifications on ActivityEdges outgoing from the DecisionNode.')
    decision_input_flow = models.ForeignKey('ObjectFlow', related_name='%(app_label)s_%(class)s_decision_input_flow', blank=True, null=True, 
                                            help_text='An additional ActivityEdge incoming to the DecisionNode ' +
                                            'that provides a decision input value for the guards ' +
                                            'ValueSpecifications on ActivityEdges outgoing from the DecisionNode.')

    def decision_input_flow_incoming(self):
        """
        The decisionInputFlow of a DecisionNode must be an incoming ActivityEdge of the DecisionNode.

        .. ocl::
            incoming->includes(decisionInputFlow)
        """
        pass

    def edges(self):
        """
        The ActivityEdges incoming to and outgoing from a DecisionNode, other than the decisionInputFlow (if
        any), must be either all ObjectFlows or all ControlFlows.

        .. ocl::
            let allEdges: Set(ActivityEdge) = incoming->union(outgoing) in
            let allRelevantEdges: Set(ActivityEdge) = if decisionInputFlow->notEmpty() then allEdges->excluding(decisionInputFlow) else allEdges endif in
            allRelevantEdges->forAll(oclIsKindOf(ControlFlow)) or allRelevantEdges->forAll(oclIsKindOf(ObjectFlow))
        """
        pass

    def incoming_control_one_input_parameter(self):
        """
        If the DecisionNode has a decisionInputFlow and an incoming ControlFlow, then any decisionInput Behavior
        has one in Parameter whose type is the same as or a supertype of the type of object tokens offered on
        the decisionInputFlow.

        .. ocl::
            (decisionInput<>null and decisionInputFlow<>null and incoming->exists(oclIsKindOf(ControlFlow))) implies
            	decisionInput.inputParameters()->size()=1
        """
        pass

    def incoming_object_one_input_parameter(self):
        """
        If the DecisionNode has no decisionInputFlow and an incoming ObjectFlow, then any decisionInput Behavior
        has one in Parameter whose type is the same as or a supertype of the type of object tokens offered on
        the incoming ObjectFlow.

        .. ocl::
            (decisionInput<>null and decisionInputFlow=null and incoming->forAll(oclIsKindOf(ObjectFlow))) implies
            	decisionInput.inputParameters()->size()=1
        """
        pass

    def incoming_outgoing_edges(self):
        """
        A DecisionNode has one or two incoming ActivityEdges and at least one outgoing ActivityEdge.

        .. ocl::
            (incoming->size() = 1 or incoming->size() = 2) and outgoing->size() > 0
        """
        pass

    def parameters(self):
        """
        A decisionInput Behavior has no out parameters, no inout parameters, and one return parameter.

        .. ocl::
            decisionInput<>null implies 
              (decisionInput.ownedParameter->forAll(par | 
                 par.direction <> ParameterDirectionKind::out and 
                 par.direction <> ParameterDirectionKind::inout ) and
               decisionInput.ownedParameter->one(par | 
                 par.direction <> ParameterDirectionKind::return))
        """
        pass

    def two_input_parameters(self):
        """
        If the DecisionNode has a decisionInputFlow and an second incoming ObjectFlow, then any decisionInput
        has two in Parameters, the first of which has a type that is the same as or a supertype of the type of
        object tokens offered on the non-decisionInputFlow and the second of which has a type that is the same
        as or a supertype of the type of object tokens offered on the decisionInputFlow.

        .. ocl::
            (decisionInput<>null and decisionInputFlow<>null and incoming->forAll(oclIsKindOf(ObjectFlow))) implies
            	decisionInput.inputParameters()->size()=2
        """
        pass

    def zero_input_parameters(self):
        """
        If the DecisionNode has no decisionInputFlow and an incoming ControlFlow, then any decisionInput
        Behavior has no in parameters.

        .. ocl::
            (decisionInput<>null and decisionInputFlow=null and incoming->exists(oclIsKindOf(ControlFlow))) implies
               decisionInput.inputParameters()->isEmpty()
        """
        pass

class ValueSpecificationAction(models.Model):
    """
    A ValueSpecificationAction is an Action that evaluates a ValueSpecification and provides a result.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the result value is placed.')
    value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_value', null=True, 
                              help_text='The ValueSpecification to be evaluated.')

    def compatible_type(self):
        """
        The type of the value ValueSpecification must conform to the type of the result OutputPin.

        .. ocl::
            value.type.conformsTo(result.type)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the result OutputPin is 1..1

        .. ocl::
            result.is(1,1)
        """
        pass

class TestIdentityAction(models.Model):
    """
    A TestIdentityAction is an Action that tests if two values are identical objects.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    first = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_first', null=True, 
                              help_text='The InputPin on which the first input object is placed.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin whose Boolean value indicates whether the two input ' +
                               'objects are identical.')
    second = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_second', null=True, 
                               help_text='The OutputPin on which the second input object is placed.')

    def multiplicity(self):
        """
        The multiplicity of the InputPins is 1..1.

        .. ocl::
            first.is(1,1) and second.is(1,1)
        """
        pass

    def no_type(self):
        """
        The InputPins have no type.

        .. ocl::
            first.type= null and second.type = null
        """
        pass

    def result_is_boolean(self):
        """
        The type of the result OutputPin is Boolean.

        .. ocl::
            result.type=Boolean
        """
        pass

class TemplateSignature(models.Model):
    """
    A Template Signature bundles the set of formal TemplateParameters for a template.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owned_parameter = models.ManyToManyField('TemplateParameter', related_name='%(app_label)s_%(class)s_owned_parameter', blank=True, 
                                             help_text='The formal parameters that are owned by this ' +
                                             'TemplateSignature.')
    parameter = models.ManyToManyField('TemplateParameter', related_name='%(app_label)s_%(class)s_parameter', 
                                       help_text='The ordered set of all formal TemplateParameters for this ' +
                                       'TemplateSignature.')
    template = models.ForeignKey('TemplateableElement', related_name='%(app_label)s_%(class)s_template', null=True, 
                                 help_text='The TemplateableElement that owns this TemplateSignature.')

    def own_elements(self):
        """
        Parameters must own the ParameterableElements they parameter or those ParameterableElements must be
        owned by the TemplateableElement being templated.

        .. ocl::
            template.ownedElement->includesAll(parameter.parameteredElement->asSet() - parameter.ownedParameteredElement->asSet())
        """
        pass

    def unique_parameters(self):
        """
        The names of the parameters of a TemplateSignature are unique.

        .. ocl::
            parameter->forAll( p1, p2 | (p1 <> p2 and p1.parameteredElement.oclIsKindOf(NamedElement) and p2.parameteredElement.oclIsKindOf(NamedElement) ) implies
               p1.parameteredElement.oclAsType(NamedElement).name <> p2.parameteredElement.oclAsType(NamedElement).name)
        """
        pass

class RedefinableTemplateSignature(models.Model):
    """
    A RedefinableTemplateSignature supports the addition of formal template parameters in a specialization of a
    template classifier.
    """

    __package__ = 'UML.Classification'

    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', null=True, 
                                   help_text='The Classifier that owns this RedefinableTemplateSignature.')
    extended_signature = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_extended_signature', blank=True, 
                                                help_text='The signatures extended by this ' +
                                                'RedefinableTemplateSignature.')
    inherited_parameter = models.ManyToManyField('TemplateParameter', related_name='%(app_label)s_%(class)s_inherited_parameter', blank=True, 
                                                 help_text='The formal template parameters of the extended ' +
                                                 'signatures.')
    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    template_signature = models.OneToOneField('TemplateSignature')

    def inherited_parameter(self):
        """
        Derivation for RedefinableTemplateSignature::/inheritedParameter

        .. ocl::
            result = (if extendedSignature->isEmpty() then Set{} else extendedSignature.parameter->asSet() endif)
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two RedefinableTemplateSignatures in a context in which
        redefinition is possible, whether redefinition would be logically consistent. A redefining template
        signature is always consistent with a redefined template signature, as redefinition only adds new formal
        parameters.
        """
        pass

    def redefines_parents(self):
        """
        If any of the parent Classifiers are a template, then the extendedSignature must include the signature
        of that Classifier.

        .. ocl::
            classifier.allParents()->forAll(c | c.ownedTemplateSignature->notEmpty() implies self->closure(extendedSignature)->includes(c.ownedTemplateSignature))
        """
        pass

class ReadLinkAction(models.Model):
    """
    A ReadLinkAction is a LinkAction that navigates across an Association to retrieve the objects on one end.
    """

    __package__ = 'UML.Actions'

    link_action = models.OneToOneField('LinkAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the objects retrieved from the "open" end of ' +
                               'those links whose values on other ends are given by the endData.')

    def compatible_multiplicity(self):
        """
        The multiplicity of the open Association end must be compatible with the multiplicity of the result
        OutputPin.

        .. ocl::
            self.openEnd()->first().compatibleWith(result)
        """
        pass

    def navigable_open_end(self):
        """
        The open end must be navigable.

        .. ocl::
            self.openEnd()->first().isNavigable()
        """
        pass

    def one_open_end(self):
        """
        Exactly one linkEndData specification (corresponding to the "open" end) must not have an value InputPin.

        .. ocl::
            self.openEnd()->size() = 1
        """
        pass

    def open_end(self):
        """
        Returns the ends corresponding to endData with no value InputPin. (A well-formed ReadLinkAction is
        constrained to have only one of these.)

        .. ocl::
            result = (endData->select(value=null).end->asOrderedSet())
        """
        pass

    def type_and_ordering(self):
        """
        The type and ordering of the result OutputPin are same as the type and ordering of the open Association
        end.

        .. ocl::
            self.openEnd()->forAll(type=result.type and isOrdered=result.isOrdered)
        """
        pass

    def visibility(self):
        """
        Visibility of the open end must allow access from the object performing the action.

        .. ocl::
            let openEnd : Property = self.openEnd()->first() in
              openEnd.visibility = VisibilityKind::public or 
              endData->exists(oed | 
                oed.end<>openEnd and 
                (_'context' = oed.end.type or 
                  (openEnd.visibility = VisibilityKind::protected and 
                    _'context'.conformsTo(oed.end.type.oclAsType(Classifier)))))
        """
        pass

class LiteralReal(models.Model):
    """
    A LiteralReal is a specification of a Real value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.FloatField(null=True, )

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

    def real_value(self):
        """
        The query realValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass

class RaiseExceptionAction(models.Model):
    """
    A RaiseExceptionAction is an Action that causes an exception to occur. The input value becomes the exception
    object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    exception = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_exception', null=True, 
                                  help_text='An InputPin whose value becomes the exception object.')

class ValuePin(models.Model):
    """
    A ValuePin is an InputPin that provides a value by evaluating a ValueSpecification.
    """

    __package__ = 'UML.Actions'

    input_pin = models.OneToOneField('InputPin', on_delete=models.CASCADE, primary_key=True)
    value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_value', null=True, 
                              help_text='The ValueSpecification that is evaluated to obtain the value that the ' +
                              'ValuePin will provide.')

    def compatible_type(self):
        """
        The type of the value ValueSpecification must conform to the type of the ValuePin.

        .. ocl::
            value.type.conformsTo(type)
        """
        pass

    def no_incoming_edges(self):
        """
        A ValuePin may have no incoming ActivityEdges.

        .. ocl::
            incoming->isEmpty()
        """
        pass

class ReadLinkObjectEndAction(models.Model):
    """
    A ReadLinkObjectEndAction is an Action that retrieves an end object from a link object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_end', null=True, 
                            help_text='The Association end to be read.')
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The input pin from which the link object is obtained.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin where the result value is placed.')

    def association_of_association(self):
        """
        The association of the end must be an AssociationClass.

        .. ocl::
            end.association.oclIsKindOf(AssociationClass)
        """
        pass

    def ends_of_association(self):
        """
        The ends of the association must not be static.

        .. ocl::
            end.association.memberEnd->forAll(e | not e.isStatic)
        """
        pass

    def multiplicity_of_object(self):
        """
        The multiplicity of the object InputPin is 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def multiplicity_of_result(self):
        """
        The multiplicity of the result OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def property(self):
        """
        The end Property must be an Association memberEnd.

        .. ocl::
            end.association <> null
        """
        pass

    def type_of_object(self):
        """
        The type of the object InputPin is the AssociationClass that owns the end Property.

        .. ocl::
            object.type = end.association
        """
        pass

    def type_of_result(self):
        """
        The type of the result OutputPin is the same as the type of the end Property.

        .. ocl::
            result.type = end.type
        """
        pass

class Variable(models.Model):
    """
    A Variable is a ConnectableElement that may store values during the execution of an Activity. Reading and
    writing the values of a Variable provides an alternative means for passing data than the use of ObjectFlows.
    A Variable may be owned directly by an Activity, in which case it is accessible from anywhere within that
    activity, or it may be owned by a StructuredActivityNode, in which case it is only accessible within that
    node.
    """

    __package__ = 'UML.Activities'

    activity_scope = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity_scope', blank=True, null=True, 
                                       help_text='An Activity that owns the Variable.')
    connectable_element = models.OneToOneField('ConnectableElement', on_delete=models.CASCADE, primary_key=True)
    multiplicity_element = models.OneToOneField('MultiplicityElement')
    scope = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_scope', blank=True, null=True, 
                              help_text='A StructuredActivityNode that owns the Variable.')

    def is_accessible_by(self):
        """
        A Variable is accessible by Actions within its scope (the Activity or StructuredActivityNode that owns
        it).

        .. ocl::
            result = (if scope<>null then scope.allOwnedNodes()->includes(a)
            else a.containingActivity()=activityScope
            endif)
        """
        pass

class ClearAssociationAction(models.Model):
    """
    A ClearAssociationAction is an Action that destroys all links of an Association in which a particular object
    participates.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_association', null=True, 
                                    help_text='The Association to be cleared.')
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin that gives the object whose participation in the ' +
                               'Association is to be cleared.')

    def multiplicity(self):
        """
        The multiplicity of the object InputPin is 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def same_type(self):
        """
        The type of the InputPin must conform to the type of at least one of the memberEnds of the association.

        .. ocl::
            association.memberEnd->exists(self.object.type.conformsTo(type))
        """
        pass

class Trigger(models.Model):
    """
    A Trigger specifies a specific point  at which an Event occurrence may trigger an effect in a Behavior. A
    Trigger may be qualified by the Port on which the Event occurred.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.ForeignKey('Event', related_name='%(app_label)s_%(class)s_event', null=True, 
                              help_text='The Event that detected by the Trigger.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    port = models.ManyToManyField('Port', related_name='%(app_label)s_%(class)s_port', blank=True, 
                                  help_text='A optional Port of through which the given effect is detected.')

    def trigger_with_ports(self):
        """
        If a Trigger specifies one or more ports, the event of the Trigger must be a MessageEvent.

        .. ocl::
            port->notEmpty() implies event.oclIsKindOf(MessageEvent)
        """
        pass

class SequenceNode(models.Model):
    """
    A SequenceNode is a StructuredActivityNode that executes a sequence of ExecutableNodes in order.
    """

    __package__ = 'UML.Actions'

    executable_node = models.ManyToManyField('ExecutableNode', related_name='%(app_label)s_%(class)s_executable_node', blank=True, 
                                             help_text='The ordered set of ExecutableNodes to be sequenced.')
    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)

class ReadStructuralFeatureAction(models.Model):
    """
    A ReadStructuralFeatureAction is a StructuralFeatureAction that retrieves the values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the result values are placed.')
    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)

    def multiplicity(self):
        """
        The multiplicity of the StructuralFeature must be compatible with the multiplicity of the result
        OutputPin.

        .. ocl::
            structuralFeature.compatibleWith(result)
        """
        pass

    def type_and_ordering(self):
        """
        The type and ordering of the result OutputPin are the same as the type and ordering of the
        StructuralFeature.

        .. ocl::
            result.type =structuralFeature.type and 
            result.isOrdered = structuralFeature.isOrdered
        """
        pass

class MessageSort(models.Model):
    """
    This is an enumerated type that identifies the type of communication action that was used to generate the
    Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class Property(models.Model):
    """
    A Property is a StructuralFeature. A Property related by ownedAttribute to a Classifier (other than an
    association) represents an attribute and might also represent an association end. It relates an instance of
    the Classifier to a value or set of values of the type of the attribute. A Property related by memberEnd to
    an Association represents an end of the Association. The type of the Property is the type of the end of the
    Association. A Property has the capability of being a DeploymentTarget in a Deployment relationship. This
    enables modeling the deployment to hierarchical nodes that have Properties functioning as internal parts.
    Property specializes ParameterableElement to specify that a Property can be exposed as a formal template
    parameter, and provided as an actual parameter in a binding of a template.
    """

    __package__ = 'UML.Classification'

    aggregation = models.ForeignKey('AggregationKind', related_name='%(app_label)s_%(class)s_aggregation', null=True, default='none', 
                                    help_text='Specifies the kind of aggregation that applies to the Property.')
    association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_association', blank=True, null=True, 
                                    help_text='The Association of which this Property is a member, if any.')
    association_end = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_association_end', blank=True, null=True, 
                                        help_text='Designates the optional association end that owns a qualifier ' +
                                        'attribute.')
    connectable_element = models.OneToOneField('ConnectableElement', on_delete=models.CASCADE, primary_key=True)
    datatype = models.ForeignKey('DataType', related_name='%(app_label)s_%(class)s_datatype', blank=True, null=True, 
                                 help_text='The DataType that owns this Property, if any.')
    default_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_default_value', blank=True, null=True, 
                                      help_text='A ValueSpecification that is evaluated to give a default value ' +
                                      'for the Property when an instance of the owning Classifier is ' +
                                      'instantiated.')
    deployment_target = models.OneToOneField('DeploymentTarget')
    has_class = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_has_class', blank=True, null=True, 
                                  help_text='The Class that owns this Property, if any.')
    interface = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_interface', blank=True, null=True, 
                                  help_text='The Interface that owns this Property, if any.')
    is_composite = models.BooleanField(help_text='If isComposite is true, the object containing the attribute is ' +
                                       'a container for the object or value contained in the attribute. This is a ' +
                                       'derived value, indicating whether the aggregation of the Property is ' +
                                       'composite or not.')
    is_derived = models.BooleanField(help_text='Specifies whether the Property is derived, i.e., whether its ' +
                                     'value or values can be computed from other information.')
    is_derived_union = models.BooleanField(help_text='Specifies whether the property is derived as the union of ' +
                                           'all of the Properties that are constrained to subset it.')
    is_id = models.BooleanField(help_text='True indicates this property can be used to uniquely identify an ' +
                                'instance of the containing Class.')
    opposite = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_opposite', blank=True, null=True, 
                                 help_text='In the case where the Property is one end of a binary association ' +
                                 'this gives the other end.')
    owning_association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_owning_association', blank=True, null=True, 
                                           help_text='The owning association of this property, if any.')
    qualifier = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_qualifier', blank=True, 
                                       help_text='An optional list of ordered qualifier attributes for the end.')
    redefined_property = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_property', blank=True, 
                                                help_text='The properties that are redefined by this property, if ' +
                                                'any.')
    structural_feature = models.OneToOneField('StructuralFeature')
    subsetted_property = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_subsetted_property', blank=True, 
                                                help_text='The properties of which this Property is constrained ' +
                                                'to be a subset, if any.')

    def binding_to_attribute(self):
        """
        A binding of a PropertyTemplateParameter representing an attribute must be to an attribute.

        .. ocl::
            (self.isAttribute()
            and (templateParameterSubstitution->notEmpty())
            implies (templateParameterSubstitution->forAll(ts |
                ts.formal.oclIsKindOf(Property)
                and ts.formal.oclAsType(Property).isAttribute())))
        """
        pass

    def deployment_target(self):
        """
        A Property can be a DeploymentTarget if it is a kind of Node and functions as a part in the internal
        structure of an encompassing Node.

        .. ocl::
            deployment->notEmpty() implies owner.oclIsKindOf(Node) and Node.allInstances()->exists(n | n.part->exists(p | p = self))
        """
        pass

    def derived_union_is_derived(self):
        """
        A derived union is derived.

        .. ocl::
            isDerivedUnion implies isDerived
        """
        pass

    def derived_union_is_read_only(self):
        """
        A derived union is read only.

        .. ocl::
            isDerivedUnion implies isReadOnly
        """
        pass

    def is_attribute(self):
        """
        The query isAttribute() is true if the Property is defined as an attribute of some Classifier.

        .. ocl::
            result = (not classifier->isEmpty())
        """
        pass

    def is_compatible_with(self):
        """
        The query isCompatibleWith() determines if this Property is compatible with the specified
        ParameterableElement. This Property is compatible with ParameterableElement p if the kind of this
        Property is thesame as or a subtype of the kind of p. Further, if p is a TypedElement, then the type of
        this Property must be conformant with the type of p.

        .. ocl::
            result = (self.oclIsKindOf(p.oclType()) and (p.oclIsKindOf(TypeElement) implies
            self.type.conformsTo(p.oclAsType(TypedElement).type)))
        """
        pass

    def is_composite(self):
        """
        The value of isComposite is true only if aggregation is composite.

        .. ocl::
            result = (aggregation = AggregationKind::composite)
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two Properties in a context in which redefinition is
        possible, whether redefinition would be logically consistent. A redefining Property is consistent with a
        redefined Property if the type of the redefining Property conforms to the type of the redefined
        Property, and the multiplicity of the redefining Property (if specified) is contained in the
        multiplicity of the redefined Property.
        """
        pass

    def is_navigable(self):
        """
        The query isNavigable() indicates whether it is possible to navigate across the property.

        .. ocl::
            result = (not classifier->isEmpty() or association.navigableOwnedEnd->includes(self))
        """
        pass

    def multiplicity_of_composite(self):
        """
        A multiplicity on the composing end of a composite aggregation must not have an upper bound greater than
        1.

        .. ocl::
            isComposite and association <> null implies opposite.upperBound() <= 1
        """
        pass

    def get_opposite(self):
        """
        If this property is a memberEnd of a binary association, then opposite gives the other end.

        .. ocl::
            result = (if association <> null and association.memberEnd->size() = 2
            then
                association.memberEnd->any(e | e <> self)
            else
                null
            endif)
        """
        pass

    def qualified_is_association_end(self):
        """
        All qualified Properties must be Association ends

        .. ocl::
            qualifier->notEmpty() implies association->notEmpty()
        """
        pass

    def redefined_property_inherited(self):
        """
        A redefined Property must be inherited from a more general Classifier.

        .. ocl::
            (redefinedProperty->notEmpty()) implies
              (redefinitionContext->notEmpty() and
                  redefinedProperty->forAll(rp|
                    ((redefinitionContext->collect(fc|
                      fc.allParents()))->asSet())->collect(c| c.allFeatures())->asSet()->includes(rp)))
        """
        pass

    def subsetted_property_names(self):
        """
        A Property may not subset a Property with the same name.

        .. ocl::
            subsettedProperty->forAll(sp | sp.name <> name)
        """
        pass

    def subsetting_context(self):
        """
        The query subsettingContext() gives the context for subsetting a Property. It consists, in the case of
        an attribute, of the corresponding Classifier, and in the case of an association end, all of the
        Classifiers at the other ends.

        .. ocl::
            result = (if association <> null
            then association.memberEnd->excluding(self)->collect(type)->asSet()
            else 
              if classifier<>null
              then classifier->asSet()
              else Set{} 
              endif
            endif)
        """
        pass

    def subsetting_context_conforms(self):
        """
        Subsetting may only occur when the context of the subsetting property conforms to the context of the
        subsetted property.

        .. ocl::
            subsettedProperty->notEmpty() implies
              (subsettingContext()->notEmpty() and subsettingContext()->forAll (sc |
                subsettedProperty->forAll(sp |
                  sp.subsettingContext()->exists(c | sc.conformsTo(c)))))
        """
        pass

    def subsetting_rules(self):
        """
        A subsetting Property may strengthen the type of the subsetted Property, and its upper bound may be
        less.

        .. ocl::
            subsettedProperty->forAll(sp |
              self.type.conformsTo(sp.type) and
                ((self.upperBound()->notEmpty() and sp.upperBound()->notEmpty()) implies
                  self.upperBound() <= sp.upperBound() ))
        """
        pass

    def type_of_opposite_end(self):
        """
        If a Property is a classifier-owned end of a binary Association, its owner must be the type of the
        opposite end.

        .. ocl::
            (opposite->notEmpty() and owningAssociation->isEmpty()) implies classifier = opposite.type
        """
        pass

class UnmarshallAction(models.Model):
    """
    An UnmarshallAction is an Action that retrieves the values of the StructuralFeatures of an object and places
    them on OutputPins.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin that gives the object to be unmarshalled.')
    result = models.ManyToManyField('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                                    help_text='The OutputPins on which are placed the values of the ' +
                                    'StructuralFeatures of the input object.')
    unmarshall_type = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_unmarshall_type', null=True, 
                                        help_text='The type of the object to be unmarshalled.')

    def multiplicity_of_object(self):
        """
        The multiplicity of the object InputPin is 1..1

        .. ocl::
            object.is(1,1)
        """
        pass

    def number_of_result(self):
        """
        The number of result outputPins must be the same as the number of attributes of the unmarshallType.

        .. ocl::
            unmarshallType.allAttributes()->size() = result->size()
        """
        pass

    def object_type(self):
        """
        The type of the object InputPin conform to the unmarshallType.

        .. ocl::
            object.type.conformsTo(unmarshallType)
        """
        pass

    def structural_feature(self):
        """
        The unmarshallType must have at least one StructuralFeature.

        .. ocl::
            unmarshallType.allAttributes()->size() >= 1
        """
        pass

    def type_ordering_and_multiplicity(self):
        """
        The type, ordering and multiplicity of each attribute of the unmarshallType must be compatible with the
        type, ordering and multiplicity of the corresponding result OutputPin.

        .. ocl::
            let attribute:OrderedSet(Property) = unmarshallType.allAttributes() in
            Sequence{1..result->size()}->forAll(i | 
            	attribute->at(i).type.conformsTo(result->at(i).type) and
            	attribute->at(i).isOrdered=result->at(i).isOrdered and
            	attribute->at(i).compatibleWith(result->at(i)))
        """
        pass

class ExecutionSpecification(models.Model):
    """
    An ExecutionSpecification is a specification of the execution of a unit of Behavior or Action within the
    Lifeline. The duration of an ExecutionSpecification is represented by two OccurrenceSpecifications, the
    start OccurrenceSpecification and the finish OccurrenceSpecification.
    """

    __package__ = 'UML.Interactions'

    finish = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_finish', null=True, 
                               help_text='References the OccurrenceSpecification that designates the finish of ' +
                               'the Action or Behavior.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    start = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_start', null=True, 
                              help_text='References the OccurrenceSpecification that designates the start of the ' +
                              'Action or Behavior.')

    def same_lifeline(self):
        """
        The startEvent and the finishEvent must be on the same Lifeline.

        .. ocl::
            start.covered = finish.covered
        """
        pass

class ActionExecutionSpecification(models.Model):
    """
    An ActionExecutionSpecification is a kind of ExecutionSpecification representing the execution of an Action.
    """

    __package__ = 'UML.Interactions'

    action = models.ForeignKey('Action', related_name='%(app_label)s_%(class)s_action', null=True, 
                               help_text='Action whose execution is occurring.')
    execution_specification = models.OneToOneField('ExecutionSpecification', on_delete=models.CASCADE, primary_key=True)

    def action_referenced(self):
        """
        The Action referenced by the ActionExecutionSpecification must be owned by the Interaction owning that
        ActionExecutionSpecification.

        .. ocl::
            (enclosingInteraction->notEmpty() or enclosingOperand.combinedFragment->notEmpty()) and
            let parentInteraction : Set(Interaction) = enclosingInteraction.oclAsType(Interaction)->asSet()->union(
            enclosingOperand.combinedFragment->closure(enclosingOperand.combinedFragment)->
            collect(enclosingInteraction).oclAsType(Interaction)->asSet()) in
            (parentInteraction->size() = 1) and self.action.interaction->asSet() = parentInteraction
        """
        pass

class ProfileApplication(models.Model):
    """
    A profile application is used to show which profiles have been applied to a package.
    """

    __package__ = 'UML.Packages'

    applied_profile = models.ForeignKey('Profile', related_name='%(app_label)s_%(class)s_applied_profile', null=True, 
                                        help_text='References the Profiles that are applied to a Package through ' +
                                        'this ProfileApplication.')
    applying_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_applying_package', null=True, 
                                         help_text='The package that owns the profile application.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    is_strict = models.BooleanField(help_text='Specifies that the Profile filtering rules for the metaclasses of ' +
                                    'the referenced metamodel shall be strictly applied.')

class LinkEndData(models.Model):
    """
    LinkEndData is an Element that identifies on end of a link to be read or written by a LinkAction. As a link
    (that is not a link object) cannot be passed as a runtime value to or from an Action, it is instead
    identified by its end objects and qualifier values, if any. A LinkEndData instance provides these values for
    a single Association end.
    """

    __package__ = 'UML.Actions'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_end', null=True, 
                            help_text='The Association"end"for"which"this"LinkEndData"specifies"values.')
    qualifier = models.ManyToManyField('QualifierValue', related_name='%(app_label)s_%(class)s_qualifier', blank=True, 
                                       help_text='A set of QualifierValues used to provide values for the ' +
                                       'qualifiers of the end.')
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', blank=True, null=True, 
                              help_text='The InputPin that provides the specified value for the given end. This ' +
                              'InputPin is omitted if the LinkEndData specifies the "open" end for a ' +
                              'ReadLinkAction.')

    def all_pins(self):
        """
        Returns all the InputPins referenced by this LinkEndData. By default this includes the value and
        qualifier InputPins, but subclasses may override the operation to add other InputPins.

        .. ocl::
            result = (value->asBag()->union(qualifier.value))
        """
        pass

    def end_object_input_pin(self):
        """
        The value InputPin is not also the qualifier value InputPin.

        .. ocl::
            value->excludesAll(qualifier.value)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the value InputPin must be 1..1.

        .. ocl::
            value<>null implies value.is(1,1)
        """
        pass

    def property_is_association_end(self):
        """
        The Property must be an Association memberEnd.

        .. ocl::
            end.association <> null
        """
        pass

    def qualifiers(self):
        """
        The qualifiers must be qualifiers of the Association end.

        .. ocl::
            end.qualifier->includesAll(qualifier.qualifier)
        """
        pass

    def same_type(self):
        """
        The type of the value InputPin conforms to the type of the Association end.

        .. ocl::
            value<>null implies value.type.conformsTo(end.type)
        """
        pass

class LinkEndCreationData(models.Model):
    """
    LinkEndCreationData is LinkEndData used to provide values for one end of a link to be created by a
    CreateLinkAction.
    """

    __package__ = 'UML.Actions'

    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', blank=True, null=True, 
                                  help_text='For ordered Association ends, the InputPin that provides the ' +
                                  'position where the new link should be inserted or where an existing link should ' +
                                  'be moved to. The type of the insertAt InputPin is UnlimitedNatural, but the ' +
                                  'input cannot be zero. It is omitted for Association ends that are not ordered.')
    is_replace_all = models.BooleanField(help_text='Specifies whether the existing links emanating from the ' +
                                         'object on this end should be destroyed before creating a new link.')
    link_end_data = models.OneToOneField('LinkEndData', on_delete=models.CASCADE, primary_key=True)

    def all_pins(self):
        """
        Adds the insertAt InputPin (if any) to the set of all Pins.

        .. ocl::
            result = (self.LinkEndData::allPins()->including(insertAt))
        """
        pass

    def insert_at_pin(self):
        """
        LinkEndCreationData for ordered Association ends must have a single insertAt InputPin for the insertion
        point with type UnlimitedNatural and multiplicity of 1..1, if isReplaceAll=false, and must have no
        InputPin for the insertion point when the association ends are unordered.

        .. ocl::
            if  not end.isOrdered
            then insertAt = null
            else
            	not isReplaceAll=false implies
            	insertAt <> null and insertAt->forAll(type=UnlimitedNatural and is(1,1))
            endif
        """
        pass

class Connector(models.Model):
    """
    A Connector specifies links that enables communication between two or more instances. In contrast to
    Associations, which specify links between any instance of the associated Classifiers, Connectors specify
    links between instances playing the connected parts only.
    """

    __package__ = 'UML.StructuredClassifiers'

    contract = models.ManyToManyField('Behavior', related_name='%(app_label)s_%(class)s_contract', blank=True, 
                                      help_text='The set of Behaviors that specify the valid interaction patterns ' +
                                      'across the Connector.')
    end = models.ManyToManyField('ConnectorEnd', related_name='%(app_label)s_%(class)s_end', blank=True, 
                                 help_text='A Connector has at least two ConnectorEnds, each representing the ' +
                                 'participation of instances of the Classifiers typing the ConnectableElements ' +
                                 'attached to the end. The set of ConnectorEnds is ordered.')
    feature = models.OneToOneField('Feature', on_delete=models.CASCADE, primary_key=True)
    kind = models.ForeignKey('ConnectorKind', related_name='%(app_label)s_%(class)s_kind', null=True, 
                             help_text='Indicates the kind of Connector. This is derived: a Connector with one or ' +
                             'more ends connected to a Port which is not on a Part and which is not a behavior ' +
                             'port is a delegation; otherwise it is an assembly.')
    redefined_connector = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_connector', blank=True, 
                                                 help_text='A Connector may be redefined when its containing ' +
                                                 'Classifier is specialized. The redefining Connector may have a ' +
                                                 'type that specializes the type of the redefined Connector. The ' +
                                                 'types of the ConnectorEnds of the redefining Connector may ' +
                                                 'specialize the types of the ConnectorEnds of the redefined ' +
                                                 'Connector. The properties of the ConnectorEnds of the redefining ' +
                                                 'Connector may be replaced.')
    type = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_type', blank=True, null=True, 
                             help_text='An optional Association that classifies links corresponding to this ' +
                             'Connector.')

    def get_kind(self):
        """
        Derivation for Connector::/kind : ConnectorKind

        .. ocl::
            result = (if end->exists(
            		role.oclIsKindOf(Port) 
            		and partWithPort->isEmpty()
            		and not role.oclAsType(Port).isBehavior)
            then ConnectorKind::delegation 
            else ConnectorKind::assembly 
            endif)
        """
        pass

    def roles(self):
        """
        The ConnectableElements attached as roles to each ConnectorEnd owned by a Connector must be owned or
        inherited roles of the Classifier that owned the Connector, or they must be Ports of such roles.

        .. ocl::
            structuredClassifier <> null
            and
              end->forAll( e | structuredClassifier.allRoles()->includes(e.role)
            or
              e.role.oclIsKindOf(Port) and structuredClassifier.allRoles()->includes(e.partWithPort))
        """
        pass

    def types(self):
        """
        The types of the ConnectableElements that the ends of a Connector are attached to must conform to the
        types of the ends of the Association that types the Connector, if any.

        .. ocl::
            type<>null implies 
              let noOfEnds : Integer = end->size() in 
              (type.memberEnd->size() = noOfEnds) and Sequence{1..noOfEnds}->forAll(i | end->at(i).role.type.conformsTo(type.memberEnd->at(i).type))
        """
        pass

class Reception(models.Model):
    """
    A Reception is a declaration stating that a Classifier is prepared to react to the receipt of a Signal.
    """

    __package__ = 'UML.SimpleClassifiers'

    behavioral_feature = models.OneToOneField('BehavioralFeature', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal', null=True, 
                               help_text='The Signal that this Reception handles.')

    def same_name_as_signal(self):
        """
        A Reception has the same name as its signal

        .. ocl::
            name = signal.name
        """
        pass

    def same_structure_as_signal(self):
        """
        A Reception's parameters match the ownedAttributes of its signal by name, type, and multiplicity

        .. ocl::
            signal.ownedAttribute->size() = ownedParameter->size() and
            Sequence{1..signal.ownedAttribute->size()}->forAll( i | 
                ownedParameter->at(i).direction = ParameterDirectionKind::_'in' and 
                ownedParameter->at(i).name = signal.ownedAttribute->at(i).name and
                ownedParameter->at(i).type = signal.ownedAttribute->at(i).type and
                ownedParameter->at(i).lowerBound() = signal.ownedAttribute->at(i).lowerBound() and
                ownedParameter->at(i).upperBound() = signal.ownedAttribute->at(i).upperBound()
            )
        """
        pass

class SignalEvent(models.Model):
    """
    A SignalEvent represents the receipt of an asynchronous Signal instance.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal', null=True, 
                               help_text='The specific Signal that is associated with this SignalEvent.')

class Comment(models.Model):
    """
    A Comment is a textual annotation that can be attached to a set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    annotated_element = models.ManyToManyField('Element', related_name='%(app_label)s_%(class)s_annotated_element', blank=True, 
                                               help_text='References the Element(s) being commented.')
    body = models.CharField(max_length=255, blank=True, null=True, 
                            help_text='Specifies a string that is the comment.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)

class MessageEnd(models.Model):
    """
    MessageEnd is an abstract specialization of NamedElement that represents what can occur at the end of a
    Message.
    """

    __package__ = 'UML.Interactions'

    message = models.ForeignKey('Message', related_name='%(app_label)s_%(class)s_message', blank=True, null=True, 
                                help_text='References a Message.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

    def enclosing_fragment(self):
        """
        This query returns a set including the enclosing InteractionFragment this MessageEnd is enclosed within.

        .. ocl::
            result = (if self->select(oclIsKindOf(Gate))->notEmpty() 
            then -- it is a Gate
            let endGate : Gate = 
              self->select(oclIsKindOf(Gate)).oclAsType(Gate)->asOrderedSet()->first()
              in
              if endGate.isOutsideCF() 
              then endGate.combinedFragment.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(endGate.combinedFragment.enclosingOperand.oclAsType(InteractionFragment)->asSet())
              else if endGate.isInsideCF() 
                then endGate.combinedFragment.oclAsType(InteractionFragment)->asSet()
                else if endGate.isFormal() 
                  then endGate.interaction.oclAsType(InteractionFragment)->asSet()
                  else if endGate.isActual() 
                    then endGate.interactionUse.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(endGate.interactionUse.enclosingOperand.oclAsType(InteractionFragment)->asSet())
                    else null
                    endif
                  endif
                endif
              endif
            else -- it is a MessageOccurrenceSpecification
            let endMOS : MessageOccurrenceSpecification  = 
              self->select(oclIsKindOf(MessageOccurrenceSpecification)).oclAsType(MessageOccurrenceSpecification)->asOrderedSet()->first() 
              in
              if endMOS.enclosingInteraction->notEmpty() 
              then endMOS.enclosingInteraction.oclAsType(InteractionFragment)->asSet()
              else endMOS.enclosingOperand.oclAsType(InteractionFragment)->asSet()
              endif
            endif)
        """
        pass

    def is_receive(self):
        """
        This query returns value true if this MessageEnd is a receiveEvent.
        """
        pass

    def is_send(self):
        """
        This query returns value true if this MessageEnd is a sendEvent.
        """
        pass

    def opposite_end(self):
        """
        This query returns a set including the MessageEnd (if exists) at the opposite end of the Message for
        this MessageEnd.
        """
        pass

class ExpansionKind(models.Model):
    """
    ExpansionKind is an enumeration type used to specify how an ExpansionRegion executes its contents.
    """

    __package__ = 'UML.Actions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class StartObjectBehaviorAction(models.Model):
    """
    A StartObjectBehaviorAction is an InvocationAction that starts the execution either of a directly
    instantiated Behavior or of the classifierBehavior of an object. Argument values may be supplied for the
    input Parameters of the Behavior. If the Behavior is invoked synchronously, then output values may be
    obtained for output Parameters.
    """

    __package__ = 'UML.Actions'

    call_action = models.OneToOneField('CallAction', on_delete=models.CASCADE, primary_key=True)
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='An InputPin that holds the object that is either a Behavior to be ' +
                               'started or has a classifierBehavior to be started.')

    def behavior(self):
        """
        If the type of the object InputPin is a Behavior, then that Behavior. Otherwise, if the type of the
        object InputPin is a BehavioredClassifier, then the classifierBehavior of that BehavioredClassifier.

        .. ocl::
            result = (if object.type.oclIsKindOf(Behavior) then
              object.type.oclAsType(Behavior)
            else if object.type.oclIsKindOf(BehavioredClassifier) then
              object.type.oclAsType(BehavioredClassifier).classifierBehavior
            else
              null
            endif
            endif)
        """
        pass

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior being called.

        .. ocl::
            result = (self.behavior().inputParameters())
        """
        pass

    def multiplicity_of_object(self):
        """
        The multiplicity of the object InputPin must be 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def no_onport(self):
        """
        A StartObjectBehaviorAction may not specify onPort.

        .. ocl::
            onPort->isEmpty()
        """
        pass

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior being called.

        .. ocl::
            result = (self.behavior().outputParameters())
        """
        pass

    def type_of_object(self):
        """
        The type of the object InputPin must be either a Behavior or a BehavioredClassifier with a
        classifierBehavior.

        .. ocl::
            self.behavior()<>null
        """
        pass

class InformationFlow(models.Model):
    """
    InformationFlows describe circulation of information through a system in a general manner. They do not
    specify the nature of the information, mechanisms by which it is conveyed, sequences of exchange or any
    control conditions. During more detailed modeling, representation and realization links may be added to
    specify which model elements implement an InformationFlow and to show how information is conveyed.
    InformationFlows require some kind of 'information channel' for unidirectional transmission of information
    items from sources to targets.' They specify the information channel's realizations, if any, and identify
    the information that flows along them.' Information moving along the information channel may be represented
    by abstract InformationItems and by concrete Classifiers.
    """

    __package__ = 'UML.InformationFlows'

    conveyed = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_conveyed', 
                                      help_text='Specifies the information items that may circulate on this ' +
                                      'information flow.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    information_source = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_information_source', 
                                                help_text='Defines from which source the conveyed ' +
                                                'InformationItems are initiated.')
    information_target = models.ManyToManyField('NamedElement', related_name='%(app_label)s_%(class)s_information_target', 
                                                help_text='Defines to which target the conveyed InformationItems ' +
                                                'are directed.')
    packageable_element = models.OneToOneField('PackageableElement')
    realization = models.ManyToManyField('Relationship', related_name='%(app_label)s_%(class)s_realization', blank=True, 
                                         help_text='Determines which Relationship will realize the specified ' +
                                         'flow.')
    realizing_activity_edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_realizing_activity_edge', blank=True, 
                                                     help_text='Determines which ActivityEdges will realize the ' +
                                                     'specified flow.')
    realizing_connector = models.ManyToManyField('Connector', related_name='%(app_label)s_%(class)s_realizing_connector', blank=True, 
                                                 help_text='Determines which Connectors will realize the ' +
                                                 'specified flow.')
    realizing_message = models.ManyToManyField('Message', related_name='%(app_label)s_%(class)s_realizing_message', blank=True, 
                                               help_text='Determines which Messages will realize the specified ' +
                                               'flow.')

    def convey_classifiers(self):
        """
        An information flow can only convey classifiers that are allowed to represent an information item.

        .. ocl::
            self.conveyed->forAll(oclIsKindOf(Class) or oclIsKindOf(Interface)
              or oclIsKindOf(InformationItem) or oclIsKindOf(Signal) or oclIsKindOf(Component))
        """
        pass

    def must_conform(self):
        """
        The sources and targets of the information flow must conform to the sources and targets or conversely
        the targets and sources of the realization relationships.
        """
        pass

    def sources_and_targets_kind(self):
        """
        The sources and targets of the information flow can only be one of the following kind: Actor, Node,
        UseCase, Artifact, Class, Component, Port, Property, Interface, Package, ActivityNode,
        ActivityPartition,  Behavior and InstanceSpecification except when its classifier is a relationship
        (i.e. it represents a link).

        .. ocl::
            (self.informationSource->forAll( sis |
              oclIsKindOf(Actor) or oclIsKindOf(Node) or oclIsKindOf(UseCase) or oclIsKindOf(Artifact) or 
              oclIsKindOf(Class) or oclIsKindOf(Component) or oclIsKindOf(Port) or oclIsKindOf(Property) or 
              oclIsKindOf(Interface) or oclIsKindOf(Package) or oclIsKindOf(ActivityNode) or oclIsKindOf(ActivityPartition) or 
              (oclIsKindOf(InstanceSpecification) and not sis.oclAsType(InstanceSpecification).classifier->exists(oclIsKindOf(Relationship))))) 
            
            and
            
            (self.informationTarget->forAll( sit | 
              oclIsKindOf(Actor) or oclIsKindOf(Node) or oclIsKindOf(UseCase) or oclIsKindOf(Artifact) or 
              oclIsKindOf(Class) or oclIsKindOf(Component) or oclIsKindOf(Port) or oclIsKindOf(Property) or 
              oclIsKindOf(Interface) or oclIsKindOf(Package) or oclIsKindOf(ActivityNode) or oclIsKindOf(ActivityPartition) or 
            (oclIsKindOf(InstanceSpecification) and not sit.oclAsType(InstanceSpecification).classifier->exists(oclIsKindOf(Relationship)))))
        """
        pass

class InformationItem(models.Model):
    """
    InformationItems represent many kinds of information that can flow from sources to targets in very abstract
    ways.' They represent the kinds of information that may move within a system, but do not elaborate details
    of the transferred information.' Details of transferred information are the province of other Classifiers
    that may ultimately define InformationItems.' Consequently, InformationItems cannot be instantiated and do
    not themselves have features, generalizations, or associations.'An important use of InformationItems is to
    represent information during early design stages, possibly before the detailed modeling decisions that will
    ultimately define them have been made. Another purpose of InformationItems is to abstract portions of
    complex models in less precise, but perhaps more general and communicable, ways.
    """

    __package__ = 'UML.InformationFlows'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    represented = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_represented', blank=True, 
                                         help_text='Determines the classifiers that will specify the structure ' +
                                         'and nature of the information. An information item represents all its ' +
                                         'represented classifiers.')

    def has_no(self):
        """
        An informationItem has no feature, no generalization, and no associations.

        .. ocl::
            self.generalization->isEmpty() and self.feature->isEmpty()
        """
        pass

    def not_instantiable(self):
        """
        It is not instantiable.

        .. ocl::
            isAbstract
        """
        pass

    def sources_and_targets(self):
        """
        The sources and targets of an information item (its related information flows) must designate subsets of
        the sources and targets of the representation information item, if any. The Classifiers that can realize
        an information item can only be of the following kind: Class, Interface, InformationItem, Signal,
        Component.

        .. ocl::
            (self.represented->select(oclIsKindOf(InformationItem))->forAll(p |
              p.conveyingFlow.source->forAll(q | self.conveyingFlow.source->includes(q)) and
                p.conveyingFlow.target->forAll(q | self.conveyingFlow.target->includes(q)))) and
                  (self.represented->forAll(oclIsKindOf(Class) or oclIsKindOf(Interface) or
                    oclIsKindOf(InformationItem) or oclIsKindOf(Signal) or oclIsKindOf(Component)))
        """
        pass

class Model(models.Model):
    """
    A model captures a view of a physical system. It is an abstraction of the physical system, with a certain
    purpose. This purpose determines what is to be included in the model and what is irrelevant. Thus the model
    completely describes those aspects of the physical system that are relevant to the purpose of the model, at
    the appropriate level of detail.
    """

    __package__ = 'UML.Packages'

    package = models.OneToOneField('Package', on_delete=models.CASCADE, primary_key=True)
    viewpoint = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text='The name of the viewpoint that is expressed by a model (this name may ' +
                                 'refer to a profile definition).')

class Region(models.Model):
    """
    A Region is a top-level part of a StateMachine or a composite State, that serves as a container for the
    Vertices and Transitions of the StateMachine. A StateMachine or composite State may contain multiple Regions
    representing behaviors that may occur in parallel.
    """

    __package__ = 'UML.StateMachines'

    extended_region = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_extended_region', blank=True, null=True, 
                                        help_text='The region of which this region is an extension.')
    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    redefinable_element = models.OneToOneField('RedefinableElement')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', null=True, 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    state_machine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_state_machine', blank=True, null=True, 
                                      help_text='The StateMachine that owns the Region. If a Region is owned by a ' +
                                      'StateMachine, then it cannot also be owned by a State.')
    subvertex = models.ManyToManyField('Vertex', related_name='%(app_label)s_%(class)s_subvertex', blank=True, 
                                       help_text='The set of Vertices that are owned by this Region.')
    transition = models.ManyToManyField('Transition', related_name='%(app_label)s_%(class)s_transition', blank=True, 
                                        help_text='The set of Transitions owned by the Region.')

    def belongs_to_psm(self):
        """
        The operation belongsToPSM () checks if the Region belongs to a ProtocolStateMachine.

        .. ocl::
            result = (if  stateMachine <> null 
            then
              stateMachine.oclIsKindOf(ProtocolStateMachine)
            else 
              state <> null  implies  state.container.belongsToPSM()
            endif )
        """
        pass

    def containing_state_machine(self):
        """
        The operation containingStateMachine() returns the StateMachine in which this Region is defined.

        .. ocl::
            result = (if stateMachine = null 
            then
              state.containingStateMachine()
            else
              stateMachine
            endif)
        """
        pass

    def deep_history_vertex(self):
        """
        A Region can have at most one deep history Vertex.

        .. ocl::
            self.subvertex->select (oclIsKindOf(Pseudostate))->collect(oclAsType(Pseudostate))->
               select(kind = PseudostateKind::deepHistory)->size() <= 1
        """
        pass

    def initial_vertex(self):
        """
        A Region can have at most one initial Vertex.

        .. ocl::
            self.subvertex->select (oclIsKindOf(Pseudostate))->collect(oclAsType(Pseudostate))->
              select(kind = PseudostateKind::initial)->size() <= 1
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies that a redefining Region is consistent with a redefined Region
        provided that the redefining Region is an extension of the Redefined region, i.e., its Vertices and
        Transitions conform to one of the following: (1) they are equal to corresponding elements of the
        redefined Region or, (2) they consistently redefine a State or Transition of the redefined region, or
        (3) they add new States or Transitions.
        """
        pass

    def is_redefinition_context_valid(self):
        """
        The query isRedefinitionContextValid() specifies whether the redefinition contexts of a Region are
        properly related to the redefinition contexts of the specified Region to allow this element to redefine
        the other. The containing StateMachine or State of a redefining Region must Redefine the containing
        StateMachine or State of the redefined Region.

        .. ocl::
            result = (if redefinedElement.oclIsKindOf(Region) then
              let redefinedRegion : Region = redefinedElement.oclAsType(Region) in
                if stateMachine->isEmpty() then
                -- the Region is owned by a State
                  (state.redefinedState->notEmpty() and state.redefinedState.region->includes(redefinedRegion))
                else -- the region is owned by a StateMachine
                  (stateMachine.extendedStateMachine->notEmpty() and
                    stateMachine.extendedStateMachine->exists(sm : StateMachine |
                      sm.region->includes(redefinedRegion)))
                endif
            else
              false
            endif)
        """
        pass

    def owned(self):
        """
        If a Region is owned by a StateMachine, then it cannot also be owned by a State and vice versa.

        .. ocl::
            (stateMachine <> null implies state = null) and (state <> null implies stateMachine = null)
        """
        pass

    def redefinition_context(self):
        """
        The redefinition context of a Region is the nearest containing StateMachine.

        .. ocl::
            result = (let sm : StateMachine = containingStateMachine() in
            if sm._'context' = null or sm.general->notEmpty() then
              sm
            else
              sm._'context'
            endif)
        """
        pass

    def shallow_history_vertex(self):
        """
        A Region can have at most one shallow history Vertex.

        .. ocl::
            subvertex->select(oclIsKindOf(Pseudostate))->collect(oclAsType(Pseudostate))->
              select(kind = PseudostateKind::shallowHistory)->size() <= 1
        """
        pass

class DurationObservation(models.Model):
    """
    A DurationObservation is a reference to a duration during an execution. It points out the NamedElement(s) in
    the model to observe and whether the observations are when this NamedElement is entered or when it is
    exited.
    """

    __package__ = 'UML.Values'

    event = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_event', null=True, 
                              help_text='The DurationObservation is determined as the duration between the ' +
                              'entering or exiting of a single event Element during execution, or the ' +
                              'entering/exiting of one event Element and the entering/exiting of a second.')
    first_event = models.BooleanField(blank=True, 
                                      help_text='The value of firstEvent[i] is related to event[i] (where i is 1 ' +
                                      'or 2). If firstEvent[i] is true, then the corresponding observation event ' +
                                      'is the first time instant the execution enters event[i]. If firstEvent[i] ' +
                                      'is false, then the corresponding observation event is the time instant the ' +
                                      'execution exits event[i].')
    observation = models.OneToOneField('Observation', on_delete=models.CASCADE, primary_key=True)

    def first_event_multiplicity(self):
        """
        The multiplicity of firstEvent must be 2 if the multiplicity of event is 2. Otherwise the multiplicity
        of firstEvent is 0.

        .. ocl::
            if (event->size() = 2)
              then (firstEvent->size() = 2) else (firstEvent->size() = 0)
            endif
        """
        pass

class OpaqueExpression(models.Model):
    """
    An OpaqueExpression is a ValueSpecification that specifies the computation of a collection of values either
    in terms of a UML Behavior or based on a textual statement in a language other than UML
    """

    __package__ = 'UML.Values'

    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior', blank=True, null=True, 
                                 help_text='Specifies the behavior of the OpaqueExpression as a UML Behavior.')
    body = models.CharField(max_length=255, blank=True, null=True, 
                            help_text='A textual definition of the behavior of the OpaqueExpression, possibly in ' +
                            'multiple languages.')
    language = models.CharField(max_length=255, blank=True, null=True, 
                                help_text='Specifies the languages used to express the textual bodies of the ' +
                                'OpaqueExpression.  Languages are matched to body Strings by order. The ' +
                                'interpretation of the body depends on the languages. If the languages are ' +
                                'unspecified, they may be implicit from the expression body or the context.')
    result = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_result', blank=True, null=True, 
                               help_text='If an OpaqueExpression is specified using a UML Behavior, then this ' +
                               'refers to the single required return Parameter of that Behavior. When the Behavior ' +
                               'completes execution, the values on this Parameter give the result of evaluating ' +
                               'the OpaqueExpression.')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

    def is_integral(self):
        """
        The query isIntegral() tells whether an expression is intended to produce an Integer.

        .. ocl::
            result = (false)
        """
        pass

    def is_non_negative(self):
        """
        The query isNonNegative() tells whether an integer expression has a non-negative value.
        """
        pass

    def is_positive(self):
        """
        The query isPositive() tells whether an integer expression has a positive value.
        """
        pass

    def language_body_size(self):
        """
        If the language attribute is not empty, then the size of the body and language arrays must be the same.

        .. ocl::
            language->notEmpty() implies (_'body'->size() = language->size())
        """
        pass

    def one_return_result_parameter(self):
        """
        The behavior must have exactly one return result parameter.

        .. ocl::
            behavior <> null implies
               behavior.ownedParameter->select(direction=ParameterDirectionKind::return)->size() = 1
        """
        pass

    def only_return_result_parameters(self):
        """
        The behavior may only have return result parameters.

        .. ocl::
            behavior <> null implies behavior.ownedParameter->select(direction<>ParameterDirectionKind::return)->isEmpty()
        """
        pass

    def get_result(self):
        """
        Derivation for OpaqueExpression::/result

        .. ocl::
            result = (if behavior = null then
            	null
            else
            	behavior.ownedParameter->first()
            endif)
        """
        pass

    def value(self):
        """
        The query value() gives an integer value for an expression intended to produce one.
        """
        pass

class DestroyObjectAction(models.Model):
    """
    A DestroyObjectAction is an Action that destroys objects.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    is_destroy_links = models.BooleanField(help_text='Specifies whether links in which the object participates ' +
                                           'are destroyed along with the object.')
    is_destroy_owned_objects = models.BooleanField(help_text='Specifies whether objects owned by the object (via ' +
                                                   'composition) are destroyed along with the object.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='The InputPin providing the object to be destroyed.')

    def multiplicity(self):
        """
        The multiplicity of the targe IinputPin is 1..1.

        .. ocl::
            target.is(1,1)
        """
        pass

    def no_type(self):
        """
        The target InputPin has no type.

        .. ocl::
            target.type= null
        """
        pass

class Profile(models.Model):
    """
    A profile defines limited extensions to a reference metamodel with the purpose of adapting the metamodel to
    a specific platform or domain.
    """

    __package__ = 'UML.Packages'

    metaclass_reference = models.ManyToManyField('ElementImport', related_name='%(app_label)s_%(class)s_metaclass_reference', blank=True, 
                                                 help_text='References a metaclass that may be extended.')
    metamodel_reference = models.ManyToManyField('PackageImport', related_name='%(app_label)s_%(class)s_metamodel_reference', blank=True, 
                                                 help_text='References a package containing (directly or ' +
                                                 'indirectly) metaclasses that may be extended.')
    package = models.OneToOneField('Package', on_delete=models.CASCADE, primary_key=True)

    def metaclass_reference_not_specialized(self):
        """
        An element imported as a metaclassReference is not specialized or generalized in a Profile.

        .. ocl::
            metaclassReference.importedElement->
            	select(c | c.oclIsKindOf(Classifier) and
            		(c.oclAsType(Classifier).allParents()->collect(namespace)->includes(self)))->isEmpty()
            and 
            packagedElement->
                select(oclIsKindOf(Classifier))->collect(oclAsType(Classifier).allParents())->
                   intersection(metaclassReference.importedElement->select(oclIsKindOf(Classifier))->collect(oclAsType(Classifier)))->isEmpty()
        """
        pass

    def references_same_metamodel(self):
        """
        All elements imported either as metaclassReferences or through metamodelReferences are members of the
        same base reference metamodel.

        .. ocl::
            metamodelReference.importedPackage.elementImport.importedElement.allOwningPackages()->
              union(metaclassReference.importedElement.allOwningPackages() )->notEmpty()
        """
        pass

class ReduceAction(models.Model):
    """
    A ReduceAction is an Action that reduces a collection to a single value by repeatedly combining the elements
    of the collection using a reducer Behavior.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    collection = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_collection', null=True, 
                                   help_text='The InputPin that provides the collection to be reduced.')
    is_ordered = models.BooleanField(help_text='Indicates whether the order of the input collection should ' +
                                     'determine the order in which the reducer Behavior is applied to its ' +
                                     'elements.')
    reducer = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_reducer', null=True, 
                                help_text='A Behavior that is repreatedly applied to two elements of the input ' +
                                'collection to produce a value that is of the same type as elements of the ' +
                                'collection.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The output pin on which the result value is placed.')

    def input_type_is_collection(self):
        """
        The type of the collection InputPin must be a collection.
        """
        pass

    def output_types_are_compatible(self):
        """
        The type of the output of the reducer Behavior must conform to the type of the result OutputPin.

        .. ocl::
            reducer.outputParameters().type->forAll(conformsTo(result.type))
        """
        pass

    def reducer_inputs_output(self):
        """
        The reducer Behavior must have two input ownedParameters and one output ownedParameter, where the type
        of the output Parameter and the type of elements of the input collection conform to the types of the
        input Parameters.

        .. ocl::
            let inputs: OrderedSet(Parameter) = reducer.inputParameters() in
            let outputs: OrderedSet(Parameter) = reducer.outputParameters() in
            inputs->size()=2 and outputs->size()=1 and
            inputs.type->forAll(t | 
            	outputs.type->forAll(conformsTo(t)) and 
            	-- Note that the following only checks the case when the collection is via multiple tokens.
            	collection.upperBound()>1 implies collection.type.conformsTo(t))
        """
        pass

class ConnectorKind(models.Model):
    """
    ConnectorKind is an enumeration that defines whether a Connector is an assembly or a delegation.
    """

    __package__ = 'UML.StructuredClassifiers'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class ConnectorEnd(models.Model):
    """
    A ConnectorEnd is an endpoint of a Connector, which attaches the Connector to a ConnectableElement.
    """

    __package__ = 'UML.StructuredClassifiers'

    defining_end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_defining_end', blank=True, null=True, 
                                     help_text='A derived property referencing the corresponding end on the ' +
                                     'Association which types the Connector owing this ConnectorEnd, if any. It is ' +
                                     'derived by selecting the end at the same place in the ordering of ' +
                                     'Association ends as this ConnectorEnd.')
    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    part_with_port = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_part_with_port', blank=True, null=True, 
                                       help_text='Indicates the role of the internal structure of a Classifier ' +
                                       'with the Port to which the ConnectorEnd is attached.')
    role = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_role', null=True, 
                             help_text='The ConnectableElement attached at this ConnectorEnd. When an instance of ' +
                             'the containing Classifier is created, a link may (depending on the multiplicities) ' +
                             'be created to an instance of the Classifier that types this ConnectableElement.')

    def defining_end(self):
        """
        Derivation for ConnectorEnd::/definingEnd : Property

        .. ocl::
            result = (if connector.type = null 
            then
              null 
            else
              let index : Integer = connector.end->indexOf(self) in
                connector.type.memberEnd->at(index)
            endif)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the ConnectorEnd may not be more general than the multiplicity of the corresponding
        end of the Association typing the owning Connector, if any.

        .. ocl::
            self.compatibleWith(definingEnd)
        """
        pass

    def part_with_port_empty(self):
        """
        If a ConnectorEnd is attached to a Port of the containing Classifier, partWithPort will be empty.

        .. ocl::
            (role.oclIsKindOf(Port) and role.owner = connector.owner) implies partWithPort->isEmpty()
        """
        pass

    def role_and_part_with_port(self):
        """
        If a ConnectorEnd references a partWithPort, then the role must be a Port that is defined or inherited
        by the type of the partWithPort.

        .. ocl::
            partWithPort->notEmpty() implies 
              (role.oclIsKindOf(Port) and partWithPort.type.oclAsType(Namespace).member->includes(role))
        """
        pass

    def self_part_with_port(self):
        """
        The Property held in self.partWithPort must not be a Port.

        .. ocl::
            partWithPort->notEmpty() implies not partWithPort.oclIsKindOf(Port)
        """
        pass

class LinkEndDestructionData(models.Model):
    """
    LinkEndDestructionData is LinkEndData used to provide values for one end of a link to be destroyed by a
    DestroyLinkAction.
    """

    __package__ = 'UML.Actions'

    destroy_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_destroy_at', blank=True, null=True, 
                                   help_text='The InputPin that provides the position of an existing link to be ' +
                                   'destroyed in an ordered, nonunique Association end. The type of the destroyAt ' +
                                   'InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.')
    is_destroy_duplicates = models.BooleanField(help_text='Specifies whether to destroy duplicates of the value ' +
                                                'in nonunique Association ends.')
    link_end_data = models.OneToOneField('LinkEndData', on_delete=models.CASCADE, primary_key=True)

    def all_pins(self):
        """
        Adds the destroyAt InputPin (if any) to the set of all Pins.

        .. ocl::
            result = (self.LinkEndData::allPins()->including(destroyAt))
        """
        pass

    def destroy_at_pin(self):
        """
        LinkEndDestructionData for ordered, nonunique Association ends must have a single destroyAt InputPin if
        isDestroyDuplicates is false, which must be of type UnlimitedNatural and have a multiplicity of 1..1.
        Otherwise, the action has no destroyAt input pin.

        .. ocl::
            if  not end.isOrdered or end.isUnique or isDestroyDuplicates
            then destroyAt = null
            else
            	destroyAt <> null and 
            	destroyAt->forAll(type=UnlimitedNatural and is(1,1))
            endif
        """
        pass

class Transition(models.Model):
    """
    A Transition represents an arc between exactly one source Vertex and exactly one Target vertex (the source
    and targets may be the same Vertex). It may form part of a compound transition, which takes the StateMachine
    from one steady State configuration to another, representing the full response of the StateMachine to an
    occurrence of an Event that triggered it.
    """

    __package__ = 'UML.StateMachines'

    container = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_container', null=True, 
                                  help_text='Designates the Region that owns this Transition.')
    effect = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_effect', blank=True, null=True, 
                               help_text='Specifies an optional behavior to be performed when the Transition ' +
                               'fires.')
    guard = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_guard', blank=True, null=True, 
                              help_text='A guard is a Constraint that provides a fine-grained control over the ' +
                              'firing of the Transition. The guard is evaluated when an Event occurrence is ' +
                              'dispatched by the StateMachine. If the guard is true at that time, the Transition ' +
                              'may be enabled, otherwise, it is disabled. Guards should be pure expressions ' +
                              'without side effects. Guard expressions with side effects are ill formed.')
    kind = models.ForeignKey('TransitionKind', related_name='%(app_label)s_%(class)s_kind', null=True, default='external', 
                             help_text='Indicates the precise type of the Transition.')
    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    redefinable_element = models.OneToOneField('RedefinableElement')
    redefined_transition = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_transition', blank=True, null=True, 
                                             help_text='The Transition that is redefined by this Transition.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', null=True, 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    source = models.ForeignKey('Vertex', related_name='%(app_label)s_%(class)s_source', null=True, 
                               help_text='Designates the originating Vertex (State or Pseudostate) of the ' +
                               'Transition.')
    target = models.ForeignKey('Vertex', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='Designates the target Vertex that is reached when the Transition is ' +
                               'taken.')
    trigger = models.ManyToManyField('Trigger', related_name='%(app_label)s_%(class)s_trigger', blank=True, 
                                     help_text='Specifies the Triggers that may fire the transition.')

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the Transition either directly
        or transitively.

        .. ocl::
            result = (container.containingStateMachine())
        """
        pass

    def fork_segment_guards(self):
        """
        A fork segment must not have Guards or Triggers.

        .. ocl::
            (source.oclIsKindOf(Pseudostate) and source.oclAsType(Pseudostate).kind = PseudostateKind::fork) implies (guard = null and trigger->isEmpty())
        """
        pass

    def fork_segment_state(self):
        """
        A fork segment must always target a State.

        .. ocl::
            (source.oclIsKindOf(Pseudostate) and  source.oclAsType(Pseudostate).kind = PseudostateKind::fork) implies (target.oclIsKindOf(State))
        """
        pass

    def initial_transition(self):
        """
        An initial Transition at the topmost level Region of a StateMachine that has no Trigger.

        .. ocl::
            (source.oclIsKindOf(Pseudostate) and container.stateMachine->notEmpty()) implies
            	trigger->isEmpty()
        """
        pass

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies that a redefining Transition is consistent with a redefined
        Transition provided that the redefining Transition has the following relation to the redefined
        Transition: A redefining Transition redefines all properties of the corresponding redefined Transition
        except the source State and the Trigger.
        """
        pass

    def join_segment_guards(self):
        """
        A join segment must not have Guards or Triggers.

        .. ocl::
            (target.oclIsKindOf(Pseudostate) and target.oclAsType(Pseudostate).kind = PseudostateKind::join) implies (guard = null and trigger->isEmpty())
        """
        pass

    def join_segment_state(self):
        """
        A join segment must always originate from a State.

        .. ocl::
            (target.oclIsKindOf(Pseudostate) and target.oclAsType(Pseudostate).kind = PseudostateKind::join) implies (source.oclIsKindOf(State))
        """
        pass

    def outgoing_pseudostates(self):
        """
        Transitions outgoing Pseudostates may not have a Trigger.

        .. ocl::
            source.oclIsKindOf(Pseudostate) and (source.oclAsType(Pseudostate).kind <> PseudostateKind::initial) implies trigger->isEmpty()
        """
        pass

    def redefinition_context(self):
        """
        The redefinition context of a Transition is the nearest containing StateMachine.

        .. ocl::
            result = (let sm : StateMachine = containingStateMachine() in
            if sm._'context' = null or sm.general->notEmpty() then
              sm
            else
              sm._'context'
            endif)
        """
        pass

    def state_is_external(self):
        """
        A Transition with kind external can source any Vertex except entry points.

        .. ocl::
            (kind = TransitionKind::external) implies
            	not (source.oclIsKindOf(Pseudostate) and source.oclAsType(Pseudostate).kind = PseudostateKind::entryPoint)
        """
        pass

    def state_is_internal(self):
        """
        A Transition with kind internal must have a State as its source, and its source and target must be
        equal.

        .. ocl::
            (kind = TransitionKind::internal) implies
            		(source.oclIsKindOf (State) and source = target)
        """
        pass

    def state_is_local(self):
        """
        A Transition with kind local must have a composite State or an entry point as its source.

        .. ocl::
            (kind = TransitionKind::local) implies
            		((source.oclIsKindOf (State) and source.oclAsType(State).isComposite) or
            		(source.oclIsKindOf (Pseudostate) and source.oclAsType(Pseudostate).kind = PseudostateKind::entryPoint))
        """
        pass

class StartClassifierBehaviorAction(models.Model):
    """
    A StartClassifierBehaviorAction is an Action that starts the classifierBehavior of the input object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin that holds the object whose classifierBehavior is to be ' +
                               'started.')

    def multiplicity(self):
        """
        The multiplicity of the object InputPin is 1..1

        .. ocl::
            object.is(1,1)
        """
        pass

    def type_has_classifier(self):
        """
        If the InputPin has a type, then the type or one of its ancestors must have a classifierBehavior.

        .. ocl::
            object.type->notEmpty() implies 
               (object.type.oclIsKindOf(BehavioredClassifier) and object.type.oclAsType(BehavioredClassifier).classifierBehavior<>null)
        """
        pass

class CallEvent(models.Model):
    """
    A CallEvent models the receipt by an object of a message invoking a call of an Operation.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation', null=True, 
                                  help_text='Designates the Operation whose invocation raised the CalEvent.')

class ControlFlow(models.Model):
    """
    A ControlFlow is an ActivityEdge traversed by control tokens or object tokens of control type, which are use
    to control the execution of ExecutableNodes.
    """

    __package__ = 'UML.Activities'

    activity_edge = models.OneToOneField('ActivityEdge', on_delete=models.CASCADE, primary_key=True)

    def object_nodes(self):
        """
        ControlFlows may not have ObjectNodes at either end, except for ObjectNodes with control type.

        .. ocl::
            (source.oclIsKindOf(ObjectNode) implies source.oclAsType(ObjectNode).isControlType) and 
            (target.oclIsKindOf(ObjectNode) implies target.oclAsType(ObjectNode).isControlType)
        """
        pass

class ReplyAction(models.Model):
    """
    A ReplyAction is an Action that accepts a set of reply values and a value containing return information
    produced by a previous AcceptCallAction. The ReplyAction returns the values to the caller of the previous
    call, completing execution of the call.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    reply_to_call = models.ForeignKey('Trigger', related_name='%(app_label)s_%(class)s_reply_to_call', null=True, 
                                      help_text='The Trigger specifying the Operation whose call is being replied ' +
                                      'to.')
    reply_value = models.ManyToManyField('InputPin', related_name='%(app_label)s_%(class)s_reply_value', blank=True, 
                                         help_text='A list of InputPins providing the values for the output ' +
                                         '(inout, out, and return) Parameters of the Operation. These values are ' +
                                         'returned to the caller.')
    return_information = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_return_information', null=True, 
                                           help_text='An InputPin that holds the return information value ' +
                                           'produced by an earlier AcceptCallAction.')

    def event_on_reply_to_call_trigger(self):
        """
        The event of the replyToCall Trigger must be a CallEvent.

        .. ocl::
            replyToCall.event.oclIsKindOf(CallEvent)
        """
        pass

    def pins_match_parameter(self):
        """
        The replyValue InputPins must match the output (return, out, and inout) parameters of the operation of
        the event of the replyToCall Trigger in number, type, ordering, and multiplicity.

        .. ocl::
            let parameter:OrderedSet(Parameter) = replyToCall.event.oclAsType(CallEvent).operation.outputParameters() in
            replyValue->size()=parameter->size() and
            Sequence{1..replyValue->size()}->forAll(i |
            	replyValue->at(i).type.conformsTo(parameter->at(i).type) and
            	replyValue->at(i).isOrdered=parameter->at(i).isOrdered and
            	replyValue->at(i).compatibleWith(parameter->at(i)))
        """
        pass

class ExceptionHandler(models.Model):
    """
    An ExceptionHandler is an Element that specifies a handlerBody ExecutableNode to execute in case the
    specified exception occurs during the execution of the protected ExecutableNode.
    """

    __package__ = 'UML.Activities'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    exception_input = models.ForeignKey('ObjectNode', related_name='%(app_label)s_%(class)s_exception_input', null=True, 
                                        help_text='An ObjectNode within the handlerBody. When the ' +
                                        'ExceptionHandler catches an exception, the exception token is placed on ' +
                                        'this ObjectNode, causing the handlerBody to execute.')
    exception_type = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_exception_type', 
                                            help_text='The Classifiers whose instances the ExceptionHandler ' +
                                            'catches as exceptions. If an exception occurs whose type is any ' +
                                            'exceptionType, the ExceptionHandler catches the exception and ' +
                                            'executes the handlerBody.')
    handler_body = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_handler_body', null=True, 
                                     help_text='An ExecutableNode that is executed if the ExceptionHandler ' +
                                     'catches an exception.')
    protected_node = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_protected_node', null=True, 
                                       help_text='The ExecutableNode protected by the ExceptionHandler. If an ' +
                                       'exception propagates out of the protectedNode and has a type matching one ' +
                                       'of the exceptionTypes, then it is caught by this ExceptionHandler.')

    def edge_source_target(self):
        """
        An ActivityEdge that has a source within the handlerBody of an ExceptionHandler must have its target in
        the handlerBody also, and vice versa.

        .. ocl::
            let nodes:Set(ActivityNode) = handlerBody.oclAsType(Action).allOwnedNodes() in
            nodes.outgoing->forAll(nodes->includes(target)) and
            nodes.incoming->forAll(nodes->includes(source))
        """
        pass

    def exception_input_type(self):
        """
        The exceptionInput must either have no type or every exceptionType must conform to the exceptionInput
        type.

        .. ocl::
            exceptionInput.type=null or 
            exceptionType->forAll(conformsTo(exceptionInput.type.oclAsType(Classifier)))
        """
        pass

    def handler_body_edges(self):
        """
        The handlerBody has no incoming or outgoing ActivityEdges and the exceptionInput has no incoming
        ActivityEdges.

        .. ocl::
            handlerBody.incoming->isEmpty() and handlerBody.outgoing->isEmpty() and exceptionInput.incoming->isEmpty()
        """
        pass

    def handler_body_owner(self):
        """
        The handlerBody must have the same owner as the protectedNode.

        .. ocl::
            handlerBody.owner=protectedNode.owner
        """
        pass

    def one_input(self):
        """
        The handlerBody is an Action with one InputPin, and that InputPin is the same as the exceptionInput.

        .. ocl::
            handlerBody.oclIsKindOf(Action) and
            let inputs: OrderedSet(InputPin) = handlerBody.oclAsType(Action).input in
            inputs->size()=1 and inputs->first()=exceptionInput
        """
        pass

    def output_pins(self):
        """
        If the protectedNode is an Action with OutputPins, then the handlerBody must also be an Action with the
        same number of OutputPins, which are compatible in type, ordering, and multiplicity to those of the
        protectedNode.

        .. ocl::
            (protectedNode.oclIsKindOf(Action) and protectedNode.oclAsType(Action).output->notEmpty()) implies
            (
              handlerBody.oclIsKindOf(Action) and 
              let protectedNodeOutput : OrderedSet(OutputPin) = protectedNode.oclAsType(Action).output,
                    handlerBodyOutput : OrderedSet(OutputPin) =  handlerBody.oclAsType(Action).output in
                protectedNodeOutput->size() = handlerBodyOutput->size() and
                Sequence{1..protectedNodeOutput->size()}->forAll(i |
                	handlerBodyOutput->at(i).type.conformsTo(protectedNodeOutput->at(i).type) and
                	handlerBodyOutput->at(i).isOrdered=protectedNodeOutput->at(i).isOrdered and
                	handlerBodyOutput->at(i).compatibleWith(protectedNodeOutput->at(i)))
            )
        """
        pass

class PackageMerge(models.Model):
    """
    A package merge defines how the contents of one package are extended by the contents of another package.
    """

    __package__ = 'UML.Packages'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    merged_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_merged_package', null=True, 
                                       help_text='References the Package that is to be merged with the receiving ' +
                                       'package of the PackageMerge.')
    receiving_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_receiving_package', null=True, 
                                          help_text='References the Package that is being extended with the ' +
                                          'contents of the merged package of the PackageMerge.')

class ReadIsClassifiedObjectAction(models.Model):
    """
    A ReadIsClassifiedObjectAction is an Action that determines whether an object is classified by a given
    Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', null=True, 
                                   help_text='The Classifier against which the classification of the input object ' +
                                   'is tested.')
    is_direct = models.BooleanField(help_text='Indicates whether the input object must be directly classified by ' +
                                    'the given Classifier or whether it may also be an instance of a ' +
                                    'specialization of the given Classifier.')
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin that holds the object whose classification is to be ' +
                               'tested.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin that holds the Boolean result of the test.')

    def boolean_result(self):
        """
        The type of the result OutputPin is Boolean.

        .. ocl::
            result.type = Boolean
        """
        pass

    def multiplicity_of_input(self):
        """
        The multiplicity of the object InputPin is 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

    def multiplicity_of_output(self):
        """
        The multiplicity of the result OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def no_type(self):
        """
        The object InputPin has no type.

        .. ocl::
            object.type = null
        """
        pass

class Duration(models.Model):
    """
    A Duration is a ValueSpecification that specifies the temporal distance between two time instants.
    """

    __package__ = 'UML.Values'

    expr = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_expr', blank=True, null=True, 
                             help_text='A ValueSpecification that evaluates to the value of the Duration.')
    observation = models.ManyToManyField('Observation', related_name='%(app_label)s_%(class)s_observation', blank=True, 
                                         help_text='Refers to the Observations that are involved in the ' +
                                         'computation of the Duration value')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

    def no_expr_requires_observation(self):
        """
        If a Duration has no expr, then it must have a single observation that is a DurationObservation.

        .. ocl::
            expr = null implies (observation->size() = 1 and observation->forAll(oclIsKindOf(DurationObservation)))
        """
        pass

class InterruptibleActivityRegion(models.Model):
    """
    An InterruptibleActivityRegion is an ActivityGroup that supports the termination of tokens flowing in the
    portions of an activity within it.
    """

    __package__ = 'UML.Activities'

    activity_group = models.OneToOneField('ActivityGroup', on_delete=models.CASCADE, primary_key=True)
    interrupting_edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_interrupting_edge', blank=True, 
                                               help_text='The ActivityEdges leaving the ' +
                                               'InterruptibleActivityRegion on which a traversing token will ' +
                                               'result in the termination of other tokens flowing in the ' +
                                               'InterruptibleActivityRegion.')
    node = models.ManyToManyField('ActivityNode', related_name='%(app_label)s_%(class)s_node', blank=True, 
                                  help_text='ActivityNodes immediately contained in the ' +
                                  'InterruptibleActivityRegion.')

    def interrupting_edges(self):
        """
        The interruptingEdges of an InterruptibleActivityRegion must have their source in the region and their
        target outside the region, but within the same Activity containing the region.

        .. ocl::
            interruptingEdge->forAll(edge | 
              node->includes(edge.source) and node->excludes(edge.target) and edge.target.containingActivity() = inActivity)
        """
        pass

class ReclassifyObjectAction(models.Model):
    """
    A ReclassifyObjectAction is an Action that changes the Classifiers that classify an object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    is_replace_all = models.BooleanField(help_text='Specifies whether existing Classifiers should be removed ' +
                                         'before adding the new Classifiers.')
    new_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_new_classifier', blank=True, 
                                            help_text='A set of Classifiers to be added to the Classifiers of the ' +
                                            'given object.')
    object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_object', null=True, 
                               help_text='The InputPin that holds the object to be reclassified.')
    old_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_old_classifier', blank=True, 
                                            help_text='A set of Classifiers to be removed from the Classifiers of ' +
                                            'the given object.')

    def classifier_not_abstract(self):
        """
        None of the newClassifiers may be abstract.

        .. ocl::
            not newClassifier->exists(isAbstract)
        """
        pass

    def input_pin(self):
        """
        The object InputPin has no type.

        .. ocl::
            object.type = null
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the object InputPin is 1..1.

        .. ocl::
            object.is(1,1)
        """
        pass

class ProtocolConformance(models.Model):
    """
    A ProtocolStateMachine can be redefined into a more specific ProtocolStateMachine or into behavioral
    StateMachine. ProtocolConformance declares that the specific ProtocolStateMachine specifies a protocol that
    conforms to the general ProtocolStateMachine or that the specific behavioral StateMachine abides by the
    protocol of the general ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    general_machine = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_general_machine', null=True, 
                                        help_text='Specifies the ProtocolStateMachine to which the specific ' +
                                        'ProtocolStateMachine conforms.')
    specific_machine = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_specific_machine', null=True, 
                                         help_text='Specifies the ProtocolStateMachine which conforms to the ' +
                                         'general ProtocolStateMachine.')

class ConnectionPointReference(models.Model):
    """
    A ConnectionPointReference represents a usage (as part of a submachine State) of an entry/exit point
    Pseudostate defined in the StateMachine referenced by the submachine State.
    """

    __package__ = 'UML.StateMachines'

    entry = models.ManyToManyField('Pseudostate', related_name='%(app_label)s_%(class)s_entry', blank=True, 
                                   help_text='The entryPoint Pseudostates corresponding to this connection ' +
                                   'point.')
    exit = models.ManyToManyField('Pseudostate', related_name='%(app_label)s_%(class)s_exit', blank=True, 
                                  help_text='The exitPoints kind Pseudostates corresponding to this connection ' +
                                  'point.')
    state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_state', blank=True, null=True, 
                              help_text='The State in which the ConnectionPointReference is defined.')
    vertex = models.OneToOneField('Vertex', on_delete=models.CASCADE, primary_key=True)

    def entry_pseudostates(self):
        """
        The entry Pseudostates must be Pseudostates with kind entryPoint.

        .. ocl::
            entry->forAll(kind = PseudostateKind::entryPoint)
        """
        pass

    def exit_pseudostates(self):
        """
        The exit Pseudostates must be Pseudostates with kind exitPoint.

        .. ocl::
            exit->forAll(kind = PseudostateKind::exitPoint)
        """
        pass

class Slot(models.Model):
    """
    A Slot designates that an entity modeled by an InstanceSpecification has a value or values for a specific
    StructuralFeature.
    """

    __package__ = 'UML.Classification'

    defining_feature = models.ForeignKey('StructuralFeature', related_name='%(app_label)s_%(class)s_defining_feature', null=True, 
                                         help_text='The StructuralFeature that specifies the values that may be ' +
                                         'held by the Slot.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owning_instance = models.ForeignKey('InstanceSpecification', related_name='%(app_label)s_%(class)s_owning_instance', null=True, 
                                        help_text='The InstanceSpecification that owns this Slot.')
    value = models.ManyToManyField('ValueSpecification', related_name='%(app_label)s_%(class)s_value', blank=True, 
                                   help_text='The value or values held by the Slot.')

class MessageKind(models.Model):
    """
    This is an enumerated type that identifies the type of Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class CallBehaviorAction(models.Model):
    """
    A CallBehaviorAction is a CallAction that invokes a Behavior directly. The argument values of the
    CallBehaviorAction are passed on the input Parameters of the invoked Behavior. If the call is synchronous,
    the execution of the CallBehaviorAction waits until the execution of the invoked Behavior completes and the
    values of output Parameters of the Behavior are placed on the result OutputPins. If the call is
    asynchronous, the CallBehaviorAction completes immediately and no results values can be provided.
    """

    __package__ = 'UML.Actions'

    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior', null=True, 
                                 help_text='The Behavior being invoked.')
    call_action = models.OneToOneField('CallAction', on_delete=models.CASCADE, primary_key=True)

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior being called.

        .. ocl::
            result = (behavior.inputParameters())
        """
        pass

    def no_onport(self):
        """
        A CallBehaviorAction may not specify onPort.

        .. ocl::
            onPort=null
        """
        pass

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior being called.

        .. ocl::
            result = (behavior.outputParameters())
        """
        pass

class Include(models.Model):
    """
    An Include relationship specifies that a UseCase contains the behavior defined in another UseCase.
    """

    __package__ = 'UML.UseCases'

    addition = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_addition', null=True, 
                                 help_text='The UseCase that is to be included.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    including_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_including_case', null=True, 
                                       help_text='The UseCase which includes the addition and owns the Include ' +
                                       'relationship.')
    named_element = models.OneToOneField('NamedElement')

class Component(models.Model):
    """
    A Component represents a modular part of a system that encapsulates its contents and whose manifestation is
    replaceable within its environment.
    """

    __package__ = 'UML.StructuredClassifiers'

    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    is_indirectly_instantiated = models.BooleanField(help_text='If true, the Component is defined at design-time, ' +
                                                     'but at run-time (or execution-time) an object specified by ' +
                                                     'the Component does not exist, that is, the Component is ' +
                                                     'instantiated indirectly, through the instantiation of its ' +
                                                     'realizing Classifiers or parts.')
    packaged_element = models.ManyToManyField('PackageableElement', related_name='%(app_label)s_%(class)s_packaged_element', blank=True, 
                                              help_text='The set of PackageableElements that a Component owns. In ' +
                                              'the namespace of a Component, all model elements that are involved ' +
                                              'in or related to its definition may be owned or imported ' +
                                              'explicitly. These may include e.g., Classes, Interfaces, ' +
                                              'Components, Packages, UseCases, Dependencies (e.g., mappings), and ' +
                                              'Artifacts.')
    provided = models.ManyToManyField('Interface', related_name='%(app_label)s_%(class)s_provided', blank=True, 
                                      help_text='The Interfaces that the Component exposes to its environment. ' +
                                      'These Interfaces may be Realized by the Component or any of its ' +
                                      'realizingClassifiers, or they may be the Interfaces that are provided by ' +
                                      'its public Ports.')
    realization = models.ManyToManyField('ComponentRealization', related_name='%(app_label)s_%(class)s_realization', blank=True, 
                                         help_text='The set of Realizations owned by the Component. Realizations ' +
                                         'reference the Classifiers of which the Component is an abstraction; ' +
                                         'i.e., that realize its behavior.')
    required = models.ManyToManyField('Interface', related_name='%(app_label)s_%(class)s_required', blank=True, 
                                      help_text='The Interfaces that the Component requires from other Components ' +
                                      'in its environment in order to be able to offer its full set of provided ' +
                                      'functionality. These Interfaces may be used by the Component or any of its ' +
                                      'realizingClassifiers, or they may be the Interfaces that are required by ' +
                                      'its public Ports.')

    def no_nested_classifiers(self):
        """
        A Component cannot nest Classifiers.

        .. ocl::
            nestedClassifier->isEmpty()
        """
        pass

    def no_packaged_elements(self):
        """
        A Component nested in a Class cannot have any packaged elements.

        .. ocl::
            nestingClass <> null implies packagedElement->isEmpty()
        """
        pass

    def get_provided(self):
        """
        Derivation for Component::/provided

        .. ocl::
            result = (let 	ris : Set(Interface) = allRealizedInterfaces(),
                    realizingClassifiers : Set(Classifier) =  self.realization.realizingClassifier->union(self.allParents()->collect(realization.realizingClassifier))->asSet(),
                    allRealizingClassifiers : Set(Classifier) = realizingClassifiers->union(realizingClassifiers.allParents())->asSet(),
                    realizingClassifierInterfaces : Set(Interface) = allRealizingClassifiers->iterate(c; rci : Set(Interface) = Set{} | rci->union(c.allRealizedInterfaces())),
                    ports : Set(Port) = self.ownedPort->union(allParents()->collect(ownedPort))->asSet(),
                    providedByPorts : Set(Interface) = ports.provided->asSet()
            in     ris->union(realizingClassifierInterfaces) ->union(providedByPorts)->asSet())
        """
        pass

    def get_required(self):
        """
        Derivation for Component::/required

        .. ocl::
            result = (let 	uis : Set(Interface) = allUsedInterfaces(),
                    realizingClassifiers : Set(Classifier) = self.realization.realizingClassifier->union(self.allParents()->collect(realization.realizingClassifier))->asSet(),
                    allRealizingClassifiers : Set(Classifier) = realizingClassifiers->union(realizingClassifiers.allParents())->asSet(),
                    realizingClassifierInterfaces : Set(Interface) = allRealizingClassifiers->iterate(c; rci : Set(Interface) = Set{} | rci->union(c.allUsedInterfaces())),
                    ports : Set(Port) = self.ownedPort->union(allParents()->collect(ownedPort))->asSet(),
                    usedByPorts : Set(Interface) = ports.required->asSet()
            in	    uis->union(realizingClassifierInterfaces)->union(usedByPorts)->asSet()
            )
        """
        pass

class CallConcurrencyKind(models.Model):
    """
    CallConcurrencyKind is an Enumeration used to specify the semantics of concurrent calls to a
    BehavioralFeature.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class ParameterSet(models.Model):
    """
    A ParameterSet designates alternative sets of inputs or outputs that a Behavior may use.
    """

    __package__ = 'UML.Classification'

    condition = models.ManyToManyField('Constraint', related_name='%(app_label)s_%(class)s_condition', blank=True, 
                                       help_text='A constraint that should be satisfied for the owner of the ' +
                                       'Parameters in an input ParameterSet to start execution using the values ' +
                                       'provided for those Parameters, or the owner of the Parameters in an output ' +
                                       'ParameterSet to end execution providing the values for those Parameters, ' +
                                       'if all preconditions and conditions on input ParameterSets were ' +
                                       'satisfied.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    parameter = models.ManyToManyField('Parameter', related_name='%(app_label)s_%(class)s_parameter', 
                                       help_text='Parameters in the ParameterSet.')

    def input(self):
        """
        If a parameterized entity has input Parameters that are in a ParameterSet, then any inputs that are not
        in a ParameterSet must be streaming. Same for output Parameters.

        .. ocl::
            ((parameter->exists(direction = ParameterDirectionKind::_'in')) implies 
                behavioralFeature.ownedParameter->select(p | p.direction = ParameterDirectionKind::_'in' and p.parameterSet->isEmpty())->forAll(isStream))
                and
            ((parameter->exists(direction = ParameterDirectionKind::out)) implies 
                behavioralFeature.ownedParameter->select(p | p.direction = ParameterDirectionKind::out and p.parameterSet->isEmpty())->forAll(isStream))
        """
        pass

    def same_parameterized_entity(self):
        """
        The Parameters in a ParameterSet must all be inputs or all be outputs of the same parameterized entity,
        and the ParameterSet is owned by that entity.

        .. ocl::
            parameter->forAll(p1, p2 | self.owner = p1.owner and self.owner = p2.owner and p1.direction = p2.direction)
        """
        pass

    def two_parameter_sets(self):
        """
        Two ParameterSets cannot have exactly the same set of Parameters.

        .. ocl::
            parameter->forAll(parameterSet->forAll(s1, s2 | s1->size() = s2->size() implies s1.parameter->exists(p | not s2.parameter->includes(p))))
        """
        pass

class RemoveStructuralFeatureValueAction(models.Model):
    """
    A RemoveStructuralFeatureValueAction is a WriteStructuralFeatureAction that removes values from a
    StructuralFeature.
    """

    __package__ = 'UML.Actions'

    is_remove_duplicates = models.BooleanField(help_text='Specifies whether to remove duplicates of the value in ' +
                                               'nonunique StructuralFeatures.')
    remove_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_remove_at', blank=True, null=True, 
                                  help_text='An InputPin that provides the position of an existing value to ' +
                                  'remove in ordered, nonunique structural features. The type of the removeAt ' +
                                  'InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.')
    write_structural_feature_action = models.OneToOneField('WriteStructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)

    def remove_at_and_value(self):
        """
        RemoveStructuralFeatureValueActions removing a value from ordered, non-unique StructuralFeatures must
        have a single removeAt InputPin and no value InputPin, if isRemoveDuplicates is false. The removeAt
        InputPin must be of type Unlimited Natural with multiplicity 1..1. Otherwise, the Action has a value
        InputPin and no removeAt InputPin.

        .. ocl::
            if structuralFeature.isOrdered and not structuralFeature.isUnique and  not isRemoveDuplicates then
              value = null and
              removeAt <> null and
              removeAt.type = UnlimitedNatural and
              removeAt.is(1,1)
            else
              removeAt = null and value <> null
            endif
        """
        pass

class InteractionOperand(models.Model):
    """
    An InteractionOperand is contained in a CombinedFragment. An InteractionOperand represents one operand of
    the expression given by the enclosing CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    fragment = models.ManyToManyField('InteractionFragment', related_name='%(app_label)s_%(class)s_fragment', blank=True, 
                                      help_text='The fragments of the operand.')
    guard = models.ForeignKey('InteractionConstraint', related_name='%(app_label)s_%(class)s_guard', blank=True, null=True, 
                              help_text='Constraint of the operand.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    namespace = models.OneToOneField('Namespace')

    def guard_contain_references(self):
        """
        The guard must contain only references to values local to the Lifeline on which it resides, or values
        global to the whole Interaction.
        """
        pass

    def guard_directly_prior(self):
        """
        The guard must be placed directly prior to (above) the OccurrenceSpecification that will become the
        first OccurrenceSpecification within this InteractionOperand.
        """
        pass

class FinalState(models.Model):
    """
    A special kind of State, which, when entered, signifies that the enclosing Region has completed. If the
    enclosing Region is directly contained in a StateMachine and all other Regions in that StateMachine also are
    completed, then it means that the entire StateMachine behavior is completed.
    """

    __package__ = 'UML.StateMachines'

    state = models.OneToOneField('State', on_delete=models.CASCADE, primary_key=True)

    def cannot_reference_submachine(self):
        """
        A FinalState cannot reference a submachine.

        .. ocl::
            submachine->isEmpty()
        """
        pass

    def no_entry_behavior(self):
        """
        A FinalState has no entry Behavior.

        .. ocl::
            entry->isEmpty()
        """
        pass

    def no_exit_behavior(self):
        """
        A FinalState has no exit Behavior.

        .. ocl::
            exit->isEmpty()
        """
        pass

    def no_outgoing_transitions(self):
        """
        A FinalState cannot have any outgoing Transitions.

        .. ocl::
            outgoing->size() = 0
        """
        pass

    def no_regions(self):
        """
        A FinalState cannot have Regions.

        .. ocl::
            region->size() = 0
        """
        pass

    def no_state_behavior(self):
        """
        A FinalState has no state (doActivity) Behavior.

        .. ocl::
            doActivity->isEmpty()
        """
        pass

class ObjectNodeOrderingKind(models.Model):
    """
    ObjectNodeOrderingKind is an enumeration indicating queuing order for offering the tokens held by an
    ObjectNode.
    """

    __package__ = 'UML.Activities'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class CollaborationUse(models.Model):
    """
    A CollaborationUse is used to specify the application of a pattern specified by a Collaboration to a
    specific situation.
    """

    __package__ = 'UML.StructuredClassifiers'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    role_binding = models.ManyToManyField('Dependency', related_name='%(app_label)s_%(class)s_role_binding', blank=True, 
                                          help_text='A mapping between features of the Collaboration and features ' +
                                          'of the owning Classifier. This mapping indicates which ' +
                                          'ConnectableElement of the Classifier plays which role(s) in the ' +
                                          'Collaboration. A ConnectableElement may be bound to multiple roles in ' +
                                          'the same CollaborationUse (that is, it may play multiple roles).')
    type = models.ForeignKey('Collaboration', related_name='%(app_label)s_%(class)s_type', null=True, 
                             help_text='The Collaboration which is used in this CollaborationUse. The ' +
                             'Collaboration defines the cooperation between its roles which are mapped to ' +
                             'ConnectableElements relating to the Classifier owning the CollaborationUse.')

    def client_elements(self):
        """
        All the client elements of a roleBinding are in one Classifier and all supplier elements of a
        roleBinding are in one Collaboration.

        .. ocl::
            roleBinding->collect(client)->forAll(ne1, ne2 |
              ne1.oclIsKindOf(ConnectableElement) and ne2.oclIsKindOf(ConnectableElement) and
                let ce1 : ConnectableElement = ne1.oclAsType(ConnectableElement), ce2 : ConnectableElement = ne2.oclAsType(ConnectableElement) in
                  ce1.structuredClassifier = ce2.structuredClassifier)
            and
              roleBinding->collect(supplier)->forAll(ne1, ne2 |
              ne1.oclIsKindOf(ConnectableElement) and ne2.oclIsKindOf(ConnectableElement) and
                let ce1 : ConnectableElement = ne1.oclAsType(ConnectableElement), ce2 : ConnectableElement = ne2.oclAsType(ConnectableElement) in
                  ce1.collaboration = ce2.collaboration)
        """
        pass

    def connectors(self):
        """
        Connectors in a Collaboration typing a CollaborationUse must have corresponding Connectors between
        elements bound in the context Classifier, and these corresponding Connectors must have the same or more
        general type than the Collaboration Connectors.

        .. ocl::
            type.ownedConnector->forAll(connector |
              let rolesConnectedInCollab : Set(ConnectableElement) = connector.end.role->asSet(),
                    relevantBindings : Set(Dependency) = roleBinding->select(rb | rb.supplier->intersection(rolesConnectedInCollab)->notEmpty()),
                    boundRoles : Set(ConnectableElement) = relevantBindings->collect(client.oclAsType(ConnectableElement))->asSet(),
                    contextClassifier : StructuredClassifier = boundRoles->any(true).structuredClassifier->any(true) in
                      contextClassifier.ownedConnector->exists( correspondingConnector | 
                          correspondingConnector.end.role->forAll( role | boundRoles->includes(role) )
                          and (connector.type->notEmpty() and correspondingConnector.type->notEmpty()) implies connector.type->forAll(conformsTo(correspondingConnector.type)) )
            )
        """
        pass

    def every_role(self):
        """
        Every collaborationRole in the Collaboration is bound within the CollaborationUse.

        .. ocl::
            type.collaborationRole->forAll(role | roleBinding->exists(rb | rb.supplier->includes(role)))
        """
        pass

class TimeObservation(models.Model):
    """
    A TimeObservation is a reference to a time instant during an execution. It points out the NamedElement in
    the model to observe and whether the observation is when this NamedElement is entered or when it is exited.
    """

    __package__ = 'UML.Values'

    event = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_event', null=True, 
                              help_text='The TimeObservation is determined by the entering or exiting of the ' +
                              'event Element during execution.')
    first_event = models.BooleanField(help_text='The value of firstEvent is related to the event. If firstEvent ' +
                                      'is true, then the corresponding observation event is the first time instant ' +
                                      'the execution enters the event Element. If firstEvent is false, then the ' +
                                      'corresponding observation event is the time instant the execution exits the ' +
                                      'event Element.')
    observation = models.OneToOneField('Observation', on_delete=models.CASCADE, primary_key=True)

class ElementImport(models.Model):
    """
    An ElementImport identifies a NamedElement in a Namespace other than the one that owns that NamedElement and
    allows the NamedElement to be referenced using an unqualified name in the Namespace owning the
    ElementImport.
    """

    __package__ = 'UML.CommonStructure'

    alias = models.CharField(max_length=255, blank=True, null=True, 
                             help_text='Specifies the name that should be added to the importing Namespace in ' +
                             'lieu of the name of the imported PackagableElement. The alias must not clash with ' +
                             'any other member in the importing Namespace. By default, no alias is used.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    imported_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_imported_element', null=True, 
                                         help_text='Specifies the PackageableElement whose name is to be added to ' +
                                         'a Namespace.')
    importing_namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_importing_namespace', null=True, 
                                            help_text='Specifies the Namespace that imports a PackageableElement ' +
                                            'from another Namespace.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', null=True, default='public', 
                                   help_text='Specifies the visibility of the imported PackageableElement within ' +
                                   'the importingNamespace, i.e., whether the  importedElement will in turn be ' +
                                   'visible to other Namespaces. If the ElementImport is public, the ' +
                                   'importedElement will be visible outside the importingNamespace while, if the ' +
                                   'ElementImport is private, it will not.')

    def get_name(self):
        """
        The query getName() returns the name under which the imported PackageableElement will be known in the
        importing namespace.

        .. ocl::
            result = (if alias->notEmpty() then
              alias
            else
              importedElement.name
            endif)
        """
        pass

    def imported_element_is_public(self):
        """
        An importedElement has either public visibility or no visibility at all.

        .. ocl::
            importedElement.visibility <> null implies importedElement.visibility = VisibilityKind::public
        """
        pass

    def visibility_public_or_private(self):
        """
        The visibility of an ElementImport is either public or private.

        .. ocl::
            visibility = VisibilityKind::public or visibility = VisibilityKind::private
        """
        pass

class OutputPin(models.Model):
    """
    An OutputPin is a Pin that holds output values produced by an Action.
    """

    __package__ = 'UML.Actions'

    pin = models.OneToOneField('Pin', on_delete=models.CASCADE, primary_key=True)

    def incoming_edges_structured_only(self):
        """
        An OutputPin may have incoming ActivityEdges only when it is owned by a StructuredActivityNode, and
        these edges must have sources contained (directly or indirectly) in the owning StructuredActivityNode.

        .. ocl::
            incoming->notEmpty() implies
            	action<>null and
            	action.oclIsKindOf(StructuredActivityNode) and
            	action.oclAsType(StructuredActivityNode).allOwnedNodes()->includesAll(incoming.source)
        """
        pass

class GeneralOrdering(models.Model):
    """
    A GeneralOrdering represents a binary relation between two OccurrenceSpecifications, to describe that one
    OccurrenceSpecification must occur before the other in a valid trace. This mechanism provides the ability to
    define partial orders of OccurrenceSpecifications that may otherwise not have a specified order.
    """

    __package__ = 'UML.Interactions'

    after = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_after', null=True, 
                              help_text='The OccurrenceSpecification referenced comes after the ' +
                              'OccurrenceSpecification referenced by before.')
    before = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_before', null=True, 
                               help_text='The OccurrenceSpecification referenced comes before the ' +
                               'OccurrenceSpecification referenced by after.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)

    def irreflexive_transitive_closure(self):
        """
        An occurrence specification must not be ordered relative to itself through a series of general
        orderings. (In other words, the transitive closure of the general orderings is irreflexive.)

        .. ocl::
            after->closure(toAfter.after)->excludes(before)
        """
        pass

class TimeInterval(models.Model):
    """
    A TimeInterval defines the range between two TimeExpressions.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval', on_delete=models.CASCADE, primary_key=True)
    max = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_max', null=True, 
                            help_text='Refers to the TimeExpression denoting the maximum value of the range.')
    min = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_min', null=True, 
                            help_text='Refers to the TimeExpression denoting the minimum value of the range.')

class Extension(models.Model):
    """
    An extension is used to indicate that the properties of a metaclass are extended through a stereotype, and
    gives the ability to flexibly add (and later remove) stereotypes to classes.
    """

    __package__ = 'UML.Packages'

    association = models.OneToOneField('Association', on_delete=models.CASCADE, primary_key=True)
    is_required = models.BooleanField(help_text='Indicates whether an instance of the extending stereotype must ' +
                                      'be created when an instance of the extended class is created. The attribute ' +
                                      'value is derived from the value of the lower property of the ExtensionEnd ' +
                                      'referenced by Extension::ownedEnd; a lower value of 1 means that isRequired ' +
                                      'is true, but otherwise it is false. Since the default value of ' +
                                      'ExtensionEnd::lower is 0, the default value of isRequired is false.')
    metaclass = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_metaclass', null=True, 
                                  help_text='References the Class that is extended through an Extension. The ' +
                                  'property is derived from the type of the memberEnd that is not the ownedEnd.')
    owned_end = models.ForeignKey('ExtensionEnd', related_name='%(app_label)s_%(class)s_owned_end', null=True, 
                                  help_text='References the end of the extension that is typed by a Stereotype.')

    def is_required(self):
        """
        The query isRequired() is true if the owned end has a multiplicity with the lower bound of 1.

        .. ocl::
            result = (ownedEnd.lowerBound() = 1)
        """
        pass

    def is_binary(self):
        """
        An Extension is binary, i.e., it has only two memberEnds.

        .. ocl::
            memberEnd->size() = 2
        """
        pass

    def get_metaclass(self):
        """
        The query metaclass() returns the metaclass that is being extended (as opposed to the extending
        stereotype).

        .. ocl::
            result = (metaclassEnd().type.oclAsType(Class))
        """
        pass

    def metaclass_end(self):
        """
        The query metaclassEnd() returns the Property that is typed by a metaclass (as opposed to a stereotype).

        .. ocl::
            result = (memberEnd->reject(p | ownedEnd->includes(p.oclAsType(ExtensionEnd)))->any(true))
        """
        pass

    def non_owned_end(self):
        """
        The non-owned end of an Extension is typed by a Class.

        .. ocl::
            metaclassEnd()->notEmpty() and metaclassEnd().type.oclIsKindOf(Class)
        """
        pass

class CreateObjectAction(models.Model):
    """
    A CreateObjectAction is an Action that creates an instance of the specified Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', null=True, 
                                   help_text='The Classifier to be instantiated.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the newly created object is placed.')

    def classifier_not_abstract(self):
        """
        The classifier cannot be abstract.

        .. ocl::
            not classifier.isAbstract
        """
        pass

    def classifier_not_association_class(self):
        """
        The classifier cannot be an AssociationClass.

        .. ocl::
            not classifier.oclIsKindOf(AssociationClass)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of the result OutputPin is 1..1.

        .. ocl::
            result.is(1,1)
        """
        pass

    def same_type(self):
        """
        The type of the result OutputPin must be the same as the classifier of the CreateObjectAction.

        .. ocl::
            result.type = classifier
        """
        pass

class Gate(models.Model):
    """
    A Gate is a MessageEnd which serves as a connection point for relating a Message which has a MessageEnd
    (sendEvent / receiveEvent) outside an InteractionFragment with another Message which has a MessageEnd
    (receiveEvent / sendEvent)  inside that InteractionFragment.
    """

    __package__ = 'UML.Interactions'

    message_end = models.OneToOneField('MessageEnd', on_delete=models.CASCADE, primary_key=True)

    def actual_gate_distinguishable(self):
        """
        isActual() implies that no other actualGate of the parent InteractionUse returns the same getName() as
        returned for self

        .. ocl::
            isActual() implies interactionUse.actualGate->select(getName() = self.getName())->size()=1
        """
        pass

    def actual_gate_matched(self):
        """
        If this Gate is an actualGate, it must have exactly one matching formalGate within the referred
        Interaction.

        .. ocl::
            interactionUse->notEmpty() implies interactionUse.refersTo.formalGate->select(matches(self))->size()=1
        """
        pass

    def formal_gate_distinguishable(self):
        """
        isFormal() implies that no other formalGate of the parent Interaction returns the same getName() as
        returned for self

        .. ocl::
            isFormal() implies interaction.formalGate->select(getName() = self.getName())->size()=1
        """
        pass

    def get_name(self):
        """
        This query returns the name of the gate, either the explicit name (.name) or the constructed name
        ('out_" or 'in_' concatenated in front of .message.name) if the explicit name is not present.

        .. ocl::
            result = (if name->notEmpty() then name->asOrderedSet()->first()
            else  if isActual() or isOutsideCF() 
              then if isSend() 
                then 'out_'.concat(self.message.name->asOrderedSet()->first())
                else 'in_'.concat(self.message.name->asOrderedSet()->first())
                endif
              else if isSend()
                then 'in_'.concat(self.message.name->asOrderedSet()->first())
                else 'out_'.concat(self.message.name->asOrderedSet()->first())
                endif
              endif
            endif)
        """
        pass

    def get_operand(self):
        """
        If the Gate is an inside Combined Fragment Gate, this operation returns the InteractionOperand that the
        opposite end of this Gate is included within.

        .. ocl::
            result = (if isInsideCF() then
              let oppEnd : MessageEnd = self.oppositeEnd()->asOrderedSet()->first() in
                if oppEnd.oclIsKindOf(MessageOccurrenceSpecification)
                then let oppMOS : MessageOccurrenceSpecification = oppEnd.oclAsType(MessageOccurrenceSpecification)
                    in oppMOS.enclosingOperand->asOrderedSet()->first()
                else let oppGate : Gate = oppEnd.oclAsType(Gate)
                    in oppGate.combinedFragment.enclosingOperand->asOrderedSet()->first()
                endif
              else null
            endif)
        """
        pass

    def inside_cf_gate_distinguishable(self):
        """
        isInsideCF() implies that no other inside cfragmentGate attached to a message with its other end in the
        same InteractionOperator as self, returns the same getName() as returned for self

        .. ocl::
            isInsideCF() implies
            let selfOperand : InteractionOperand = self.getOperand() in
              combinedFragment.cfragmentGate->select(isInsideCF() and getName() = self.getName())->select(getOperand() = selfOperand)->size()=1
        """
        pass

    def inside_cf_matched(self):
        """
        If this Gate is inside a CombinedFragment, it must have exactly one matching Gate which is outside of
        that CombinedFragment.

        .. ocl::
            isInsideCF() implies combinedFragment.cfragmentGate->select(isOutsideCF() and matches(self))->size()=1
        """
        pass

    def is_actual(self):
        """
        This query returns true value if this Gate is an actualGate of an InteractionUse.

        .. ocl::
            result = (interactionUse->notEmpty())
        """
        pass

    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() specifies that two Gates may coexist in the same Namespace, without an
        explicit name property. The association end formalGate subsets ownedElement, and since the Gate name
        attribute  is optional, it is allowed to have two formal gates without an explicit name, but having
        derived names which are distinct.

        .. ocl::
            result = (true)
        """
        pass

    def is_formal(self):
        """
        This query returns true if this Gate is a formalGate of an Interaction.

        .. ocl::
            result = (interaction->notEmpty())
        """
        pass

    def is_inside_cf(self):
        """
        This query returns true if this Gate is attached to the boundary of a CombinedFragment, and its other
        end (if present) is inside of an InteractionOperator of the same CombinedFragment.

        .. ocl::
            result = (self.oppositeEnd()-> notEmpty() and combinedFragment->notEmpty() implies
            let oppEnd : MessageEnd = self.oppositeEnd()->asOrderedSet()->first() in
            if oppEnd.oclIsKindOf(MessageOccurrenceSpecification)
            then let oppMOS : MessageOccurrenceSpecification
            = oppEnd.oclAsType(MessageOccurrenceSpecification)
            in combinedFragment = oppMOS.enclosingOperand.combinedFragment
            else let oppGate : Gate = oppEnd.oclAsType(Gate)
            in combinedFragment = oppGate.combinedFragment.enclosingOperand.combinedFragment
            endif)
        """
        pass

    def is_outside_cf(self):
        """
        This query returns true if this Gate is attached to the boundary of a CombinedFragment, and its other
        end (if present)  is outside of the same CombinedFragment.

        .. ocl::
            result = (self.oppositeEnd()-> notEmpty() and combinedFragment->notEmpty() implies
            let oppEnd : MessageEnd = self.oppositeEnd()->asOrderedSet()->first() in
            if oppEnd.oclIsKindOf(MessageOccurrenceSpecification) 
            then let oppMOS : MessageOccurrenceSpecification = oppEnd.oclAsType(MessageOccurrenceSpecification)
            in  self.combinedFragment.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(self.combinedFragment.enclosingOperand.oclAsType(InteractionFragment)->asSet()) =
                 oppMOS.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(oppMOS.enclosingOperand.oclAsType(InteractionFragment)->asSet())
            else let oppGate : Gate = oppEnd.oclAsType(Gate) 
            in self.combinedFragment.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(self.combinedFragment.enclosingOperand.oclAsType(InteractionFragment)->asSet()) =
                 oppGate.combinedFragment.enclosingInteraction.oclAsType(InteractionFragment)->asSet()->
                 union(oppGate.combinedFragment.enclosingOperand.oclAsType(InteractionFragment)->asSet())
            endif)
        """
        pass

    def matches(self):
        """
        This query returns true if the name of this Gate matches the name of the in parameter Gate, and the
        messages for the two Gates correspond. The Message for one Gate (say A) corresponds to the Message for
        another Gate (say B) if (A and B have the same name value) and (if A is a sendEvent then B is a
        receiveEvent) and (if A is a receiveEvent then B is a sendEvent) and (A and B have the same messageSort
        value) and (A and B have the same signature value).

        .. ocl::
            result = (self.getName() = gateToMatch.getName() and 
            self.message.messageSort = gateToMatch.message.messageSort and
            self.message.name = gateToMatch.message.name and
            self.message.sendEvent->includes(self) implies gateToMatch.message.receiveEvent->includes(gateToMatch)  and
            self.message.receiveEvent->includes(self) implies gateToMatch.message.sendEvent->includes(gateToMatch) and
            self.message.signature = gateToMatch.message.signature)
        """
        pass

    def outside_cf_gate_distinguishable(self):
        """
        isOutsideCF() implies that no other outside cfragmentGate of the parent CombinedFragment returns the
        same getName() as returned for self

        .. ocl::
            isOutsideCF() implies combinedFragment.cfragmentGate->select(getName() = self.getName())->size()=1
        """
        pass

    def outside_cf_matched(self):
        """
        If this Gate is outside an 'alt' CombinedFragment,  for every InteractionOperator inside that
        CombinedFragment there must be exactly one matching Gate inside the CombindedFragment with its opposing
        end enclosed by that InteractionOperator. If this Gate is outside CombinedFragment with operator other
        than 'alt',   there must be exactly one matching Gate inside that CombinedFragment.

        .. ocl::
            isOutsideCF() implies
             if self.combinedFragment.interactionOperator->asOrderedSet()->first() = InteractionOperatorKind::alt
             then self.combinedFragment.operand->forAll(op : InteractionOperand |
             self.combinedFragment.cfragmentGate->select(isInsideCF() and 
             oppositeEnd().enclosingFragment()->includes(self.combinedFragment) and matches(self))->size()=1)
             else  self.combinedFragment.cfragmentGate->select(isInsideCF() and matches(self))->size()=1
             endif
        """
        pass

class ActivityPartition(models.Model):
    """
    An ActivityPartition is a kind of ActivityGroup for identifying ActivityNodes that have some characteristic
    in common.
    """

    __package__ = 'UML.Activities'

    activity_group = models.OneToOneField('ActivityGroup', on_delete=models.CASCADE, primary_key=True)
    edge = models.ManyToManyField('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', blank=True, 
                                  help_text='ActivityEdges immediately contained in the ActivityPartition.')
    is_dimension = models.BooleanField(help_text='Indicates whether the ActivityPartition groups other ' +
                                       'ActivityPartitions along a dimension.')
    is_external = models.BooleanField(help_text='Indicates whether the ActivityPartition represents an entity to ' +
                                      'which the partitioning structure does not apply.')
    node = models.ManyToManyField('ActivityNode', related_name='%(app_label)s_%(class)s_node', blank=True, 
                                  help_text='ActivityNodes immediately contained in the ActivityPartition.')
    represents = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_represents', blank=True, null=True, 
                                   help_text='An Element represented by the functionality modeled within the ' +
                                   'ActivityPartition.')
    subpartition = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_subpartition', blank=True, 
                                          help_text='Other ActivityPartitions immediately contained in this ' +
                                          'ActivityPartition (as its subgroups).')
    super_partition = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_super_partition', blank=True, null=True, 
                                        help_text='Other ActivityPartitions immediately containing this ' +
                                        'ActivityPartition (as its superGroups).')

    def dimension_not_contained(self):
        """
        An ActvivityPartition with isDimension = true may not be contained by another ActivityPartition.

        .. ocl::
            isDimension implies superPartition->isEmpty()
        """
        pass

    def represents_classifier(self):
        """
        If a non-external ActivityPartition represents a Classifier and has a superPartition, then the
        superPartition must represent a Classifier, and the Classifier of the subpartition must be nested
        (nestedClassifier or ownedBehavior) in the Classifier represented by the superPartition, or be at the
        contained end of a composition Association with the Classifier represented by the superPartition.

        .. ocl::
            (not isExternal and represents.oclIsKindOf(Classifier) and superPartition->notEmpty()) implies
            (
               let representedClassifier : Classifier = represents.oclAsType(Classifier) in
                 superPartition.represents.oclIsKindOf(Classifier) and
                  let representedSuperClassifier : Classifier = superPartition.represents.oclAsType(Classifier) in
                   (representedSuperClassifier.oclIsKindOf(BehavioredClassifier) and representedClassifier.oclIsKindOf(Behavior) and 
                    representedSuperClassifier.oclAsType(BehavioredClassifier).ownedBehavior->includes(representedClassifier.oclAsType(Behavior))) 
                   or
                   (representedSuperClassifier.oclIsKindOf(Class) and  representedSuperClassifier.oclAsType(Class).nestedClassifier->includes(representedClassifier))
                   or
                   (Association.allInstances()->exists(a | a.memberEnd->exists(end1 | end1.isComposite and end1.type = representedClassifier and 
                                                                                  a.memberEnd->exists(end2 | end1<>end2 and end2.type = representedSuperClassifier))))
            )
        """
        pass

    def represents_property(self):
        """
        If an ActivityPartition represents a Property and has a superPartition representing a Classifier, then
        all the other non-external subpartitions of the superPartition must represent Properties directly owned
        by the same Classifier.

        .. ocl::
            (represents.oclIsKindOf(Property) and superPartition->notEmpty() and superPartition.represents.oclIsKindOf(Classifier)) implies
            (
              let representedClassifier : Classifier = superPartition.represents.oclAsType(Classifier)
              in
                superPartition.subpartition->reject(isExternal)->forAll(p | 
                   p.represents.oclIsKindOf(Property) and p.owner=representedClassifier)
            )
        """
        pass

    def represents_property_and_is_contained(self):
        """
        If an ActivityPartition represents a Property and has a superPartition, then the Property must be of a
        Classifier represented by the superPartition, or of a Classifier that is the type of a Property
        represented by the superPartition.

        .. ocl::
            (represents.oclIsKindOf(Property) and superPartition->notEmpty()) implies
            (
              (superPartition.represents.oclIsKindOf(Classifier) and represents.owner = superPartition.represents) or 
              (superPartition.represents.oclIsKindOf(Property) and represents.owner = superPartition.represents.oclAsType(Property).type)
            )
        """
        pass

class SendSignalAction(models.Model):
    """
    A SendSignalAction is an InvocationAction that creates a Signal instance and transmits it to the target
    object. Values from the argument InputPins are used to provide values for the attributes of the Signal. The
    requestor continues execution immediately after the Signal instance is sent out and cannot receive reply
    values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal', null=True, 
                               help_text='The Signal whose instance is transmitted to the target.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='The InputPin that provides the target object to which the Signal ' +
                               'instance is sent.')

    def number_order(self):
        """
        The number and order of argument InputPins must be the same as the number and order of attributes of the
        signal.

        .. ocl::
            argument->size()=signal.allAttributes()->size()
        """
        pass

    def type_ordering_multiplicity(self):
        """
        The type, ordering, and multiplicity of an argument InputPin must be the same as the corresponding
        attribute of the signal.

        .. ocl::
            let attribute: OrderedSet(Property) = signal.allAttributes() in
            Sequence{1..argument->size()}->forAll(i | 
            	argument->at(i).type.conformsTo(attribute->at(i).type) and 
            	argument->at(i).isOrdered = attribute->at(i).isOrdered and
            	argument->at(i).compatibleWith(attribute->at(i)))
        """
        pass

    def type_target_pin(self):
        """
        If onPort is not empty, the Port given by onPort must be an owned or inherited feature of the type of
        the target InputPin.

        .. ocl::
            not onPort->isEmpty() implies target.type.oclAsType(Classifier).allFeatures()->includes(onPort)
        """
        pass

class ParameterEffectKind(models.Model):
    """
    ParameterEffectKind is an Enumeration that indicates the effect of a Behavior on values passed in or out of
    its parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class InteractionConstraint(models.Model):
    """
    An InteractionConstraint is a Boolean expression that guards an operand in a CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    constraint = models.OneToOneField('Constraint', on_delete=models.CASCADE, primary_key=True)
    maxint = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_maxint', blank=True, null=True, 
                               help_text='The maximum number of iterations of a loop')
    minint = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_minint', blank=True, null=True, 
                               help_text='The minimum number of iterations of a loop')

    def dynamic_variables(self):
        """
        The dynamic variables that take part in the constraint must be owned by the ConnectableElement
        corresponding to the covered Lifeline.
        """
        pass

    def global_data(self):
        """
        The constraint may contain references to global data or write-once data.
        """
        pass

    def maxint_greater_equal_minint(self):
        """
        If maxint is specified, then minint must be specified and the evaluation of maxint must be >= the
        evaluation of minint.

        .. ocl::
            maxint->notEmpty() implies (minint->notEmpty() and 
            maxint->asSequence()->first().integerValue() >=
            minint->asSequence()->first().integerValue() )
        """
        pass

    def maxint_positive(self):
        """
        If maxint is specified, then the expression must evaluate to a positive integer.

        .. ocl::
            maxint->notEmpty() implies 
            maxint->asSequence()->first().integerValue() > 0
        """
        pass

    def minint_maxint(self):
        """
        Minint/maxint can only be present if the InteractionConstraint is associated with the operand of a loop
        CombinedFragment.

        .. ocl::
            maxint->notEmpty() or minint->notEmpty() implies
            interactionOperand.combinedFragment.interactionOperator =
            InteractionOperatorKind::loop
        """
        pass

    def minint_non_negative(self):
        """
        If minint is specified, then the expression must evaluate to a non-negative integer.

        .. ocl::
            minint->notEmpty() implies 
            minint->asSequence()->first().integerValue() >= 0
        """
        pass

class DataStoreNode(models.Model):
    """
    A DataStoreNode is a CentralBufferNode for persistent data.
    """

    __package__ = 'UML.Activities'

    central_buffer_node = models.OneToOneField('CentralBufferNode', on_delete=models.CASCADE, primary_key=True)

class ChangeEvent(models.Model):
    """
    A ChangeEvent models a change in the system configuration that makes a condition true.
    """

    __package__ = 'UML.CommonBehavior'

    change_expression = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_change_expression', null=True, 
                                          help_text='A Boolean-valued ValueSpecification that will result in a ' +
                                          'ChangeEvent whenever its value changes from false to true.')
    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)

class Deployment(models.Model):
    """
    A deployment is the allocation of an artifact or artifact instance to a deployment target. A component
    deployment is the deployment of one or more artifacts or artifact instances to a deployment target,
    optionally parameterized by a deployment specification. Examples are executables and configuration files.
    """

    __package__ = 'UML.Deployments'

    configuration = models.ManyToManyField('DeploymentSpecification', related_name='%(app_label)s_%(class)s_configuration', blank=True, 
                                           help_text='The specification of properties that parameterize the ' +
                                           'deployment and execution of one or more Artifacts.')
    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)
    deployed_artifact = models.ManyToManyField('DeployedArtifact', related_name='%(app_label)s_%(class)s_deployed_artifact', blank=True, 
                                               help_text='The Artifacts that are deployed onto a Node. This ' +
                                               'association specializes the supplier association.')
    location = models.ForeignKey('DeploymentTarget', related_name='%(app_label)s_%(class)s_location', null=True, 
                                 help_text='The DeployedTarget which is the target of a Deployment.')

class Collaboration(models.Model):
    """
    A Collaboration describes a structure of collaborating elements (roles), each performing a specialized
    function, which collectively accomplish some desired functionality.
    """

    __package__ = 'UML.StructuredClassifiers'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier')
    collaboration_role = models.ManyToManyField('ConnectableElement', related_name='%(app_label)s_%(class)s_collaboration_role', blank=True, 
                                                help_text='Represents the participants in the Collaboration.')
    structured_classifier = models.OneToOneField('StructuredClassifier', on_delete=models.CASCADE, primary_key=True)

class OccurrenceSpecification(models.Model):
    """
    An OccurrenceSpecification is the basic semantic unit of Interactions. The sequences of occurrences
    specified by them are the meanings of Interactions.
    """

    __package__ = 'UML.Interactions'

    covered = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_covered', null=True, 
                                help_text='References the Lifeline on which the OccurrenceSpecification appears.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    to_after = models.ManyToManyField('GeneralOrdering', related_name='%(app_label)s_%(class)s_to_after', blank=True, 
                                      help_text='References the GeneralOrderings that specify EventOcurrences ' +
                                      'that must occur after this OccurrenceSpecification.')
    to_before = models.ManyToManyField('GeneralOrdering', related_name='%(app_label)s_%(class)s_to_before', blank=True, 
                                       help_text='References the GeneralOrderings that specify EventOcurrences ' +
                                       'that must occur before this OccurrenceSpecification.')

class MessageOccurrenceSpecification(models.Model):
    """
    A MessageOccurrenceSpecification specifies the occurrence of Message events, such as sending and receiving
    of Signals or invoking or receiving of Operation calls. A MessageOccurrenceSpecification is a kind of
    MessageEnd. Messages are generated either by synchronous Operation calls or asynchronous Signal sends. They
    are received by the execution of corresponding AcceptEventActions.
    """

    __package__ = 'UML.Interactions'

    message_end = models.OneToOneField('MessageEnd', on_delete=models.CASCADE, primary_key=True)
    occurrence_specification = models.OneToOneField('OccurrenceSpecification')

class DestructionOccurrenceSpecification(models.Model):
    """
    A DestructionOccurenceSpecification models the destruction of an object.
    """

    __package__ = 'UML.Interactions'

    message_occurrence_specification = models.OneToOneField('MessageOccurrenceSpecification', on_delete=models.CASCADE, primary_key=True)

    def no_occurrence_specifications_below(self):
        """
        No other OccurrenceSpecifications on a given Lifeline in an InteractionOperand may appear below a
        DestructionOccurrenceSpecification.

        .. ocl::
            let o : InteractionOperand = enclosingOperand in o->notEmpty() and 
            let peerEvents : OrderedSet(OccurrenceSpecification) = covered.events->select(enclosingOperand = o)
            in peerEvents->last() = self
        """
        pass

class ExtensionEnd(models.Model):
    """
    An extension end is used to tie an extension to a stereotype when extending a metaclass. The default
    multiplicity of an extension end is 0..1.
    """

    __package__ = 'UML.Packages'

    lower = models.IntegerField(blank=True, null=True, 
                                help_text='This redefinition changes the default multiplicity of association ' +
                                'ends, since model elements are usually extended by 0 or 1 instance of the ' +
                                'extension stereotype.')
    property = models.OneToOneField('Property', on_delete=models.CASCADE, primary_key=True)
    type = models.ForeignKey('Stereotype', related_name='%(app_label)s_%(class)s_type', null=True, 
                             help_text='References the type of the ExtensionEnd. Note that this association ' +
                             'restricts the possible types of an ExtensionEnd to only be Stereotypes.')

    def aggregation(self):
        """
        The aggregation of an ExtensionEnd is composite.

        .. ocl::
            self.aggregation = AggregationKind::composite
        """
        pass

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an Integer. This is a redefinition
        of the default lower bound, which normally, for MultiplicityElements, evaluates to 1 if empty.

        .. ocl::
            result = (if lowerValue=null then 0 else lowerValue.integerValue() endif)
        """
        pass

    def multiplicity(self):
        """
        The multiplicity of ExtensionEnd is 0..1 or 1.

        .. ocl::
            (lowerBound() = 0 or lowerBound() = 1) and upperBound() = 1
        """
        pass

class Interface(models.Model):
    """
    Interfaces declare coherent services that are implemented by BehavioredClassifiers that implement the
    Interfaces via InterfaceRealizations.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    nested_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_nested_classifier', blank=True, 
                                               help_text='References all the Classifiers that are defined ' +
                                               '(nested) within the Interface.')
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The attributes (i.e., the Properties) owned by the ' +
                                             'Interface.')
    owned_operation = models.ManyToManyField('Operation', related_name='%(app_label)s_%(class)s_owned_operation', blank=True, 
                                             help_text='The Operations owned by the Interface.')
    owned_reception = models.ManyToManyField('Reception', related_name='%(app_label)s_%(class)s_owned_reception', blank=True, 
                                             help_text='Receptions that objects providing this Interface are ' +
                                             'willing to accept.')
    protocol = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_protocol', blank=True, null=True, 
                                 help_text='References a ProtocolStateMachine specifying the legal sequences of ' +
                                 'the invocation of the BehavioralFeatures described in the Interface.')
    redefined_interface = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_interface', blank=True, 
                                                 help_text='References all the Interfaces redefined by this ' +
                                                 'Interface.')

    def visibility(self):
        """
        The visibility of all Features owned by an Interface must be public.

        .. ocl::
            feature->forAll(visibility = VisibilityKind::public)
        """
        pass

class TemplateParameterSubstitution(models.Model):
    """
    A TemplateParameterSubstitution relates the actual parameter to a formal TemplateParameter as part of a
    template binding.
    """

    __package__ = 'UML.CommonStructure'

    actual = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_actual', null=True, 
                               help_text='The ParameterableElement that is the actual parameter for this ' +
                               'TemplateParameterSubstitution.')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    formal = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_formal', null=True, 
                               help_text='The formal TemplateParameter that is associated with this ' +
                               'TemplateParameterSubstitution.')
    owned_actual = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_actual', blank=True, null=True, 
                                     help_text='The ParameterableElement that is owned by this ' +
                                     'TemplateParameterSubstitution as its actual parameter.')
    template_binding = models.ForeignKey('TemplateBinding', related_name='%(app_label)s_%(class)s_template_binding', null=True, 
                                         help_text='The TemplateBinding that owns this ' +
                                         'TemplateParameterSubstitution.')

    def must_be_compatible(self):
        """
        The actual ParameterableElement must be compatible with the formal TemplateParameter, e.g., the actual
        ParameterableElement for a Class TemplateParameter must be a Class.

        .. ocl::
            actual->forAll(a | a.isCompatibleWith(formal.parameteredElement))
        """
        pass

class PackageImport(models.Model):
    """
    A PackageImport is a Relationship that imports all the non-private members of a Package into the Namespace
    owning the PackageImport, so that those Elements may be referred to by their unqualified names in the
    importingNamespace.
    """

    __package__ = 'UML.CommonStructure'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    imported_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_imported_package', null=True, 
                                         help_text='Specifies the Package whose members are imported into a ' +
                                         'Namespace.')
    importing_namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_importing_namespace', null=True, 
                                            help_text='Specifies the Namespace that imports the members from a ' +
                                            'Package.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', null=True, default='public', 
                                   help_text='Specifies the visibility of the imported PackageableElements within ' +
                                   'the importingNamespace, i.e., whether imported Elements will in turn be ' +
                                   'visible to other Namespaces. If the PackageImport is public, the imported ' +
                                   'Elements will be visible outside the importingNamespace, while, if the ' +
                                   'PackageImport is private, they will not.')

    def public_or_private(self):
        """
        The visibility of a PackageImport is either public or private.

        .. ocl::
            visibility = VisibilityKind::public or visibility = VisibilityKind::private
        """
        pass

class InstanceSpecification(models.Model):
    """
    An InstanceSpecification is a model element that represents an instance in a modeled system. An
    InstanceSpecification can act as a DeploymentTarget in a Deployment relationship, in the case that it
    represents an instance of a Node. It can also act as a DeployedArtifact, if it represents an instance of an
    Artifact.
    """

    __package__ = 'UML.Classification'

    classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_classifier', blank=True, 
                                        help_text='The Classifier or Classifiers of the represented instance. If ' +
                                        'multiple Classifiers are specified, the instance is classified by all of ' +
                                        'them.')
    deployed_artifact = models.OneToOneField('DeployedArtifact')
    deployment_target = models.OneToOneField('DeploymentTarget', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')
    slot = models.ManyToManyField('Slot', related_name='%(app_label)s_%(class)s_slot', blank=True, 
                                  help_text='A Slot giving the value or values of a StructuralFeature of the ' +
                                  'instance. An InstanceSpecification can have one Slot per StructuralFeature of ' +
                                  'its Classifiers, including inherited features. It is not necessary to model a ' +
                                  'Slot for every StructuralFeature, in which case the InstanceSpecification is a ' +
                                  'partial description.')
    specification = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_specification', blank=True, null=True, 
                                      help_text='A specification of how to compute, derive, or construct the ' +
                                      'instance.')

    def defining_feature(self):
        """
        The definingFeature of each slot is a StructuralFeature related to a classifier of the
        InstanceSpecification, including direct attributes, inherited attributes, private attributes in
        generalizations, and memberEnds of Associations, but excluding redefined StructuralFeatures.

        .. ocl::
            slot->forAll(s | classifier->exists (c | c.allSlottableFeatures()->includes (s.definingFeature)))
        """
        pass

    def deployment_artifact(self):
        """
        An InstanceSpecification can act as a DeployedArtifact if it represents an instance of an Artifact.

        .. ocl::
            deploymentForArtifact->notEmpty() implies classifier->exists(oclIsKindOf(Artifact))
        """
        pass

    def deployment_target(self):
        """
        An InstanceSpecification can act as a DeploymentTarget if it represents an instance of a Node and
        functions as a part in the internal structure of an encompassing Node.

        .. ocl::
            deployment->notEmpty() implies classifier->exists(node | node.oclIsKindOf(Node) and Node.allInstances()->exists(n | n.part->exists(p | p.type = node)))
        """
        pass

    def structural_feature(self):
        """
        No more than one slot in an InstanceSpecification may have the same definingFeature.

        .. ocl::
            classifier->forAll(c | (c.allSlottableFeatures()->forAll(f | slot->select(s | s.definingFeature = f)->size() <= 1)))
        """
        pass

class EnumerationLiteral(models.Model):
    """
    An EnumerationLiteral is a user-defined data value for an Enumeration.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.ForeignKey('Enumeration', related_name='%(app_label)s_%(class)s_classifier', null=True, 
                                   help_text='The classifier of this EnumerationLiteral derived to be equal to ' +
                                   'its Enumeration.')
    enumeration = models.ForeignKey('Enumeration', related_name='%(app_label)s_%(class)s_enumeration', null=True, 
                                    help_text='The Enumeration that this EnumerationLiteral is a member of.')
    instance_specification = models.OneToOneField('InstanceSpecification', on_delete=models.CASCADE, primary_key=True)

    def get_classifier(self):
        """
        Derivation of Enumeration::/classifier

        .. ocl::
            result = (enumeration)
        """
        pass

class Lifeline(models.Model):
    """
    A Lifeline represents an individual participant in the Interaction. While parts and structural features may
    have multiplicity greater than 1, Lifelines represent only one interacting entity.
    """

    __package__ = 'UML.Interactions'

    covered_by = models.ManyToManyField('InteractionFragment', related_name='%(app_label)s_%(class)s_covered_by', blank=True, 
                                        help_text='References the InteractionFragments in which this Lifeline ' +
                                        'takes part.')
    decomposed_as = models.ForeignKey('PartDecomposition', related_name='%(app_label)s_%(class)s_decomposed_as', blank=True, null=True, 
                                      help_text='References the Interaction that represents the decomposition.')
    interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_interaction', null=True, 
                                    help_text='References the Interaction enclosing this Lifeline.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    represents = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_represents', blank=True, null=True, 
                                   help_text='References the ConnectableElement within the classifier that ' +
                                   'contains the enclosing interaction.')
    selector = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_selector', blank=True, null=True, 
                                 help_text='If the referenced ConnectableElement is multivalued, then this ' +
                                 'specifies the specific individual part within that set.')

    def interaction_uses_share_lifeline(self):
        """
        If a lifeline is in an Interaction referred to by an InteractionUse in an enclosing Interaction,  and
        that lifeline is common with another lifeline in an Interaction referred to by another InteractonUse
        within that same enclosing Interaction, it must be common to a lifeline within that enclosing
        Interaction. By common Lifelines we mean Lifelines with the same selector and represents associations.

        .. ocl::
            let intUses : Set(InteractionUse) = interaction.interactionUse  in 
            intUses->forAll
            ( iuse : InteractionUse | 
            let usingInteraction : Set(Interaction)  = iuse.enclosingInteraction->asSet()
            ->union(
            iuse.enclosingOperand.combinedFragment->asSet()->closure(enclosingOperand.combinedFragment).enclosingInteraction->asSet()
                           ) 
            in
            let peerUses : Set(InteractionUse) = usingInteraction.fragment->select(oclIsKindOf(InteractionUse)).oclAsType(InteractionUse)->asSet()
            ->union(
            usingInteraction.fragment->select(oclIsKindOf(CombinedFragment)).oclAsType(CombinedFragment)->asSet()
            ->closure(operand.fragment->select(oclIsKindOf(CombinedFragment)).oclAsType(CombinedFragment)).operand.fragment->
            select(oclIsKindOf(InteractionUse)).oclAsType(InteractionUse)->asSet()
                           )->excluding(iuse)
             in
            peerUses->forAll( peerUse : InteractionUse |
             peerUse.refersTo.lifeline->forAll( l : Lifeline | (l.represents = self.represents and 
             ( self.selector.oclIsKindOf(LiteralString) implies
              l.selector.oclIsKindOf(LiteralString) and 
              self.selector.oclAsType(LiteralString).value = l.selector.oclAsType(LiteralString).value )
              and 
            ( self.selector.oclIsKindOf(LiteralInteger) implies
              l.selector.oclIsKindOf(LiteralInteger) and 
              self.selector.oclAsType(LiteralInteger).value = l.selector.oclAsType(LiteralInteger).value )
            )  
            implies
             usingInteraction.lifeline->select(represents = self.represents and
             ( self.selector.oclIsKindOf(LiteralString) implies
              l.selector.oclIsKindOf(LiteralString) and 
              self.selector.oclAsType(LiteralString).value = l.selector.oclAsType(LiteralString).value )
            and 
            ( self.selector.oclIsKindOf(LiteralInteger) implies
              l.selector.oclIsKindOf(LiteralInteger) and 
              self.selector.oclAsType(LiteralInteger).value = l.selector.oclAsType(LiteralInteger).value )
            )
                                                            )
                                )
            )
        """
        pass

    def same_classifier(self):
        """
        The classifier containing the referenced ConnectableElement must be the same classifier, or an ancestor,
        of the classifier that contains the interaction enclosing this lifeline.

        .. ocl::
            represents.namespace->closure(namespace)->includes(interaction._'context')
        """
        pass

    def selector_int_or_string(self):
        """
        The selector value, if present, must be a LiteralString or a LiteralInteger

        .. ocl::
            self.selector->notEmpty() implies 
            self.selector.oclIsKindOf(LiteralInteger) or 
            self.selector.oclIsKindOf(LiteralString)
        """
        pass

    def selector_specified(self):
        """
        The selector for a Lifeline must only be specified if the referenced Part is multivalued.

        .. ocl::
            self.selector->notEmpty() = (self.represents.oclIsKindOf(MultiplicityElement) and self.represents.oclAsType(MultiplicityElement).isMultivalued())
        """
        pass

class ObjectFlow(models.Model):
    """
    An ObjectFlow is an ActivityEdge that is traversed by object tokens that may hold values. Object flows also
    support multicast/receive, token selection from object nodes, and transformation of tokens.
    """

    __package__ = 'UML.Activities'

    activity_edge = models.OneToOneField('ActivityEdge', on_delete=models.CASCADE, primary_key=True)
    is_multicast = models.BooleanField(help_text='Indicates whether the objects in the ObjectFlow are passed by ' +
                                       'multicasting.')
    is_multireceive = models.BooleanField(help_text='Indicates whether the objects in the ObjectFlow are gathered ' +
                                          'from respondents to multicasting.')
    selection = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_selection', blank=True, null=True, 
                                  help_text='A Behavior used to select tokens from a source ObjectNode.')
    transformation = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_transformation', blank=True, null=True, 
                                       help_text='A Behavior used to change or replace object tokens flowing ' +
                                       'along the ObjectFlow.')

    def compatible_types(self):
        """
        ObjectNodes connected by an ObjectFlow, with optionally intervening ControlNodes, must have compatible
        types. In particular, the downstream ObjectNode type must be the same or a supertype of the upstream
        ObjectNode type.
        """
        pass

    def input_and_output_parameter(self):
        """
        A selection Behavior has one input Parameter and one output Parameter. The input Parameter must have the
        same as or a supertype of the type of the source ObjectNode, be non-unique and have multiplicity 0..*.
        The output Parameter must be the same or a subtype of the type of source ObjectNode. The Behavior cannot
        have side effects.

        .. ocl::
            selection<>null implies
            	selection.inputParameters()->size()=1 and
            	selection.inputParameters()->forAll(not isUnique and is(0,*)) and
            	selection.outputParameters()->size()=1
        """
        pass

    def is_multicast_or_is_multireceive(self):
        """
        isMulticast and isMultireceive cannot both be true.

        .. ocl::
            not (isMulticast and isMultireceive)
        """
        pass

    def no_executable_nodes(self):
        """
        ObjectFlows may not have ExecutableNodes at either end.

        .. ocl::
            not (source.oclIsKindOf(ExecutableNode) or target.oclIsKindOf(ExecutableNode))
        """
        pass

    def same_upper_bounds(self):
        """
        ObjectNodes connected by an ObjectFlow, with optionally intervening ControlNodes, must have the same
        upperBounds.
        """
        pass

    def selection_behavior(self):
        """
        An ObjectFlow may have a selection Behavior only if it has an ObjectNode as its source.

        .. ocl::
            selection<>null implies source.oclIsKindOf(ObjectNode)
        """
        pass

    def target(self):
        """
        An ObjectFlow with a constant weight may not target an ObjectNode, with optionally intervening
        ControlNodes, that has an upper bound less than the weight.
        """
        pass

    def transformation_behavior(self):
        """
        A transformation Behavior has one input Parameter and one output Parameter. The input Parameter must be
        the same as or a supertype of the type of object token coming from the source end. The output Parameter
        must be the same or a subtype of the type of object token expected downstream. The Behavior cannot have
        side effects.

        .. ocl::
            transformation<>null implies
            	transformation.inputParameters()->size()=1 and
            	transformation.outputParameters()->size()=1
        """
        pass

class AnyReceiveEvent(models.Model):
    """
    A trigger for an AnyReceiveEvent is triggered by the receipt of any message that is not explicitly handled
    by any related trigger.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)

class QualifierValue(models.Model):
    """
    A QualifierValue is an Element that is used as part of LinkEndData to provide the value for a single
    qualifier of the end given by the LinkEndData.
    """

    __package__ = 'UML.Actions'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    qualifier = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_qualifier', null=True, 
                                  help_text='The qualifier Property for which the value is to be specified.')
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', null=True, 
                              help_text='The InputPin from which the specified value for the qualifier is taken.')

    def multiplicity_of_qualifier(self):
        """
        The multiplicity of the value InputPin is 1..1.

        .. ocl::
            value.is(1,1)
        """
        pass

    def qualifier_attribute(self):
        """
        The qualifier must be a qualifier of the Association end of the linkEndData that owns this
        QualifierValue.

        .. ocl::
            linkEndData.end.qualifier->includes(qualifier)
        """
        pass

    def type_of_qualifier(self):
        """
        The type of the value InputPin conforms to the type of the qualifier Property.

        .. ocl::
            value.type.conformsTo(qualifier.type)
        """
        pass

class Continuation(models.Model):
    """
    A Continuation is a syntactic way to define continuations of different branches of an alternative
    CombinedFragment. Continuations are intuitively similar to labels representing intermediate points in a flow
    of control.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    setting = models.BooleanField(help_text='True: when the Continuation is at the end of the enclosing ' +
                                  'InteractionFragment and False when it is in the beginning.')

    def first_or_last_interaction_fragment(self):
        """
        Continuations always occur as the very first InteractionFragment or the very last InteractionFragment of
        the enclosing InteractionOperand.

        .. ocl::
            enclosingOperand->notEmpty() and 
             let peerFragments : OrderedSet(InteractionFragment) =  enclosingOperand.fragment in 
               ( peerFragments->notEmpty() and 
               ((peerFragments->first() = self) or  (peerFragments->last() = self)))
        """
        pass

    def has_global(self):
        """
        Continuations are always global in the enclosing InteractionFragment e.g., it always covers all
        Lifelines covered by the enclosing InteractionOperator.

        .. ocl::
            enclosingOperand->notEmpty() and
              let operandLifelines : Set(Lifeline) =  enclosingOperand.covered in 
                (operandLifelines->notEmpty() and 
                operandLifelines->forAll(ol :Lifeline |self.covered->includes(ol)))
        """
        pass

    def same_name(self):
        """
        Across all Interaction instances having the same context value, every Lifeline instance covered by a
        Continuation (self) must be common with one covered Lifeline instance of all other Continuation
        instances with the same name as self, and every Lifeline instance covered by a Continuation instance
        with the same name as self must be common with one covered Lifeline instance of self. Lifeline instances
        are common if they have the same selector and represents associationEnd values.

        .. ocl::
            enclosingOperand.combinedFragment->notEmpty() and
            let parentInteraction : Set(Interaction) = 
            enclosingOperand.combinedFragment->closure(enclosingOperand.combinedFragment)->
            collect(enclosingInteraction).oclAsType(Interaction)->asSet()
            in 
            (parentInteraction->size() = 1) 
            and let peerInteractions : Set(Interaction) =
             (parentInteraction->union(parentInteraction->collect(_'context')->collect(behavior)->
             select(oclIsKindOf(Interaction)).oclAsType(Interaction)->asSet())->asSet()) in
             (peerInteractions->notEmpty()) and 
              let combinedFragments1 : Set(CombinedFragment) = peerInteractions.fragment->
             select(oclIsKindOf(CombinedFragment)).oclAsType(CombinedFragment)->asSet() in
               combinedFragments1->notEmpty() and  combinedFragments1->closure(operand.fragment->
               select(oclIsKindOf(CombinedFragment)).oclAsType(CombinedFragment))->asSet().operand.fragment->
               select(oclIsKindOf(Continuation)).oclAsType(Continuation)->asSet()->
               forAll(c : Continuation |  (c.name = self.name) implies 
              (c.covered->asSet()->forAll(cl : Lifeline | --  cl must be common to one lifeline covered by self
              self.covered->asSet()->
              select(represents = cl.represents and selector = cl.selector)->asSet()->size()=1))
               and
             (self.covered->asSet()->forAll(cl : Lifeline | --  cl must be common to one lifeline covered by c
             c.covered->asSet()->
              select(represents = cl.represents and selector = cl.selector)->asSet()->size()=1))
              )
        """
        pass

class InstanceValue(models.Model):
    """
    An InstanceValue is a ValueSpecification that identifies an instance.
    """

    __package__ = 'UML.Classification'

    instance = models.ForeignKey('InstanceSpecification', related_name='%(app_label)s_%(class)s_instance', null=True, 
                                 help_text='The InstanceSpecification that represents the specified value.')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

class PseudostateKind(models.Model):
    """
    PseudostateKind is an Enumeration type that is used to differentiate various kinds of Pseudostates.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class BehaviorExecutionSpecification(models.Model):
    """
    A BehaviorExecutionSpecification is a kind of ExecutionSpecification representing the execution of a
    Behavior.
    """

    __package__ = 'UML.Interactions'

    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior', blank=True, null=True, 
                                 help_text='Behavior whose execution is occurring.')
    execution_specification = models.OneToOneField('ExecutionSpecification', on_delete=models.CASCADE, primary_key=True)

class ActivityFinalNode(models.Model):
    """
    An ActivityFinalNode is a FinalNode that terminates the execution of its owning Activity or
    StructuredActivityNode.
    """

    __package__ = 'UML.Activities'

    final_node = models.OneToOneField('FinalNode', on_delete=models.CASCADE, primary_key=True)

class Signal(models.Model):
    """
    A Signal is a specification of a kind of communication between objects in which a reaction is asynchronously
    triggered in the receiver without a reply.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ManyToManyField('Property', related_name='%(app_label)s_%(class)s_owned_attribute', blank=True, 
                                             help_text='The attributes owned by the Signal.')

class Manifestation(models.Model):
    """
    A manifestation is the concrete physical rendering of one or more model elements by an artifact.
    """

    __package__ = 'UML.Deployments'

    abstraction = models.OneToOneField('Abstraction', on_delete=models.CASCADE, primary_key=True)
    utilized_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_utilized_element', null=True, 
                                         help_text='The model element that is utilized in the manifestation in an ' +
                                         'Artifact.')

class Image(models.Model):
    """
    Physical definition of a graphical image.
    """

    __package__ = 'UML.Packages'

    content = models.CharField(max_length=255, blank=True, null=True, 
                               help_text='This contains the serialization of the image according to the format. ' +
                               'The value could represent a bitmap, image such as a GIF file, or drawing ' +
                               '"instructions" using a standard such as Scalable Vector Graphic (SVG) (which is ' +
                               'XML based).')
    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    format = models.CharField(max_length=255, blank=True, null=True, 
                              help_text='This indicates the format of the content, which is how the string ' +
                              'content should be interpreted. The following values are reserved: SVG, GIF, PNG, ' +
                              'JPG, WMF, EMF, BMP. In addition the prefix "MIME: " is also reserved. This option ' +
                              'can be used as an alternative to express the reserved values above, for example ' +
                              '"SVG" could instead be expressed as "MIME: image/svg+xml".')
    location = models.CharField(max_length=255, blank=True, null=True, 
                                help_text='This contains a location that can be used by a tool to locate the ' +
                                'image as an alternative to embedding it in the stereotype.')

class AggregationKind(models.Model):
    """
    AggregationKind is an Enumeration for specifying the kind of aggregation of a Property.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class Port(models.Model):
    """
    A Port is a property of an EncapsulatedClassifier that specifies a distinct interaction point between that
    EncapsulatedClassifier and its environment or between the (behavior of the) EncapsulatedClassifier and its
    internal parts. Ports are connected to Properties of the EncapsulatedClassifier by Connectors through which
    requests can be made to invoke BehavioralFeatures. A Port may specify the services an EncapsulatedClassifier
    provides (offers) to its environment as well as the services that an EncapsulatedClassifier expects
    (requires) of its environment.  A Port may have an associated ProtocolStateMachine.
    """

    __package__ = 'UML.StructuredClassifiers'

    is_behavior = models.BooleanField(help_text='Specifies whether requests arriving at this Port are sent to the ' +
                                      'classifier behavior of this EncapsulatedClassifier. Such a Port is referred ' +
                                      'to as a behavior Port. Any invocation of a BehavioralFeature targeted at a ' +
                                      'behavior Port will be handled by the instance of the owning ' +
                                      'EncapsulatedClassifier itself, rather than by any instances that it may ' +
                                      'contain.')
    is_conjugated = models.BooleanField(help_text='Specifies the way that the provided and required Interfaces ' +
                                        'are derived from the Port"s Type.')
    is_service = models.BooleanField(help_text='If true, indicates that this Port is used to provide the ' +
                                     'published functionality of an EncapsulatedClassifier.  If false, this Port ' +
                                     'is used to implement the EncapsulatedClassifier but is not part of the ' +
                                     'essential externally-visible functionality of the EncapsulatedClassifier and ' +
                                     'can, therefore, be altered or deleted along with the internal implementation ' +
                                     'of the EncapsulatedClassifier and other properties that are considered part ' +
                                     'of its implementation.')
    property = models.OneToOneField('Property', on_delete=models.CASCADE, primary_key=True)
    protocol = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_protocol', blank=True, null=True, 
                                 help_text='An optional ProtocolStateMachine which describes valid interactions ' +
                                 'at this interaction point.')
    provided = models.ManyToManyField('Interface', related_name='%(app_label)s_%(class)s_provided', blank=True, 
                                      help_text='The Interfaces specifying the set of Operations and Receptions ' +
                                      'that the EncapsulatedCclassifier offers to its environment via this Port, ' +
                                      'and which it will handle either directly or by forwarding it to a part of ' +
                                      'its internal structure. This association is derived according to the value ' +
                                      'of isConjugated. If isConjugated is false, provided is derived as the union ' +
                                      'of the sets of Interfaces realized by the type of the port and its ' +
                                      'supertypes, or directly from the type of the Port if the Port is typed by ' +
                                      'an Interface. If isConjugated is true, it is derived as the union of the ' +
                                      'sets of Interfaces used by the type of the Port and its supertypes.')
    redefined_port = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_redefined_port', blank=True, 
                                            help_text='A Port may be redefined when its containing ' +
                                            'EncapsulatedClassifier is specialized. The redefining Port may have ' +
                                            'additional Interfaces to those that are associated with the redefined ' +
                                            'Port or it may replace an Interface by one of its subtypes.')
    required = models.ManyToManyField('Interface', related_name='%(app_label)s_%(class)s_required', blank=True, 
                                      help_text='The Interfaces specifying the set of Operations and Receptions ' +
                                      'that the EncapsulatedCassifier expects its environment to handle via this ' +
                                      'port. This association is derived according to the value of isConjugated. ' +
                                      'If isConjugated is false, required is derived as the union of the sets of ' +
                                      'Interfaces used by the type of the Port and its supertypes. If isConjugated ' +
                                      'is true, it is derived as the union of the sets of Interfaces realized by ' +
                                      'the type of the Port and its supertypes, or directly from the type of the ' +
                                      'Port if the Port is typed by an Interface.')

    def basic_provided(self):
        """
        The union of the sets of Interfaces realized by the type of the Port and its supertypes, or directly the
        type of the Port if the Port is typed by an Interface.

        .. ocl::
            result = (if type.oclIsKindOf(Interface) 
            then type.oclAsType(Interface)->asSet() 
            else type.oclAsType(Classifier).allRealizedInterfaces() 
            endif)
        """
        pass

    def basic_required(self):
        """
        The union of the sets of Interfaces used by the type of the Port and its supertypes.

        .. ocl::
            result = ( type.oclAsType(Classifier).allUsedInterfaces() )
        """
        pass

    def default_value(self):
        """
        A defaultValue for port cannot be specified when the type of the Port is an Interface.

        .. ocl::
            type.oclIsKindOf(Interface) implies defaultValue->isEmpty()
        """
        pass

    def encapsulated_owner(self):
        """
        All Ports are owned by an EncapsulatedClassifier.

        .. ocl::
            owner = encapsulatedClassifier
        """
        pass

    def port_aggregation(self):
        """
        Port.aggregation must be composite.

        .. ocl::
            aggregation = AggregationKind::composite
        """
        pass

    def get_provided(self):
        """
        Derivation for Port::/provided

        .. ocl::
            result = (if isConjugated then basicRequired() else basicProvided() endif)
        """
        pass

    def get_required(self):
        """
        Derivation for Port::/required

        .. ocl::
            result = (if isConjugated then basicProvided() else basicRequired() endif)
        """
        pass

class RemoveVariableValueAction(models.Model):
    """
    A RemoveVariableValueAction is a WriteVariableAction that removes values from a Variables.
    """

    __package__ = 'UML.Actions'

    is_remove_duplicates = models.BooleanField(help_text='Specifies whether to remove duplicates of the value in ' +
                                               'nonunique Variables.')
    remove_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_remove_at', blank=True, null=True, 
                                  help_text='An InputPin that provides the position of an existing value to ' +
                                  'remove in ordered, nonunique Variables. The type of the removeAt InputPin is ' +
                                  'UnlimitedNatural, but the value cannot be zero or unlimited.')
    write_variable_action = models.OneToOneField('WriteVariableAction', on_delete=models.CASCADE, primary_key=True)

    def remove_at_and_value(self):
        """
        ReadVariableActions removing a value from ordered, non-unique Variables must have a single removeAt
        InputPin and no value InputPin, if isRemoveDuplicates is false. The removeAt InputPin must be of type
        Unlimited Natural with multiplicity 1..1. Otherwise, the Action has a value InputPin and no removeAt
        InputPin.

        .. ocl::
            if  variable.isOrdered and not variable.isUnique and not isRemoveDuplicates then 
              value = null and
              removeAt <> null and
              removeAt.type = UnlimitedNatural and
              removeAt.is(1,1)
            else
              removeAt = null and value <> null
            endif
        """
        pass

class UseCase(models.Model):
    """
    A UseCase specifies a set of actions performed by its subjects, which yields an observable result that is of
    value for one or more Actors or other stakeholders of each subject.
    """

    __package__ = 'UML.UseCases'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier', on_delete=models.CASCADE, primary_key=True)
    extend = models.ManyToManyField('Extend', related_name='%(app_label)s_%(class)s_extend', blank=True, 
                                    help_text='The Extend relationships owned by this UseCase.')
    include = models.ManyToManyField('Include', related_name='%(app_label)s_%(class)s_include', blank=True, 
                                     help_text='The Include relationships owned by this UseCase.')
    subject = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_subject', blank=True, 
                                     help_text='The subjects to which this UseCase applies. Each subject or its ' +
                                     'parts realize all the UseCases that apply to it.')

    def all_included_use_cases(self):
        """
        The query allIncludedUseCases() returns the transitive closure of all UseCases (directly or indirectly)
        included by this UseCase.

        .. ocl::
            result = (self.include.addition->union(self.include.addition->collect(uc | uc.allIncludedUseCases()))->asSet())
        """
        pass

    def binary_associations(self):
        """
        UseCases can only be involved in binary Associations.

        .. ocl::
            Association.allInstances()->forAll(a | a.memberEnd.type->includes(self) implies a.memberEnd->size() = 2)
        """
        pass

    def cannot_include_self(self):
        """
        A UseCase cannot include UseCases that directly or indirectly include it.

        .. ocl::
            not allIncludedUseCases()->includes(self)
        """
        pass

    def must_have_name(self):
        """
        A UseCase must have a name.

        .. ocl::
            name -> notEmpty ()
        """
        pass

    def no_association_to_use_case(self):
        """
        UseCases cannot have Associations to UseCases specifying the same subject.

        .. ocl::
            Association.allInstances()->forAll(a | a.memberEnd.type->includes(self) implies 
               (
               let usecases: Set(UseCase) = a.memberEnd.type->select(oclIsKindOf(UseCase))->collect(oclAsType(UseCase))->asSet() in
               usecases->size() > 1 implies usecases->collect(subject)->size() > 1
               )
            )
        """
        pass

class Actor(models.Model):
    """
    An Actor specifies a role played by a user or any other system that interacts with the subject.
    """

    __package__ = 'UML.UseCases'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier', on_delete=models.CASCADE, primary_key=True)

    def associations(self):
        """
        An Actor can only have Associations to UseCases, Components, and Classes. Furthermore these Associations
        must be binary.

        .. ocl::
            Association.allInstances()->forAll( a |
              a.memberEnd->collect(type)->includes(self) implies
              (
                a.memberEnd->size() = 2 and
                let actorEnd : Property = a.memberEnd->any(type = self) in
                  actorEnd.opposite.class.oclIsKindOf(UseCase) or
                  ( actorEnd.opposite.class.oclIsKindOf(Class) and not
                     actorEnd.opposite.class.oclIsKindOf(Behavior))
                  )
              )
        """
        pass

    def must_have_name(self):
        """
        An Actor must have a name.

        .. ocl::
            name->notEmpty()
        """
        pass

class Message(models.Model):
    """
    A Message defines a particular communication between Lifelines of an Interaction.
    """

    __package__ = 'UML.Interactions'

    argument = models.ManyToManyField('ValueSpecification', related_name='%(app_label)s_%(class)s_argument', blank=True, 
                                      help_text='The arguments of the Message.')
    connector = models.ForeignKey('Connector', related_name='%(app_label)s_%(class)s_connector', blank=True, null=True, 
                                  help_text='The Connector on which this Message is sent.')
    interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_interaction', null=True, 
                                    help_text='The enclosing Interaction owning the Message.')
    message_kind = models.ForeignKey('MessageKind', related_name='%(app_label)s_%(class)s_message_kind', null=True, 
                                     help_text='The derived kind of the Message (complete, lost, found, or ' +
                                     'unknown).')
    message_sort = models.ForeignKey('MessageSort', related_name='%(app_label)s_%(class)s_message_sort', null=True, default='synchCall', 
                                     help_text='The sort of communication reflected by the Message.')
    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    receive_event = models.ForeignKey('MessageEnd', related_name='%(app_label)s_%(class)s_receive_event', blank=True, null=True, 
                                      help_text='References the Receiving of the Message.')
    send_event = models.ForeignKey('MessageEnd', related_name='%(app_label)s_%(class)s_send_event', blank=True, null=True, 
                                   help_text='References the Sending of the Message.')
    signature = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, 
                                  help_text='The signature of the Message is the specification of its content. It ' +
                                  'refers either an Operation or a Signal.')

    def arguments(self):
        """
        Arguments of a Message must only be: i) attributes of the sending lifeline, ii) constants, iii) symbolic
        values (which are wildcard values representing any legal value), iv) explicit parameters of the
        enclosing Interaction, v) attributes of the class owning the Interaction.
        """
        pass

    def cannot_cross_boundaries(self):
        """
        Messages cannot cross boundaries of CombinedFragments or their operands.  This is true if and only if
        both MessageEnds are enclosed within the same InteractionFragment (i.e., an InteractionOperand or an
        Interaction).

        .. ocl::
            sendEvent->notEmpty() and receiveEvent->notEmpty() implies
            let sendEnclosingFrag : Set(InteractionFragment) = 
            sendEvent->asOrderedSet()->first().enclosingFragment()
            in 
            let receiveEnclosingFrag : Set(InteractionFragment) = 
            receiveEvent->asOrderedSet()->first().enclosingFragment()
            in  sendEnclosingFrag = receiveEnclosingFrag
        """
        pass

    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() specifies that any two Messages may coexist in the same Namespace,
        regardless of their names.

        .. ocl::
            result = (true)
        """
        pass

    def message_kind(self):
        """
        This query returns the MessageKind value for this Message.

        .. ocl::
            result = (messageKind)
        """
        pass

    def occurrence_specifications(self):
        """
        If the MessageEnds are both OccurrenceSpecifications, then the connector must go between the Parts
        represented by the Lifelines of the two MessageEnds.
        """
        pass

    def sending_receiving_message_event(self):
        """
        If the sendEvent and the receiveEvent of the same Message are on the same Lifeline, the sendEvent must
        be ordered before the receiveEvent.

        .. ocl::
            receiveEvent.oclIsKindOf(MessageOccurrenceSpecification)
            implies
            let f :  Lifeline = sendEvent->select(oclIsKindOf(MessageOccurrenceSpecification)).oclAsType(MessageOccurrenceSpecification)->asOrderedSet()->first().covered in
            f = receiveEvent->select(oclIsKindOf(MessageOccurrenceSpecification)).oclAsType(MessageOccurrenceSpecification)->asOrderedSet()->first().covered  implies
            f.events->indexOf(sendEvent.oclAsType(MessageOccurrenceSpecification)->asOrderedSet()->first() ) < 
            f.events->indexOf(receiveEvent.oclAsType(MessageOccurrenceSpecification)->asOrderedSet()->first() )
        """
        pass

    def signature_is_operation_reply(self):
        """
        In the case when a Message with messageSort reply has a non empty Operation signature, the arguments of
        the Message must correspond to the out, inout, and return parameters of the Operation. A Parameter
        corresponds to an Argument if the Argument is of the same Class or a specialization of that of the
        Parameter.

        .. ocl::
            (messageSort = MessageSort::reply) and signature.oclIsKindOf(Operation) implies 
             let replyParms : OrderedSet(Parameter) = signature.oclAsType(Operation).ownedParameter->
            select(direction = ParameterDirectionKind::inout or direction = ParameterDirectionKind::out or direction = ParameterDirectionKind::return)
            in replyParms->size() = self.argument->size() and
            self.argument->forAll( o: ValueSpecification | o.oclIsKindOf(Expression) and let e : Expression = o.oclAsType(Expression) in
            e.operand->notEmpty()  implies 
            let p : Parameter = replyParms->at(self.argument->indexOf(o)) in
            e.operand->asSequence()->first().type.oclAsType(Classifier).conformsTo(p.type.oclAsType(Classifier))
            )
        """
        pass

    def signature_is_operation_request(self):
        """
        In the case when a Message with messageSort synchCall or asynchCall has a non empty Operation signature,
        the arguments of the Message must correspond to the in and inout parameters of the Operation. A
        Parameter corresponds to an Argument if the Argument is of the same Class or a specialization of that of
        the Parameter.

        .. ocl::
            (messageSort = MessageSort::asynchCall or messageSort = MessageSort::synchCall) and signature.oclIsKindOf(Operation)  implies 
             let requestParms : OrderedSet(Parameter) = signature.oclAsType(Operation).ownedParameter->
             select(direction = ParameterDirectionKind::inout or direction = ParameterDirectionKind::_'in'  )
            in requestParms->size() = self.argument->size() and
            self.argument->forAll( o: ValueSpecification | 
            not (o.oclIsKindOf(Expression) and o.oclAsType(Expression).symbol->size()=0 and o.oclAsType(Expression).operand->isEmpty() ) implies 
            let p : Parameter = requestParms->at(self.argument->indexOf(o)) in
            o.type.oclAsType(Classifier).conformsTo(p.type.oclAsType(Classifier))
            )
        """
        pass

    def signature_is_signal(self):
        """
        In the case when the Message signature is a Signal, the arguments of the Message must correspond to the
        attributes of the Signal. A Message Argument corresponds to a Signal Attribute if the Argument is of the
        same Class or a specialization of that of the Attribute.

        .. ocl::
            (messageSort = MessageSort::asynchSignal ) and signature.oclIsKindOf(Signal) implies
               let signalAttributes : OrderedSet(Property) = signature.oclAsType(Signal).inheritedMember()->
                         select(n:NamedElement | n.oclIsTypeOf(Property))->collect(oclAsType(Property))->asOrderedSet()
               in signalAttributes->size() = self.argument->size()
               and self.argument->forAll( o: ValueSpecification |
                      not (o.oclIsKindOf(Expression)
                      and o.oclAsType(Expression).symbol->size()=0
                      and o.oclAsType(Expression).operand->isEmpty() ) implies
                          let p : Property = signalAttributes->at(self.argument->indexOf(o))
                          in o.type.oclAsType(Classifier).conformsTo(p.type.oclAsType(Classifier)))
        """
        pass

    def signature_refer_to(self):
        """
        The signature must either refer an Operation (in which case messageSort is either synchCall or
        asynchCall or reply) or a Signal (in which case messageSort is asynchSignal). The name of the
        NamedElement referenced by signature must be the same as that of the Message.

        .. ocl::
            signature->notEmpty() implies 
            ((signature.oclIsKindOf(Operation) and 
            (messageSort = MessageSort::asynchCall or messageSort = MessageSort::synchCall or messageSort = MessageSort::reply) 
            ) or (signature.oclIsKindOf(Signal)  and messageSort = MessageSort::asynchSignal )
             ) and name = signature.name
        """
        pass

class InteractionOperatorKind(models.Model):
    """
    InteractionOperatorKind is an enumeration designating the different kinds of operators of CombinedFragments.
    The InteractionOperand defines the type of operator of a CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)

class LiteralBoolean(models.Model):
    """
    A LiteralBoolean is a specification of a Boolean value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.BooleanField()

    def boolean_value(self):
        """
        The query booleanValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.

        .. ocl::
            result = (true)
        """
        pass

class PrimitiveType(models.Model):
    """
    A PrimitiveType defines a predefined DataType, without any substructure. A PrimitiveType may have an algebra
    and operations defined outside of UML, for example, mathematically.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType', on_delete=models.CASCADE, primary_key=True)

class TimeEvent(models.Model):
    """
    A TimeEvent is an Event that occurs at a specific point in time.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)
    is_relative = models.BooleanField(help_text='Specifies whether the TimeEvent is specified as an absolute or ' +
                                      'relative time.')
    when = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_when', null=True, 
                             help_text='Specifies the time of the TimeEvent.')

    def when_non_negative(self):
        """
        The ValueSpecification when must return a non-negative Integer.

        .. ocl::
            when.integerValue() >= 0
        """
        pass

class Interaction(models.Model):
    """
    An Interaction is a unit of Behavior that focuses on the observable exchange of information between
    connectable elements.
    """

    __package__ = 'UML.Interactions'

    action = models.ManyToManyField('Action', related_name='%(app_label)s_%(class)s_action', blank=True, 
                                    help_text='Actions owned by the Interaction.')
    behavior = models.OneToOneField('Behavior')
    formal_gate = models.ManyToManyField('Gate', related_name='%(app_label)s_%(class)s_formal_gate', blank=True, 
                                         help_text='Specifies the gates that form the message interface between ' +
                                         'this Interaction and any InteractionUses which reference it.')
    fragment = models.ManyToManyField('InteractionFragment', related_name='%(app_label)s_%(class)s_fragment', blank=True, 
                                      help_text='The ordered set of fragments in the Interaction.')
    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)

    def not_contained(self):
        """
        An Interaction instance must not be contained within another Interaction instance.

        .. ocl::
            enclosingInteraction->isEmpty()
        """
        pass

class CommunicationPath(models.Model):
    """
    A communication path is an association between two deployment targets, through which they are able to
    exchange signals and messages.
    """

    __package__ = 'UML.Deployments'

    association = models.OneToOneField('Association', on_delete=models.CASCADE, primary_key=True)

    def association_ends(self):
        """
        The association ends of a CommunicationPath are typed by DeploymentTargets.

        .. ocl::
            endType->forAll (oclIsKindOf(DeploymentTarget))
        """
        pass

class GeneralizationSet(models.Model):
    """
    A GeneralizationSet is a PackageableElement whose instances represent sets of Generalization relationships.
    """

    __package__ = 'UML.Classification'

    generalization = models.ManyToManyField('Generalization', related_name='%(app_label)s_%(class)s_generalization', blank=True, 
                                            help_text='Designates the instances of Generalization that are ' +
                                            'members of this GeneralizationSet.')
    is_covering = models.BooleanField(help_text='Indicates (via the associated Generalizations) whether or not ' +
                                      'the set of specific Classifiers are covering for a particular general ' +
                                      'classifier. When isCovering is true, every instance of a particular general ' +
                                      'Classifier is also an instance of at least one of its specific Classifiers ' +
                                      'for the GeneralizationSet. When isCovering is false, there are one or more ' +
                                      'instances of the particular general Classifier that are not instances of at ' +
                                      'least one of its specific Classifiers defined for the GeneralizationSet.')
    is_disjoint = models.BooleanField(help_text='Indicates whether or not the set of specific Classifiers in a ' +
                                      'Generalization relationship have instance in common. If isDisjoint is true, ' +
                                      'the specific Classifiers for a particular GeneralizationSet have no members ' +
                                      'in common; that is, their intersection is empty. If isDisjoint is false, ' +
                                      'the specific Classifiers in a particular GeneralizationSet have one or more ' +
                                      'members in common; that is, their intersection is not empty.')
    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    powertype = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_powertype', blank=True, null=True, 
                                  help_text='Designates the Classifier that is defined as the power type for the ' +
                                  'associated GeneralizationSet, if there is one.')

    def generalization_same_classifier(self):
        """
        Every Generalization associated with a particular GeneralizationSet must have the same general
        Classifier.

        .. ocl::
            generalization->collect(general)->asSet()->size() <= 1
        """
        pass

    def maps_to_generalization_set(self):
        """
        The Classifier that maps to a GeneralizationSet may neither be a specific nor a general Classifier in
        any of the Generalization relationships defined for that GeneralizationSet. In other words, a power type
        may not be an instance of itself nor may its instances be its subclasses.

        .. ocl::
            powertype <> null implies generalization->forAll( gen | 
                not (gen.general = powertype) and not gen.general.allParents()->includes(powertype) and not (gen.specific = powertype) and not powertype.allParents()->includes(gen.specific)
              )
        """
        pass

class AddStructuralFeatureValueAction(models.Model):
    """
    An AddStructuralFeatureValueAction is a WriteStructuralFeatureAction for adding values to a
    StructuralFeature.
    """

    __package__ = 'UML.Actions'

    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', blank=True, null=True, 
                                  help_text='The InputPin that gives the position at which to insert the value in ' +
                                  'an ordered StructuralFeature. The type of the insertAt InputPin is ' +
                                  'UnlimitedNatural, but the value cannot be zero. It is omitted for unordered ' +
                                  'StructuralFeatures.')
    is_replace_all = models.BooleanField(help_text='Specifies whether existing values of the StructuralFeature ' +
                                         'should be removed before adding the new value.')
    write_structural_feature_action = models.OneToOneField('WriteStructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)

    def insert_at_pin(self):
        """
        AddStructuralFeatureActions adding a value to ordered StructuralFeatures must have a single InputPin for
        the insertion point with type UnlimitedNatural and multiplicity of 1..1 if isReplaceAll=false, and must
        have no Input Pin for the insertion point when the StructuralFeature is unordered.

        .. ocl::
            if not structuralFeature.isOrdered then insertAt = null
            else 
              not isReplaceAll implies
              	insertAt<>null and 
              	insertAt->forAll(type=UnlimitedNatural and is(1,1.oclAsType(UnlimitedNatural)))
            endif
        """
        pass

    def required_value(self):
        """
        A value InputPin is required.

        .. ocl::
            value<>null
        """
        pass

class Device(models.Model):
    """
    A device is a physical computational resource with processing capability upon which artifacts may be
    deployed for execution. Devices may be complex (i.e., they may consist of other devices).
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node', on_delete=models.CASCADE, primary_key=True)

class Parameter(models.Model):
    """
    A Parameter is a specification of an argument used to pass information into or out of an invocation of a
    BehavioralFeature.  Parameters can be treated as ConnectableElements within Collaborations.
    """

    __package__ = 'UML.Classification'

    connectable_element = models.OneToOneField('ConnectableElement')
    default = models.CharField(max_length=255, blank=True, null=True, 
                               help_text='A String that represents a value to be used when no argument is ' +
                               'supplied for the Parameter.')
    default_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_default_value', blank=True, null=True, 
                                      help_text='Specifies a ValueSpecification that represents a value to be ' +
                                      'used when no argument is supplied for the Parameter.')
    direction = models.ForeignKey('ParameterDirectionKind', related_name='%(app_label)s_%(class)s_direction', null=True, default='in', 
                                  help_text='Indicates whether a parameter is being sent into or out of a ' +
                                  'behavioral element.')
    effect = models.ForeignKey('ParameterEffectKind', related_name='%(app_label)s_%(class)s_effect', blank=True, null=True, 
                               help_text='Specifies the effect that executions of the owner of the Parameter have ' +
                               'on objects passed in or out of the parameter.')
    is_exception = models.BooleanField(help_text='Tells whether an output parameter may emit a value to the ' +
                                       'exclusion of the other outputs.')
    is_stream = models.BooleanField(help_text='Tells whether an input parameter may accept values while its ' +
                                    'behavior is executing, or whether an output parameter may post values while ' +
                                    'the behavior is executing.')
    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation', blank=True, null=True, 
                                  help_text='The Operation owning this parameter.')

    def connector_end(self):
        """
        A Parameter may only be associated with a Connector end within the context of a Collaboration.

        .. ocl::
            end->notEmpty() implies collaboration->notEmpty()
        """
        pass

    def get_default(self):
        """
        Derivation for Parameter::/default

        .. ocl::
            result = (if self.type = String then defaultValue.stringValue() else null endif)
        """
        pass

    def in_and_out(self):
        """
        Only in and inout Parameters may have a delete effect. Only out, inout, and return Parameters may have a
        create effect.

        .. ocl::
            (effect = ParameterEffectKind::delete implies (direction = ParameterDirectionKind::_'in' or direction = ParameterDirectionKind::inout))
            and
            (effect = ParameterEffectKind::create implies (direction = ParameterDirectionKind::out or direction = ParameterDirectionKind::inout or direction = ParameterDirectionKind::return))
        """
        pass

    def not_exception(self):
        """
        An input Parameter cannot be an exception.

        .. ocl::
            isException implies (direction <> ParameterDirectionKind::_'in' and direction <> ParameterDirectionKind::inout)
        """
        pass

    def object_effect(self):
        """
        Parameters typed by DataTypes cannot have an effect.

        .. ocl::
            (type.oclIsKindOf(DataType)) implies (effect = null)
        """
        pass

    def reentrant_behaviors(self):
        """
        Reentrant behaviors cannot have stream Parameters.

        .. ocl::
            (isStream and behavior <> null) implies not behavior.isReentrant
        """
        pass

    def stream_and_exception(self):
        """
        A Parameter cannot be a stream and exception at the same time.

        .. ocl::
            not (isException and isStream)
        """
        pass

class ClearVariableAction(models.Model):
    """
    A ClearVariableAction is a VariableAction that removes all values of a Variable.
    """

    __package__ = 'UML.Actions'

    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)

class PartDecomposition(models.Model):
    """
    A PartDecomposition is a description of the internal Interactions of one Lifeline relative to an
    Interaction.
    """

    __package__ = 'UML.Interactions'

    interaction_use = models.OneToOneField('InteractionUse', on_delete=models.CASCADE, primary_key=True)

    def assume(self):
        """
        Assume that within Interaction X, Lifeline L is of class C and decomposed to D. Within X there is a
        sequence of constructs along L (such constructs are CombinedFragments, InteractionUse and (plain)
        OccurrenceSpecifications). Then a corresponding sequence of constructs must appear within D, matched
        one-to-one in the same order. i) CombinedFragment covering L are matched with an extra-global
        CombinedFragment in D. ii) An InteractionUse covering L is matched with a global (i.e., covering all
        Lifelines) InteractionUse in D. iii) A plain OccurrenceSpecification on L is considered an actualGate
        that must be matched by a formalGate of D.
        """
        pass

    def commutativity_of_decomposition(self):
        """
        Assume that within Interaction X, Lifeline L is of class C and decomposed to D. Assume also that there
        is within X an InteractionUse (say) U that covers L. According to the constraint above U will have a
        counterpart CU within D. Within the Interaction referenced by U, L should also be decomposed, and the
        decomposition should reference CU. (This rule is called commutativity of decomposition.)
        """
        pass

    def parts_of_internal_structures(self):
        """
        PartDecompositions apply only to Parts that are Parts of Internal Structures not to Parts of
        Collaborations.
        """
        pass

class ProtocolTransition(models.Model):
    """
    A ProtocolTransition specifies a legal Transition for an Operation. Transitions of ProtocolStateMachines
    have the following information: a pre-condition (guard), a Trigger, and a post-condition. Every
    ProtocolTransition is associated with at most one BehavioralFeature belonging to the context Classifier of
    the ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    post_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_post_condition', blank=True, null=True, 
                                       help_text='Specifies the post condition of the Transition which is the ' +
                                       'Condition that should be obtained once the Transition is triggered. This ' +
                                       'post condition is part of the post condition of the Operation connected to ' +
                                       'the Transition.')
    pre_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_pre_condition', blank=True, null=True, 
                                      help_text='Specifies the precondition of the Transition. It specifies the ' +
                                      'Condition that should be verified before triggering the Transition. This ' +
                                      'guard condition added to the source State will be evaluated as part of the ' +
                                      'precondition of the Operation referred by the Transition if any.')
    referred = models.ManyToManyField('Operation', related_name='%(app_label)s_%(class)s_referred', blank=True, 
                                      help_text='This association refers to the associated Operation. It is ' +
                                      'derived from the Operation of the CallEvent Trigger when applicable.')
    transition = models.OneToOneField('Transition', on_delete=models.CASCADE, primary_key=True)

    def associated_actions(self):
        """
        A ProtocolTransition never has associated Behaviors.

        .. ocl::
            effect = null
        """
        pass

    def belongs_to_psm(self):
        """
        A ProtocolTransition always belongs to a ProtocolStateMachine.

        .. ocl::
            container.belongsToPSM()
        """
        pass

    def get_referred(self):
        """
        Derivation for ProtocolTransition::/referred

        .. ocl::
            result = (trigger->collect(event)->select(oclIsKindOf(CallEvent))->collect(oclAsType(CallEvent).operation)->asSet())
        """
        pass

    def refers_to_operation(self):
        """
        If a ProtocolTransition refers to an Operation (i.e., has a CallEvent trigger corresponding to an
        Operation), then that Operation should apply to the context Classifier of the StateMachine of the
        ProtocolTransition.

        .. ocl::
            if (referred()->notEmpty() and containingStateMachine()._'context'->notEmpty()) then 
                containingStateMachine()._'context'.oclAsType(BehavioredClassifier).allFeatures()->includesAll(referred())
            else true endif
        """
        pass

class SendObjectAction(models.Model):
    """
    A SendObjectAction is an InvocationAction that transmits an input object to the target object, which is
    handled as a request message by the target object. The requestor continues execution immediately after the
    object is sent out and cannot receive reply values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    request = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_request', null=True, 
                                help_text='The request object, which is transmitted to the target object. The ' +
                                'object may be copied in transmission, so identity might not be preserved.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', null=True, 
                               help_text='The target object to which the object is sent.')

    def type_target_pin(self):
        """
        If onPort is not empty, the Port given by onPort must be an owned or inherited feature of the type of
        the target InputPin.

        .. ocl::
            onPort<>null implies target.type.oclAsType(Classifier).allFeatures()->includes(onPort)
        """
        pass

class DeploymentSpecification(models.Model):
    """
    A deployment specification specifies a set of properties that determine execution parameters of a component
    artifact that is deployed on a node. A deployment specification can be aimed at a specific type of
    container. An artifact that reifies or implements deployment specification properties is a deployment
    descriptor.
    """

    __package__ = 'UML.Deployments'

    artifact = models.OneToOneField('Artifact', on_delete=models.CASCADE, primary_key=True)
    deployment = models.ForeignKey('Deployment', related_name='%(app_label)s_%(class)s_deployment', blank=True, null=True, 
                                   help_text='The deployment with which the DeploymentSpecification is ' +
                                   'associated.')
    deployment_location = models.CharField(max_length=255, blank=True, null=True, 
                                           help_text='The location where an Artifact is deployed onto a Node. ' +
                                           'This is typically a "directory" or "memory address."')
    execution_location = models.CharField(max_length=255, blank=True, null=True, 
                                          help_text='The location where a component Artifact executes. This may ' +
                                          'be a local or remote location.')

    def deployed_elements(self):
        """
        The deployedElements of a DeploymentTarget that are involved in a Deployment that has an associated
        Deployment-Specification is a kind of Component (i.e., the configured components).

        .. ocl::
            deployment->forAll (location.deployedElement->forAll (oclIsKindOf(Component)))
        """
        pass

    def deployment_target(self):
        """
        The DeploymentTarget of a DeploymentSpecification is a kind of ExecutionEnvironment.

        .. ocl::
            deployment->forAll (location.oclIsKindOf(ExecutionEnvironment))
        """
        pass

class ExpansionNode(models.Model):
    """
    An ExpansionNode is an ObjectNode used to indicate a collection input or output for an ExpansionRegion. A
    collection input of an ExpansionRegion contains a collection that is broken into its individual elements
    inside the region, whose content is executed once per element. A collection output of an ExpansionRegion
    combines individual elements produced by the execution of the region into a collection for use outside the
    region.
    """

    __package__ = 'UML.Actions'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)
    region_as_input = models.ForeignKey('ExpansionRegion', related_name='%(app_label)s_%(class)s_region_as_input', blank=True, null=True, 
                                        help_text='The ExpansionRegion for which the ExpansionNode is an input.')
    region_as_output = models.ForeignKey('ExpansionRegion', related_name='%(app_label)s_%(class)s_region_as_output', blank=True, null=True, 
                                         help_text='The ExpansionRegion for which the ExpansionNode is an ' +
                                         'output.')

    def region_as_input_or_output(self):
        """
        One of regionAsInput or regionAsOutput must be non-empty, but not both.

        .. ocl::
            regionAsInput->notEmpty() xor regionAsOutput->notEmpty()
        """
        pass

class TimeExpression(models.Model):
    """
    A TimeExpression is a ValueSpecification that represents a time value.
    """

    __package__ = 'UML.Values'

    expr = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_expr', blank=True, null=True, 
                             help_text='A ValueSpecification that evaluates to the value of the TimeExpression.')
    observation = models.ManyToManyField('Observation', related_name='%(app_label)s_%(class)s_observation', blank=True, 
                                         help_text='Refers to the Observations that are involved in the ' +
                                         'computation of the TimeExpression value.')
    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)

    def no_expr_requires_observation(self):
        """
        If a TimeExpression has no expr, then it must have a single observation that is a TimeObservation.

        .. ocl::
            expr = null implies (observation->size() = 1 and observation->forAll(oclIsKindOf(TimeObservation)))
        """
        pass

class Generalization(models.Model):
    """
    A Generalization is a taxonomic relationship between a more general Classifier and a more specific
    Classifier. Each instance of the specific Classifier is also an instance of the general Classifier. The
    specific Classifier inherits the features of the more general Classifier. A Generalization is owned by the
    specific Classifier.
    """

    __package__ = 'UML.Classification'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    general = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_general', null=True, 
                                help_text='The general classifier in the Generalization relationship.')
    is_substitutable = models.BooleanField(blank=True, 
                                           help_text='Indicates whether the specific Classifier can be used ' +
                                           'wherever the general Classifier can be used. If true, the execution ' +
                                           'traces of the specific Classifier shall be a superset of the execution ' +
                                           'traces of the general Classifier. If false, there is no such ' +
                                           'constraint on execution traces. If unset, the modeler has not stated ' +
                                           'whether there is such a constraint or not.')
    specific = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_specific', null=True, 
                                 help_text='The specializing Classifier in the Generalization relationship.')

class ConnectableElementTemplateParameter(models.Model):
    """
    A ConnectableElementTemplateParameter exposes a ConnectableElement as a formal parameter for a template.
    """

    __package__ = 'UML.StructuredClassifiers'

    parametered_element = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_parametered_element', null=True, 
                                            help_text='The ConnectableElement for this ' +
                                            'ConnectableElementTemplateParameter.')
    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)

class ClassifierTemplateParameter(models.Model):
    """
    A ClassifierTemplateParameter exposes a Classifier as a formal template parameter.
    """

    __package__ = 'UML.Classification'

    allow_substitutable = models.BooleanField(help_text='Constrains the required relationship between an actual ' +
                                              'parameter and the parameteredElement for this formal parameter.')
    constraining_classifier = models.ManyToManyField('Classifier', related_name='%(app_label)s_%(class)s_constraining_classifier', blank=True, 
                                                     help_text='The classifiers that constrain the argument that ' +
                                                     'can be used for the parameter. If the allowSubstitutable ' +
                                                     'attribute is true, then any Classifier that is compatible ' +
                                                     'with this constraining Classifier can be substituted; ' +
                                                     'otherwise, it must be either this Classifier or one of its ' +
                                                     'specializations. If this property is empty, there are no ' +
                                                     'constraints on the Classifier that can be used as an ' +
                                                     'argument.')
    parametered_element = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_parametered_element', null=True, 
                                            help_text='The Classifier exposed by this ' +
                                            'ClassifierTemplateParameter.')
    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)

    def actual_is_classifier(self):
        """
        The argument to a ClassifierTemplateParameter is a Classifier.

        .. ocl::
            templateParameterSubstitution.actual->forAll(a | a.oclIsKindOf(Classifier))
        """
        pass

    def constraining_classifiers_constrain_args(self):
        """
        If there are any constrainingClassifiers, then every argument must be the same as or a specialization of
        them, or if allowSubstitutable is true, then it can also be substitutable.

        .. ocl::
            templateParameterSubstitution.actual->forAll( a |
              let arg : Classifier = a.oclAsType(Classifier) in
                constrainingClassifier->forAll(
                  cc |  
                     arg = cc or arg.conformsTo(cc) or (allowSubstitutable and arg.isSubstitutableFor(cc))
                  )
            )
        """
        pass

    def constraining_classifiers_constrain_parametered_element(self):
        """
        If there are any constrainingClassifiers, then the parameteredElement must be the same as or a
        specialization of them, or if allowSubstitutable is true, then it can also be substitutable.

        .. ocl::
            constrainingClassifier->forAll(
                 cc |  parameteredElement = cc or parameteredElement.conformsTo(cc) or (allowSubstitutable and parameteredElement.isSubstitutableFor(cc))
            )
        """
        pass

    def has_constraining_classifier(self):
        """
        If allowSubstitutable is true, then there must be a constrainingClassifier.

        .. ocl::
            allowSubstitutable implies constrainingClassifier->notEmpty()
        """
        pass

    def matching_abstract(self):
        """
        If the parameteredElement is not abstract, then the Classifier used as an argument shall not be
        abstract.

        .. ocl::
            (not parameteredElement.isAbstract) implies templateParameterSubstitution.actual->forAll(a | not a.oclAsType(Classifier).isAbstract)
        """
        pass

    def parametered_element_no_features(self):
        """
        The parameteredElement has no direct features, and if constrainedElement is empty it has no
        generalizations.

        .. ocl::
            parameteredElement.feature->isEmpty() and (constrainingClassifier->isEmpty() implies  parameteredElement.allParents()->isEmpty())
        """
        pass

class StringExpression(models.Model):
    """
    A StringExpression is an Expression that specifies a String value that is derived by concatenating a
    sequence of operands with String values or a sequence of subExpressions, some of which might be template
    parameters.
    """

    __package__ = 'UML.Values'

    expression = models.OneToOneField('Expression')
    owning_expression = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_owning_expression', blank=True, null=True, 
                                          help_text='The StringExpression of which this StringExpression is a ' +
                                          'subExpression.')
    sub_expression = models.ManyToManyField('self', related_name='%(app_label)s_%(class)s_sub_expression', blank=True, 
                                            help_text='The StringExpressions that constitute this ' +
                                            'StringExpression.')
    templateable_element = models.OneToOneField('TemplateableElement', on_delete=models.CASCADE, primary_key=True)

    def operands(self):
        """
        All the operands of a StringExpression must be LiteralStrings

        .. ocl::
            operand->forAll (oclIsKindOf (LiteralString))
        """
        pass

    def string_value(self):
        """
        The query stringValue() returns the String resulting from concatenating, in order, all the component
        String values of all the operands or subExpressions that are part of the StringExpression.

        .. ocl::
            result = (if subExpression->notEmpty()
            then subExpression->iterate(se; stringValue: String = '' | stringValue.concat(se.stringValue()))
            else operand->iterate(op; stringValue: String = '' | stringValue.concat(op.stringValue()))
            endif)
        """
        pass

    def subexpressions(self):
        """
        If a StringExpression has sub-expressions, it cannot have operands and vice versa (this avoids the
        problem of having to define a collating sequence between operands and subexpressions).

        .. ocl::
            if subExpression->notEmpty() then operand->isEmpty() else operand->notEmpty() endif
        """
        pass

class InterfaceRealization(models.Model):
    """
    An InterfaceRealization is a specialized realization relationship between a BehavioredClassifier and an
    Interface. This relationship signifies that the realizing BehavioredClassifier conforms to the contract
    specified by the Interface.
    """

    __package__ = 'UML.SimpleClassifiers'

    contract = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_contract', null=True, 
                                 help_text='References the Interface specifying the conformance contract.')
    implementing_classifier = models.ForeignKey('BehavioredClassifier', related_name='%(app_label)s_%(class)s_implementing_classifier', null=True, 
                                                help_text='References the BehavioredClassifier that owns this ' +
                                                'InterfaceRealization, i.e., the BehavioredClassifier that ' +
                                                'realizes the Interface to which it refers.')
    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)

class ExecutionOccurrenceSpecification(models.Model):
    """
    An ExecutionOccurrenceSpecification represents moments in time at which Actions or Behaviors start or
    finish.
    """

    __package__ = 'UML.Interactions'

    execution = models.ForeignKey('ExecutionSpecification', related_name='%(app_label)s_%(class)s_execution', null=True, 
                                  help_text='References the execution specification describing the execution that ' +
                                  'is started or finished at this execution event.')
    occurrence_specification = models.OneToOneField('OccurrenceSpecification', on_delete=models.CASCADE, primary_key=True)

class TemplateBinding(models.Model):
    """
    A TemplateBinding is a DirectedRelationship between a TemplateableElement and a template. A TemplateBinding
    specifies the TemplateParameterSubstitutions of actual parameters for the formal parameters of the template.
    """

    __package__ = 'UML.CommonStructure'

    bound_element = models.ForeignKey('TemplateableElement', related_name='%(app_label)s_%(class)s_bound_element', null=True, 
                                      help_text='The TemplateableElement that is bound by this TemplateBinding.')
    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    parameter_substitution = models.ManyToManyField('TemplateParameterSubstitution', related_name='%(app_label)s_%(class)s_parameter_substitution', blank=True, 
                                                    help_text='The TemplateParameterSubstitutions owned by this ' +
                                                    'TemplateBinding.')
    signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_signature', null=True, 
                                  help_text='The TemplateSignature for the template that is the target of this ' +
                                  'TemplateBinding.')

    def one_parameter_substitution(self):
        """
        A TemplateBiinding contains at most one TemplateParameterSubstitution for each formal TemplateParameter
        of the target TemplateSignature.

        .. ocl::
            signature.parameter->forAll(p | parameterSubstitution->select(b | b.formal = p)->size() <= 1)
        """
        pass

    def parameter_substitution_formal(self):
        """
        Each parameterSubstitution must refer to a formal TemplateParameter of the target TemplateSignature.

        .. ocl::
            parameterSubstitution->forAll(b | signature.parameter->includes(b.formal))
        """
        pass

class ReadVariableAction(models.Model):
    """
    A ReadVariableAction is a VariableAction that retrieves the values of a Variable.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', null=True, 
                               help_text='The OutputPin on which the result values are placed.')
    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)

    def compatible_multiplicity(self):
        """
        The multiplicity of the variable must be compatible with the multiplicity of the output pin.

        .. ocl::
            variable.compatibleWith(result)
        """
        pass

    def type_and_ordering(self):
        """
        The type and ordering of the result OutputPin are the same as the type and ordering of the variable.

        .. ocl::
            result.type =variable.type and 
            result.isOrdered = variable.isOrdered
        """
        pass