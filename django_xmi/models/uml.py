from django.db import models


class Element(models.Model):
    """
    An Element is a constituent of a model. As such, it has the capability of owning other Elements.
    """

    __package__ = 'UML.CommonStructure'

    owned_comment = models.ForeignKey('Comment', related_name='%(app_label)s_%(class)s_owned_comment', 
                                      help_text='The Comments owned by this Element.')
    owned_element = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_owned_element', 
                                      help_text='The Elements owned by this Element.')
    owner = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_owner', 
                              help_text='The Element that owns this Element.')

    def all_owned_elements(self):
        """
        The query allOwnedElements() gives all of the direct and indirect ownedElements of an Element.

        .. ocl::
            result = (ownedElement->union(ownedElement->collect(e | e.allOwnedElements()))->asSet())
        """
        pass


class NamedElement(models.Model):
    """
    A NamedElement is an Element in a model that may have a name. The name may be given directly and/or via the
    use of a StringExpression.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    client_dependency = models.ForeignKey('Dependency', related_name='%(app_label)s_%(class)s_client_dependency', 
                                          help_text='Indicates the Dependencies that reference this NamedElement ' +
                                          'as a client.')
    name = models.CharField(max_length=255, help_text='The name of the NamedElement.')
    name_expression = models.ForeignKey('StringExpression', related_name='%(app_label)s_%(class)s_name_expression', 
                                        help_text='The StringExpression used to define the name of this ' +
                                        'NamedElement.')
    namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_namespace+', 
                                  help_text='Specifies the Namespace that owns the NamedElement.')
    qualified_name = models.CharField(max_length=255, 
                                      help_text='A name that allows the NamedElement to be identified within a ' +
                                      'hierarchy of nested Namespaces. It is constructed from the names of the ' +
                                      'containing Namespaces starting at the root of the hierarchy and ending with ' +
                                      'the name of the NamedElement itself.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', 
                                   help_text='Determines whether and how the NamedElement is visible outside its ' +
                                   'owning Namespace.')

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


class Vertex(models.Model):
    """
    A Vertex is an abstraction of a node in a StateMachine graph. It can be the source or destination of any
    number of Transitions.
    """

    __package__ = 'UML.StateMachines'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    container = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_container', 
                                  help_text='The Region that contains this Vertex.')
    incoming = models.ForeignKey('Transition', related_name='%(app_label)s_%(class)s_incoming', 
                                 help_text='Specifies the Transitions entering this Vertex.')
    outgoing = models.ForeignKey('Transition', related_name='%(app_label)s_%(class)s_outgoing', 
                                 help_text='Specifies the Transitions departing from this Vertex.')

    def outgoing_operation(self):
        """
        Derivation for Vertex::/outgoing

        .. ocl::
            result = (Transition.allInstances()->select(source=self))
        """
        pass


class Pseudostate(models.Model):
    """
    A Pseudostate is an abstraction that encompasses different types of transient Vertices in the StateMachine
    graph. A StateMachine instance never comes to rest in a Pseudostate, instead, it will exit and enter the
    Pseudostate within a single run-to-completion step.
    """

    __package__ = 'UML.StateMachines'

    vertex = models.OneToOneField('Vertex', on_delete=models.CASCADE, primary_key=True)
    kind = models.ForeignKey('PseudostateKind', related_name='%(app_label)s_%(class)s_kind', 
                             help_text='Determines the precise type of the Pseudostate and can be one of: ' +
                             'entryPoint, exitPoint, initial, deepHistory, shallowHistory, join, fork, junction, ' +
                             'terminate or choice.')
    state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_state', 
                              help_text='The State that owns this Pseudostate and in which it appears.')
    state_machine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_state_machine', 
                                      help_text='The StateMachine in which this Pseudostate is defined. This only ' +
                                      'applies to Pseudostates of the kind entryPoint or exitPoint.')


class RedefinableElement(models.Model):
    """
    A RedefinableElement is an element that, when defined in the context of a Classifier, can be redefined more
    specifically or differently in the context of another Classifier that specializes (directly or indirectly)
    the context Classifier.
    """

    __package__ = 'UML.Classification'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    is_leaf = models.BooleanField(help_text='Indicates whether it is possible to further redefine a ' +
                                  'RedefinableElement. If the value is true, then it is not possible to further ' +
                                  'redefine the RedefinableElement.')
    redefined_element = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_element', 
                                          help_text='The RedefinableElement that is being redefined by this ' +
                                          'element.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', 
                                             help_text='The contexts that this element may be redefined from.')

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


class TemplateableElement(models.Model):
    """
    A TemplateableElement is an Element that can optionally be defined as a template and bound to other
    templates.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owned_template_signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_owned_template_signature', 
                                                 help_text='The optional TemplateSignature specifying the formal ' +
                                                 'TemplateParameters for this TemplateableElement. If a ' +
                                                 'TemplateableElement has a TemplateSignature, then it is a ' +
                                                 'template.')
    template_binding = models.ForeignKey('TemplateBinding', related_name='%(app_label)s_%(class)s_template_binding', 
                                         help_text='The optional TemplateBindings from this TemplateableElement ' +
                                         'to one or more templates.')

    def is_template(self):
        """
        The query isTemplate() returns whether this TemplateableElement is actually a template.

        .. ocl::
            result = (ownedTemplateSignature <> null)
        """
        pass


class Namespace(models.Model):
    """
    A Namespace is an Element in a model that owns and/or imports a set of NamedElements that can be identified
    by name.
    """

    __package__ = 'UML.CommonStructure'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    element_import = models.ForeignKey('ElementImport', related_name='%(app_label)s_%(class)s_element_import', 
                                       help_text='References the ElementImports owned by the Namespace.')
    imported_member = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_imported_member', 
                                        help_text='References the PackageableElements that are members of this ' +
                                        'Namespace as a result of either PackageImports or ElementImports.')
    member = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_member', 
                               help_text='A collection of NamedElements identifiable within the Namespace, either ' +
                               'by being owned or by being introduced by importing or inheritance.')
    owned_member = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_owned_member', 
                                     help_text='A collection of NamedElements owned by the Namespace.')
    owned_rule = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_owned_rule', 
                                   help_text='Specifies a set of Constraints owned by this Namespace.')
    package_import = models.ForeignKey('PackageImport', related_name='%(app_label)s_%(class)s_package_import', 
                                       help_text='References the PackageImports owned by the Namespace.')

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


class ParameterableElement(models.Model):
    """
    A ParameterableElement is an Element that can be exposed as a formal TemplateParameter for a template, or
    specified as an actual parameter in a binding of a template.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owning_template_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_owning_template_parameter', 
                                                  help_text='The formal TemplateParameter that owns this ' +
                                                  'ParameterableElement.')
    template_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', 
                                           help_text='The TemplateParameter that exposes this ' +
                                           'ParameterableElement as a formal parameter.')

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

    parameterable_element = models.OneToOneField('ParameterableElement', on_delete=models.CASCADE, primary_key=True)
    named_element = models.OneToOneField('NamedElement')

    def __init__(self, *args, **kwargs):
        if 'visibility' not in kwargs:
            kwargs['visibility'] = 'public'
        super(PackageableElement).__init__(*args, **kwargs)


class Type(models.Model):
    """
    A Type constrains the values represented by a TypedElement.
    """

    __package__ = 'UML.CommonStructure'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_package')

    def conforms_to(self):
        """
        The query conformsTo() gives true for a Type that conforms to another. By default, two Types do not
        conform to each other. This query is intended to be redefined for specific conformance situations.

        .. ocl::
            result = (false)
        """
        pass


class Classifier(models.Model):
    """
    A Classifier represents a classification of instances according to their Features.
    """

    __package__ = 'UML.Classification'

    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    has_type = models.OneToOneField('Type')
    templateable_element = models.OneToOneField('TemplateableElement')
    redefinable_element = models.OneToOneField('RedefinableElement')
    attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_attribute', 
                                  help_text='All of the Properties that are direct (i.e., not inherited or ' +
                                  'imported) attributes of the Classifier.')
    collaboration_use = models.ForeignKey('CollaborationUse', related_name='%(app_label)s_%(class)s_collaboration_use', 
                                          help_text='The CollaborationUses owned by the Classifier.')
    feature = models.ForeignKey('Feature', related_name='%(app_label)s_%(class)s_feature', 
                                help_text='Specifies each Feature directly defined in the classifier. Note that ' +
                                'there may be members of the Classifier that are of the type Feature but are not ' +
                                'included, e.g., inherited features.')
    general = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_general', 
                                help_text='The generalizing Classifiers for this Classifier.')
    generalization = models.ForeignKey('Generalization', related_name='%(app_label)s_%(class)s_generalization', 
                                       help_text='The Generalization relationships for this Classifier. These ' +
                                       'Generalizations navigate to more general Classifiers in the generalization ' +
                                       'hierarchy.')
    inherited_member = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_inherited_member', 
                                         help_text='All elements inherited by this Classifier from its general ' +
                                         'Classifiers.')
    is_abstract = models.BooleanField(help_text='If true, the Classifier can only be instantiated by ' +
                                      'instantiating one of its specializations. An abstract Classifier is ' +
                                      'intended to be used by other Classifiers e.g., as the target of ' +
                                      'Associations or Generalizations.')
    is_final_specialization = models.BooleanField(help_text='If true, the Classifier cannot be specialized.')
    owned_template_signature = models.ForeignKey('RedefinableTemplateSignature', related_name='%(app_label)s_%(class)s_owned_template_signature', 
                                                 help_text='The optional RedefinableTemplateSignature specifying ' +
                                                 'the formal template parameters.')
    owned_use_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_owned_use_case', 
                                       help_text='The UseCases owned by this classifier.')
    powertype_extent = models.ForeignKey('GeneralizationSet', related_name='%(app_label)s_%(class)s_powertype_extent', 
                                         help_text='The GeneralizationSet of which this Classifier is a power ' +
                                         'type.')
    redefined_classifier = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_classifier', 
                                             help_text='The Classifiers redefined by this Classifier.')
    representation = models.ForeignKey('CollaborationUse', related_name='%(app_label)s_%(class)s_representation', 
                                       help_text='A CollaborationUse which indicates the Collaboration that ' +
                                       'represents this Classifier.')
    substitution = models.ForeignKey('Substitution', related_name='%(app_label)s_%(class)s_substitution', 
                                     help_text='The Substitutions owned by this Classifier.')
    template_parameter = models.ForeignKey('ClassifierTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', 
                                           help_text='TheClassifierTemplateParameter that exposes this element as ' +
                                           'a formal parameter.')
    use_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_use_case', 
                                 help_text='The set of UseCases for which this Classifier is the subject.')

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


class BehavioredClassifier(models.Model):
    """
    A BehavioredClassifier may have InterfaceRealizations, and owns a set of Behaviors one of which may specify
    the behavior of the BehavioredClassifier itself.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    classifier_behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_classifier_behavior', 
                                            help_text='A Behavior that specifies the behavior of the ' +
                                            'BehavioredClassifier itself.')
    interface_realization = models.ForeignKey('InterfaceRealization', related_name='%(app_label)s_%(class)s_interface_realization', 
                                              help_text='The set of InterfaceRealizations owned by the ' +
                                              'BehavioredClassifier. Interface realizations reference the ' +
                                              'Interfaces of which the BehavioredClassifier is an implementation.')
    owned_behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_owned_behavior', 
                                       help_text='Behaviors owned by a BehavioredClassifier.')


class StructuredClassifier(models.Model):
    """
    StructuredClassifiers may contain an internal structure of connected elements each of which plays a role in
    the overall Behavior modeled by the StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute', 
                                        help_text='The Properties owned by the StructuredClassifier.')
    owned_connector = models.ForeignKey('Connector', related_name='%(app_label)s_%(class)s_owned_connector', 
                                        help_text='The connectors owned by the StructuredClassifier.')
    part = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_part', 
                             help_text='The Properties specifying instances that the StructuredClassifier owns by ' +
                             'composition. This collection is derived, selecting those owned Properties where ' +
                             'isComposite is true.')
    role = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_role', 
                             help_text='The roles that instances may play in this StructuredClassifier.')

    def all_roles(self):
        """
        All features of type ConnectableElement, equivalent to all direct and inherited roles.

        .. ocl::
            result = (allFeatures()->select(oclIsKindOf(ConnectableElement))->collect(oclAsType(ConnectableElement))->asSet())
        """
        pass


class EncapsulatedClassifier(models.Model):
    """
    An EncapsulatedClassifier may own Ports to specify typed interaction points.
    """

    __package__ = 'UML.StructuredClassifiers'

    structured_classifier = models.OneToOneField('StructuredClassifier', on_delete=models.CASCADE, primary_key=True)
    owned_port = models.ForeignKey('Port', related_name='%(app_label)s_%(class)s_owned_port')

    def owned_port_operation(self):
        """
        Derivation for EncapsulatedClassifier::/ownedPort : Port

        .. ocl::
            result = (ownedAttribute->select(oclIsKindOf(Port))->collect(oclAsType(Port))->asOrderedSet())
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
    extension = models.ForeignKey('Extension', related_name='%(app_label)s_%(class)s_extension', 
                                  help_text='This property is used when the Class is acting as a metaclass. It ' +
                                  'references the Extensions that specify additional properties of the metaclass. ' +
                                  'The property is derived from the Extensions whose memberEnds are typed by the ' +
                                  'Class.')
    is_active = models.BooleanField(help_text='Determines whether an object specified by this Class is active or ' +
                                    'not. If true, then the owning Class is referred to as an active Class. If ' +
                                    'false, then such a Class is referred to as a passive Class.')
    nested_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_nested_classifier', 
                                          help_text='The Classifiers owned by the Class that are not ' +
                                          'ownedBehaviors.')
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute', 
                                        help_text='The attributes (i.e., the Properties) owned by the Class.')
    owned_operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_owned_operation', 
                                        help_text='The Operations owned by the Class.')
    owned_reception = models.ForeignKey('Reception', related_name='%(app_label)s_%(class)s_owned_reception', 
                                        help_text='The Receptions owned by the Class.')
    super_class = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_super_class', 
                                    help_text='The superclasses of a Class, derived from its Generalizations.')

    def super_class_operation(self):
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
    icon = models.ForeignKey('Image', related_name='%(app_label)s_%(class)s_icon', 
                             help_text='Stereotype can change the graphical appearance of the extended model ' +
                             'element by using attached icons. When this association is not null, it references ' +
                             'the location of the icon content to be displayed within diagrams presenting the ' +
                             'extended model elements.')
    profile = models.ForeignKey('Profile', related_name='%(app_label)s_%(class)s_profile', 
                                help_text='The profile that directly or indirectly contains this stereotype.')

    def containing_profile(self):
        """
        The query containingProfile returns the closest profile directly or indirectly containing this
        stereotype.

        .. ocl::
            result = (self.namespace.oclAsType(Package).containingProfile())
        """
        pass


class DeploymentTarget(models.Model):
    """
    A deployment target is the location for a deployed artifact.
    """

    __package__ = 'UML.Deployments'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    deployed_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_deployed_element', 
                                         help_text='The set of elements that are manifested in an Artifact that ' +
                                         'is involved in Deployment to a DeploymentTarget.')
    deployment = models.ForeignKey('Deployment', related_name='%(app_label)s_%(class)s_deployment', 
                                   help_text='The set of Deployments for a DeploymentTarget.')

    def deployed_element_operation(self):
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

    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    deployment_target = models.OneToOneField('DeploymentTarget')
    nested_node = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_nested_node')


class ExecutionEnvironment(models.Model):
    """
    An execution environment is a node that offers an execution environment for specific types of components
    that are deployed on it in the form of executable artifacts.
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node', on_delete=models.CASCADE, primary_key=True)


class Constraint(models.Model):
    """
    A Constraint is a condition or restriction expressed in natural language text or in a machine readable
    language for the purpose of declaring some of the semantics of an Element or set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    constrained_element = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_constrained_element', 
                                            help_text='The ordered set of Elements referenced by this ' +
                                            'Constraint.')
    context = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_context', 
                                help_text='Specifies the Namespace that owns the Constraint.')
    specification = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_specification', 
                                      help_text='A condition that must be true when evaluated in order for the ' +
                                      'Constraint to be satisfied.')


class InteractionConstraint(models.Model):
    """
    An InteractionConstraint is a Boolean expression that guards an operand in a CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    constraint = models.OneToOneField('Constraint', on_delete=models.CASCADE, primary_key=True)
    maxint = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_maxint', 
                               help_text='The maximum number of iterations of a loop')
    minint = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_minint', 
                               help_text='The minimum number of iterations of a loop')


class ActivityNode(models.Model):
    """
    ActivityNode is an abstract class for points in the flow of an Activity connected by ActivityEdges.
    """

    __package__ = 'UML.Activities'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', 
                                 help_text='The Activity containing the ActivityNode, if it is directly owned by ' +
                                 'an Activity.')
    in_group = models.ForeignKey('ActivityGroup', related_name='%(app_label)s_%(class)s_in_group', 
                                 help_text='ActivityGroups containing the ActivityNode.')
    in_interruptible_region = models.ForeignKey('InterruptibleActivityRegion', related_name='%(app_label)s_%(class)s_in_interruptible_region', 
                                                help_text='InterruptibleActivityRegions containing the ' +
                                                'ActivityNode.')
    in_partition = models.ForeignKey('ActivityPartition', related_name='%(app_label)s_%(class)s_in_partition', 
                                     help_text='ActivityPartitions containing the ActivityNode.')
    in_structured_node = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_in_structured_node', 
                                           help_text='The StructuredActivityNode containing the ActvityNode, if ' +
                                           'it is directly owned by a StructuredActivityNode.')
    incoming = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_incoming', 
                                 help_text='ActivityEdges that have the ActivityNode as their target.')
    outgoing = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_outgoing', 
                                 help_text='ActivityEdges that have the ActivityNode as their source.')
    redefined_node = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_node', 
                                       help_text='ActivityNodes from a generalization of the Activity ' +
                                       'containining this ActivityNode that are redefined by this ActivityNode.')

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityNode.

        .. ocl::
            result = (if inStructuredNode<>null then inStructuredNode.containingActivity()
            else activity
            endif)
        """
        pass


class ExecutableNode(models.Model):
    """
    An ExecutableNode is an abstract class for ActivityNodes whose execution may be controlled using
    ControlFlows and to which ExceptionHandlers may be attached.
    """

    __package__ = 'UML.Activities'

    activity_node = models.OneToOneField('ActivityNode', on_delete=models.CASCADE, primary_key=True)
    handler = models.ForeignKey('ExceptionHandler', related_name='%(app_label)s_%(class)s_handler')


class Action(models.Model):
    """
    An Action is the fundamental unit of executable functionality. The execution of an Action represents some
    transformation or processing in the modeled system. Actions provide the ExecutableNodes within Activities
    and may also be used within Interactions.
    """

    __package__ = 'UML.Actions'

    executable_node = models.OneToOneField('ExecutableNode', on_delete=models.CASCADE, primary_key=True)
    context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_context', 
                                help_text='The context Classifier of the Behavior that contains this Action, or ' +
                                'the Behavior itself if it has no context.')
    has_input = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_input', 
                                  help_text='The ordered set of InputPins representing the inputs to the Action.')
    is_locally_reentrant = models.BooleanField(help_text='If true, the Action can begin a new, concurrent ' +
                                               'execution, even if there is already another execution of the ' +
                                               'Action ongoing. If false, the Action cannot begin a new execution ' +
                                               'until any previous execution has completed.')
    local_postcondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_local_postcondition', 
                                            help_text='A Constraint that must be satisfied when execution of the ' +
                                            'Action is completed.')
    local_precondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_local_precondition', 
                                           help_text='A Constraint that must be satisfied when execution of the ' +
                                           'Action is started.')
    output = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_output', 
                               help_text='The ordered set of OutputPins representing outputs from the Action.')

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


class ReduceAction(models.Model):
    """
    A ReduceAction is an Action that reduces a collection to a single value by repeatedly combining the elements
    of the collection using a reducer Behavior.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    collection = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_collection', 
                                   help_text='The InputPin that provides the collection to be reduced.')
    is_ordered = models.BooleanField(help_text='Indicates whether the order of the input collection should ' +
                                     'determine the order in which the reducer Behavior is applied to its ' +
                                     'elements.')
    reducer = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_reducer', 
                                help_text='A Behavior that is repreatedly applied to two elements of the input ' +
                                'collection to produce a value that is of the same type as elements of the ' +
                                'collection.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The output pin on which the result value is placed.')


class TemplateParameter(models.Model):
    """
    A TemplateParameter exposes a ParameterableElement as a formal parameter of a template.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    default = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_default', 
                                help_text='The ParameterableElement that is the default for this formal ' +
                                'TemplateParameter.')
    owned_default = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_default', 
                                      help_text='The ParameterableElement that is owned by this TemplateParameter ' +
                                      'for the purpose of providing a default.')
    owned_parametered_element = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_parametered_element', 
                                                  help_text='The ParameterableElement that is owned by this ' +
                                                  'TemplateParameter for the purpose of exposing it as the ' +
                                                  'parameteredElement.')
    parametered_element = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_parametered_element', 
                                            help_text='The ParameterableElement exposed by this ' +
                                            'TemplateParameter.')
    signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_signature', 
                                  help_text='The TemplateSignature that owns this TemplateParameter.')


class ClassifierTemplateParameter(models.Model):
    """
    A ClassifierTemplateParameter exposes a Classifier as a formal template parameter.
    """

    __package__ = 'UML.Classification'

    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)
    allow_substitutable = models.BooleanField(help_text='Constrains the required relationship between an actual ' +
                                              'parameter and the parameteredElement for this formal parameter.')
    constraining_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_constraining_classifier', 
                                                help_text='The classifiers that constrain the argument that can ' +
                                                'be used for the parameter. If the allowSubstitutable attribute is ' +
                                                'true, then any Classifier that is compatible with this ' +
                                                'constraining Classifier can be substituted; otherwise, it must be ' +
                                                'either this Classifier or one of its specializations. If this ' +
                                                'property is empty, there are no constraints on the Classifier ' +
                                                'that can be used as an argument.')
    parametered_element = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_parametered_element', 
                                            help_text='The Classifier exposed by this ' +
                                            'ClassifierTemplateParameter.')


class DataType(models.Model):
    """
    A DataType is a type whose instances are identified only by their value.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute', 
                                        help_text='The attributes owned by the DataType.')
    owned_operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_owned_operation', 
                                        help_text='The Operations owned by the DataType.')


class Enumeration(models.Model):
    """
    An Enumeration is a DataType whose values are enumerated in the model as EnumerationLiterals.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType', on_delete=models.CASCADE, primary_key=True)
    owned_literal = models.ForeignKey('EnumerationLiteral', related_name='%(app_label)s_%(class)s_owned_literal')


class MessageSort(models.Model):
    """
    This is an enumerated type that identifies the type of communication action that was used to generate the
    Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    ASYNCHCALL = 'asynchcall'
    CREATEMESSAGE = 'createmessage'
    REPLY = 'reply'
    SYNCHCALL = 'synchcall'
    ASYNCHSIGNAL = 'asynchsignal'
    DELETEMESSAGE = 'deletemessage'
    CHOICES = (
        (ASYNCHCALL, 'The message was generated by an asynchronous call to an operation; ' +
                     'i.e., a CallAction with isSynchronous = false.'),
        (CREATEMESSAGE, 'The message designating the creation of another lifeline ' +
                        'object.'),
        (REPLY, 'The message is a reply message to an operation call.'),
        (SYNCHCALL, 'The message was generated by a synchronous call to an operation.'),
        (ASYNCHSIGNAL, 'The message was generated by an asynchronous send action.'),
        (DELETEMESSAGE, 'The message designating the termination of another lifeline.'),
    )

    message_sort = models.CharField(max_length=255, choices=CHOICES, default=DELETEMESSAGE)


class TypedElement(models.Model):
    """
    A TypedElement is a NamedElement that may have a Type specified for it.
    """

    __package__ = 'UML.CommonStructure'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    has_type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_has_type')


class ValueSpecification(models.Model):
    """
    A ValueSpecification is the specification of a (possibly empty) set of values. A ValueSpecification is a
    ParameterableElement that may be exposed as a formal TemplateParameter and provided as the actual parameter
    in the binding of a template.
    """

    __package__ = 'UML.Values'

    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')

    def unlimited_value(self):
        """
        The query unlimitedValue() gives a single UnlimitedNatural value when one can be computed.

        .. ocl::
            result = (null)
        """
        pass


class Relationship(models.Model):
    """
    Relationship is an abstract concept that specifies some kind of relationship between Elements.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    related_element = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_related_element')


class Association(models.Model):
    """
    A link is a tuple of values that refer to typed objects.  An Association classifies a set of links, each of
    which is an instance of the Association.  Each value in the link refers to an instance of the type of the
    corresponding end of the Association.
    """

    __package__ = 'UML.StructuredClassifiers'

    relationship = models.OneToOneField('Relationship', on_delete=models.CASCADE, primary_key=True)
    classifier = models.OneToOneField('Classifier')
    end_type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_end_type', 
                                 help_text='The Classifiers that are used as types of the ends of the ' +
                                 'Association.')
    is_derived = models.BooleanField(help_text='Specifies whether the Association is derived from other model ' +
                                     'elements such as other Associations.')
    member_end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_member_end', 
                                   help_text='Each end represents participation of instances of the Classifier ' +
                                   'connected to the end in links of the Association.')
    navigable_owned_end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_navigable_owned_end', 
                                            help_text='The navigable ends that are owned by the Association ' +
                                            'itself.')
    owned_end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_end', 
                                  help_text='The ends that are owned by the Association itself.')

    def end_type_operation(self):
        """
        endType is derived from the types of the member ends.

        .. ocl::
            result = (memberEnd->collect(type)->asSet())
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

    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    association = models.OneToOneField('Association')


class Region(models.Model):
    """
    A Region is a top-level part of a StateMachine or a composite State, that serves as a container for the
    Vertices and Transitions of the StateMachine. A StateMachine or composite State may contain multiple Regions
    representing behaviors that may occur in parallel.
    """

    __package__ = 'UML.StateMachines'

    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    redefinable_element = models.OneToOneField('RedefinableElement')
    extended_region = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_extended_region', 
                                        help_text='The region of which this region is an extension.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_state', 
                              help_text='The State that owns the Region. If a Region is owned by a State, then it ' +
                              'cannot also be owned by a StateMachine.')
    state_machine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_state_machine', 
                                      help_text='The StateMachine that owns the Region. If a Region is owned by a ' +
                                      'StateMachine, then it cannot also be owned by a State.')
    subvertex = models.ForeignKey('Vertex', related_name='%(app_label)s_%(class)s_subvertex', 
                                  help_text='The set of Vertices that are owned by this Region.')
    transition = models.ForeignKey('Transition', related_name='%(app_label)s_%(class)s_transition', 
                                   help_text='The set of Transitions owned by the Region.')

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


class Package(models.Model):
    """
    A package can have one or more profile applications to indicate which profiles have been applied. Because a
    profile is a package, it is possible to apply a profile not only to packages, but also to profiles. Package
    specializes TemplateableElement and PackageableElement specializes ParameterableElement to specify that a
    package can be used as a template and a PackageableElement as a template parameter. A package is used to
    group elements, and provides a namespace for the grouped elements.
    """

    __package__ = 'UML.Packages'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    templateable_element = models.OneToOneField('TemplateableElement')
    namespace = models.OneToOneField('Namespace')
    uri = models.CharField(max_length=255, 
                           help_text='Provides an identifier for the package that can be used for many purposes. ' +
                           'A URI is the universally unique identification of the package following the IETF URI ' +
                           'specification, RFC 2396 http://www.ietf.org/rfc/rfc2396.txt and it must comply with ' +
                           'those syntax rules.')
    nested_package = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_nested_package', 
                                       help_text='References the packaged elements that are Packages.')
    nesting_package = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_nesting_package', 
                                        help_text='References the Package that owns this Package.')
    owned_stereotype = models.ForeignKey('Stereotype', related_name='%(app_label)s_%(class)s_owned_stereotype', 
                                         help_text='References the Stereotypes that are owned by the Package.')
    owned_type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_owned_type', 
                                   help_text='References the packaged elements that are Types.')
    package_merge = models.ForeignKey('PackageMerge', related_name='%(app_label)s_%(class)s_package_merge', 
                                      help_text='References the PackageMerges that are owned by this Package.')
    packaged_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_packaged_element', 
                                         help_text='Specifies the packageable elements that are owned by this ' +
                                         'Package.')
    profile_application = models.ForeignKey('ProfileApplication', related_name='%(app_label)s_%(class)s_profile_application', 
                                            help_text='References the ProfileApplications that indicate which ' +
                                            'profiles have been applied to the Package.')

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


class LinkAction(models.Model):
    """
    LinkAction is an abstract class for all Actions that identify the links to be acted on using LinkEndData.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    end_data = models.ForeignKey('LinkEndData', related_name='%(app_label)s_%(class)s_end_data', 
                                 help_text='The LinkEndData identifying the values on the ends of the links ' +
                                 'acting on by this LinkAction.')
    input_value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_input_value', 
                                    help_text='InputPins used by the LinkEndData of the LinkAction.')

    def association(self):
        """
        Returns the Association acted on by this LinkAction.

        .. ocl::
            result = (endData->asSequence()->first().end.association)
        """
        pass


class Observation(models.Model):
    """
    Observation specifies a value determined by observing an event or events that occur relative to other model
    Elements.
    """

    __package__ = 'UML.Values'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)


class DurationObservation(models.Model):
    """
    A DurationObservation is a reference to a duration during an execution. It points out the NamedElement(s) in
    the model to observe and whether the observations are when this NamedElement is entered or when it is
    exited.
    """

    __package__ = 'UML.Values'

    observation = models.OneToOneField('Observation', on_delete=models.CASCADE, primary_key=True)
    event = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_event', 
                              help_text='The DurationObservation is determined as the duration between the ' +
                              'entering or exiting of a single event Element during execution, or the ' +
                              'entering/exiting of one event Element and the entering/exiting of a second.')
    first_event = models.BooleanField(help_text='The value of firstEvent[i] is related to event[i] (where i is 1 ' +
                                      'or 2). If firstEvent[i] is true, then the corresponding observation event ' +
                                      'is the first time instant the execution enters event[i]. If firstEvent[i] ' +
                                      'is false, then the corresponding observation event is the time instant the ' +
                                      'execution exits event[i].')


class VariableAction(models.Model):
    """
    VariableAction is an abstract class for Actions that operate on a specified Variable.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    variable = models.ForeignKey('Variable', related_name='%(app_label)s_%(class)s_variable')


class InteractionFragment(models.Model):
    """
    InteractionFragment is an abstract notion of the most general interaction unit. An InteractionFragment is a
    piece of an Interaction. Each InteractionFragment is conceptually like an Interaction by itself.
    """

    __package__ = 'UML.Interactions'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    covered = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_covered', 
                                help_text='References the Lifelines that the InteractionFragment involves.')
    enclosing_interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_enclosing_interaction', 
                                              help_text='The Interaction enclosing this InteractionFragment.')
    enclosing_operand = models.ForeignKey('InteractionOperand', related_name='%(app_label)s_%(class)s_enclosing_operand', 
                                          help_text='The operand enclosing this InteractionFragment (they may ' +
                                          'nest recursively).')
    general_ordering = models.ForeignKey('GeneralOrdering', related_name='%(app_label)s_%(class)s_general_ordering', 
                                         help_text='The general ordering relationships contained in this ' +
                                         'fragment.')


class InteractionUse(models.Model):
    """
    An InteractionUse refers to an Interaction. The InteractionUse is a shorthand for copying the contents of
    the referenced Interaction where the InteractionUse is. To be accurate the copying must take into account
    substituting parameters with arguments and connect the formal Gates with the actual ones.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    actual_gate = models.ForeignKey('Gate', related_name='%(app_label)s_%(class)s_actual_gate', 
                                    help_text='The actual gates of the InteractionUse.')
    argument = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_argument', 
                                 help_text='The actual arguments of the Interaction.')
    refers_to = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_refers_to', 
                                  help_text='Refers to the Interaction that defines its meaning.')
    return_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_return_value', 
                                     help_text='The value of the executed Interaction.')
    return_value_recipient = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_return_value_recipient', 
                                               help_text='The recipient of the return value.')


class Profile(models.Model):
    """
    A profile defines limited extensions to a reference metamodel with the purpose of adapting the metamodel to
    a specific platform or domain.
    """

    __package__ = 'UML.Packages'

    package = models.OneToOneField('Package', on_delete=models.CASCADE, primary_key=True)
    metaclass_reference = models.ForeignKey('ElementImport', related_name='%(app_label)s_%(class)s_metaclass_reference', 
                                            help_text='References a metaclass that may be extended.')
    metamodel_reference = models.ForeignKey('PackageImport', related_name='%(app_label)s_%(class)s_metamodel_reference', 
                                            help_text='References a package containing (directly or indirectly) ' +
                                            'metaclasses that may be extended.')


class IntervalConstraint(models.Model):
    """
    An IntervalConstraint is a Constraint that is specified by an Interval.
    """

    __package__ = 'UML.Values'

    constraint = models.OneToOneField('Constraint', on_delete=models.CASCADE, primary_key=True)
    specification = models.ForeignKey('Interval', related_name='%(app_label)s_%(class)s_specification')


class TimeConstraint(models.Model):
    """
    A TimeConstraint is a Constraint that refers to a TimeInterval.
    """

    __package__ = 'UML.Values'

    interval_constraint = models.OneToOneField('IntervalConstraint', on_delete=models.CASCADE, primary_key=True)
    first_event = models.BooleanField(help_text='The value of firstEvent is related to the constrainedElement. If ' +
                                      'firstEvent is true, then the corresponding observation event is the first ' +
                                      'time instant the execution enters the constrainedElement. If firstEvent is ' +
                                      'false, then the corresponding observation event is the last time instant ' +
                                      'the execution is within the constrainedElement.')
    specification = models.ForeignKey('TimeInterval', related_name='%(app_label)s_%(class)s_specification', 
                                      help_text='TheTimeInterval constraining the duration.')


class Interval(models.Model):
    """
    An Interval defines the range between two ValueSpecifications.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    has_max = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_has_max', 
                                help_text='Refers to the ValueSpecification denoting the maximum value of the ' +
                                'range.')
    has_min = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_has_min', 
                                help_text='Refers to the ValueSpecification denoting the minimum value of the ' +
                                'range.')


class ControlNode(models.Model):
    """
    A ControlNode is an abstract ActivityNode that coordinates flows in an Activity.
    """

    __package__ = 'UML.Activities'

    activity_node = models.OneToOneField('ActivityNode', on_delete=models.CASCADE, primary_key=True)


class ForkNode(models.Model):
    """
    A ForkNode is a ControlNode that splits a flow into multiple concurrent flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)


class Behavior(models.Model):
    """
    Behavior is a specification of how its context BehavioredClassifier changes state over time. This
    specification may be either a definition of possible behavior execution or emergent behavior, or a selective
    illustration of an interesting subset of possible executions. The latter form is typically used for
    capturing examples, such as a trace of a particular execution.
    """

    __package__ = 'UML.CommonBehavior'

    has_class = models.OneToOneField('Class', on_delete=models.CASCADE, primary_key=True)
    context = models.ForeignKey('BehavioredClassifier', related_name='%(app_label)s_%(class)s_context', 
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
    is_reentrant = models.BooleanField(help_text='Tells whether the Behavior can be invoked while it is still ' +
                                       'executing from a previous invocation.')
    owned_parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', 
                                        help_text='References a list of Parameters to the Behavior which ' +
                                        'describes the order and type of arguments that can be given when the ' +
                                        'Behavior is invoked and of the values which will be returned when the ' +
                                        'Behavior completes its execution.')
    owned_parameter_set = models.ForeignKey('ParameterSet', related_name='%(app_label)s_%(class)s_owned_parameter_set', 
                                            help_text='The ParameterSets owned by this Behavior.')
    postcondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_postcondition', 
                                      help_text='An optional set of Constraints specifying what is fulfilled ' +
                                      'after the execution of the Behavior is completed, if its precondition was ' +
                                      'fulfilled before its invocation.')
    precondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_precondition', 
                                     help_text='An optional set of Constraints specifying what must be fulfilled ' +
                                     'before the Behavior is invoked.')
    redefined_behavior = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_behavior', 
                                           help_text='References the Behavior that this Behavior redefines. A ' +
                                           'subtype of Behavior may redefine any other subtype of Behavior. If the ' +
                                           'Behavior implements a BehavioralFeature, it replaces the redefined ' +
                                           'Behavior. If the Behavior is a classifierBehavior, it extends the ' +
                                           'redefined Behavior.')
    specification = models.ForeignKey('BehavioralFeature', related_name='%(app_label)s_%(class)s_specification', 
                                      help_text='Designates a BehavioralFeature that the Behavior implements. The ' +
                                      'BehavioralFeature must be owned by the BehavioredClassifier that owns the ' +
                                      'Behavior or be inherited by it. The Parameters of the BehavioralFeature and ' +
                                      'the implementing Behavior must match. A Behavior does not need to have a ' +
                                      'specification, in which case it either is the classifierBehavior of a ' +
                                      'BehavioredClassifier or it can only be invoked by another Behavior of the ' +
                                      'Classifier.')

    def output_parameters(self):
        """
        The out, inout and return ownedParameters.

        .. ocl::
            result = (ownedParameter->select(direction=ParameterDirectionKind::out or direction=ParameterDirectionKind::inout or direction=ParameterDirectionKind::return))
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
    connection_point = models.ForeignKey('Pseudostate', related_name='%(app_label)s_%(class)s_connection_point', 
                                         help_text='The connection points defined for this StateMachine. They ' +
                                         'represent the interface of the StateMachine when used as part of ' +
                                         'submachine State')
    extended_state_machine = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_extended_state_machine', 
                                               help_text='The StateMachines of which this is an extension.')
    region = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_region', 
                               help_text='The Regions owned directly by the StateMachine.')
    submachine_state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_submachine_state', 
                                         help_text='References the submachine(s) in case of a submachine State. ' +
                                         'Multiple machines are referenced in case of a concurrent State.')

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


class Comment(models.Model):
    """
    A Comment is a textual annotation that can be attached to a set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    annotated_element = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_annotated_element', 
                                          help_text='References the Element(s) being commented.')
    body = models.CharField(max_length=255, help_text='Specifies a string that is the comment.')


class UnmarshallAction(models.Model):
    """
    An UnmarshallAction is an Action that retrieves the values of the StructuralFeatures of an object and places
    them on OutputPins.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin that gives the object to be unmarshalled.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPins on which are placed the values of the StructuralFeatures ' +
                               'of the input object.')
    unmarshall_type = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_unmarshall_type', 
                                        help_text='The type of the object to be unmarshalled.')


class GeneralOrdering(models.Model):
    """
    A GeneralOrdering represents a binary relation between two OccurrenceSpecifications, to describe that one
    OccurrenceSpecification must occur before the other in a valid trace. This mechanism provides the ability to
    define partial orders of OccurrenceSpecifications that may otherwise not have a specified order.
    """

    __package__ = 'UML.Interactions'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    after = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_after', 
                              help_text='The OccurrenceSpecification referenced comes after the ' +
                              'OccurrenceSpecification referenced by before.')
    before = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_before', 
                               help_text='The OccurrenceSpecification referenced comes before the ' +
                               'OccurrenceSpecification referenced by after.')


class QualifierValue(models.Model):
    """
    A QualifierValue is an Element that is used as part of LinkEndData to provide the value for a single
    qualifier of the end given by the LinkEndData.
    """

    __package__ = 'UML.Actions'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    qualifier = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_qualifier', 
                                  help_text='The qualifier Property for which the value is to be specified.')
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', 
                              help_text='The InputPin from which the specified value for the qualifier is taken.')


class StructuralFeatureAction(models.Model):
    """
    StructuralFeatureAction is an abstract class for all Actions that operate on StructuralFeatures.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin from which the object whose StructuralFeature is to be ' +
                                   'read or written is obtained.')
    structural_feature = models.ForeignKey('StructuralFeature', related_name='%(app_label)s_%(class)s_structural_feature', 
                                           help_text='The StructuralFeature to be read or written.')


class ObjectNode(models.Model):
    """
    An ObjectNode is an abstract ActivityNode that may hold tokens within the object flow in an Activity.
    ObjectNodes also support token selection, limitation on the number of tokens held, specification of the
    state required for tokens being held, and carrying control values.
    """

    __package__ = 'UML.Activities'

    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)
    activity_node = models.OneToOneField('ActivityNode')
    in_state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_in_state', 
                                 help_text='The States required to be associated with the values held by tokens ' +
                                 'on this ObjectNode.')
    is_control_type = models.BooleanField(help_text='Indicates whether the type of the ObjectNode is to be ' +
                                          'treated as representing control values that may traverse ControlFlows.')
    ordering = models.ForeignKey('ObjectNodeOrderingKind', related_name='%(app_label)s_%(class)s_ordering', 
                                 help_text='Indicates how the tokens held by the ObjectNode are ordered for ' +
                                 'selection to traverse ActivityEdges outgoing from the ObjectNode.')
    selection = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_selection', 
                                  help_text='A Behavior used to select tokens to be offered on outgoing ' +
                                  'ActivityEdges.')
    upper_bound = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_upper_bound', 
                                    help_text='The maximum number of tokens that may be held by this ObjectNode. ' +
                                    'Tokens cannot flow into the ObjectNode if the upperBound is reached. If no ' +
                                    'upperBound is specified, then there is no limit on how many tokens the ' +
                                    'ObjectNode can hold.')


class ActivityParameterNode(models.Model):
    """
    An ActivityParameterNode is an ObjectNode for accepting values from the input Parameters or providing values
    to the output Parameters of an Activity.
    """

    __package__ = 'UML.Activities'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)
    parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_parameter')


class MessageEnd(models.Model):
    """
    MessageEnd is an abstract specialization of NamedElement that represents what can occur at the end of a
    Message.
    """

    __package__ = 'UML.Interactions'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    message = models.ForeignKey('Message', related_name='%(app_label)s_%(class)s_message')

    def is_receive(self):
        """
        This query returns value true if this MessageEnd is a receiveEvent.
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


class CommunicationPath(models.Model):
    """
    A communication path is an association between two deployment targets, through which they are able to
    exchange signals and messages.
    """

    __package__ = 'UML.Deployments'

    association = models.OneToOneField('Association', on_delete=models.CASCADE, primary_key=True)


class AcceptEventAction(models.Model):
    """
    An AcceptEventAction is an Action that waits for the occurrence of one or more specific Events.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    is_unmarshall = models.BooleanField(help_text='Indicates whether there is a single OutputPin for a ' +
                                        'SignalEvent occurrence, or multiple OutputPins for attribute values of ' +
                                        'the instance of the Signal associated with a SignalEvent occurrence.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='OutputPins holding the values received from an Event occurrence.')
    trigger = models.ForeignKey('Trigger', related_name='%(app_label)s_%(class)s_trigger', 
                                help_text='The Triggers specifying the Events of which the AcceptEventAction ' +
                                'waits for occurrences.')


class DurationInterval(models.Model):
    """
    A DurationInterval defines the range between two Durations.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval', on_delete=models.CASCADE, primary_key=True)
    has_max = models.ForeignKey('Duration', related_name='%(app_label)s_%(class)s_has_max', 
                                help_text='Refers to the Duration denoting the maximum value of the range.')
    has_min = models.ForeignKey('Duration', related_name='%(app_label)s_%(class)s_has_min', 
                                help_text='Refers to the Duration denoting the minimum value of the range.')


class PseudostateKind(models.Model):
    """
    PseudostateKind is an Enumeration type that is used to differentiate various kinds of Pseudostates.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    SHALLOWHISTORY = 0
    FORK = 1
    INITIAL = 2
    CHOICE = 3
    DEEPHISTORY = 4
    JOIN = 5
    TERMINATE = 6
    JUNCTION = 7
    EXITPOINT = 8
    ENTRYPOINT = 9
    CHOICES = (
        (SHALLOWHISTORY, 'shallowHistory'),
        (FORK, 'fork'),
        (INITIAL, 'initial'),
        (CHOICE, 'choice'),
        (DEEPHISTORY, 'deepHistory'),
        (JOIN, 'join'),
        (TERMINATE, 'terminate'),
        (JUNCTION, 'junction'),
        (EXITPOINT, 'exitPoint'),
        (ENTRYPOINT, 'entryPoint'),
    )

    pseudostate_kind = models.IntegerField(choices=CHOICES, default=ENTRYPOINT)


class RaiseExceptionAction(models.Model):
    """
    A RaiseExceptionAction is an Action that causes an exception to occur. The input value becomes the exception
    object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    exception = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_exception')


class DirectedRelationship(models.Model):
    """
    A DirectedRelationship represents a relationship between a collection of source model Elements and a
    collection of target model Elements.
    """

    __package__ = 'UML.CommonStructure'

    relationship = models.OneToOneField('Relationship', on_delete=models.CASCADE, primary_key=True)
    source = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_source', 
                               help_text='Specifies the source Element(s) of the DirectedRelationship.')
    target = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_target', 
                               help_text='Specifies the target Element(s) of the DirectedRelationship.')


class ElementImport(models.Model):
    """
    An ElementImport identifies a NamedElement in a Namespace other than the one that owns that NamedElement and
    allows the NamedElement to be referenced using an unqualified name in the Namespace owning the
    ElementImport.
    """

    __package__ = 'UML.CommonStructure'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    alias = models.CharField(max_length=255, 
                             help_text='Specifies the name that should be added to the importing Namespace in ' +
                             'lieu of the name of the imported PackagableElement. The alias must not clash with ' +
                             'any other member in the importing Namespace. By default, no alias is used.')
    imported_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_imported_element', 
                                         help_text='Specifies the PackageableElement whose name is to be added to ' +
                                         'a Namespace.')
    importing_namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_importing_namespace', 
                                            help_text='Specifies the Namespace that imports a PackageableElement ' +
                                            'from another Namespace.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', 
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


class CentralBufferNode(models.Model):
    """
    A CentralBufferNode is an ObjectNode for managing flows from multiple sources and targets.
    """

    __package__ = 'UML.Activities'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)


class ExtensionPoint(models.Model):
    """
    An ExtensionPoint identifies a point in the behavior of a UseCase where that behavior can be extended by the
    behavior of some other (extending) UseCase, as specified by an Extend relationship.
    """

    __package__ = 'UML.UseCases'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    use_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_use_case')


class ActivityEdge(models.Model):
    """
    An ActivityEdge is an abstract class for directed connections between two ActivityNodes.
    """

    __package__ = 'UML.Activities'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', 
                                 help_text='The Activity containing the ActivityEdge, if it is directly owned by ' +
                                 'an Activity.')
    guard = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_guard', 
                              help_text='A ValueSpecification that is evaluated to determine if a token can ' +
                              'traverse the ActivityEdge. If an ActivityEdge has no guard, then there is no ' +
                              'restriction on tokens traversing the edge.')
    in_group = models.ForeignKey('ActivityGroup', related_name='%(app_label)s_%(class)s_in_group', 
                                 help_text='ActivityGroups containing the ActivityEdge.')
    in_partition = models.ForeignKey('ActivityPartition', related_name='%(app_label)s_%(class)s_in_partition', 
                                     help_text='ActivityPartitions containing the ActivityEdge.')
    in_structured_node = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_in_structured_node', 
                                           help_text='The StructuredActivityNode containing the ActivityEdge, if ' +
                                           'it is owned by a StructuredActivityNode.')
    interrupts = models.ForeignKey('InterruptibleActivityRegion', related_name='%(app_label)s_%(class)s_interrupts', 
                                   help_text='The InterruptibleActivityRegion for which this ActivityEdge is an ' +
                                   'interruptingEdge.')
    redefined_edge = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_edge', 
                                       help_text='ActivityEdges from a generalization of the Activity containing ' +
                                       'this ActivityEdge that are redefined by this ActivityEdge.')
    source = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_source', 
                               help_text='The ActivityNode from which tokens are taken when they traverse the ' +
                               'ActivityEdge.')
    target = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_target', 
                               help_text='The ActivityNode to which tokens are put when they traverse the ' +
                               'ActivityEdge.')
    weight = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_weight', 
                               help_text='The minimum number of tokens that must traverse the ActivityEdge at the ' +
                               'same time. If no weight is specified, this is equivalent to specifying a constant ' +
                               'value of 1.')

    def is_consistent_with(self):
        """
        .. ocl::
            result = (redefiningElement.oclIsKindOf(ActivityEdge))
        """
        pass


class ControlFlow(models.Model):
    """
    A ControlFlow is an ActivityEdge traversed by control tokens or object tokens of control type, which are use
    to control the execution of ExecutableNodes.
    """

    __package__ = 'UML.Activities'

    activity_edge = models.OneToOneField('ActivityEdge', on_delete=models.CASCADE, primary_key=True)


class ParameterDirectionKind(models.Model):
    """
    ParameterDirectionKind is an Enumeration that defines literals used to specify direction of parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    IN = 'in'
    INOUT = 'inout'
    RETURN = 'return'
    OUT = 'out'
    CHOICES = (
        (IN, 'Indicates that Parameter values are passed in by the caller.'),
        (INOUT, 'Indicates that Parameter values are passed in by the caller and ' +
                '(possibly different) values passed out to the caller.'),
        (RETURN, 'Indicates that Parameter values are passed as return values back to ' +
                 'the caller.'),
        (OUT, 'Indicates that Parameter values are passed out to the caller.'),
    )

    parameter_direction_kind = models.CharField(max_length=255, choices=CHOICES, default=OUT)


class Transition(models.Model):
    """
    A Transition represents an arc between exactly one source Vertex and exactly one Target vertex (the source
    and targets may be the same Vertex). It may form part of a compound transition, which takes the StateMachine
    from one steady State configuration to another, representing the full response of the StateMachine to an
    occurrence of an Event that triggered it.
    """

    __package__ = 'UML.StateMachines'

    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    redefinable_element = models.OneToOneField('RedefinableElement')
    container = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_container', 
                                  help_text='Designates the Region that owns this Transition.')
    effect = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_effect', 
                               help_text='Specifies an optional behavior to be performed when the Transition ' +
                               'fires.')
    guard = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_guard', 
                              help_text='A guard is a Constraint that provides a fine-grained control over the ' +
                              'firing of the Transition. The guard is evaluated when an Event occurrence is ' +
                              'dispatched by the StateMachine. If the guard is true at that time, the Transition ' +
                              'may be enabled, otherwise, it is disabled. Guards should be pure expressions ' +
                              'without side effects. Guard expressions with side effects are ill formed.')
    kind = models.ForeignKey('TransitionKind', related_name='%(app_label)s_%(class)s_kind', 
                             help_text='Indicates the precise type of the Transition.')
    redefined_transition = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_transition', 
                                             help_text='The Transition that is redefined by this Transition.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    source = models.ForeignKey('Vertex', related_name='%(app_label)s_%(class)s_source', 
                               help_text='Designates the originating Vertex (State or Pseudostate) of the ' +
                               'Transition.')
    target = models.ForeignKey('Vertex', related_name='%(app_label)s_%(class)s_target', 
                               help_text='Designates the target Vertex that is reached when the Transition is ' +
                               'taken.')
    trigger = models.ForeignKey('Trigger', related_name='%(app_label)s_%(class)s_trigger', 
                                help_text='Specifies the Triggers that may fire the transition.')

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the Transition either directly
        or transitively.

        .. ocl::
            result = (container.containingStateMachine())
        """
        pass


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
    metaclass = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_metaclass', 
                                  help_text='References the Class that is extended through an Extension. The ' +
                                  'property is derived from the type of the memberEnd that is not the ownedEnd.')
    owned_end = models.ForeignKey('ExtensionEnd', related_name='%(app_label)s_%(class)s_owned_end', 
                                  help_text='References the end of the extension that is typed by a Stereotype.')

    def metaclass_operation(self):
        """
        The query metaclass() returns the metaclass that is being extended (as opposed to the extending
        stereotype).

        .. ocl::
            result = (metaclassEnd().type.oclAsType(Class))
        """
        pass


class ParameterEffectKind(models.Model):
    """
    ParameterEffectKind is an Enumeration that indicates the effect of a Behavior on values passed in or out of
    its parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    READ = 'read'
    DELETE = 'delete'
    CREATE = 'create'
    UPDATE = 'update'
    CHOICES = (
        (READ, 'Indicates objects that are values of the parameter have values of their ' +
               'properties, or links in which they participate, or their classifiers retrieved ' +
               'during executions of the behavior.'),
        (DELETE, 'Indicates objects that are values of the parameter do not exist after ' +
                 'executions of the behavior are finished.'),
        (CREATE, 'Indicates that the behavior creates values.'),
        (UPDATE, 'Indicates objects that are values of the parameter have values of ' +
                 'their properties, or links in which they participate, or their classification ' +
                 'changed during executions of the behavior.'),
    )

    parameter_effect_kind = models.CharField(max_length=255, choices=CHOICES, default=UPDATE)


class ActivityGroup(models.Model):
    """
    ActivityGroup is an abstract class for defining sets of ActivityNodes and ActivityEdges in an Activity.
    """

    __package__ = 'UML.Activities'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    contained_edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_contained_edge', 
                                       help_text='ActivityEdges immediately contained in the ActivityGroup.')
    contained_node = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_contained_node', 
                                       help_text='ActivityNodes immediately contained in the ActivityGroup.')
    in_activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_in_activity', 
                                    help_text='The Activity containing the ActivityGroup, if it is directly owned ' +
                                    'by an Activity.')
    subgroup = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_subgroup', 
                                 help_text='Other ActivityGroups immediately contained in this ActivityGroup.')
    super_group = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_super_group', 
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


class ActivityPartition(models.Model):
    """
    An ActivityPartition is a kind of ActivityGroup for identifying ActivityNodes that have some characteristic
    in common.
    """

    __package__ = 'UML.Activities'

    activity_group = models.OneToOneField('ActivityGroup', on_delete=models.CASCADE, primary_key=True)
    edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', 
                             help_text='ActivityEdges immediately contained in the ActivityPartition.')
    is_dimension = models.BooleanField(help_text='Indicates whether the ActivityPartition groups other ' +
                                       'ActivityPartitions along a dimension.')
    is_external = models.BooleanField(help_text='Indicates whether the ActivityPartition represents an entity to ' +
                                      'which the partitioning structure does not apply.')
    node = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_node', 
                             help_text='ActivityNodes immediately contained in the ActivityPartition.')
    represents = models.ForeignKey('Element', related_name='%(app_label)s_%(class)s_represents', 
                                   help_text='An Element represented by the functionality modeled within the ' +
                                   'ActivityPartition.')
    subpartition = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_subpartition', 
                                     help_text='Other ActivityPartitions immediately contained in this ' +
                                     'ActivityPartition (as its subgroups).')
    super_partition = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_super_partition', 
                                        help_text='Other ActivityPartitions immediately containing this ' +
                                        'ActivityPartition (as its superGroups).')


class LinkEndData(models.Model):
    """
    LinkEndData is an Element that identifies on end of a link to be read or written by a LinkAction. As a link
    (that is not a link object) cannot be passed as a runtime value to or from an Action, it is instead
    identified by its end objects and qualifier values, if any. A LinkEndData instance provides these values for
    a single Association end.
    """

    __package__ = 'UML.Actions'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_end', 
                            help_text='The Association"end"for"which"this"LinkEndData"specifies"values.')
    qualifier = models.ForeignKey('QualifierValue', related_name='%(app_label)s_%(class)s_qualifier', 
                                  help_text='A set of QualifierValues used to provide values for the qualifiers ' +
                                  'of the end.')
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', 
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


class LinkEndCreationData(models.Model):
    """
    LinkEndCreationData is LinkEndData used to provide values for one end of a link to be created by a
    CreateLinkAction.
    """

    __package__ = 'UML.Actions'

    link_end_data = models.OneToOneField('LinkEndData', on_delete=models.CASCADE, primary_key=True)
    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', 
                                  help_text='For ordered Association ends, the InputPin that provides the ' +
                                  'position where the new link should be inserted or where an existing link should ' +
                                  'be moved to. The type of the insertAt InputPin is UnlimitedNatural, but the ' +
                                  'input cannot be zero. It is omitted for Association ends that are not ordered.')
    is_replace_all = models.BooleanField(help_text='Specifies whether the existing links emanating from the ' +
                                         'object on this end should be destroyed before creating a new link.')

    def all_pins(self):
        """
        Adds the insertAt InputPin (if any) to the set of all Pins.

        .. ocl::
            result = (self.LinkEndData::allPins()->including(insertAt))
        """
        pass


class OccurrenceSpecification(models.Model):
    """
    An OccurrenceSpecification is the basic semantic unit of Interactions. The sequences of occurrences
    specified by them are the meanings of Interactions.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    covered = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_covered', 
                                help_text='References the Lifeline on which the OccurrenceSpecification appears.')
    to_after = models.ForeignKey('GeneralOrdering', related_name='%(app_label)s_%(class)s_to_after', 
                                 help_text='References the GeneralOrderings that specify EventOcurrences that ' +
                                 'must occur after this OccurrenceSpecification.')
    to_before = models.ForeignKey('GeneralOrdering', related_name='%(app_label)s_%(class)s_to_before', 
                                  help_text='References the GeneralOrderings that specify EventOcurrences that ' +
                                  'must occur before this OccurrenceSpecification.')


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
    return_information = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_return_information')


class WriteLinkAction(models.Model):
    """
    WriteLinkAction is an abstract class for LinkActions that create and destroy links.
    """

    __package__ = 'UML.Actions'

    link_action = models.OneToOneField('LinkAction', on_delete=models.CASCADE, primary_key=True)


class CreateLinkAction(models.Model):
    """
    A CreateLinkAction is a WriteLinkAction for creating links.
    """

    __package__ = 'UML.Actions'

    write_link_action = models.OneToOneField('WriteLinkAction', on_delete=models.CASCADE, primary_key=True)
    end_data = models.ForeignKey('LinkEndCreationData', related_name='%(app_label)s_%(class)s_end_data')


class ClearAssociationAction(models.Model):
    """
    A ClearAssociationAction is an Action that destroys all links of an Association in which a particular object
    participates.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_association', 
                                    help_text='The Association to be cleared.')
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin that gives the object whose participation in the ' +
                                   'Association is to be cleared.')


class InitialNode(models.Model):
    """
    An InitialNode is a ControlNode that offers a single control token when initially enabled.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)


class WriteVariableAction(models.Model):
    """
    WriteVariableAction is an abstract class for VariableActions that change Variable values.
    """

    __package__ = 'UML.Actions'

    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value')


class AddVariableValueAction(models.Model):
    """
    An AddVariableValueAction is a WriteVariableAction for adding values to a Variable.
    """

    __package__ = 'UML.Actions'

    write_variable_action = models.OneToOneField('WriteVariableAction', on_delete=models.CASCADE, primary_key=True)
    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', 
                                  help_text='The InputPin that gives the position at which to insert a new value ' +
                                  'or move an existing value in ordered Variables. The type of the insertAt ' +
                                  'InputPin is UnlimitedNatural, but the value cannot be zero. It is omitted for ' +
                                  'unordered Variables.')
    is_replace_all = models.BooleanField(help_text='Specifies whether existing values of the Variable should be ' +
                                         'removed before adding the new value.')


class State(models.Model):
    """
    A State models a situation during which some (usually implicit) invariant condition holds.
    """

    __package__ = 'UML.StateMachines'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    namespace = models.OneToOneField('Namespace')
    vertex = models.OneToOneField('Vertex')
    connection = models.ForeignKey('ConnectionPointReference', related_name='%(app_label)s_%(class)s_connection', 
                                   help_text='The entry and exit connection points used in conjunction with this ' +
                                   '(submachine) State, i.e., as targets and sources, respectively, in the Region ' +
                                   'with the submachine State. A connection point reference references the ' +
                                   'corresponding definition of a connection point Pseudostate in the StateMachine ' +
                                   'referenced by the submachine State.')
    connection_point = models.ForeignKey('Pseudostate', related_name='%(app_label)s_%(class)s_connection_point', 
                                         help_text='The entry and exit Pseudostates of a composite State. These ' +
                                         'can only be entry or exit Pseudostates, and they must have different ' +
                                         'names. They can only be defined for composite States.')
    deferrable_trigger = models.ForeignKey('Trigger', related_name='%(app_label)s_%(class)s_deferrable_trigger', 
                                           help_text='A list of Triggers that are candidates to be retained by ' +
                                           'the StateMachine if they trigger no Transitions out of the State (not ' +
                                           'consumed). A deferred Trigger is retained until the StateMachine ' +
                                           'reaches a State configuration where it is no longer deferred.')
    do_activity = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_do_activity', 
                                    help_text='An optional Behavior that is executed while being in the State. ' +
                                    'The execution starts when this State is entered, and ceases either by itself ' +
                                    'when done, or when the State is exited, whichever comes first.')
    entry = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_entry', 
                              help_text='An optional Behavior that is executed whenever this State is entered ' +
                              'regardless of the Transition taken to reach the State. If defined, entry Behaviors ' +
                              'are always executed to completion prior to any internal Behavior or Transitions ' +
                              'performed within the State.')
    exit = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_exit', 
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
    redefined_state = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_state', 
                                        help_text='The State of which this State is a redefinition.')
    redefinition_context = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_redefinition_context', 
                                             help_text='References the Classifier in which context this element ' +
                                             'may be redefined.')
    region = models.ForeignKey('Region', related_name='%(app_label)s_%(class)s_region', 
                               help_text='The Regions owned directly by the State.')
    state_invariant = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_state_invariant', 
                                        help_text='Specifies conditions that are always true when this State is ' +
                                        'the current State. In ProtocolStateMachines state invariants are ' +
                                        'additional conditions to the preconditions of the outgoing Transitions, ' +
                                        'and to the postcondition of the incoming Transitions.')
    submachine = models.ForeignKey('StateMachine', related_name='%(app_label)s_%(class)s_submachine', 
                                   help_text='The StateMachine that is to be inserted in place of the ' +
                                   '(submachine) State.')

    def is_composite_operation(self):
        """
        A composite State is a State with at least one Region.

        .. ocl::
            result = (region->notEmpty())
        """
        pass


class Dependency(models.Model):
    """
    A Dependency is a Relationship that signifies that a single model Element or a set of model Elements
    requires other model Elements for their specification or implementation. This means that the complete
    semantics of the client Element(s) are either semantically or structurally dependent on the definition of
    the supplier Element(s).
    """

    __package__ = 'UML.CommonStructure'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')
    client = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_client', 
                               help_text='The Element(s) dependent on the supplier Element(s). In some cases ' +
                               '(such as a trace Abstraction) the assignment of direction (that is, the ' +
                               'designation of the client Element) is at the discretion of the modeler and is a ' +
                               'stipulation.')
    supplier = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_supplier', 
                                 help_text='The Element(s) on which the client Element(s) depend in some respect. ' +
                                 'The modeler may stipulate a sense of Dependency direction suitable for their ' +
                                 'domain.')


class Abstraction(models.Model):
    """
    An Abstraction is a Relationship that relates two Elements or sets of Elements that represent the same
    concept at different levels of abstraction or from different viewpoints.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)
    mapping = models.ForeignKey('OpaqueExpression', related_name='%(app_label)s_%(class)s_mapping')


class Realization(models.Model):
    """
    Realization is a specialized Abstraction relationship between two sets of model Elements, one representing a
    specification (the supplier) and the other represents an implementation of the latter (the client).
    Realization can be used to model stepwise refinement, optimizations, transformations, templates, model
    synthesis, framework composition, etc.
    """

    __package__ = 'UML.CommonStructure'

    abstraction = models.OneToOneField('Abstraction', on_delete=models.CASCADE, primary_key=True)


class InterfaceRealization(models.Model):
    """
    An InterfaceRealization is a specialized realization relationship between a BehavioredClassifier and an
    Interface. This relationship signifies that the realizing BehavioredClassifier conforms to the contract
    specified by the Interface.
    """

    __package__ = 'UML.SimpleClassifiers'

    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)
    contract = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_contract', 
                                 help_text='References the Interface specifying the conformance contract.')
    implementing_classifier = models.ForeignKey('BehavioredClassifier', related_name='%(app_label)s_%(class)s_implementing_classifier', 
                                                help_text='References the BehavioredClassifier that owns this ' +
                                                'InterfaceRealization, i.e., the BehavioredClassifier that ' +
                                                'realizes the Interface to which it refers.')


class InvocationAction(models.Model):
    """
    InvocationAction is an abstract class for the various actions that request Behavior invocation.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    argument = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_argument', 
                                 help_text='The InputPins that provide the argument values passed in the ' +
                                 'invocation request.')
    on_port = models.ForeignKey('Port', related_name='%(app_label)s_%(class)s_on_port', 
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
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPins on which the reply values from the invocation are placed ' +
                               '(if the call is synchronous).')

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior or Operation being called. (This
        operation is abstract and should be overridden by subclasses of CallAction.)
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
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation', 
                                  help_text='The Operation being invoked.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', 
                               help_text='The InputPin that provides the target object to which the Operation ' +
                               'call request is sent.')

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Operation being called.

        .. ocl::
            result = (operation.outputParameters())
        """
        pass


class LiteralSpecification(models.Model):
    """
    A LiteralSpecification identifies a literal constant being modeled.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)


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
    lower = models.IntegerField(help_text='The lower bound of the multiplicity interval.')
    lower_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_lower_value', 
                                    help_text='The specification of the lower bound for this multiplicity.')
    upper = models.IntegerField('UnlimitedNatural', help_text='The upper bound of the multiplicity interval.')
    upper_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_upper_value', 
                                    help_text='The specification of the upper bound for this multiplicity.')

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an integer, which is the
        integerValue of lowerValue, if this is given, and 1 otherwise.

        .. ocl::
            result = (if (lowerValue=null or lowerValue.integerValue()=null) then 1 else lowerValue.integerValue() endif)
        """
        pass


class Feature(models.Model):
    """
    A Feature declares a behavioral or structural characteristic of Classifiers.
    """

    __package__ = 'UML.Classification'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    featuring_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_featuring_classifier', 
                                             help_text='The Classifiers that have this Feature as a feature.')
    is_static = models.BooleanField(help_text='Specifies whether this Feature characterizes individual instances ' +
                                    'classified by the Classifier (false) or the Classifier itself (true).')


class StructuralFeature(models.Model):
    """
    A StructuralFeature is a typed feature of a Classifier that specifies the structure of instances of the
    Classifier.
    """

    __package__ = 'UML.Classification'

    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    typed_element = models.OneToOneField('TypedElement')
    feature = models.OneToOneField('Feature')
    is_read_only = models.BooleanField()


class ConnectableElement(models.Model):
    """
    ConnectableElement is an abstract metaclass representing a set of instances that play roles of a
    StructuredClassifier. ConnectableElements may be joined by attached Connectors and specify configurations of
    linked instances to be created within an instance of the containing StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    typed_element = models.OneToOneField('TypedElement', on_delete=models.CASCADE, primary_key=True)
    parameterable_element = models.OneToOneField('ParameterableElement')
    end = models.ForeignKey('ConnectorEnd', related_name='%(app_label)s_%(class)s_end', 
                            help_text='A set of ConnectorEnds that attach to this ConnectableElement.')
    template_parameter = models.ForeignKey('ConnectableElementTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', 
                                           help_text='The ConnectableElementTemplateParameter for this ' +
                                           'ConnectableElement parameter.')

    def end_operation(self):
        """
        Derivation for ConnectableElement::/end : ConnectorEnd

        .. ocl::
            result = (ConnectorEnd.allInstances()->select(role = self))
        """
        pass


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

    connectable_element = models.OneToOneField('ConnectableElement', on_delete=models.CASCADE, primary_key=True)
    deployment_target = models.OneToOneField('DeploymentTarget')
    structural_feature = models.OneToOneField('StructuralFeature')
    aggregation = models.ForeignKey('AggregationKind', related_name='%(app_label)s_%(class)s_aggregation', 
                                    help_text='Specifies the kind of aggregation that applies to the Property.')
    association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_association', 
                                    help_text='The Association of which this Property is a member, if any.')
    association_end = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_association_end', 
                                        help_text='Designates the optional association end that owns a qualifier ' +
                                        'attribute.')
    has_class = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_has_class', 
                                  help_text='The Class that owns this Property, if any.')
    datatype = models.ForeignKey('DataType', related_name='%(app_label)s_%(class)s_datatype', 
                                 help_text='The DataType that owns this Property, if any.')
    default_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_default_value', 
                                      help_text='A ValueSpecification that is evaluated to give a default value ' +
                                      'for the Property when an instance of the owning Classifier is ' +
                                      'instantiated.')
    interface = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_interface', 
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
    opposite = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_opposite', 
                                 help_text='In the case where the Property is one end of a binary association ' +
                                 'this gives the other end.')
    owning_association = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_owning_association', 
                                           help_text='The owning association of this property, if any.')
    qualifier = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_qualifier', 
                                  help_text='An optional list of ordered qualifier attributes for the end.')
    redefined_property = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_property', 
                                           help_text='The properties that are redefined by this property, if ' +
                                           'any.')
    subsetted_property = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_subsetted_property', 
                                           help_text='The properties of which this Property is constrained to be ' +
                                           'a subset, if any.')

    def is_attribute(self):
        """
        The query isAttribute() is true if the Property is defined as an attribute of some Classifier.

        .. ocl::
            result = (not classifier->isEmpty())
        """
        pass


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

    has_property = models.OneToOneField('Property', on_delete=models.CASCADE, primary_key=True)
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
    protocol = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_protocol', 
                                 help_text='An optional ProtocolStateMachine which describes valid interactions ' +
                                 'at this interaction point.')
    provided = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_provided', 
                                 help_text='The Interfaces specifying the set of Operations and Receptions that ' +
                                 'the EncapsulatedCclassifier offers to its environment via this Port, and which ' +
                                 'it will handle either directly or by forwarding it to a part of its internal ' +
                                 'structure. This association is derived according to the value of isConjugated. ' +
                                 'If isConjugated is false, provided is derived as the union of the sets of ' +
                                 'Interfaces realized by the type of the port and its supertypes, or directly from ' +
                                 'the type of the Port if the Port is typed by an Interface. If isConjugated is ' +
                                 'true, it is derived as the union of the sets of Interfaces used by the type of ' +
                                 'the Port and its supertypes.')
    redefined_port = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_port', 
                                       help_text='A Port may be redefined when its containing ' +
                                       'EncapsulatedClassifier is specialized. The redefining Port may have ' +
                                       'additional Interfaces to those that are associated with the redefined Port ' +
                                       'or it may replace an Interface by one of its subtypes.')
    required = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_required', 
                                 help_text='The Interfaces specifying the set of Operations and Receptions that ' +
                                 'the EncapsulatedCassifier expects its environment to handle via this port. This ' +
                                 'association is derived according to the value of isConjugated. If isConjugated ' +
                                 'is false, required is derived as the union of the sets of Interfaces used by the ' +
                                 'type of the Port and its supertypes. If isConjugated is true, it is derived as ' +
                                 'the union of the sets of Interfaces realized by the type of the Port and its ' +
                                 'supertypes, or directly from the type of the Port if the Port is typed by an ' +
                                 'Interface.')

    def provided_operation(self):
        """
        Derivation for Port::/provided

        .. ocl::
            result = (if isConjugated then basicRequired() else basicProvided() endif)
        """
        pass


class BehavioralFeature(models.Model):
    """
    A BehavioralFeature is a feature of a Classifier that specifies an aspect of the behavior of its instances.
    A BehavioralFeature is implemented (realized) by a Behavior. A BehavioralFeature specifies that a Classifier
    will respond to a designated request by invoking its implementing method.
    """

    __package__ = 'UML.Classification'

    feature = models.OneToOneField('Feature', on_delete=models.CASCADE, primary_key=True)
    namespace = models.OneToOneField('Namespace')
    concurrency = models.ForeignKey('CallConcurrencyKind', related_name='%(app_label)s_%(class)s_concurrency', 
                                    help_text='Specifies the semantics of concurrent calls to the same passive ' +
                                    'instance (i.e., an instance originating from a Class with isActive being ' +
                                    'false). Active instances control access to their own BehavioralFeatures.')
    is_abstract = models.BooleanField(help_text='If true, then the BehavioralFeature does not have an ' +
                                      'implementation, and one must be supplied by a more specific Classifier. If ' +
                                      'false, the BehavioralFeature must have an implementation in the Classifier ' +
                                      'or one must be inherited.')
    method = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_method', 
                               help_text='A Behavior that implements the BehavioralFeature. There may be at most ' +
                               'one Behavior for a particular pairing of a Classifier (as owner of the Behavior) ' +
                               'and a BehavioralFeature (as specification of the Behavior).')
    owned_parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', 
                                        help_text='The ordered set of formal Parameters of this ' +
                                        'BehavioralFeature.')
    owned_parameter_set = models.ForeignKey('ParameterSet', related_name='%(app_label)s_%(class)s_owned_parameter_set', 
                                            help_text='The ParameterSets owned by this BehavioralFeature.')
    raised_exception = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_raised_exception', 
                                         help_text='The Types representing exceptions that may be raised during ' +
                                         'an invocation of this BehavioralFeature.')

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

    templateable_element = models.OneToOneField('TemplateableElement', on_delete=models.CASCADE, primary_key=True)
    parameterable_element = models.OneToOneField('ParameterableElement')
    behavioral_feature = models.OneToOneField('BehavioralFeature')
    body_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_body_condition', 
                                       help_text='An optional Constraint on the result values of an invocation of ' +
                                       'this Operation.')
    has_class = models.ForeignKey('Class', related_name='%(app_label)s_%(class)s_has_class', 
                                  help_text='The Class that owns this operation, if any.')
    datatype = models.ForeignKey('DataType', related_name='%(app_label)s_%(class)s_datatype', 
                                 help_text='The DataType that owns this Operation, if any.')
    interface = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_interface', 
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
    lower = models.IntegerField(help_text='Specifies the lower multiplicity of the return parameter, if present. ' +
                                'This information is derived from the return result for this Operation.')
    owned_parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_owned_parameter', 
                                        help_text='The parameters owned by this Operation.')
    postcondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_postcondition', 
                                      help_text='An optional set of Constraints specifying the state of the ' +
                                      'system when the Operation is completed.')
    precondition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_precondition', 
                                     help_text='An optional set of Constraints on the state of the system when ' +
                                     'the Operation is invoked.')
    raised_exception = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_raised_exception', 
                                         help_text='The Types representing exceptions that may be raised during ' +
                                         'an invocation of this operation.')
    redefined_operation = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_operation', 
                                            help_text='The Operations that are redefined by this Operation.')
    template_parameter = models.ForeignKey('OperationTemplateParameter', related_name='%(app_label)s_%(class)s_template_parameter', 
                                           help_text='The OperationTemplateParameter that exposes this element as ' +
                                           'a formal parameter.')
    has_type = models.ForeignKey('Type', related_name='%(app_label)s_%(class)s_has_type', 
                                 help_text='The return type of the operation, if present. This information is ' +
                                 'derived from the return result for this Operation.')
    upper = models.IntegerField('UnlimitedNatural', 
                                help_text='The upper multiplicity of the return parameter, if present. This ' +
                                'information is derived from the return result for this Operation.')

    def type_operation(self):
        """
        If this operation has a return parameter, type equals the value of type for that parameter. Otherwise
        type has no value.

        .. ocl::
            result = (if returnResult()->notEmpty() then returnResult()->any(true).type else null endif)
        """
        pass


class Event(models.Model):
    """
    An Event is the specification of some occurrence that may potentially trigger effects by an object.
    """

    __package__ = 'UML.CommonBehavior'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)


class Deployment(models.Model):
    """
    A deployment is the allocation of an artifact or artifact instance to a deployment target. A component
    deployment is the deployment of one or more artifacts or artifact instances to a deployment target,
    optionally parameterized by a deployment specification. Examples are executables and configuration files.
    """

    __package__ = 'UML.Deployments'

    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)
    configuration = models.ForeignKey('DeploymentSpecification', related_name='%(app_label)s_%(class)s_configuration', 
                                      help_text='The specification of properties that parameterize the deployment ' +
                                      'and execution of one or more Artifacts.')
    deployed_artifact = models.ForeignKey('DeployedArtifact', related_name='%(app_label)s_%(class)s_deployed_artifact', 
                                          help_text='The Artifacts that are deployed onto a Node. This ' +
                                          'association specializes the supplier association.')
    location = models.ForeignKey('DeploymentTarget', related_name='%(app_label)s_%(class)s_location', 
                                 help_text='The DeployedTarget which is the target of a Deployment.')


class WriteStructuralFeatureAction(models.Model):
    """
    WriteStructuralFeatureAction is an abstract class for StructuralFeatureActions that change StructuralFeature
    values.
    """

    __package__ = 'UML.Actions'

    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin on which is put the input object as modified by the ' +
                               'WriteStructuralFeatureAction.')
    value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_value', 
                              help_text='The InputPin that provides the value to be added or removed from the ' +
                              'StructuralFeature.')


class AddStructuralFeatureValueAction(models.Model):
    """
    An AddStructuralFeatureValueAction is a WriteStructuralFeatureAction for adding values to a
    StructuralFeature.
    """

    __package__ = 'UML.Actions'

    write_structural_feature_action = models.OneToOneField('WriteStructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    insert_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_insert_at', 
                                  help_text='The InputPin that gives the position at which to insert the value in ' +
                                  'an ordered StructuralFeature. The type of the insertAt InputPin is ' +
                                  'UnlimitedNatural, but the value cannot be zero. It is omitted for unordered ' +
                                  'StructuralFeatures.')
    is_replace_all = models.BooleanField(help_text='Specifies whether existing values of the StructuralFeature ' +
                                         'should be removed before adding the new value.')


class DestroyLinkAction(models.Model):
    """
    A DestroyLinkAction is a WriteLinkAction that destroys links (including link objects).
    """

    __package__ = 'UML.Actions'

    write_link_action = models.OneToOneField('WriteLinkAction', on_delete=models.CASCADE, primary_key=True)
    end_data = models.ForeignKey('LinkEndDestructionData', related_name='%(app_label)s_%(class)s_end_data')


class ExecutionSpecification(models.Model):
    """
    An ExecutionSpecification is a specification of the execution of a unit of Behavior or Action within the
    Lifeline. The duration of an ExecutionSpecification is represented by two OccurrenceSpecifications, the
    start OccurrenceSpecification and the finish OccurrenceSpecification.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    finish = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_finish', 
                               help_text='References the OccurrenceSpecification that designates the finish of ' +
                               'the Action or Behavior.')
    start = models.ForeignKey('OccurrenceSpecification', related_name='%(app_label)s_%(class)s_start', 
                              help_text='References the OccurrenceSpecification that designates the start of the ' +
                              'Action or Behavior.')


class BehaviorExecutionSpecification(models.Model):
    """
    A BehaviorExecutionSpecification is a kind of ExecutionSpecification representing the execution of a
    Behavior.
    """

    __package__ = 'UML.Interactions'

    execution_specification = models.OneToOneField('ExecutionSpecification', on_delete=models.CASCADE, primary_key=True)
    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior')


class Variable(models.Model):
    """
    A Variable is a ConnectableElement that may store values during the execution of an Activity. Reading and
    writing the values of a Variable provides an alternative means for passing data than the use of ObjectFlows.
    A Variable may be owned directly by an Activity, in which case it is accessible from anywhere within that
    activity, or it may be owned by a StructuredActivityNode, in which case it is only accessible within that
    node.
    """

    __package__ = 'UML.Activities'

    connectable_element = models.OneToOneField('ConnectableElement', on_delete=models.CASCADE, primary_key=True)
    multiplicity_element = models.OneToOneField('MultiplicityElement')
    activity_scope = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity_scope', 
                                       help_text='An Activity that owns the Variable.')
    scope = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_scope', 
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


class Generalization(models.Model):
    """
    A Generalization is a taxonomic relationship between a more general Classifier and a more specific
    Classifier. Each instance of the specific Classifier is also an instance of the general Classifier. The
    specific Classifier inherits the features of the more general Classifier. A Generalization is owned by the
    specific Classifier.
    """

    __package__ = 'UML.Classification'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    general = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_general', 
                                help_text='The general classifier in the Generalization relationship.')
    generalization_set = models.ForeignKey('GeneralizationSet', related_name='%(app_label)s_%(class)s_generalization_set', 
                                           help_text='Represents a set of instances of Generalization.  A ' +
                                           'Generalization may appear in many GeneralizationSets.')
    is_substitutable = models.BooleanField(help_text='Indicates whether the specific Classifier can be used ' +
                                           'wherever the general Classifier can be used. If true, the execution ' +
                                           'traces of the specific Classifier shall be a superset of the execution ' +
                                           'traces of the general Classifier. If false, there is no such ' +
                                           'constraint on execution traces. If unset, the modeler has not stated ' +
                                           'whether there is such a constraint or not.')
    specific = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_specific', 
                                 help_text='The specializing Classifier in the Generalization relationship.')


class TemplateBinding(models.Model):
    """
    A TemplateBinding is a DirectedRelationship between a TemplateableElement and a template. A TemplateBinding
    specifies the TemplateParameterSubstitutions of actual parameters for the formal parameters of the template.
    """

    __package__ = 'UML.CommonStructure'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    bound_element = models.ForeignKey('TemplateableElement', related_name='%(app_label)s_%(class)s_bound_element', 
                                      help_text='The TemplateableElement that is bound by this TemplateBinding.')
    parameter_substitution = models.ForeignKey('TemplateParameterSubstitution', related_name='%(app_label)s_%(class)s_parameter_substitution', 
                                               help_text='The TemplateParameterSubstitutions owned by this ' +
                                               'TemplateBinding.')
    signature = models.ForeignKey('TemplateSignature', related_name='%(app_label)s_%(class)s_signature', 
                                  help_text='The TemplateSignature for the template that is the target of this ' +
                                  'TemplateBinding.')


class Slot(models.Model):
    """
    A Slot designates that an entity modeled by an InstanceSpecification has a value or values for a specific
    StructuralFeature.
    """

    __package__ = 'UML.Classification'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    defining_feature = models.ForeignKey('StructuralFeature', related_name='%(app_label)s_%(class)s_defining_feature', 
                                         help_text='The StructuralFeature that specifies the values that may be ' +
                                         'held by the Slot.')
    owning_instance = models.ForeignKey('InstanceSpecification', related_name='%(app_label)s_%(class)s_owning_instance', 
                                        help_text='The InstanceSpecification that owns this Slot.')
    value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_value', 
                              help_text='The value or values held by the Slot.')


class JoinNode(models.Model):
    """
    A JoinNode is a ControlNode that synchronizes multiple flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)
    is_combine_duplicate = models.BooleanField(help_text='Indicates whether incoming tokens having objects with ' +
                                               'the same identity are combined into one by the JoinNode.')
    join_spec = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_join_spec', 
                                  help_text='A ValueSpecification giving the condition under which the JoinNode ' +
                                  'will offer a token on its outgoing ActivityEdge. If no joinSpec is specified, ' +
                                  'then the JoinNode will offer an outgoing token if tokens are offered on all of ' +
                                  'its incoming ActivityEdges (an "and" condition).')


class Expression(models.Model):
    """
    An Expression represents a node in an expression tree, which may be non-terminal or terminal. It defines a
    symbol, and has a possibly empty sequence of operands that are ValueSpecifications. It denotes a (possibly
    empty) set of values when evaluated in a context.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    operand = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_operand', 
                                help_text='Specifies a sequence of operand ValueSpecifications.')
    symbol = models.CharField(max_length=255, 
                              help_text='The symbol associated with this node in the expression tree.')


class FinalNode(models.Model):
    """
    A FinalNode is an abstract ControlNode at which a flow in an Activity stops.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)


class ActivityFinalNode(models.Model):
    """
    An ActivityFinalNode is a FinalNode that terminates the execution of its owning Activity or
    StructuredActivityNode.
    """

    __package__ = 'UML.Activities'

    final_node = models.OneToOneField('FinalNode', on_delete=models.CASCADE, primary_key=True)


class Continuation(models.Model):
    """
    A Continuation is a syntactic way to define continuations of different branches of an alternative
    CombinedFragment. Continuations are intuitively similar to labels representing intermediate points in a flow
    of control.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    setting = models.BooleanField()


class TemplateSignature(models.Model):
    """
    A Template Signature bundles the set of formal TemplateParameters for a template.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    owned_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_owned_parameter', 
                                        help_text='The formal parameters that are owned by this ' +
                                        'TemplateSignature.')
    parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_parameter', 
                                  help_text='The ordered set of all formal TemplateParameters for this ' +
                                  'TemplateSignature.')
    template = models.ForeignKey('TemplateableElement', related_name='%(app_label)s_%(class)s_template', 
                                 help_text='The TemplateableElement that owns this TemplateSignature.')


class RedefinableTemplateSignature(models.Model):
    """
    A RedefinableTemplateSignature supports the addition of formal template parameters in a specialization of a
    template classifier.
    """

    __package__ = 'UML.Classification'

    redefinable_element = models.OneToOneField('RedefinableElement', on_delete=models.CASCADE, primary_key=True)
    template_signature = models.OneToOneField('TemplateSignature')
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The Classifier that owns this RedefinableTemplateSignature.')
    extended_signature = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_extended_signature', 
                                           help_text='The signatures extended by this ' +
                                           'RedefinableTemplateSignature.')
    inherited_parameter = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_inherited_parameter', 
                                            help_text='The formal template parameters of the extended ' +
                                            'signatures.')

    def inherited_parameter_operation(self):
        """
        Derivation for RedefinableTemplateSignature::/inheritedParameter

        .. ocl::
            result = (if extendedSignature->isEmpty() then Set{} else extendedSignature.parameter->asSet() endif)
        """
        pass


class StartObjectBehaviorAction(models.Model):
    """
    A StartObjectBehaviorAction is an InvocationAction that starts the execution either of a directly
    instantiated Behavior or of the classifierBehavior of an object. Argument values may be supplied for the
    input Parameters of the Behavior. If the Behavior is invoked synchronously, then output values may be
    obtained for output Parameters.
    """

    __package__ = 'UML.Actions'

    call_action = models.OneToOneField('CallAction', on_delete=models.CASCADE, primary_key=True)
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object')

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior being called.

        .. ocl::
            result = (self.behavior().outputParameters())
        """
        pass


class Actor(models.Model):
    """
    An Actor specifies a role played by a user or any other system that interacts with the subject.
    """

    __package__ = 'UML.UseCases'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier', on_delete=models.CASCADE, primary_key=True)


class Collaboration(models.Model):
    """
    A Collaboration describes a structure of collaborating elements (roles), each performing a specialized
    function, which collectively accomplish some desired functionality.
    """

    __package__ = 'UML.StructuredClassifiers'

    structured_classifier = models.OneToOneField('StructuredClassifier', on_delete=models.CASCADE, primary_key=True)
    behaviored_classifier = models.OneToOneField('BehavioredClassifier')
    collaboration_role = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_collaboration_role')


class OpaqueExpression(models.Model):
    """
    An OpaqueExpression is a ValueSpecification that specifies the computation of a collection of values either
    in terms of a UML Behavior or based on a textual statement in a language other than UML
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior', 
                                 help_text='Specifies the behavior of the OpaqueExpression as a UML Behavior.')
    body = models.CharField(max_length=255, 
                            help_text='A textual definition of the behavior of the OpaqueExpression, possibly in ' +
                            'multiple languages.')
    language = models.CharField(max_length=255, 
                                help_text='Specifies the languages used to express the textual bodies of the ' +
                                'OpaqueExpression.  Languages are matched to body Strings by order. The ' +
                                'interpretation of the body depends on the languages. If the languages are ' +
                                'unspecified, they may be implicit from the expression body or the context.')
    result = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_result', 
                               help_text='If an OpaqueExpression is specified using a UML Behavior, then this ' +
                               'refers to the single required return Parameter of that Behavior. When the Behavior ' +
                               'completes execution, the values on this Parameter give the result of evaluating ' +
                               'the OpaqueExpression.')

    def result_operation(self):
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


class ConnectorKind(models.Model):
    """
    ConnectorKind is an enumeration that defines whether a Connector is an assembly or a delegation.
    """

    __package__ = 'UML.StructuredClassifiers'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    ASSEMBLY = 'assembly'
    DELEGATION = 'delegation'
    CHOICES = (
        (ASSEMBLY, 'Indicates that the Connector is an assembly Connector.'),
        (DELEGATION, 'Indicates that the Connector is a delegation Connector.'),
    )

    connector_kind = models.CharField(max_length=255, choices=CHOICES, default=DELEGATION)


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
    file_name = models.CharField(max_length=255, 
                                 help_text='A concrete name that is used to refer to the Artifact in a physical ' +
                                 'context. Example: file system name, universal resource locator.')
    manifestation = models.ForeignKey('Manifestation', related_name='%(app_label)s_%(class)s_manifestation', 
                                      help_text='The set of model elements that are manifested in the Artifact. ' +
                                      'That is, these model elements are utilized in the construction (or ' +
                                      'generation) of the artifact.')
    nested_artifact = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_nested_artifact', 
                                        help_text='The Artifacts that are defined (nested) within the Artifact. ' +
                                        'The association is a specialization of the ownedMember association from ' +
                                        'Namespace to NamedElement.')
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute', 
                                        help_text='The attributes or association ends defined for the Artifact. ' +
                                        'The association is a specialization of the ownedMember association.')
    owned_operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_owned_operation', 
                                        help_text='The Operations defined for the Artifact. The association is a ' +
                                        'specialization of the ownedMember association.')


class DeploymentSpecification(models.Model):
    """
    A deployment specification specifies a set of properties that determine execution parameters of a component
    artifact that is deployed on a node. A deployment specification can be aimed at a specific type of
    container. An artifact that reifies or implements deployment specification properties is a deployment
    descriptor.
    """

    __package__ = 'UML.Deployments'

    artifact = models.OneToOneField('Artifact', on_delete=models.CASCADE, primary_key=True)
    deployment = models.ForeignKey('Deployment', related_name='%(app_label)s_%(class)s_deployment', 
                                   help_text='The deployment with which the DeploymentSpecification is ' +
                                   'associated.')
    deployment_location = models.CharField(max_length=255, 
                                           help_text='The location where an Artifact is deployed onto a Node. ' +
                                           'This is typically a "directory" or "memory address."')
    execution_location = models.CharField(max_length=255, 
                                          help_text='The location where a component Artifact executes. This may ' +
                                          'be a local or remote location.')


class MessageKind(models.Model):
    """
    This is an enumerated type that identifies the type of Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    LOST = 'lost'
    COMPLETE = 'complete'
    UNKNOWN = 'unknown'
    FOUND = 'found'
    CHOICES = (
        (LOST, 'sendEvent present and receiveEvent absent'),
        (COMPLETE, 'sendEvent and receiveEvent are present'),
        (UNKNOWN, 'sendEvent and receiveEvent absent (should not appear)'),
        (FOUND, 'sendEvent absent and receiveEvent present'),
    )

    message_kind = models.CharField(max_length=255, choices=CHOICES, default=FOUND)


class DestructionOccurrenceSpecification(models.Model):
    """
    A DestructionOccurenceSpecification models the destruction of an object.
    """

    __package__ = 'UML.Interactions'

    message_occurrence_specification = models.OneToOneField('MessageOccurrenceSpecification', on_delete=models.CASCADE, primary_key=True)


class StructuredActivityNode(models.Model):
    """
    A StructuredActivityNode is an Action that is also an ActivityGroup and whose behavior is specified by the
    ActivityNodes and ActivityEdges it so contains. Unlike other kinds of ActivityGroup, a
    StructuredActivityNode owns the ActivityNodes and ActivityEdges it contains, and so a node or edge can only
    be directly contained in one StructuredActivityNode, though StructuredActivityNodes may be nested.
    """

    __package__ = 'UML.Actions'

    namespace = models.OneToOneField('Namespace', on_delete=models.CASCADE, primary_key=True)
    activity_group = models.OneToOneField('ActivityGroup')
    action = models.OneToOneField('Action')
    activity = models.ForeignKey('Activity', related_name='%(app_label)s_%(class)s_activity', 
                                 help_text='The Activity immediately containing the StructuredActivityNode, if it ' +
                                 'is not contained in another StructuredActivityNode.')
    edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', 
                             help_text='The ActivityEdges immediately contained in the StructuredActivityNode.')
    must_isolate = models.BooleanField(help_text='If true, then any object used by an Action within the ' +
                                       'StructuredActivityNode cannot be accessed by any Action outside the node ' +
                                       'until the StructuredActivityNode as a whole completes. Any concurrent ' +
                                       'Actions that would result in accessing such objects are required to have ' +
                                       'their execution deferred until the completion of the ' +
                                       'StructuredActivityNode.')
    node = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_node', 
                             help_text='The ActivityNodes immediately contained in the StructuredActivityNode.')
    structured_node_input = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_structured_node_input', 
                                              help_text='The InputPins owned by the StructuredActivityNode.')
    structured_node_output = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_structured_node_output', 
                                               help_text='The OutputPins owned by the StructuredActivityNode.')
    variable = models.ForeignKey('Variable', related_name='%(app_label)s_%(class)s_variable', 
                                 help_text='The Variables defined in the scope of the StructuredActivityNode.')

    def all_actions(self):
        """
        Returns this StructuredActivityNode and all Actions contained in it.

        .. ocl::
            result = (node->select(oclIsKindOf(Action)).oclAsType(Action).allActions()->including(self)->asSet())
        """
        pass


class ConditionalNode(models.Model):
    """
    A ConditionalNode is a StructuredActivityNode that chooses one among some number of alternative collections
    of ExecutableNodes to execute.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)
    clause = models.ForeignKey('Clause', related_name='%(app_label)s_%(class)s_clause', 
                               help_text='The set of Clauses composing the ConditionalNode.')
    is_assured = models.BooleanField(help_text='If true, the modeler asserts that the test for at least one ' +
                                     'Clause of the ConditionalNode will succeed.')
    is_determinate = models.BooleanField(help_text='If true, the modeler asserts that the test for at most one ' +
                                         'Clause of the ConditionalNode will succeed.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPins that onto which are moved values from the bodyOutputs of ' +
                               'the Clause selected for execution.')

    def all_actions(self):
        """
        Return only this ConditionalNode. This prevents Actions within the ConditionalNode from having their
        OutputPins used as bodyOutputs or decider Pins in containing LoopNodes or ConditionalNodes.

        .. ocl::
            result = (self->asSet())
        """
        pass


class TimeEvent(models.Model):
    """
    A TimeEvent is an Event that occurs at a specific point in time.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)
    is_relative = models.BooleanField(help_text='Specifies whether the TimeEvent is specified as an absolute or ' +
                                      'relative time.')
    when = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_when', 
                             help_text='Specifies the time of the TimeEvent.')


class FlowFinalNode(models.Model):
    """
    A FlowFinalNode is a FinalNode that terminates a flow by consuming the tokens offered to it.
    """

    __package__ = 'UML.Activities'

    final_node = models.OneToOneField('FinalNode', on_delete=models.CASCADE, primary_key=True)


class ObjectNodeOrderingKind(models.Model):
    """
    ObjectNodeOrderingKind is an enumeration indicating queuing order for offering the tokens held by an
    ObjectNode.
    """

    __package__ = 'UML.Activities'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    UNORDERED = 'unordered'
    LIFO = 'lifo'
    FIFO = 'fifo'
    ORDERED = 'ordered'
    CHOICES = (
        (UNORDERED, 'Indicates that tokens are unordered.'),
        (LIFO, 'Indicates that tokens are queued in a last in, first out manner.'),
        (FIFO, 'Indicates that tokens are queued in a first in, first out manner.'),
        (ORDERED, 'Indicates that tokens are ordered.'),
    )

    object_node_ordering_kind = models.CharField(max_length=255, choices=CHOICES, default=ORDERED)


class ReadLinkAction(models.Model):
    """
    A ReadLinkAction is a LinkAction that navigates across an Association to retrieve the objects on one end.
    """

    __package__ = 'UML.Actions'

    link_action = models.OneToOneField('LinkAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')

    def open_end(self):
        """
        Returns the ends corresponding to endData with no value InputPin. (A well-formed ReadLinkAction is
        constrained to have only one of these.)

        .. ocl::
            result = (endData->select(value=null).end->asOrderedSet())
        """
        pass


class MergeNode(models.Model):
    """
    A merge node is a control node that brings together multiple alternate flows. It is not used to synchronize
    concurrent flows but to accept one among several alternate flows.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)


class Trigger(models.Model):
    """
    A Trigger specifies a specific point  at which an Event occurrence may trigger an effect in a Behavior. A
    Trigger may be qualified by the Port on which the Event occurred.
    """

    __package__ = 'UML.CommonBehavior'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    event = models.ForeignKey('Event', related_name='%(app_label)s_%(class)s_event', 
                              help_text='The Event that detected by the Trigger.')
    port = models.ForeignKey('Port', related_name='%(app_label)s_%(class)s_port', 
                             help_text='A optional Port of through which the given effect is detected.')


class ReadSelfAction(models.Model):
    """
    A ReadSelfAction is an Action that retrieves the context object of the Behavior execution within which the
    ReadSelfAction execution is taking place.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')


class CombinedFragment(models.Model):
    """
    A CombinedFragment defines an expression of InteractionFragments. A CombinedFragment is defined by an
    interaction operator and corresponding InteractionOperands. Through the use of CombinedFragments the user
    will be able to describe a number of traces in a compact and concise manner.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    cfragment_gate = models.ForeignKey('Gate', related_name='%(app_label)s_%(class)s_cfragment_gate', 
                                       help_text='Specifies the gates that form the interface between this ' +
                                       'CombinedFragment and its surroundings')
    interaction_operator = models.ForeignKey('InteractionOperatorKind', related_name='%(app_label)s_%(class)s_interaction_operator', 
                                             help_text='Specifies the operation which defines the semantics of ' +
                                             'this combination of InteractionFragments.')
    operand = models.ForeignKey('InteractionOperand', related_name='%(app_label)s_%(class)s_operand', 
                                help_text='The set of operands of the combined fragment.')


class ConsiderIgnoreFragment(models.Model):
    """
    A ConsiderIgnoreFragment is a kind of CombinedFragment that is used for the consider and ignore cases, which
    require lists of pertinent Messages to be specified.
    """

    __package__ = 'UML.Interactions'

    combined_fragment = models.OneToOneField('CombinedFragment', on_delete=models.CASCADE, primary_key=True)
    message = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_message')


class LinkEndDestructionData(models.Model):
    """
    LinkEndDestructionData is LinkEndData used to provide values for one end of a link to be destroyed by a
    DestroyLinkAction.
    """

    __package__ = 'UML.Actions'

    link_end_data = models.OneToOneField('LinkEndData', on_delete=models.CASCADE, primary_key=True)
    destroy_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_destroy_at', 
                                   help_text='The InputPin that provides the position of an existing link to be ' +
                                   'destroyed in an ordered, nonunique Association end. The type of the destroyAt ' +
                                   'InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.')
    is_destroy_duplicates = models.BooleanField(help_text='Specifies whether to destroy duplicates of the value ' +
                                                'in nonunique Association ends.')

    def all_pins(self):
        """
        Adds the destroyAt InputPin (if any) to the set of all Pins.

        .. ocl::
            result = (self.LinkEndData::allPins()->including(destroyAt))
        """
        pass


class CreateObjectAction(models.Model):
    """
    A CreateObjectAction is an Action that creates an instance of the specified Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The Classifier to be instantiated.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin on which the newly created object is placed.')


class ReadStructuralFeatureAction(models.Model):
    """
    A ReadStructuralFeatureAction is a StructuralFeatureAction that retrieves the values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')


class ChangeEvent(models.Model):
    """
    A ChangeEvent models a change in the system configuration that makes a condition true.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)
    change_expression = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_change_expression')


class MessageEvent(models.Model):
    """
    A MessageEvent specifies the receipt by an object of either an Operation call or a Signal instance.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.OneToOneField('Event', on_delete=models.CASCADE, primary_key=True)


class AnyReceiveEvent(models.Model):
    """
    A trigger for an AnyReceiveEvent is triggered by the receipt of any message that is not explicitly handled
    by any related trigger.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)


class TemplateParameterSubstitution(models.Model):
    """
    A TemplateParameterSubstitution relates the actual parameter to a formal TemplateParameter as part of a
    template binding.
    """

    __package__ = 'UML.CommonStructure'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    actual = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_actual', 
                               help_text='The ParameterableElement that is the actual parameter for this ' +
                               'TemplateParameterSubstitution.')
    formal = models.ForeignKey('TemplateParameter', related_name='%(app_label)s_%(class)s_formal', 
                               help_text='The formal TemplateParameter that is associated with this ' +
                               'TemplateParameterSubstitution.')
    owned_actual = models.ForeignKey('ParameterableElement', related_name='%(app_label)s_%(class)s_owned_actual', 
                                     help_text='The ParameterableElement that is owned by this ' +
                                     'TemplateParameterSubstitution as its actual parameter.')
    template_binding = models.ForeignKey('TemplateBinding', related_name='%(app_label)s_%(class)s_template_binding', 
                                         help_text='The TemplateBinding that owns this ' +
                                         'TemplateParameterSubstitution.')


class TestIdentityAction(models.Model):
    """
    A TestIdentityAction is an Action that tests if two values are identical objects.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    first = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_first', 
                              help_text='The InputPin on which the first input object is placed.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin whose Boolean value indicates whether the two input ' +
                               'objects are identical.')
    second = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_second', 
                               help_text='The OutputPin on which the second input object is placed.')


class LoopNode(models.Model):
    """
    A LoopNode is a StructuredActivityNode that represents an iterative loop with setup, test, and body
    sections.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)
    body_output = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_body_output', 
                                    help_text='The OutputPins on Actions within the bodyPart, the values of which ' +
                                    'are moved to the loopVariable OutputPins after the completion of each ' +
                                    'execution of the bodyPart, before the next iteration of the loop begins or ' +
                                    'before the loop exits.')
    body_part = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_body_part', 
                                  help_text='The set of ExecutableNodes that perform the repetitive computations ' +
                                  'of the loop. The bodyPart is executed as long as the test section produces a ' +
                                  'true value.')
    decider = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_decider', 
                                help_text='An OutputPin on an Action in the test section whose Boolean value ' +
                                'determines whether to continue executing the loop bodyPart.')
    is_tested_first = models.BooleanField(help_text='If true, the test is performed before the first execution of ' +
                                          'the bodyPart. If false, the bodyPart is executed once before the test ' +
                                          'is performed.')
    loop_variable = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_loop_variable', 
                                      help_text='A list of OutputPins that hold the values of the loop variables ' +
                                      'during an execution of the loop. When the test fails, the values are moved ' +
                                      'to the result OutputPins of the loop.')
    loop_variable_input = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_loop_variable_input', 
                                            help_text='A list of InputPins whose values are moved into the ' +
                                            'loopVariable Pins before the first iteration of the loop.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='A list of OutputPins that receive the loopVariable values after the ' +
                               'last iteration of the loop and constitute the output of the LoopNode.')
    setup_part = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_setup_part', 
                                   help_text='The set of ExecutableNodes executed before the first iteration of ' +
                                   'the loop, in order to initialize values or perform other setup computations.')
    test = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_test', 
                             help_text='The set of ExecutableNodes executed in order to provide the test result ' +
                             'for the loop.')

    def all_actions(self):
        """
        Return only this LoopNode. This prevents Actions within the LoopNode from having their OutputPins used
        as bodyOutputs or decider Pins in containing LoopNodes or ConditionalNodes.

        .. ocl::
            result = (self->asSet())
        """
        pass


class OpaqueAction(models.Model):
    """
    An OpaqueAction is an Action whose functionality is not specified within UML.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    body = models.CharField(max_length=255, 
                            help_text='Provides a textual specification of the functionality of the Action, in ' +
                            'one or more languages other than UML.')
    input_value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_input_value', 
                                    help_text='The InputPins providing inputs to the OpaqueAction.')
    language = models.CharField(max_length=255, 
                                help_text='If provided, a specification of the language used for each of the body ' +
                                'Strings.')
    output_value = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_output_value', 
                                     help_text='The OutputPins on which the OpaqueAction provides outputs.')


class Pin(models.Model):
    """
    A Pin is an ObjectNode and MultiplicityElement that provides input values to an Action or accepts output
    values from an Action.
    """

    __package__ = 'UML.Actions'

    object_node = models.OneToOneField('ObjectNode', on_delete=models.CASCADE, primary_key=True)
    multiplicity_element = models.OneToOneField('MultiplicityElement')
    is_control = models.BooleanField()


class InputPin(models.Model):
    """
    An InputPin is a Pin that holds input values to be consumed by an Action.
    """

    __package__ = 'UML.Actions'

    pin = models.OneToOneField('Pin', on_delete=models.CASCADE, primary_key=True)


class ProtocolTransition(models.Model):
    """
    A ProtocolTransition specifies a legal Transition for an Operation. Transitions of ProtocolStateMachines
    have the following information: a pre-condition (guard), a Trigger, and a post-condition. Every
    ProtocolTransition is associated with at most one BehavioralFeature belonging to the context Classifier of
    the ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    transition = models.OneToOneField('Transition', on_delete=models.CASCADE, primary_key=True)
    post_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_post_condition', 
                                       help_text='Specifies the post condition of the Transition which is the ' +
                                       'Condition that should be obtained once the Transition is triggered. This ' +
                                       'post condition is part of the post condition of the Operation connected to ' +
                                       'the Transition.')
    pre_condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_pre_condition', 
                                      help_text='Specifies the precondition of the Transition. It specifies the ' +
                                      'Condition that should be verified before triggering the Transition. This ' +
                                      'guard condition added to the source State will be evaluated as part of the ' +
                                      'precondition of the Operation referred by the Transition if any.')
    referred = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_referred', 
                                 help_text='This association refers to the associated Operation. It is derived ' +
                                 'from the Operation of the CallEvent Trigger when applicable.')

    def referred_operation(self):
        """
        Derivation for ProtocolTransition::/referred

        .. ocl::
            result = (trigger->collect(event)->select(oclIsKindOf(CallEvent))->collect(oclAsType(CallEvent).operation)->asSet())
        """
        pass


class ParameterSet(models.Model):
    """
    A ParameterSet designates alternative sets of inputs or outputs that a Behavior may use.
    """

    __package__ = 'UML.Classification'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_condition', 
                                  help_text='A constraint that should be satisfied for the owner of the ' +
                                  'Parameters in an input ParameterSet to start execution using the values ' +
                                  'provided for those Parameters, or the owner of the Parameters in an output ' +
                                  'ParameterSet to end execution providing the values for those Parameters, if all ' +
                                  'preconditions and conditions on input ParameterSets were satisfied.')
    parameter = models.ForeignKey('Parameter', related_name='%(app_label)s_%(class)s_parameter', 
                                  help_text='Parameters in the ParameterSet.')


class Lifeline(models.Model):
    """
    A Lifeline represents an individual participant in the Interaction. While parts and structural features may
    have multiplicity greater than 1, Lifelines represent only one interacting entity.
    """

    __package__ = 'UML.Interactions'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    covered_by = models.ForeignKey('InteractionFragment', related_name='%(app_label)s_%(class)s_covered_by', 
                                   help_text='References the InteractionFragments in which this Lifeline takes ' +
                                   'part.')
    decomposed_as = models.ForeignKey('PartDecomposition', related_name='%(app_label)s_%(class)s_decomposed_as', 
                                      help_text='References the Interaction that represents the decomposition.')
    interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_interaction', 
                                    help_text='References the Interaction enclosing this Lifeline.')
    represents = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_represents', 
                                   help_text='References the ConnectableElement within the classifier that ' +
                                   'contains the enclosing interaction.')
    selector = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_selector', 
                                 help_text='If the referenced ConnectableElement is multivalued, then this ' +
                                 'specifies the specific individual part within that set.')


class PrimitiveType(models.Model):
    """
    A PrimitiveType defines a predefined DataType, without any substructure. A PrimitiveType may have an algebra
    and operations defined outside of UML, for example, mathematically.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType', on_delete=models.CASCADE, primary_key=True)


class ProfileApplication(models.Model):
    """
    A profile application is used to show which profiles have been applied to a package.
    """

    __package__ = 'UML.Packages'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    applied_profile = models.ForeignKey('Profile', related_name='%(app_label)s_%(class)s_applied_profile', 
                                        help_text='References the Profiles that are applied to a Package through ' +
                                        'this ProfileApplication.')
    applying_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_applying_package', 
                                         help_text='The package that owns the profile application.')
    is_strict = models.BooleanField(help_text='Specifies that the Profile filtering rules for the metaclasses of ' +
                                    'the referenced metamodel shall be strictly applied.')


class TimeExpression(models.Model):
    """
    A TimeExpression is a ValueSpecification that represents a time value.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    expr = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_expr', 
                             help_text='A ValueSpecification that evaluates to the value of the TimeExpression.')
    observation = models.ForeignKey('Observation', related_name='%(app_label)s_%(class)s_observation', 
                                    help_text='Refers to the Observations that are involved in the computation of ' +
                                    'the TimeExpression value.')


class InterruptibleActivityRegion(models.Model):
    """
    An InterruptibleActivityRegion is an ActivityGroup that supports the termination of tokens flowing in the
    portions of an activity within it.
    """

    __package__ = 'UML.Activities'

    activity_group = models.OneToOneField('ActivityGroup', on_delete=models.CASCADE, primary_key=True)
    interrupting_edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_interrupting_edge', 
                                          help_text='The ActivityEdges leaving the InterruptibleActivityRegion on ' +
                                          'which a traversing token will result in the termination of other tokens ' +
                                          'flowing in the InterruptibleActivityRegion.')
    node = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_node', 
                             help_text='ActivityNodes immediately contained in the InterruptibleActivityRegion.')


class CreateLinkObjectAction(models.Model):
    """
    A CreateLinkObjectAction is a CreateLinkAction for creating link objects (AssociationClasse instances).
    """

    __package__ = 'UML.Actions'

    create_link_action = models.OneToOneField('CreateLinkAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')


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

    state_machine = models.OneToOneField('StateMachine', on_delete=models.CASCADE, primary_key=True)
    conformance = models.ForeignKey('ProtocolConformance', related_name='%(app_label)s_%(class)s_conformance')


class StateInvariant(models.Model):
    """
    A StateInvariant is a runtime constraint on the participants of the Interaction. It may be used to specify a
    variety of different kinds of Constraints, such as values of Attributes or Variables, internal or external
    States, and so on. A StateInvariant is an InteractionFragment and it is placed on a Lifeline.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    covered = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_covered', 
                                help_text='References the Lifeline on which the StateInvariant appears.')
    invariant = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_invariant', 
                                  help_text='A Constraint that should hold at runtime for this StateInvariant.')


class Activity(models.Model):
    """
    An Activity is the specification of parameterized Behavior as the coordinated sequencing of subordinate
    units.
    """

    __package__ = 'UML.Activities'

    behavior = models.OneToOneField('Behavior', on_delete=models.CASCADE, primary_key=True)
    edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_edge', 
                             help_text='ActivityEdges expressing flow between the nodes of the Activity.')
    group = models.ForeignKey('ActivityGroup', related_name='%(app_label)s_%(class)s_group', 
                              help_text='Top-level ActivityGroups in the Activity.')
    is_read_only = models.BooleanField(help_text='If true, this Activity must not make any changes to objects. ' +
                                       'The default is false (an Activity may make nonlocal changes). (This is an ' +
                                       'assertion, not an executable property. It may be used by an execution ' +
                                       'engine to optimize model execution. If the assertion is violated by the ' +
                                       'Activity, then the model is ill-formed.)')
    is_single_execution = models.BooleanField(help_text='If true, all invocations of the Activity are handled by ' +
                                              'the same execution.')
    node = models.ForeignKey('ActivityNode', related_name='%(app_label)s_%(class)s_node', 
                             help_text='ActivityNodes coordinated by the Activity.')
    partition = models.ForeignKey('ActivityPartition', related_name='%(app_label)s_%(class)s_partition', 
                                  help_text='Top-level ActivityPartitions in the Activity.')
    structured_node = models.ForeignKey('StructuredActivityNode', related_name='%(app_label)s_%(class)s_structured_node', 
                                        help_text='Top-level StructuredActivityNodes in the Activity.')
    variable = models.ForeignKey('Variable', related_name='%(app_label)s_%(class)s_variable', 
                                 help_text='Top-level Variables defined by the Activity.')


class ClearVariableAction(models.Model):
    """
    A ClearVariableAction is a VariableAction that removes all values of a Variable.
    """

    __package__ = 'UML.Actions'

    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)


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
    selection = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_selection', 
                                  help_text='A Behavior used to select tokens from a source ObjectNode.')
    transformation = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_transformation', 
                                       help_text='A Behavior used to change or replace object tokens flowing ' +
                                       'along the ObjectFlow.')


class LiteralInteger(models.Model):
    """
    A LiteralInteger is a specification of an Integer value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.IntegerField()

    def integer_value(self):
        """
        The query integerValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass


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
    packaged_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_packaged_element', 
                                         help_text='The set of PackageableElements that a Component owns. In the ' +
                                         'namespace of a Component, all model elements that are involved in or ' +
                                         'related to its definition may be owned or imported explicitly. These may ' +
                                         'include e.g., Classes, Interfaces, Components, Packages, UseCases, ' +
                                         'Dependencies (e.g., mappings), and Artifacts.')
    provided = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_provided', 
                                 help_text='The Interfaces that the Component exposes to its environment. These ' +
                                 'Interfaces may be Realized by the Component or any of its realizingClassifiers, ' +
                                 'or they may be the Interfaces that are provided by its public Ports.')
    realization = models.ForeignKey('ComponentRealization', related_name='%(app_label)s_%(class)s_realization', 
                                    help_text='The set of Realizations owned by the Component. Realizations ' +
                                    'reference the Classifiers of which the Component is an abstraction; i.e., ' +
                                    'that realize its behavior.')
    required = models.ForeignKey('Interface', related_name='%(app_label)s_%(class)s_required', 
                                 help_text='The Interfaces that the Component requires from other Components in ' +
                                 'its environment in order to be able to offer its full set of provided ' +
                                 'functionality. These Interfaces may be used by the Component or any of its ' +
                                 'realizingClassifiers, or they may be the Interfaces that are required by its ' +
                                 'public Ports.')

    def provided_operation(self):
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


class SequenceNode(models.Model):
    """
    A SequenceNode is a StructuredActivityNode that executes a sequence of ExecutableNodes in order.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)
    executable_node = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_executable_node')


class Usage(models.Model):
    """
    A Usage is a Dependency in which the client Element requires the supplier Element (or set of Elements) for
    its full implementation or operation.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency', on_delete=models.CASCADE, primary_key=True)


class RemoveVariableValueAction(models.Model):
    """
    A RemoveVariableValueAction is a WriteVariableAction that removes values from a Variables.
    """

    __package__ = 'UML.Actions'

    write_variable_action = models.OneToOneField('WriteVariableAction', on_delete=models.CASCADE, primary_key=True)
    is_remove_duplicates = models.BooleanField(help_text='Specifies whether to remove duplicates of the value in ' +
                                               'nonunique Variables.')
    remove_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_remove_at', 
                                  help_text='An InputPin that provides the position of an existing value to ' +
                                  'remove in ordered, nonunique Variables. The type of the removeAt InputPin is ' +
                                  'UnlimitedNatural, but the value cannot be zero or unlimited.')


class StartClassifierBehaviorAction(models.Model):
    """
    A StartClassifierBehaviorAction is an Action that starts the classifierBehavior of the input object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object')


class Interaction(models.Model):
    """
    An Interaction is a unit of Behavior that focuses on the observable exchange of information between
    connectable elements.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    behavior = models.OneToOneField('Behavior')
    action = models.ForeignKey('Action', related_name='%(app_label)s_%(class)s_action', 
                               help_text='Actions owned by the Interaction.')
    formal_gate = models.ForeignKey('Gate', related_name='%(app_label)s_%(class)s_formal_gate', 
                                    help_text='Specifies the gates that form the message interface between this ' +
                                    'Interaction and any InteractionUses which reference it.')
    fragment = models.ForeignKey('InteractionFragment', related_name='%(app_label)s_%(class)s_fragment', 
                                 help_text='The ordered set of fragments in the Interaction.')
    lifeline = models.ForeignKey('Lifeline', related_name='%(app_label)s_%(class)s_lifeline', 
                                 help_text='Specifies the participants in this Interaction.')
    message = models.ForeignKey('Message', related_name='%(app_label)s_%(class)s_message', 
                                help_text='The Messages contained in this Interaction.')


class SendSignalAction(models.Model):
    """
    A SendSignalAction is an InvocationAction that creates a Signal instance and transmits it to the target
    object. Values from the argument InputPins are used to provide values for the attributes of the Signal. The
    requestor continues execution immediately after the Signal instance is sent out and cannot receive reply
    values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal', 
                               help_text='The Signal whose instance is transmitted to the target.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', 
                               help_text='The InputPin that provides the target object to which the Signal ' +
                               'instance is sent.')


class ExtensionEnd(models.Model):
    """
    An extension end is used to tie an extension to a stereotype when extending a metaclass. The default
    multiplicity of an extension end is 0..1.
    """

    __package__ = 'UML.Packages'

    has_property = models.OneToOneField('Property', on_delete=models.CASCADE, primary_key=True)
    lower = models.IntegerField(help_text='This redefinition changes the default multiplicity of association ' +
                                'ends, since model elements are usually extended by 0 or 1 instance of the ' +
                                'extension stereotype.')
    has_type = models.ForeignKey('Stereotype', related_name='%(app_label)s_%(class)s_has_type', 
                                 help_text='References the type of the ExtensionEnd. Note that this association ' +
                                 'restricts the possible types of an ExtensionEnd to only be Stereotypes.')

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an Integer. This is a redefinition
        of the default lower bound, which normally, for MultiplicityElements, evaluates to 1 if empty.

        .. ocl::
            result = (if lowerValue=null then 0 else lowerValue.integerValue() endif)
        """
        pass


class Substitution(models.Model):
    """
    A substitution is a relationship between two classifiers signifying that the substituting classifier
    complies with the contract specified by the contract classifier. This implies that instances of the
    substituting classifier are runtime substitutable where instances of the contract classifier are expected.
    """

    __package__ = 'UML.Classification'

    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)
    contract = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_contract', 
                                 help_text='The contract with which the substituting classifier complies.')
    substituting_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_substituting_classifier', 
                                                help_text='Instances of the substituting classifier are runtime ' +
                                                'substitutable where instances of the contract classifier are ' +
                                                'expected.')


class ConnectorEnd(models.Model):
    """
    A ConnectorEnd is an endpoint of a Connector, which attaches the Connector to a ConnectableElement.
    """

    __package__ = 'UML.StructuredClassifiers'

    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    defining_end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_defining_end', 
                                     help_text='A derived property referencing the corresponding end on the ' +
                                     'Association which types the Connector owing this ConnectorEnd, if any. It is ' +
                                     'derived by selecting the end at the same place in the ordering of ' +
                                     'Association ends as this ConnectorEnd.')
    part_with_port = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_part_with_port', 
                                       help_text='Indicates the role of the internal structure of a Classifier ' +
                                       'with the Port to which the ConnectorEnd is attached.')
    role = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_role', 
                             help_text='The ConnectableElement attached at this ConnectorEnd. When an instance of ' +
                             'the containing Classifier is created, a link may (depending on the multiplicities) ' +
                             'be created to an instance of the Classifier that types this ConnectableElement.')

    def defining_end_operation(self):
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


class OpaqueBehavior(models.Model):
    """
    An OpaqueBehavior is a Behavior whose specification is given in a textual language other than UML.
    """

    __package__ = 'UML.CommonBehavior'

    behavior = models.OneToOneField('Behavior', on_delete=models.CASCADE, primary_key=True)
    body = models.CharField(max_length=255, help_text='Specifies the behavior in one or more languages.')
    language = models.CharField(max_length=255, 
                                help_text='Languages the body strings use in the same order as the body strings.')


class FinalState(models.Model):
    """
    A special kind of State, which, when entered, signifies that the enclosing Region has completed. If the
    enclosing Region is directly contained in a StateMachine and all other Regions in that StateMachine also are
    completed, then it means that the entire StateMachine behavior is completed.
    """

    __package__ = 'UML.StateMachines'

    state = models.OneToOneField('State', on_delete=models.CASCADE, primary_key=True)


class AggregationKind(models.Model):
    """
    AggregationKind is an Enumeration for specifying the kind of aggregation of a Property.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    SHARED = 'shared'
    COMPOSITE = 'composite'
    NONE = 'none'
    CHOICES = (
        (SHARED, 'Indicates that the Property has shared aggregation.'),
        (COMPOSITE, 'Indicates that the Property is aggregated compositely, i.e., the ' +
                    'composite object has responsibility for the existence and storage of the ' +
                    'composed objects (parts).'),
        (NONE, 'Indicates that the Property has no aggregation.'),
    )

    aggregation_kind = models.CharField(max_length=255, choices=CHOICES, default=NONE)


class ClearStructuralFeatureAction(models.Model):
    """
    A ClearStructuralFeatureAction is a StructuralFeatureAction that removes all values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    structural_feature_action = models.OneToOneField('StructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')


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


class InstanceSpecification(models.Model):
    """
    An InstanceSpecification is a model element that represents an instance in a modeled system. An
    InstanceSpecification can act as a DeploymentTarget in a Deployment relationship, in the case that it
    represents an instance of a Node. It can also act as a DeployedArtifact, if it represents an instance of an
    Artifact.
    """

    __package__ = 'UML.Classification'

    deployment_target = models.OneToOneField('DeploymentTarget', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')
    deployed_artifact = models.OneToOneField('DeployedArtifact')
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The Classifier or Classifiers of the represented instance. If ' +
                                   'multiple Classifiers are specified, the instance is classified by all of ' +
                                   'them.')
    slot = models.ForeignKey('Slot', related_name='%(app_label)s_%(class)s_slot', 
                             help_text='A Slot giving the value or values of a StructuralFeature of the instance. ' +
                             'An InstanceSpecification can have one Slot per StructuralFeature of its Classifiers, ' +
                             'including inherited features. It is not necessary to model a Slot for every ' +
                             'StructuralFeature, in which case the InstanceSpecification is a partial ' +
                             'description.')
    specification = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_specification', 
                                      help_text='A specification of how to compute, derive, or construct the ' +
                                      'instance.')


class DecisionNode(models.Model):
    """
    A DecisionNode is a ControlNode that chooses between outgoing ActivityEdges for the routing of tokens.
    """

    __package__ = 'UML.Activities'

    control_node = models.OneToOneField('ControlNode', on_delete=models.CASCADE, primary_key=True)
    decision_input = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_decision_input', 
                                       help_text='A Behavior that is executed to provide an input to guard ' +
                                       'ValueSpecifications on ActivityEdges outgoing from the DecisionNode.')
    decision_input_flow = models.ForeignKey('ObjectFlow', related_name='%(app_label)s_%(class)s_decision_input_flow', 
                                            help_text='An additional ActivityEdge incoming to the DecisionNode ' +
                                            'that provides a decision input value for the guards ' +
                                            'ValueSpecifications on ActivityEdges outgoing from the DecisionNode.')


class DataStoreNode(models.Model):
    """
    A DataStoreNode is a CentralBufferNode for persistent data.
    """

    __package__ = 'UML.Activities'

    central_buffer_node = models.OneToOneField('CentralBufferNode', on_delete=models.CASCADE, primary_key=True)


class ReadVariableAction(models.Model):
    """
    A ReadVariableAction is a VariableAction that retrieves the values of a Variable.
    """

    __package__ = 'UML.Actions'

    variable_action = models.OneToOneField('VariableAction', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result')


class LiteralNull(models.Model):
    """
    A LiteralNull specifies the lack of a value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)

    def is_null(self):
        """
        The query isNull() returns true.

        .. ocl::
            result = (true)
        """
        pass


class Manifestation(models.Model):
    """
    A manifestation is the concrete physical rendering of one or more model elements by an artifact.
    """

    __package__ = 'UML.Deployments'

    abstraction = models.OneToOneField('Abstraction', on_delete=models.CASCADE, primary_key=True)
    utilized_element = models.ForeignKey('PackageableElement', related_name='%(app_label)s_%(class)s_utilized_element')


class DurationConstraint(models.Model):
    """
    A DurationConstraint is a Constraint that refers to a DurationInterval.
    """

    __package__ = 'UML.Values'

    interval_constraint = models.OneToOneField('IntervalConstraint', on_delete=models.CASCADE, primary_key=True)
    first_event = models.BooleanField(help_text='The value of firstEvent[i] is related to constrainedElement[i] ' +
                                      '(where i is 1 or 2). If firstEvent[i] is true, then the corresponding ' +
                                      'observation event is the first time instant the execution enters ' +
                                      'constrainedElement[i]. If firstEvent[i] is false, then the corresponding ' +
                                      'observation event is the last time instant the execution is within ' +
                                      'constrainedElement[i].')
    specification = models.ForeignKey('DurationInterval', related_name='%(app_label)s_%(class)s_specification', 
                                      help_text='The DurationInterval constraining the duration.')


class UseCase(models.Model):
    """
    A UseCase specifies a set of actions performed by its subjects, which yields an observable result that is of
    value for one or more Actors or other stakeholders of each subject.
    """

    __package__ = 'UML.UseCases'

    behaviored_classifier = models.OneToOneField('BehavioredClassifier', on_delete=models.CASCADE, primary_key=True)
    extend = models.ForeignKey('Extend', related_name='%(app_label)s_%(class)s_extend', 
                               help_text='The Extend relationships owned by this UseCase.')
    extension_point = models.ForeignKey('ExtensionPoint', related_name='%(app_label)s_%(class)s_extension_point', 
                                        help_text='The ExtensionPoints owned by this UseCase.')
    include = models.ForeignKey('Include', related_name='%(app_label)s_%(class)s_include', 
                                help_text='The Include relationships owned by this UseCase.')
    subject = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_subject', 
                                help_text='The subjects to which this UseCase applies. Each subject or its parts ' +
                                'realize all the UseCases that apply to it.')

    def all_included_use_cases(self):
        """
        The query allIncludedUseCases() returns the transitive closure of all UseCases (directly or indirectly)
        included by this UseCase.

        .. ocl::
            result = (self.include.addition->union(self.include.addition->collect(uc | uc.allIncludedUseCases()))->asSet())
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
    imported_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_imported_package', 
                                         help_text='Specifies the Package whose members are imported into a ' +
                                         'Namespace.')
    importing_namespace = models.ForeignKey('Namespace', related_name='%(app_label)s_%(class)s_importing_namespace', 
                                            help_text='Specifies the Namespace that imports the members from a ' +
                                            'Package.')
    visibility = models.ForeignKey('VisibilityKind', related_name='%(app_label)s_%(class)s_visibility', 
                                   help_text='Specifies the visibility of the imported PackageableElements within ' +
                                   'the importingNamespace, i.e., whether imported Elements will in turn be ' +
                                   'visible to other Namespaces. If the PackageImport is public, the imported ' +
                                   'Elements will be visible outside the importingNamespace, while, if the ' +
                                   'PackageImport is private, they will not.')


class LiteralReal(models.Model):
    """
    A LiteralReal is a specification of a Real value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.FloatField()

    def real_value(self):
        """
        The query realValue() gives the value.

        .. ocl::
            result = (value)
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

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    packageable_element = models.OneToOneField('PackageableElement')
    conveyed = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_conveyed', 
                                 help_text='Specifies the information items that may circulate on this ' +
                                 'information flow.')
    information_source = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_information_source', 
                                           help_text='Defines from which source the conveyed InformationItems are ' +
                                           'initiated.')
    information_target = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_information_target', 
                                           help_text='Defines to which target the conveyed InformationItems are ' +
                                           'directed.')
    realization = models.ForeignKey('Relationship', related_name='%(app_label)s_%(class)s_realization', 
                                    help_text='Determines which Relationship will realize the specified flow.')
    realizing_activity_edge = models.ForeignKey('ActivityEdge', related_name='%(app_label)s_%(class)s_realizing_activity_edge', 
                                                help_text='Determines which ActivityEdges will realize the ' +
                                                'specified flow.')
    realizing_connector = models.ForeignKey('Connector', related_name='%(app_label)s_%(class)s_realizing_connector', 
                                            help_text='Determines which Connectors will realize the specified ' +
                                            'flow.')
    realizing_message = models.ForeignKey('Message', related_name='%(app_label)s_%(class)s_realizing_message', 
                                          help_text='Determines which Messages will realize the specified flow.')


class ExpansionKind(models.Model):
    """
    ExpansionKind is an enumeration type used to specify how an ExpansionRegion executes its contents.
    """

    __package__ = 'UML.Actions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    STREAM = 'stream'
    ITERATIVE = 'iterative'
    PARALLEL = 'parallel'
    CHOICES = (
        (STREAM, 'A stream of input collection elements flows into a single execution of ' +
                 'the content of the ExpansionRegion, in the order of the collection elements if ' +
                 'the input collections are ordered.'),
        (ITERATIVE, 'The content of the ExpansionRegion is executed iteratively for the ' +
                    'elements of the input collections, in the order of the input elements, if the ' +
                    'collections are ordered.'),
        (PARALLEL, 'The content of the ExpansionRegion is executed concurrently for the ' +
                   'elements of the input collections.'),
    )

    expansion_kind = models.CharField(max_length=255, choices=CHOICES, default=PARALLEL)


class ExceptionHandler(models.Model):
    """
    An ExceptionHandler is an Element that specifies a handlerBody ExecutableNode to execute in case the
    specified exception occurs during the execution of the protected ExecutableNode.
    """

    __package__ = 'UML.Activities'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    exception_input = models.ForeignKey('ObjectNode', related_name='%(app_label)s_%(class)s_exception_input', 
                                        help_text='An ObjectNode within the handlerBody. When the ' +
                                        'ExceptionHandler catches an exception, the exception token is placed on ' +
                                        'this ObjectNode, causing the handlerBody to execute.')
    exception_type = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_exception_type', 
                                       help_text='The Classifiers whose instances the ExceptionHandler catches as ' +
                                       'exceptions. If an exception occurs whose type is any exceptionType, the ' +
                                       'ExceptionHandler catches the exception and executes the handlerBody.')
    handler_body = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_handler_body', 
                                     help_text='An ExecutableNode that is executed if the ExceptionHandler ' +
                                     'catches an exception.')
    protected_node = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_protected_node', 
                                       help_text='The ExecutableNode protected by the ExceptionHandler. If an ' +
                                       'exception propagates out of the protectedNode and has a type matching one ' +
                                       'of the exceptionTypes, then it is caught by this ExceptionHandler.')


class Clause(models.Model):
    """
    A Clause is an Element that represents a single branch of a ConditionalNode, including a test and a body
    section. The body section is executed only if (but not necessarily if) the test section evaluates to true.
    """

    __package__ = 'UML.Actions'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    body = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_body', 
                             help_text='The set of ExecutableNodes that are executed if the test evaluates to ' +
                             'true and the Clause is chosen over other Clauses within the ConditionalNode that ' +
                             'also have tests that evaluate to true.')
    body_output = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_body_output', 
                                    help_text='The OutputPins on Actions within the body section whose values are ' +
                                    'moved to the result OutputPins of the containing ConditionalNode after ' +
                                    'execution of the body.')
    decider = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_decider', 
                                help_text='An OutputPin on an Action in the test section whose Boolean value ' +
                                'determines the result of the test.')
    predecessor_clause = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_predecessor_clause', 
                                           help_text='A set of Clauses whose tests must all evaluate to false ' +
                                           'before this Clause can evaluate its test.')
    successor_clause = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_successor_clause', 
                                         help_text='A set of Clauses that may not evaluate their tests unless the ' +
                                         'test for this Clause evaluates to false.')
    test = models.ForeignKey('ExecutableNode', related_name='%(app_label)s_%(class)s_test', 
                             help_text='The set of ExecutableNodes that are executed in order to provide a test ' +
                             'result for the Clause.')


class Reception(models.Model):
    """
    A Reception is a declaration stating that a Classifier is prepared to react to the receipt of a Signal.
    """

    __package__ = 'UML.SimpleClassifiers'

    behavioral_feature = models.OneToOneField('BehavioralFeature', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal')


class TimeInterval(models.Model):
    """
    A TimeInterval defines the range between two TimeExpressions.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval', on_delete=models.CASCADE, primary_key=True)
    has_max = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_has_max', 
                                help_text='Refers to the TimeExpression denoting the maximum value of the range.')
    has_min = models.ForeignKey('TimeExpression', related_name='%(app_label)s_%(class)s_has_min', 
                                help_text='Refers to the TimeExpression denoting the minimum value of the range.')


class CollaborationUse(models.Model):
    """
    A CollaborationUse is used to specify the application of a pattern specified by a Collaboration to a
    specific situation.
    """

    __package__ = 'UML.StructuredClassifiers'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    role_binding = models.ForeignKey('Dependency', related_name='%(app_label)s_%(class)s_role_binding', 
                                     help_text='A mapping between features of the Collaboration and features of ' +
                                     'the owning Classifier. This mapping indicates which ConnectableElement of ' +
                                     'the Classifier plays which role(s) in the Collaboration. A ' +
                                     'ConnectableElement may be bound to multiple roles in the same ' +
                                     'CollaborationUse (that is, it may play multiple roles).')
    has_type = models.ForeignKey('Collaboration', related_name='%(app_label)s_%(class)s_has_type', 
                                 help_text='The Collaboration which is used in this CollaborationUse. The ' +
                                 'Collaboration defines the cooperation between its roles which are mapped to ' +
                                 'ConnectableElements relating to the Classifier owning the CollaborationUse.')


class Signal(models.Model):
    """
    A Signal is a specification of a kind of communication between objects in which a reaction is asynchronously
    triggered in the receiver without a reply.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute')


class CallEvent(models.Model):
    """
    A CallEvent models the receipt by an object of a message invoking a call of an Operation.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation')


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
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', 
                               help_text='The InputPin providing the object to be destroyed.')


class ReadLinkObjectEndAction(models.Model):
    """
    A ReadLinkObjectEndAction is an Action that retrieves an end object from a link object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    end = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_end', 
                            help_text='The Association end to be read.')
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The input pin from which the link object is obtained.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin where the result value is placed.')


class ProtocolConformance(models.Model):
    """
    A ProtocolStateMachine can be redefined into a more specific ProtocolStateMachine or into behavioral
    StateMachine. ProtocolConformance declares that the specific ProtocolStateMachine specifies a protocol that
    conforms to the general ProtocolStateMachine or that the specific behavioral StateMachine abides by the
    protocol of the general ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    general_machine = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_general_machine', 
                                        help_text='Specifies the ProtocolStateMachine to which the specific ' +
                                        'ProtocolStateMachine conforms.')
    specific_machine = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_specific_machine', 
                                         help_text='Specifies the ProtocolStateMachine which conforms to the ' +
                                         'general ProtocolStateMachine.')


class Model(models.Model):
    """
    A model captures a view of a physical system. It is an abstraction of the physical system, with a certain
    purpose. This purpose determines what is to be included in the model and what is irrelevant. Thus the model
    completely describes those aspects of the physical system that are relevant to the purpose of the model, at
    the appropriate level of detail.
    """

    __package__ = 'UML.Packages'

    package = models.OneToOneField('Package', on_delete=models.CASCADE, primary_key=True)
    viewpoint = models.CharField(max_length=255)


class ReadExtentAction(models.Model):
    """
    A ReadExtentAction is an Action that retrieves the current instances of a Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The Classifier whose instances are to be retrieved.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin on which the Classifier instances are placed.')


class Include(models.Model):
    """
    An Include relationship specifies that a UseCase contains the behavior defined in another UseCase.
    """

    __package__ = 'UML.UseCases'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    named_element = models.OneToOneField('NamedElement')
    addition = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_addition', 
                                 help_text='The UseCase that is to be included.')
    including_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_including_case', 
                                       help_text='The UseCase which includes the addition and owns the Include ' +
                                       'relationship.')


class BroadcastSignalAction(models.Model):
    """
    A BroadcastSignalAction is an InvocationAction that transmits a Signal instance to all the potential target
    objects in the system. Values from the argument InputPins are used to provide values for the attributes of
    the Signal. The requestor continues execution immediately after the Signal instances are sent out and cannot
    receive reply values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal')


class CallConcurrencyKind(models.Model):
    """
    CallConcurrencyKind is an Enumeration used to specify the semantics of concurrent calls to a
    BehavioralFeature.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    GUARDED = 'guarded'
    CONCURRENT = 'concurrent'
    SEQUENTIAL = 'sequential'
    CHOICES = (
        (GUARDED, 'Multiple invocations of a BehavioralFeature that overlap in time may ' +
                  'occur to one instance, but only one is allowed to commence. The others are ' +
                  'blocked until the performance of the currently executing BehavioralFeature is ' +
                  'complete. It is the responsibility of the system designer to ensure that ' +
                  'deadlocks do not occur due to simultaneous blocking.'),
        (CONCURRENT, 'Multiple invocations of a BehavioralFeature that overlap in time ' +
                     'may occur to one instance and all of them may proceed concurrently.'),
        (SEQUENTIAL, 'No concurrency management mechanism is associated with the ' +
                     'BehavioralFeature and, therefore, concurrency conflicts may occur. Instances ' +
                     'that invoke a BehavioralFeature need to coordinate so that only one invocation ' +
                     'to a target on any BehavioralFeature occurs at once.'),
    )

    call_concurrency_kind = models.CharField(max_length=255, choices=CHOICES, default=SEQUENTIAL)


class Extend(models.Model):
    """
    A relationship from an extending UseCase to an extended UseCase that specifies how and when the behavior
    defined in the extending UseCase can be inserted into the behavior defined in the extended UseCase.
    """

    __package__ = 'UML.UseCases'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    directed_relationship = models.OneToOneField('DirectedRelationship')
    condition = models.ForeignKey('Constraint', related_name='%(app_label)s_%(class)s_condition', 
                                  help_text='References the condition that must hold when the first ' +
                                  'ExtensionPoint is reached for the extension to take place. If no constraint is ' +
                                  'associated with the Extend relationship, the extension is unconditional.')
    extended_case = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_extended_case', 
                                      help_text='The UseCase that is being extended.')
    extension = models.ForeignKey('UseCase', related_name='%(app_label)s_%(class)s_extension', 
                                  help_text='The UseCase that represents the extension and owns the Extend ' +
                                  'relationship.')
    extension_location = models.ForeignKey('ExtensionPoint', related_name='%(app_label)s_%(class)s_extension_location', 
                                           help_text='An ordered list of ExtensionPoints belonging to the ' +
                                           'extended UseCase, specifying where the respective behavioral fragments ' +
                                           'of the extending UseCase are to be inserted. The first fragment in the ' +
                                           'extending UseCase is associated with the first extension point in the ' +
                                           'list, the second fragment with the second point, and so on. Note that, ' +
                                           'in most practical cases, the extending UseCase has just a single ' +
                                           'behavior fragment, so that the list of ExtensionPoints is trivial.')


class ReclassifyObjectAction(models.Model):
    """
    A ReclassifyObjectAction is an Action that changes the Classifiers that classify an object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    is_replace_all = models.BooleanField(help_text='Specifies whether existing Classifiers should be removed ' +
                                         'before adding the new Classifiers.')
    new_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_new_classifier', 
                                       help_text='A set of Classifiers to be added to the Classifiers of the ' +
                                       'given object.')
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin that holds the object to be reclassified.')
    old_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_old_classifier', 
                                       help_text='A set of Classifiers to be removed from the Classifiers of the ' +
                                       'given object.')


class Image(models.Model):
    """
    Physical definition of a graphical image.
    """

    __package__ = 'UML.Packages'

    element = models.OneToOneField('Element', on_delete=models.CASCADE, primary_key=True)
    content = models.CharField(max_length=255, 
                               help_text='This contains the serialization of the image according to the format. ' +
                               'The value could represent a bitmap, image such as a GIF file, or drawing ' +
                               '"instructions" using a standard such as Scalable Vector Graphic (SVG) (which is ' +
                               'XML based).')
    has_format = models.CharField(max_length=255, 
                                  help_text='This indicates the format of the content, which is how the string ' +
                                  'content should be interpreted. The following values are reserved: SVG, GIF, ' +
                                  'PNG, JPG, WMF, EMF, BMP. In addition the prefix "MIME: " is also reserved. This ' +
                                  'option can be used as an alternative to express the reserved values above, for ' +
                                  'example "SVG" could instead be expressed as "MIME: image/svg+xml".')
    location = models.CharField(max_length=255, 
                                help_text='This contains a location that can be used by a tool to locate the ' +
                                'image as an alternative to embedding it in the stereotype.')


class ValuePin(models.Model):
    """
    A ValuePin is an InputPin that provides a value by evaluating a ValueSpecification.
    """

    __package__ = 'UML.Actions'

    input_pin = models.OneToOneField('InputPin', on_delete=models.CASCADE, primary_key=True)
    value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_value')


class CallBehaviorAction(models.Model):
    """
    A CallBehaviorAction is a CallAction that invokes a Behavior directly. The argument values of the
    CallBehaviorAction are passed on the input Parameters of the invoked Behavior. If the call is synchronous,
    the execution of the CallBehaviorAction waits until the execution of the invoked Behavior completes and the
    values of output Parameters of the Behavior are placed on the result OutputPins. If the call is
    asynchronous, the CallBehaviorAction completes immediately and no results values can be provided.
    """

    __package__ = 'UML.Actions'

    call_action = models.OneToOneField('CallAction', on_delete=models.CASCADE, primary_key=True)
    behavior = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_behavior')

    def output_parameters(self):
        """
        Return the inout, out and return ownedParameters of the Behavior being called.

        .. ocl::
            result = (behavior.outputParameters())
        """
        pass


class ReadIsClassifiedObjectAction(models.Model):
    """
    A ReadIsClassifiedObjectAction is an Action that determines whether an object is classified by a given
    Classifier.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The Classifier against which the classification of the input object ' +
                                   'is tested.')
    is_direct = models.BooleanField(help_text='Indicates whether the input object must be directly classified by ' +
                                    'the given Classifier or whether it may also be an instance of a ' +
                                    'specialization of the given Classifier.')
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin that holds the object whose classification is to be ' +
                                   'tested.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin that holds the Boolean result of the test.')


class ExecutionOccurrenceSpecification(models.Model):
    """
    An ExecutionOccurrenceSpecification represents moments in time at which Actions or Behaviors start or
    finish.
    """

    __package__ = 'UML.Interactions'

    occurrence_specification = models.OneToOneField('OccurrenceSpecification', on_delete=models.CASCADE, primary_key=True)
    execution = models.ForeignKey('ExecutionSpecification', related_name='%(app_label)s_%(class)s_execution')


class ActionExecutionSpecification(models.Model):
    """
    An ActionExecutionSpecification is a kind of ExecutionSpecification representing the execution of an Action.
    """

    __package__ = 'UML.Interactions'

    execution_specification = models.OneToOneField('ExecutionSpecification', on_delete=models.CASCADE, primary_key=True)
    action = models.ForeignKey('Action', related_name='%(app_label)s_%(class)s_action')


class ConnectionPointReference(models.Model):
    """
    A ConnectionPointReference represents a usage (as part of a submachine State) of an entry/exit point
    Pseudostate defined in the StateMachine referenced by the submachine State.
    """

    __package__ = 'UML.StateMachines'

    vertex = models.OneToOneField('Vertex', on_delete=models.CASCADE, primary_key=True)
    entry = models.ForeignKey('Pseudostate', related_name='%(app_label)s_%(class)s_entry', 
                              help_text='The entryPoint Pseudostates corresponding to this connection point.')
    exit = models.ForeignKey('Pseudostate', related_name='%(app_label)s_%(class)s_exit', 
                             help_text='The exitPoints kind Pseudostates corresponding to this connection point.')
    state = models.ForeignKey('State', related_name='%(app_label)s_%(class)s_state', 
                              help_text='The State in which the ConnectionPointReference is defined.')


class ActionInputPin(models.Model):
    """
    An ActionInputPin is a kind of InputPin that executes an Action to determine the values to input to another
    Action.
    """

    __package__ = 'UML.Actions'

    input_pin = models.OneToOneField('InputPin', on_delete=models.CASCADE, primary_key=True)
    from_action = models.ForeignKey('Action', related_name='%(app_label)s_%(class)s_from_action')


class InteractionOperand(models.Model):
    """
    An InteractionOperand is contained in a CombinedFragment. An InteractionOperand represents one operand of
    the expression given by the enclosing CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    interaction_fragment = models.OneToOneField('InteractionFragment', on_delete=models.CASCADE, primary_key=True)
    namespace = models.OneToOneField('Namespace')
    fragment = models.ForeignKey('InteractionFragment', related_name='%(app_label)s_%(class)s_fragment', 
                                 help_text='The fragments of the operand.')
    guard = models.ForeignKey('InteractionConstraint', related_name='%(app_label)s_%(class)s_guard', 
                              help_text='Constraint of the operand.')


class VisibilityKind(models.Model):
    """
    VisibilityKind is an enumeration type that defines literals to determine the visibility of Elements in a
    model.
    """

    __package__ = 'UML.CommonStructure'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    PROTECTED = 'protected'
    PUBLIC = 'public'
    PRIVATE = 'private'
    PACKAGE = 'package'
    CHOICES = (
        (PROTECTED, 'A NamedElement with protected visibility is visible to Elements ' +
                    'that have a generalization relationship to the Namespace that owns it.'),
        (PUBLIC, 'A Named Element with public visibility is visible to all elements that ' +
                 'can access the contents of the Namespace that owns it.'),
        (PRIVATE, 'A NamedElement with private visibility is only visible inside the ' +
                  'Namespace that owns it.'),
        (PACKAGE, 'A NamedElement with package visibility is visible to all Elements ' +
                  'within the nearest enclosing Package (given that other owning Elements have ' +
                  'proper visibility). Outside the nearest enclosing Package, a NamedElement marked ' +
                  'as having package visibility is not visible.  Only NamedElements that are not ' +
                  'owned by Packages can be marked as having package visibility.'),
    )

    visibility_kind = models.CharField(max_length=255, choices=CHOICES, default=PACKAGE)


class LiteralString(models.Model):
    """
    A LiteralString is a specification of a String value.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.CharField(max_length=255)

    def string_value(self):
        """
        The query stringValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass


class RemoveStructuralFeatureValueAction(models.Model):
    """
    A RemoveStructuralFeatureValueAction is a WriteStructuralFeatureAction that removes values from a
    StructuralFeature.
    """

    __package__ = 'UML.Actions'

    write_structural_feature_action = models.OneToOneField('WriteStructuralFeatureAction', on_delete=models.CASCADE, primary_key=True)
    is_remove_duplicates = models.BooleanField(help_text='Specifies whether to remove duplicates of the value in ' +
                                               'nonunique StructuralFeatures.')
    remove_at = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_remove_at', 
                                  help_text='An InputPin that provides the position of an existing value to ' +
                                  'remove in ordered, nonunique structural features. The type of the removeAt ' +
                                  'InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.')


class Connector(models.Model):
    """
    A Connector specifies links that enables communication between two or more instances. In contrast to
    Associations, which specify links between any instance of the associated Classifiers, Connectors specify
    links between instances playing the connected parts only.
    """

    __package__ = 'UML.StructuredClassifiers'

    feature = models.OneToOneField('Feature', on_delete=models.CASCADE, primary_key=True)
    contract = models.ForeignKey('Behavior', related_name='%(app_label)s_%(class)s_contract', 
                                 help_text='The set of Behaviors that specify the valid interaction patterns ' +
                                 'across the Connector.')
    end = models.ForeignKey('ConnectorEnd', related_name='%(app_label)s_%(class)s_end', 
                            help_text='A Connector has at least two ConnectorEnds, each representing the ' +
                            'participation of instances of the Classifiers typing the ConnectableElements attached ' +
                            'to the end. The set of ConnectorEnds is ordered.')
    kind = models.ForeignKey('ConnectorKind', related_name='%(app_label)s_%(class)s_kind', 
                             help_text='Indicates the kind of Connector. This is derived: a Connector with one or ' +
                             'more ends connected to a Port which is not on a Part and which is not a behavior ' +
                             'port is a delegation; otherwise it is an assembly.')
    redefined_connector = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_connector', 
                                            help_text='A Connector may be redefined when its containing ' +
                                            'Classifier is specialized. The redefining Connector may have a type ' +
                                            'that specializes the type of the redefined Connector. The types of ' +
                                            'the ConnectorEnds of the redefining Connector may specialize the ' +
                                            'types of the ConnectorEnds of the redefined Connector. The properties ' +
                                            'of the ConnectorEnds of the redefining Connector may be replaced.')
    has_type = models.ForeignKey('Association', related_name='%(app_label)s_%(class)s_has_type', 
                                 help_text='An optional Association that classifies links corresponding to this ' +
                                 'Connector.')

    def kind_operation(self):
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


class StringExpression(models.Model):
    """
    A StringExpression is an Expression that specifies a String value that is derived by concatenating a
    sequence of operands with String values or a sequence of subExpressions, some of which might be template
    parameters.
    """

    __package__ = 'UML.Values'

    templateable_element = models.OneToOneField('TemplateableElement', on_delete=models.CASCADE, primary_key=True)
    expression = models.OneToOneField('Expression')
    owning_expression = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_owning_expression', 
                                          help_text='The StringExpression of which this StringExpression is a ' +
                                          'subExpression.')
    sub_expression = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_sub_expression', 
                                       help_text='The StringExpressions that constitute this StringExpression.')

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


class ValueSpecificationAction(models.Model):
    """
    A ValueSpecificationAction is an Action that evaluates a ValueSpecification and provides a result.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin on which the result value is placed.')
    value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_value', 
                              help_text='The ValueSpecification to be evaluated.')


class InstanceValue(models.Model):
    """
    An InstanceValue is a ValueSpecification that identifies an instance.
    """

    __package__ = 'UML.Classification'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    instance = models.ForeignKey('InstanceSpecification', related_name='%(app_label)s_%(class)s_instance')


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
    region_as_input = models.ForeignKey('ExpansionRegion', related_name='%(app_label)s_%(class)s_region_as_input', 
                                        help_text='The ExpansionRegion for which the ExpansionNode is an input.')
    region_as_output = models.ForeignKey('ExpansionRegion', related_name='%(app_label)s_%(class)s_region_as_output', 
                                         help_text='The ExpansionRegion for which the ExpansionNode is an ' +
                                         'output.')


class ReadLinkObjectEndQualifierAction(models.Model):
    """
    A ReadLinkObjectEndQualifierAction is an Action that retrieves a qualifier end value from a link object.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    has_object = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_has_object', 
                                   help_text='The InputPin from which the link object is obtained.')
    qualifier = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_qualifier', 
                                  help_text='The qualifier Property to be read.')
    result = models.ForeignKey('OutputPin', related_name='%(app_label)s_%(class)s_result', 
                               help_text='The OutputPin where the result value is placed.')


class OperationTemplateParameter(models.Model):
    """
    An OperationTemplateParameter exposes an Operation as a formal parameter for a template.
    """

    __package__ = 'UML.Classification'

    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)
    parametered_element = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_parametered_element')


class ComponentRealization(models.Model):
    """
    Realization is specialized to (optionally) define the Classifiers that realize the contract offered by a
    Component in terms of its provided and required Interfaces. The Component forms an abstraction from these
    various Classifiers.
    """

    __package__ = 'UML.StructuredClassifiers'

    realization = models.OneToOneField('Realization', on_delete=models.CASCADE, primary_key=True)
    abstraction = models.ForeignKey('Component', related_name='%(app_label)s_%(class)s_abstraction', 
                                    help_text='The Component that owns this ComponentRealization and which is ' +
                                    'implemented by its realizing Classifiers.')
    realizing_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_realizing_classifier', 
                                             help_text='The Classifiers that are involved in the implementation ' +
                                             'of the Component that owns this Realization.')


class LiteralUnlimitedNatural(models.Model):
    """
    A LiteralUnlimitedNatural is a specification of an UnlimitedNatural number.
    """

    __package__ = 'UML.Values'

    literal_specification = models.OneToOneField('LiteralSpecification', on_delete=models.CASCADE, primary_key=True)
    value = models.IntegerField('UnlimitedNatural')

    def unlimited_value(self):
        """
        The query unlimitedValue() gives the value.

        .. ocl::
            result = (value)
        """
        pass


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


class EnumerationLiteral(models.Model):
    """
    An EnumerationLiteral is a user-defined data value for an Enumeration.
    """

    __package__ = 'UML.SimpleClassifiers'

    instance_specification = models.OneToOneField('InstanceSpecification', on_delete=models.CASCADE, primary_key=True)
    classifier = models.ForeignKey('Enumeration', related_name='%(app_label)s_%(class)s_classifier', 
                                   help_text='The classifier of this EnumerationLiteral derived to be equal to ' +
                                   'its Enumeration.')
    enumeration = models.ForeignKey('Enumeration', related_name='%(app_label)s_%(class)s_enumeration', 
                                    help_text='The Enumeration that this EnumerationLiteral is a member of.')

    def classifier_operation(self):
        """
        Derivation of Enumeration::/classifier

        .. ocl::
            result = (enumeration)
        """
        pass


class SignalEvent(models.Model):
    """
    A SignalEvent represents the receipt of an asynchronous Signal instance.
    """

    __package__ = 'UML.CommonBehavior'

    message_event = models.OneToOneField('MessageEvent', on_delete=models.CASCADE, primary_key=True)
    signal = models.ForeignKey('Signal', related_name='%(app_label)s_%(class)s_signal')


class ConnectableElementTemplateParameter(models.Model):
    """
    A ConnectableElementTemplateParameter exposes a ConnectableElement as a formal parameter for a template.
    """

    __package__ = 'UML.StructuredClassifiers'

    template_parameter = models.OneToOneField('TemplateParameter', on_delete=models.CASCADE, primary_key=True)
    parametered_element = models.ForeignKey('ConnectableElement', related_name='%(app_label)s_%(class)s_parametered_element')


class Duration(models.Model):
    """
    A Duration is a ValueSpecification that specifies the temporal distance between two time instants.
    """

    __package__ = 'UML.Values'

    value_specification = models.OneToOneField('ValueSpecification', on_delete=models.CASCADE, primary_key=True)
    expr = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_expr', 
                             help_text='A ValueSpecification that evaluates to the value of the Duration.')
    observation = models.ForeignKey('Observation', related_name='%(app_label)s_%(class)s_observation', 
                                    help_text='Refers to the Observations that are involved in the computation of ' +
                                    'the Duration value')


class OutputPin(models.Model):
    """
    An OutputPin is a Pin that holds output values produced by an Action.
    """

    __package__ = 'UML.Actions'

    pin = models.OneToOneField('Pin', on_delete=models.CASCADE, primary_key=True)


class PackageMerge(models.Model):
    """
    A package merge defines how the contents of one package are extended by the contents of another package.
    """

    __package__ = 'UML.Packages'

    directed_relationship = models.OneToOneField('DirectedRelationship', on_delete=models.CASCADE, primary_key=True)
    merged_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_merged_package', 
                                       help_text='References the Package that is to be merged with the receiving ' +
                                       'package of the PackageMerge.')
    receiving_package = models.ForeignKey('Package', related_name='%(app_label)s_%(class)s_receiving_package', 
                                          help_text='References the Package that is being extended with the ' +
                                          'contents of the merged package of the PackageMerge.')


class PartDecomposition(models.Model):
    """
    A PartDecomposition is a description of the internal Interactions of one Lifeline relative to an
    Interaction.
    """

    __package__ = 'UML.Interactions'

    interaction_use = models.OneToOneField('InteractionUse', on_delete=models.CASCADE, primary_key=True)


class Message(models.Model):
    """
    A Message defines a particular communication between Lifelines of an Interaction.
    """

    __package__ = 'UML.Interactions'

    named_element = models.OneToOneField('NamedElement', on_delete=models.CASCADE, primary_key=True)
    argument = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_argument', 
                                 help_text='The arguments of the Message.')
    connector = models.ForeignKey('Connector', related_name='%(app_label)s_%(class)s_connector', 
                                  help_text='The Connector on which this Message is sent.')
    interaction = models.ForeignKey('Interaction', related_name='%(app_label)s_%(class)s_interaction', 
                                    help_text='The enclosing Interaction owning the Message.')
    message_kind = models.ForeignKey('MessageKind', related_name='%(app_label)s_%(class)s_message_kind', 
                                     help_text='The derived kind of the Message (complete, lost, found, or ' +
                                     'unknown).')
    message_sort = models.ForeignKey('MessageSort', related_name='%(app_label)s_%(class)s_message_sort', 
                                     help_text='The sort of communication reflected by the Message.')
    receive_event = models.ForeignKey('MessageEnd', related_name='%(app_label)s_%(class)s_receive_event', 
                                      help_text='References the Receiving of the Message.')
    send_event = models.ForeignKey('MessageEnd', related_name='%(app_label)s_%(class)s_send_event', 
                                   help_text='References the Sending of the Message.')
    signature = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_signature', 
                                  help_text='The signature of the Message is the specification of its content. It ' +
                                  'refers either an Operation or a Signal.')

    def message_kind_operation(self):
        """
        This query returns the MessageKind value for this Message.

        .. ocl::
            result = (messageKind)
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
    represented = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_represented')


class Parameter(models.Model):
    """
    A Parameter is a specification of an argument used to pass information into or out of an invocation of a
    BehavioralFeature.  Parameters can be treated as ConnectableElements within Collaborations.
    """

    __package__ = 'UML.Classification'

    multiplicity_element = models.OneToOneField('MultiplicityElement', on_delete=models.CASCADE, primary_key=True)
    connectable_element = models.OneToOneField('ConnectableElement')
    default = models.CharField(max_length=255, 
                               help_text='A String that represents a value to be used when no argument is ' +
                               'supplied for the Parameter.')
    default_value = models.ForeignKey('ValueSpecification', related_name='%(app_label)s_%(class)s_default_value', 
                                      help_text='Specifies a ValueSpecification that represents a value to be ' +
                                      'used when no argument is supplied for the Parameter.')
    direction = models.ForeignKey('ParameterDirectionKind', related_name='%(app_label)s_%(class)s_direction', 
                                  help_text='Indicates whether a parameter is being sent into or out of a ' +
                                  'behavioral element.')
    effect = models.ForeignKey('ParameterEffectKind', related_name='%(app_label)s_%(class)s_effect', 
                               help_text='Specifies the effect that executions of the owner of the Parameter have ' +
                               'on objects passed in or out of the parameter.')
    is_exception = models.BooleanField(help_text='Tells whether an output parameter may emit a value to the ' +
                                       'exclusion of the other outputs.')
    is_stream = models.BooleanField(help_text='Tells whether an input parameter may accept values while its ' +
                                    'behavior is executing, or whether an output parameter may post values while ' +
                                    'the behavior is executing.')
    operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_operation', 
                                  help_text='The Operation owning this parameter.')
    parameter_set = models.ForeignKey('ParameterSet', related_name='%(app_label)s_%(class)s_parameter_set', 
                                      help_text='The ParameterSets containing the parameter. See ParameterSet.')

    def default_operation(self):
        """
        Derivation for Parameter::/default

        .. ocl::
            result = (if self.type = String then defaultValue.stringValue() else null endif)
        """
        pass


class TimeObservation(models.Model):
    """
    A TimeObservation is a reference to a time instant during an execution. It points out the NamedElement in
    the model to observe and whether the observation is when this NamedElement is entered or when it is exited.
    """

    __package__ = 'UML.Values'

    observation = models.OneToOneField('Observation', on_delete=models.CASCADE, primary_key=True)
    event = models.ForeignKey('NamedElement', related_name='%(app_label)s_%(class)s_event', 
                              help_text='The TimeObservation is determined by the entering or exiting of the ' +
                              'event Element during execution.')
    first_event = models.BooleanField(help_text='The value of firstEvent is related to the event. If firstEvent ' +
                                      'is true, then the corresponding observation event is the first time instant ' +
                                      'the execution enters the event Element. If firstEvent is false, then the ' +
                                      'corresponding observation event is the time instant the execution exits the ' +
                                      'event Element.')


class ExpansionRegion(models.Model):
    """
    An ExpansionRegion is a StructuredActivityNode that executes its content multiple times corresponding to
    elements of input collection(s).
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode', on_delete=models.CASCADE, primary_key=True)
    input_element = models.ForeignKey('ExpansionNode', related_name='%(app_label)s_%(class)s_input_element', 
                                      help_text='The ExpansionNodes that hold the input collections for the ' +
                                      'ExpansionRegion.')
    mode = models.ForeignKey('ExpansionKind', related_name='%(app_label)s_%(class)s_mode', 
                             help_text='The mode in which the ExpansionRegion executes its contents. If parallel, ' +
                             'executions are concurrent. If iterative, executions are sequential. If stream, a ' +
                             'stream of values flows into a single execution.')
    output_element = models.ForeignKey('ExpansionNode', related_name='%(app_label)s_%(class)s_output_element', 
                                       help_text='The ExpansionNodes that form the output collections of the ' +
                                       'ExpansionRegion.')


class InteractionOperatorKind(models.Model):
    """
    InteractionOperatorKind is an enumeration designating the different kinds of operators of CombinedFragments.
    The InteractionOperand defines the type of operator of a CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    NEG = 'neg'
    CRITICAL = 'critical'
    BREAK = 'break'
    ASSERT = 'assert'
    STRICT = 'strict'
    PAR = 'par'
    SEQ = 'seq'
    CONSIDER = 'consider'
    LOOP = 'loop'
    OPT = 'opt'
    IGNORE = 'ignore'
    ALT = 'alt'
    CHOICES = (
        (NEG, 'The InteractionOperatorKind neg designates that the CombinedFragment ' +
              'represents traces that are defined to be invalid.'),
        (CRITICAL, 'The InteractionOperatorKind critical designates that the ' +
                   'CombinedFragment represents a critical region. A critical region means that the ' +
                   'traces of the region cannot be interleaved by other OccurrenceSpecifications (on ' +
                   'those Lifelines covered by the region). This means that the region is treated ' +
                   'atomically by the enclosing fragment when determining the set of valid traces. ' +
                   'Even though enclosing CombinedFragments may imply that some ' +
                   'OccurrenceSpecifications may interleave into the region, such as with par- ' +
                   'operator, this is prevented by defining a region.'),
        (BREAK, 'The InteractionOperatorKind break designates that the CombinedFragment ' +
                'represents a breaking scenario in the sense that the operand is a scenario that ' +
                'is performed instead of the remainder of the enclosing InteractionFragment. A ' +
                'break operator with a guard is chosen when the guard is true and the rest of the ' +
                'enclosing Interaction Fragment is ignored. When the guard of the break operand ' +
                'is false, the break operand is ignored and the rest of the enclosing ' +
                'InteractionFragment is chosen. The choice between a break operand without a ' +
                'guard and the rest of the enclosing InteractionFragment is done non- ' +
                'deterministically.'),
        (ASSERT, 'The InteractionOperatorKind assert designates that the ' +
                 'CombinedFragment represents an assertion. The sequences of the operand of the ' +
                 'assertion are the only valid continuations. All other continuations result in an ' +
                 'invalid trace.'),
        (STRICT, 'The InteractionOperatorKind strict designates that the ' +
                 'CombinedFragment represents a strict sequencing between the behaviors of the ' +
                 'operands. The semantics of strict sequencing defines a strict ordering of the ' +
                 'operands on the first level within the CombinedFragment with interactionOperator ' +
                 'strict. Therefore OccurrenceSpecifications within contained CombinedFragment ' +
                 'will not directly be compared with other OccurrenceSpecifications of the ' +
                 'enclosing CombinedFragment.'),
        (PAR, 'The InteractionOperatorKind par designates that the CombinedFragment ' +
              'represents a parallel merge between the behaviors of the operands. The ' +
              'OccurrenceSpecifications of the different operands can be interleaved in any way ' +
              'as long as the ordering imposed by each operand as such is preserved.'),
        (SEQ, 'The InteractionOperatorKind seq designates that the CombinedFragment ' +
              'represents a weak sequencing between the behaviors of the operands.'),
        (CONSIDER, 'The InteractionOperatorKind consider designates which messages ' +
                   'should be considered within this combined fragment. This is equivalent to ' +
                   'defining every other message to be ignored.'),
        (LOOP, 'The InteractionOperatorKind loop designates that the CombinedFragment ' +
               'represents a loop. The loop operand will be repeated a number of times.'),
        (OPT, 'The InteractionOperatorKind opt designates that the CombinedFragment ' +
              'represents a choice of behavior where either the (sole) operand happens or ' +
              'nothing happens. An option is semantically equivalent to an alternative ' +
              'CombinedFragment where there is one operand with non-empty content and the ' +
              'second operand is empty.'),
        (IGNORE, 'The InteractionOperatorKind ignore designates that there are some ' +
                 'message types that are not shown within this combined fragment. These message ' +
                 'types can be considered insignificant and are implicitly ignored if they appear ' +
                 'in a corresponding execution. Alternatively, one can understand ignore to mean ' +
                 'that the message types that are ignored can appear anywhere in the traces.'),
        (ALT, 'The InteractionOperatorKind alt designates that the CombinedFragment ' +
              'represents a choice of behavior. At most one of the operands will be chosen. The ' +
              'chosen operand must have an explicit or implicit guard expression that evaluates ' +
              'to true at this point in the interaction. An implicit true guard is implied if ' +
              'the operand has no guard.'),
    )

    interaction_operator_kind = models.CharField(max_length=255, choices=CHOICES, default=ALT)


class TransitionKind(models.Model):
    """
    TransitionKind is an Enumeration type used to differentiate the various kinds of Transitions.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration', on_delete=models.CASCADE, primary_key=True)
    EXTERNAL = 'external'
    INTERNAL = 'internal'
    LOCAL = 'local'
    CHOICES = (
        (EXTERNAL, 'Implies that the Transition, if triggered, will exit the composite ' +
                   '(source) State.'),
        (INTERNAL, 'Implies that the Transition, if triggered, occurs without exiting or ' +
                   'entering the source State (i.e., it does not cause a state change). This means ' +
                   'that the entry or exit condition of the source State will not be invoked. An ' +
                   'internal Transition can be taken even if the SateMachine is in one or more ' +
                   'Regions nested within the associated State.'),
        (LOCAL, 'Implies that the Transition, if triggered, will not exit the composite ' +
                '(source) State, but it will exit and re-enter any state within the composite ' +
                'State that is in the current state configuration.'),
    )

    transition_kind = models.CharField(max_length=255, choices=CHOICES, default=LOCAL)


class SendObjectAction(models.Model):
    """
    A SendObjectAction is an InvocationAction that transmits an input object to the target object, which is
    handled as a request message by the target object. The requestor continues execution immediately after the
    object is sent out and cannot receive reply values.
    """

    __package__ = 'UML.Actions'

    invocation_action = models.OneToOneField('InvocationAction', on_delete=models.CASCADE, primary_key=True)
    request = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_request', 
                                help_text='The request object, which is transmitted to the target object. The ' +
                                'object may be copied in transmission, so identity might not be preserved.')
    target = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_target', 
                               help_text='The target object to which the object is sent.')


class ReplyAction(models.Model):
    """
    A ReplyAction is an Action that accepts a set of reply values and a value containing return information
    produced by a previous AcceptCallAction. The ReplyAction returns the values to the caller of the previous
    call, completing execution of the call.
    """

    __package__ = 'UML.Actions'

    action = models.OneToOneField('Action', on_delete=models.CASCADE, primary_key=True)
    reply_to_call = models.ForeignKey('Trigger', related_name='%(app_label)s_%(class)s_reply_to_call', 
                                      help_text='The Trigger specifying the Operation whose call is being replied ' +
                                      'to.')
    reply_value = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_reply_value', 
                                    help_text='A list of InputPins providing the values for the output (inout, ' +
                                    'out, and return) Parameters of the Operation. These values are returned to ' +
                                    'the caller.')
    return_information = models.ForeignKey('InputPin', related_name='%(app_label)s_%(class)s_return_information', 
                                           help_text='An InputPin that holds the return information value ' +
                                           'produced by an earlier AcceptCallAction.')


class Interface(models.Model):
    """
    Interfaces declare coherent services that are implemented by BehavioredClassifiers that implement the
    Interfaces via InterfaceRealizations.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier = models.OneToOneField('Classifier', on_delete=models.CASCADE, primary_key=True)
    nested_classifier = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_nested_classifier', 
                                          help_text='References all the Classifiers that are defined (nested) ' +
                                          'within the Interface.')
    owned_attribute = models.ForeignKey('Property', related_name='%(app_label)s_%(class)s_owned_attribute', 
                                        help_text='The attributes (i.e., the Properties) owned by the Interface.')
    owned_operation = models.ForeignKey('Operation', related_name='%(app_label)s_%(class)s_owned_operation', 
                                        help_text='The Operations owned by the Interface.')
    owned_reception = models.ForeignKey('Reception', related_name='%(app_label)s_%(class)s_owned_reception', 
                                        help_text='Receptions that objects providing this Interface are willing ' +
                                        'to accept.')
    protocol = models.ForeignKey('ProtocolStateMachine', related_name='%(app_label)s_%(class)s_protocol', 
                                 help_text='References a ProtocolStateMachine specifying the legal sequences of ' +
                                 'the invocation of the BehavioralFeatures described in the Interface.')
    redefined_interface = models.ForeignKey('self', related_name='%(app_label)s_%(class)s_redefined_interface', 
                                            help_text='References all the Interfaces redefined by this ' +
                                            'Interface.')


class Device(models.Model):
    """
    A device is a physical computational resource with processing capability upon which artifacts may be
    deployed for execution. Devices may be complex (i.e., they may consist of other devices).
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node', on_delete=models.CASCADE, primary_key=True)


class GeneralizationSet(models.Model):
    """
    A GeneralizationSet is a PackageableElement whose instances represent sets of Generalization relationships.
    """

    __package__ = 'UML.Classification'

    packageable_element = models.OneToOneField('PackageableElement', on_delete=models.CASCADE, primary_key=True)
    generalization = models.ForeignKey('Generalization', related_name='%(app_label)s_%(class)s_generalization', 
                                       help_text='Designates the instances of Generalization that are members of ' +
                                       'this GeneralizationSet.')
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
    powertype = models.ForeignKey('Classifier', related_name='%(app_label)s_%(class)s_powertype', 
                                  help_text='Designates the Classifier that is defined as the power type for the ' +
                                  'associated GeneralizationSet, if there is one.')
