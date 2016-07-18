from django.db import models


class Element(models.Model):
    """
    An Element is a constituent of a model. As such, it has the capability of owning
    other Elements.
    """

    __package__ = 'UML.CommonStructure'

    owned_comment = models.ForeignKey('Comment', 
                                      )
    owned_element = models.ForeignKey('self', 
                                      )
    owner = models.ForeignKey('self', help_text='The Element that owns this Element.')

    class Meta:
        abstract = True

    def all_owned_elements(self):
        """
        The query allOwnedElements() gives all of the direct and indirect ownedElements
        of an Element.
        """
        # OCL: "result = (ownedElement->union(ownedElement->collect(e | e.allOwnedElements()))->asSet())"
        pass


class TemplateableElement(Element):
    """
    A TemplateableElement is an Element that can optionally be defined as a template
    and bound to other templates.
    """

    __package__ = 'UML.CommonStructure'

    owned_template_signature = models.ForeignKey('TemplateSignature', 
                                                 )
    template_binding = models.ForeignKey('TemplateBinding', 
                                         )

    class Meta:
        abstract = True

    def parameterable_elements(self):
        """
        The query parameterableElements() returns the set of ParameterableElements that
        may be used as the parameteredElements for a TemplateParameter of this
        TemplateableElement. By default, this set includes all the ownedElements.
        Subclasses may override this operation if they choose to restrict the set of
        ParameterableElements.
        """
        # OCL: "result = (self.allOwnedElements()->select(oclIsKindOf(ParameterableElement)).oclAsType(ParameterableElement)->asSet())"
        pass


class NamedElement(Element):
    """
    A NamedElement is an Element in a model that may have a name. The name may be
    given directly and/or via the use of a StringExpression.
    """

    __package__ = 'UML.CommonStructure'

    client_dependency = models.ForeignKey('Dependency', 
                                          )
    name = models.CharField(max_length=255, help_text='The name of the NamedElement.')
    name_expression = models.ForeignKey('StringExpression', 
                                        )
    namespace = models.ForeignKey('Namespace', 
                                  )
    qualified_name = models.CharField(max_length=255, 
                                      )
    visibility = models.ForeignKey('VisibilityKind', 
                                   )

    class Meta:
        abstract = True

    def client_dependency_operation(self):
        # OCL: "result = (Dependency.allInstances()->select(d | d.client->includes(self)))"
        pass


class Namespace(NamedElement):
    """
    A Namespace is an Element in a model that owns and/or imports a set of
    NamedElements that can be identified by name.
    """

    __package__ = 'UML.CommonStructure'

    element_import = models.ForeignKey('ElementImport', 
                                       )
    imported_member = models.ForeignKey('PackageableElement', 
                                        )
    member = models.ForeignKey('NamedElement', 
                               )
    owned_member = models.ForeignKey('NamedElement', 
                                     )
    owned_rule = models.ForeignKey('Constraint', 
                                   )
    package_import = models.ForeignKey('PackageImport', 
                                       )

    class Meta:
        abstract = True

    def get_names_of_member(self):
        """
        The query getNamesOfMember() gives a set of all of the names that a member would
        have in a Namespace, taking importing into account. In general a member can have
        multiple names in a Namespace if it is imported more than once with different
        aliases.
        """
        """
        .. ocl:
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


class RedefinableElement(NamedElement):
    """
    A RedefinableElement is an element that, when defined in the context of a
    Classifier, can be redefined more specifically or differently in the context of
    another Classifier that specializes (directly or indirectly) the context
    Classifier.
    """

    __package__ = 'UML.Classification'

    is_leaf = models.BooleanField()
    redefined_element = models.ForeignKey('self', 
                                          )
    redefinition_context = models.ForeignKey('Classifier', 
                                             )

    class Meta:
        abstract = True

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two RedefinableElements in a
        context in which redefinition is possible, whether redefinition would be
        logically consistent. By default, this is false; this operation must be
        overridden for subclasses of RedefinableElement to define the consistency
        conditions.
        """
        pass


class ParameterableElement(Element):
    """
    A ParameterableElement is an Element that can be exposed as a formal
    TemplateParameter for a template, or specified as an actual parameter in a
    binding of a template.
    """

    __package__ = 'UML.CommonStructure'

    owning_template_parameter = models.ForeignKey('TemplateParameter', 
                                                  )
    template_parameter = models.ForeignKey('TemplateParameter', 
                                           )

    class Meta:
        abstract = True

    def is_template_parameter(self):
        """
        The query isTemplateParameter() determines if this ParameterableElement is
        exposed as a formal TemplateParameter.
        """
        # OCL: "result = (templateParameter->notEmpty())"
        pass


class PackageableElement(ParameterableElement, NamedElement):
    """
    A PackageableElement is a NamedElement that may be owned directly by a Package.
    A PackageableElement is also able to serve as the parameteredElement of a
    TemplateParameter.
    """

    __package__ = 'UML.CommonStructure'


    def __init__(self, *args, **kwargs):
        if 'visibility' not in kwargs:
            kwargs['visibility'] = 'public'
        super(PackageableElement).__init__(*args, **kwargs)

    class Meta:
        abstract = True


class Type(PackageableElement):
    """
    A Type constrains the values represented by a TypedElement.
    """

    __package__ = 'UML.CommonStructure'

    package = models.ForeignKey('Package', 
                                )

    class Meta:
        abstract = True

    def conforms_to(self):
        """
        The query conformsTo() gives true for a Type that conforms to another. By
        default, two Types do not conform to each other. This query is intended to be
        redefined for specific conformance situations.
        """
        # OCL: "result = (false)"
        pass


class Classifier(Namespace, Type, TemplateableElement, RedefinableElement):
    """
    A Classifier represents a classification of instances according to their
    Features.
    """

    __package__ = 'UML.Classification'

    attribute = models.ForeignKey('Property', 
                                  )
    collaboration_use = models.ForeignKey('CollaborationUse', 
                                          )
    feature = models.ForeignKey('Feature', 
                                )
    general = models.ForeignKey('self', 
                                )
    generalization = models.ForeignKey('Generalization', 
                                       )
    inherited_member = models.ForeignKey('NamedElement', 
                                         )
    is_abstract = models.BooleanField()
    is_final_specialization = models.BooleanField()
    owned_use_case = models.ForeignKey('UseCase', 
                                       )
    powertype_extent = models.ForeignKey('GeneralizationSet', 
                                         )
    redefined_classifier = models.ForeignKey('self', 
                                             )
    representation = models.ForeignKey('CollaborationUse', 
                                       )
    substitution = models.ForeignKey('Substitution', 
                                     )
    use_case = models.ForeignKey('UseCase', 
                                 )

    def __init__(self, *args, **kwargs):
        super(Classifier).__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def all_realized_interfaces(self):
        """
        The Interfaces realized by this Classifier and all of its generalizations
        """
        # OCL: "result = (directlyRealizedInterfaces()->union(self.allParents()->collect(directlyRealizedInterfaces()))->asSet())"
        pass


class StructuredClassifier(Classifier):
    """
    StructuredClassifiers may contain an internal structure of connected elements
    each of which plays a role in the overall Behavior modeled by the
    StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    owned_attribute = models.ForeignKey('Property', 
                                        )
    owned_connector = models.ForeignKey('Connector', 
                                        )
    part = models.ForeignKey('Property', 
                             )
    role = models.ForeignKey('ConnectableElement', 
                             )

    class Meta:
        abstract = True

    def part_operation(self):
        """
        Derivation for StructuredClassifier::/part
        """
        # OCL: "result = (ownedAttribute->select(isComposite))"
        pass


class EncapsulatedClassifier(StructuredClassifier):
    """
    An EncapsulatedClassifier may own Ports to specify typed interaction points.
    """

    __package__ = 'UML.StructuredClassifiers'

    owned_port = models.ForeignKey('Port', 
                                   )

    class Meta:
        abstract = True

    def owned_port_operation(self):
        """
        Derivation for EncapsulatedClassifier::/ownedPort : Port
        """
        # OCL: "result = (ownedAttribute->select(oclIsKindOf(Port))->collect(oclAsType(Port))->asOrderedSet())"
        pass


class BehavioredClassifier(Classifier):
    """
    A BehavioredClassifier may have InterfaceRealizations, and owns a set of
    Behaviors one of which may specify the behavior of the BehavioredClassifier
    itself.
    """

    __package__ = 'UML.SimpleClassifiers'

    classifier_behavior = models.ForeignKey('Behavior', 
                                            )
    interface_realization = models.ForeignKey('InterfaceRealization', 
                                              )
    owned_behavior = models.ForeignKey('Behavior', 
                                       )

    class Meta:
        abstract = True


class Class(BehavioredClassifier, EncapsulatedClassifier):
    """
    A Class classifies a set of objects and specifies the features that characterize
    the structure and behavior of those objects.  A Class may have an internal
    structure and Ports.
    """

    __package__ = 'UML.StructuredClassifiers'

    extension = models.ForeignKey('Extension', 
                                  )
    is_active = models.BooleanField()
    nested_classifier = models.ForeignKey('Classifier', 
                                          )
    owned_operation = models.ForeignKey('Operation', 
                                        )
    owned_reception = models.ForeignKey('Reception', 
                                        )

    def __init__(self, *args, **kwargs):
        super(Class).__init__(*args, **kwargs)

    def super_class_operation(self):
        """
        Derivation for Class::/superClass : Class
        """
        # OCL: "result = (self.general()->select(oclIsKindOf(Class))->collect(oclAsType(Class))->asSet())"
        pass


class Stereotype(models.Model):
    """
    A stereotype defines how an existing metaclass may be extended, and enables the
    use of platform or domain specific terminology or notation in place of, or in
    addition to, the ones used for the extended metaclass.
    """

    __package__ = 'UML.Packages'

    class_ = models.OneToOneField('Class')
    icon = models.ForeignKey('Image', 
                             )
    profile = models.ForeignKey('Profile', 
                                )

    def containing_profile(self):
        """
        The query containingProfile returns the closest profile directly or indirectly
        containing this stereotype.
        """
        # OCL: "result = (self.namespace.oclAsType(Package).containingProfile())"
        pass


class ActivityNode(RedefinableElement):
    """
    ActivityNode is an abstract class for points in the flow of an Activity
    connected by ActivityEdges.
    """

    __package__ = 'UML.Activities'

    activity = models.ForeignKey('Activity', 
                                 )
    in_group = models.ForeignKey('ActivityGroup', 
                                 )
    in_interruptible_region = models.ForeignKey('InterruptibleActivityRegion', 
                                                )
    in_partition = models.ForeignKey('ActivityPartition', 
                                     )
    in_structured_node = models.ForeignKey('StructuredActivityNode', 
                                           )
    incoming = models.ForeignKey('ActivityEdge', 
                                 )
    outgoing = models.ForeignKey('ActivityEdge', 
                                 )
    redefined_node = models.ForeignKey('self', 
                                       )

    class Meta:
        abstract = True

    def is_consistent_with(self):
        # OCL: "result = (redefiningElement.oclIsKindOf(ActivityNode))"
        pass


class ExecutableNode(ActivityNode):
    """
    An ExecutableNode is an abstract class for ActivityNodes whose execution may be
    controlled using ControlFlows and to which ExceptionHandlers may be attached.
    """

    __package__ = 'UML.Activities'

    handler = models.ForeignKey('ExceptionHandler', 
                                )

    class Meta:
        abstract = True


class Action(ExecutableNode):
    """
    An Action is the fundamental unit of executable functionality. The execution of
    an Action represents some transformation or processing in the modeled system.
    Actions provide the ExecutableNodes within Activities and may also be used
    within Interactions.
    """

    __package__ = 'UML.Actions'

    context = models.ForeignKey('Classifier', 
                                )
    input_ = models.ForeignKey('InputPin', 
                               )
    is_locally_reentrant = models.BooleanField()
    local_postcondition = models.ForeignKey('Constraint', 
                                            )
    local_precondition = models.ForeignKey('Constraint', 
                                           )
    output = models.ForeignKey('OutputPin', 
                               )

    class Meta:
        abstract = True

    def all_owned_nodes(self):
        """
        Returns all the ActivityNodes directly or indirectly owned by this Action. This
        includes at least all the Pins of the Action.
        """
        # OCL: "result = (input.oclAsType(Pin)->asSet()->union(output->asSet()))"
        pass


class StructuralFeatureAction(Action):
    """
    StructuralFeatureAction is an abstract class for all Actions that operate on
    StructuralFeatures.
    """

    __package__ = 'UML.Actions'

    object_ = models.ForeignKey('InputPin', 
                                )
    structural_feature = models.ForeignKey('StructuralFeature', 
                                           )

    class Meta:
        abstract = True


class ReadStructuralFeatureAction(StructuralFeatureAction):
    """
    A ReadStructuralFeatureAction is a StructuralFeatureAction that retrieves the
    values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )


class Relationship(Element):
    """
    Relationship is an abstract concept that specifies some kind of relationship
    between Elements.
    """

    __package__ = 'UML.CommonStructure'

    related_element = models.ForeignKey('Element', 
                                        )

    class Meta:
        abstract = True


class DirectedRelationship(Relationship):
    """
    A DirectedRelationship represents a relationship between a collection of source
    model Elements and a collection of target model Elements.
    """

    __package__ = 'UML.CommonStructure'

    source = models.ForeignKey('Element', 
                               )
    target = models.ForeignKey('Element', 
                               )

    class Meta:
        abstract = True


class Dependency(DirectedRelationship, PackageableElement):
    """
    A Dependency is a Relationship that signifies that a single model Element or a
    set of model Elements requires other model Elements for their specification or
    implementation. This means that the complete semantics of the client Element(s)
    are either semantically or structurally dependent on the definition of the
    supplier Element(s).
    """

    __package__ = 'UML.CommonStructure'

    client = models.ForeignKey('NamedElement', 
                               )
    supplier = models.ForeignKey('NamedElement', 
                                 )


class Abstraction(models.Model):
    """
    An Abstraction is a Relationship that relates two Elements or sets of Elements
    that represent the same concept at different levels of abstraction or from
    different viewpoints.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency')
    mapping = models.ForeignKey('OpaqueExpression', 
                                )


class Realization(models.Model):
    """
    Realization is a specialized Abstraction relationship between two sets of model
    Elements, one representing a specification (the supplier) and the other
    represents an implementation of the latter (the client). Realization can be used
    to model stepwise refinement, optimizations, transformations, templates, model
    synthesis, framework composition, etc.
    """

    __package__ = 'UML.CommonStructure'

    abstraction = models.OneToOneField('Abstraction')


class ComponentRealization(models.Model):
    """
    Realization is specialized to (optionally) define the Classifiers that realize
    the contract offered by a Component in terms of its provided and required
    Interfaces. The Component forms an abstraction from these various Classifiers.
    """

    __package__ = 'UML.StructuredClassifiers'

    realization = models.OneToOneField('Realization')
    abstraction = models.ForeignKey('Component', 
                                    )
    realizing_classifier = models.ForeignKey('Classifier', 
                                             )


class LinkEndData(Element):
    """
    LinkEndData is an Element that identifies on end of a link to be read or written
    by a LinkAction. As a link (that is not a link object) cannot be passed as a
    runtime value to or from an Action, it is instead identified by its end objects
    and qualifier values, if any. A LinkEndData instance provides these values for a
    single Association end.
    """

    __package__ = 'UML.Actions'

    end = models.ForeignKey('Property', 
                            )
    qualifier = models.ForeignKey('QualifierValue', 
                                  )
    value = models.ForeignKey('InputPin', 
                              )

    def all_pins(self):
        """
        Returns all the InputPins referenced by this LinkEndData. By default this
        includes the value and qualifier InputPins, but subclasses may override the
        operation to add other InputPins.
        """
        # OCL: "result = (value->asBag()->union(qualifier.value))"
        pass


class DataType(Classifier):
    """
    A DataType is a type whose instances are identified only by their value.
    """

    __package__ = 'UML.SimpleClassifiers'

    owned_attribute = models.ForeignKey('Property', 
                                        )
    owned_operation = models.ForeignKey('Operation', 
                                        )


class Enumeration(models.Model):
    """
    An Enumeration is a DataType whose values are enumerated in the model as
    EnumerationLiterals.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType')
    owned_literal = models.ForeignKey('EnumerationLiteral', 
                                      )


class CallConcurrencyKind(models.Model):
    """
    CallConcurrencyKind is an Enumeration used to specify the semantics of
    concurrent calls to a BehavioralFeature.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration')
    SEQUENTIAL = 'sequential'
    GUARDED = 'guarded'
    CONCURRENT = 'concurrent'
    CHOICES = (
        (SEQUENTIAL, 'No concurrency management mechanism is associated with the ' +
                     'BehavioralFeature and, therefore, concurrency conflicts may occur. Instances ' +
                     'that invoke a BehavioralFeature need to coordinate so that only one invocation ' +
                     'to a target on any BehavioralFeature occurs at once.'),
        (GUARDED, 'Multiple invocations of a BehavioralFeature that overlap in time may ' +
                  'occur to one instance, but only one is allowed to commence. The others are ' +
                  'blocked until the performance of the currently executing BehavioralFeature is ' +
                  'complete. It is the responsibility of the system designer to ensure that ' +
                  'deadlocks do not occur due to simultaneous blocking.'),
        (CONCURRENT, 'Multiple invocations of a BehavioralFeature that overlap in time ' +
                     'may occur to one instance and all of them may proceed concurrently.'),
    )

    call_concurrency_kind = models.CharField(max_length=255, choices=CHOICES, default=CONCURRENT)


class TemplateSignature(Element):
    """
    A Template Signature bundles the set of formal TemplateParameters for a
    template.
    """

    __package__ = 'UML.CommonStructure'

    owned_parameter = models.ForeignKey('TemplateParameter', 
                                        )
    parameter = models.ForeignKey('TemplateParameter', 
                                  )
    template = models.ForeignKey('TemplateableElement', 
                                 )


class RedefinableTemplateSignature(RedefinableElement):
    """
    A RedefinableTemplateSignature supports the addition of formal template
    parameters in a specialization of a template classifier.
    """

    __package__ = 'UML.Classification'

    template_signature = models.OneToOneField('TemplateSignature')
    extended_signature = models.ForeignKey('self', 
                                           )
    inherited_parameter = models.ForeignKey('TemplateParameter', 
                                            )

    def __init__(self, *args, **kwargs):
        super(RedefinableTemplateSignature).__init__(*args, **kwargs)

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two
        RedefinableTemplateSignatures in a context in which redefinition is possible,
        whether redefinition would be logically consistent. A redefining template
        signature is always consistent with a redefined template signature, as
        redefinition only adds new formal parameters.
        """
        pass


class TypedElement(NamedElement):
    """
    A TypedElement is a NamedElement that may have a Type specified for it.
    """

    __package__ = 'UML.CommonStructure'

    type_ = models.ForeignKey('Type', help_text='The type of the TypedElement.')

    class Meta:
        abstract = True


class ValueSpecification(TypedElement, PackageableElement):
    """
    A ValueSpecification is the specification of a (possibly empty) set of values. A
    ValueSpecification is a ParameterableElement that may be exposed as a formal
    TemplateParameter and provided as the actual parameter in the binding of a
    template.
    """

    __package__ = 'UML.Values'


    class Meta:
        abstract = True

    def is_computable(self):
        """
        The query isComputable() determines whether a value specification can be
        computed in a model. This operation cannot be fully defined in OCL. A conforming
        implementation is expected to deliver true for this operation for all
        ValueSpecifications that it can compute, and to compute all of those for which
        the operation is true. A conforming implementation is expected to be able to
        compute at least the value of all LiteralSpecifications.
        """
        # OCL: "result = (false)"
        pass


class LiteralSpecification(ValueSpecification):
    """
    A LiteralSpecification identifies a literal constant being modeled.
    """

    __package__ = 'UML.Values'


    class Meta:
        abstract = True


class LiteralBoolean(LiteralSpecification):
    """
    A LiteralBoolean is a specification of a Boolean value.
    """

    __package__ = 'UML.Values'

    value = models.BooleanField(help_text='The specified Boolean value.')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL: "result = (true)"
        pass


class VisibilityKind(models.Model):
    """
    VisibilityKind is an enumeration type that defines literals to determine the
    visibility of Elements in a model.
    """

    __package__ = 'UML.CommonStructure'

    enumeration = models.OneToOneField('Enumeration')
    PUBLIC = 'public'
    PRIVATE = 'private'
    PACKAGE = 'package'
    PROTECTED = 'protected'
    CHOICES = (
        (PUBLIC, 'A Named Element with public visibility is visible to all elements that ' +
                 'can access the contents of the Namespace that owns it.'),
        (PRIVATE, 'A NamedElement with private visibility is only visible inside the ' +
                  'Namespace that owns it.'),
        (PACKAGE, 'A NamedElement with package visibility is visible to all Elements ' +
                  'within the nearest enclosing Package (given that other owning Elements have ' +
                  'proper visibility). Outside the nearest enclosing Package, a NamedElement marked ' +
                  'as having package visibility is not visible.  Only NamedElements that are not ' +
                  'owned by Packages can be marked as having package visibility.'),
        (PROTECTED, 'A NamedElement with protected visibility is visible to Elements ' +
                    'that have a generalization relationship to the Namespace that owns it.'),
    )

    visibility_kind = models.CharField(max_length=255, choices=CHOICES, default=PROTECTED)


class Observation(PackageableElement):
    """
    Observation specifies a value determined by observing an event or events that
    occur relative to other model Elements.
    """

    __package__ = 'UML.Values'


    class Meta:
        abstract = True


class ActivityGroup(NamedElement):
    """
    ActivityGroup is an abstract class for defining sets of ActivityNodes and
    ActivityEdges in an Activity.
    """

    __package__ = 'UML.Activities'

    contained_edge = models.ForeignKey('ActivityEdge', 
                                       )
    contained_node = models.ForeignKey('ActivityNode', 
                                       )
    in_activity = models.ForeignKey('Activity', 
                                    )
    subgroup = models.ForeignKey('self', 
                                 )
    super_group = models.ForeignKey('self', 
                                    )

    class Meta:
        abstract = True

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityGroup.
        """
        """
        .. ocl:
            result = (if superGroup<>null then superGroup.containingActivity()
            else inActivity
            endif)
        """
        pass


class StructuredActivityNode(Namespace, ActivityGroup, Action):
    """
    A StructuredActivityNode is an Action that is also an ActivityGroup and whose
    behavior is specified by the ActivityNodes and ActivityEdges it so contains.
    Unlike other kinds of ActivityGroup, a StructuredActivityNode owns the
    ActivityNodes and ActivityEdges it contains, and so a node or edge can only be
    directly contained in one StructuredActivityNode, though StructuredActivityNodes
    may be nested.
    """

    __package__ = 'UML.Actions'

    edge = models.ForeignKey('ActivityEdge', 
                             )
    must_isolate = models.BooleanField()
    node = models.ForeignKey('ActivityNode', 
                             )
    structured_node_input = models.ForeignKey('InputPin', 
                                              )
    structured_node_output = models.ForeignKey('OutputPin', 
                                               )
    variable = models.ForeignKey('Variable', 
                                 )

    def __init__(self, *args, **kwargs):
        super(StructuredActivityNode).__init__(*args, **kwargs)

    def all_owned_nodes(self):
        """
        Returns all the ActivityNodes contained directly or indirectly within this
        StructuredActivityNode, in addition to the Pins of the StructuredActivityNode.
        """
        # OCL: "result = (self.Action::allOwnedNodes()->union(node)->union(node->select(oclIsKindOf(Action)).oclAsType(Action).allOwnedNodes())->asSet())"
        pass


class LoopNode(models.Model):
    """
    A LoopNode is a StructuredActivityNode that represents an iterative loop with
    setup, test, and body sections.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode')
    body_output = models.ForeignKey('OutputPin', 
                                    )
    body_part = models.ForeignKey('ExecutableNode', 
                                  )
    decider = models.ForeignKey('OutputPin', 
                                )
    is_tested_first = models.BooleanField()
    loop_variable = models.ForeignKey('OutputPin', 
                                      )
    setup_part = models.ForeignKey('ExecutableNode', 
                                   )
    test = models.ForeignKey('ExecutableNode', 
                             )

    def __init__(self, *args, **kwargs):
        super(LoopNode).__init__(*args, **kwargs)

    def all_actions(self):
        """
        Return only this LoopNode. This prevents Actions within the LoopNode from having
        their OutputPins used as bodyOutputs or decider Pins in containing LoopNodes or
        ConditionalNodes.
        """
        # OCL: "result = (self->asSet())"
        pass


class ConnectorKind(models.Model):
    """
    ConnectorKind is an enumeration that defines whether a Connector is an assembly
    or a delegation.
    """

    __package__ = 'UML.StructuredClassifiers'

    enumeration = models.OneToOneField('Enumeration')
    DELEGATION = 'delegation'
    ASSEMBLY = 'assembly'
    CHOICES = (
        (DELEGATION, 'Indicates that the Connector is a delegation Connector.'),
        (ASSEMBLY, 'Indicates that the Connector is an assembly Connector.'),
    )

    connector_kind = models.CharField(max_length=255, choices=CHOICES, default=ASSEMBLY)


class LinkEndCreationData(models.Model):
    """
    LinkEndCreationData is LinkEndData used to provide values for one end of a link
    to be created by a CreateLinkAction.
    """

    __package__ = 'UML.Actions'

    link_end_data = models.OneToOneField('LinkEndData')
    insert_at = models.ForeignKey('InputPin', 
                                  )
    is_replace_all = models.BooleanField()

    def all_pins(self):
        """
        Adds the insertAt InputPin (if any) to the set of all Pins.
        """
        # OCL: "result = (self.LinkEndData::allPins()->including(insertAt))"
        pass


class MessageKind(models.Model):
    """
    This is an enumerated type that identifies the type of Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration')
    COMPLETE = 'complete'
    FOUND = 'found'
    UNKNOWN = 'unknown'
    LOST = 'lost'
    CHOICES = (
        (COMPLETE, 'sendEvent and receiveEvent are present'),
        (FOUND, 'sendEvent absent and receiveEvent present'),
        (UNKNOWN, 'sendEvent and receiveEvent absent (should not appear)'),
        (LOST, 'sendEvent present and receiveEvent absent'),
    )

    message_kind = models.CharField(max_length=255, choices=CHOICES, default=LOST)


class Transition(Namespace, RedefinableElement):
    """
    A Transition represents an arc between exactly one source Vertex and exactly one
    Target vertex (the source and targets may be the same Vertex). It may form part
    of a compound transition, which takes the StateMachine from one steady State
    configuration to another, representing the full response of the StateMachine to
    an occurrence of an Event that triggered it.
    """

    __package__ = 'UML.StateMachines'

    container = models.ForeignKey('Region', 
                                  )
    effect = models.ForeignKey('Behavior', 
                               )
    guard = models.ForeignKey('Constraint', 
                              )
    kind = models.ForeignKey('TransitionKind', 
                             )
    redefined_transition = models.ForeignKey('self', 
                                             )
    source = models.ForeignKey('Vertex', 
                               )
    target = models.ForeignKey('Vertex', 
                               )
    trigger = models.ForeignKey('Trigger', 
                                )

    def __init__(self, *args, **kwargs):
        super(Transition).__init__(*args, **kwargs)

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the
        Transition either directly or transitively.
        """
        # OCL: "result = (container.containingStateMachine())"
        pass


class InstanceValue(ValueSpecification):
    """
    An InstanceValue is a ValueSpecification that identifies an instance.
    """

    __package__ = 'UML.Classification'

    instance = models.ForeignKey('InstanceSpecification', 
                                 )


class TemplateParameterSubstitution(Element):
    """
    A TemplateParameterSubstitution relates the actual parameter to a formal
    TemplateParameter as part of a template binding.
    """

    __package__ = 'UML.CommonStructure'

    actual = models.ForeignKey('ParameterableElement', 
                               )
    formal = models.ForeignKey('TemplateParameter', 
                               )
    owned_actual = models.ForeignKey('ParameterableElement', 
                                     )
    template_binding = models.ForeignKey('TemplateBinding', 
                                         )


class AcceptEventAction(Action):
    """
    An AcceptEventAction is an Action that waits for the occurrence of one or more
    specific Events.
    """

    __package__ = 'UML.Actions'

    is_unmarshall = models.BooleanField()
    result = models.ForeignKey('OutputPin', 
                               )
    trigger = models.ForeignKey('Trigger', 
                                )


class ReclassifyObjectAction(Action):
    """
    A ReclassifyObjectAction is an Action that changes the Classifiers that classify
    an object.
    """

    __package__ = 'UML.Actions'

    is_replace_all = models.BooleanField()
    new_classifier = models.ForeignKey('Classifier', 
                                       )
    object_ = models.ForeignKey('InputPin', 
                                )
    old_classifier = models.ForeignKey('Classifier', 
                                       )


class DeploymentTarget(NamedElement):
    """
    A deployment target is the location for a deployed artifact.
    """

    __package__ = 'UML.Deployments'

    deployed_element = models.ForeignKey('PackageableElement', 
                                         )
    deployment = models.ForeignKey('Deployment', 
                                   )

    class Meta:
        abstract = True

    def deployed_element_operation(self):
        """
        Derivation for DeploymentTarget::/deployedElement
        """
        # OCL: "result = (deployment.deployedArtifact->select(oclIsKindOf(Artifact))->collect(oclAsType(Artifact).manifestation)->collect(utilizedElement)->asSet())"
        pass


class Node(DeploymentTarget):
    """
    A Node is computational resource upon which artifacts may be deployed for
    execution. Nodes can be interconnected through communication paths to define
    network structures.
    """

    __package__ = 'UML.Deployments'

    class_ = models.OneToOneField('Class')
    nested_node = models.ForeignKey('self', 
                                    )


class ExecutionEnvironment(models.Model):
    """
    An execution environment is a node that offers an execution environment for
    specific types of components that are deployed on it in the form of executable
    artifacts.
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node')


class DurationObservation(Observation):
    """
    A DurationObservation is a reference to a duration during an execution. It
    points out the NamedElement(s) in the model to observe and whether the
    observations are when this NamedElement is entered or when it is exited.
    """

    __package__ = 'UML.Values'

    event = models.ForeignKey('NamedElement', 
                              )
    first_event = models.BooleanField()


class VariableAction(Action):
    """
    VariableAction is an abstract class for Actions that operate on a specified
    Variable.
    """

    __package__ = 'UML.Actions'

    variable = models.ForeignKey('Variable', help_text='The Variable to be read or written.')

    class Meta:
        abstract = True


class ReadVariableAction(VariableAction):
    """
    A ReadVariableAction is a VariableAction that retrieves the values of a
    Variable.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )


class Lifeline(NamedElement):
    """
    A Lifeline represents an individual participant in the Interaction. While parts
    and structural features may have multiplicity greater than 1, Lifelines
    represent only one interacting entity.
    """

    __package__ = 'UML.Interactions'

    covered_by = models.ForeignKey('InteractionFragment', 
                                   )
    decomposed_as = models.ForeignKey('PartDecomposition', 
                                      )
    interaction = models.ForeignKey('Interaction', 
                                    )
    represents = models.ForeignKey('ConnectableElement', 
                                   )
    selector = models.ForeignKey('ValueSpecification', 
                                 )


class DeployedArtifact(NamedElement):
    """
    A deployed artifact is an artifact or artifact instance that has been deployed
    to a deployment target.
    """

    __package__ = 'UML.Deployments'


    class Meta:
        abstract = True


class Artifact(Classifier, DeployedArtifact):
    """
    An artifact is the specification of a physical piece of information that is used
    or produced by a software development process, or by deployment and operation of
    a system. Examples of artifacts include model files, source files, scripts, and
    binary executable files, a table in a database system, a development
    deliverable, or a word-processing document, a mail message. An artifact is the
    source of a deployment to a node.
    """

    __package__ = 'UML.Deployments'

    file_name = models.CharField(max_length=255, 
                                 )
    manifestation = models.ForeignKey('Manifestation', 
                                      )
    nested_artifact = models.ForeignKey('self', 
                                        )
    owned_attribute = models.ForeignKey('Property', 
                                        )
    owned_operation = models.ForeignKey('Operation', 
                                        )


class ControlNode(ActivityNode):
    """
    A ControlNode is an abstract ActivityNode that coordinates flows in an Activity.
    """

    __package__ = 'UML.Activities'


    class Meta:
        abstract = True


class MergeNode(ControlNode):
    """
    A merge node is a control node that brings together multiple alternate flows. It
    is not used to synchronize concurrent flows but to accept one among several
    alternate flows.
    """

    __package__ = 'UML.Activities'



class ActivityEdge(RedefinableElement):
    """
    An ActivityEdge is an abstract class for directed connections between two
    ActivityNodes.
    """

    __package__ = 'UML.Activities'

    activity = models.ForeignKey('Activity', 
                                 )
    guard = models.ForeignKey('ValueSpecification', 
                              )
    in_group = models.ForeignKey('ActivityGroup', 
                                 )
    in_partition = models.ForeignKey('ActivityPartition', 
                                     )
    in_structured_node = models.ForeignKey('StructuredActivityNode', 
                                           )
    interrupts = models.ForeignKey('InterruptibleActivityRegion', 
                                   )
    redefined_edge = models.ForeignKey('self', 
                                       )
    source = models.ForeignKey('ActivityNode', 
                               )
    target = models.ForeignKey('ActivityNode', 
                               )
    weight = models.ForeignKey('ValueSpecification', 
                               )

    class Meta:
        abstract = True

    def is_consistent_with(self):
        # OCL: "result = (redefiningElement.oclIsKindOf(ActivityEdge))"
        pass


class ObjectFlow(ActivityEdge):
    """
    An ObjectFlow is an ActivityEdge that is traversed by object tokens that may
    hold values. Object flows also support multicast/receive, token selection from
    object nodes, and transformation of tokens.
    """

    __package__ = 'UML.Activities'

    is_multicast = models.BooleanField()
    is_multireceive = models.BooleanField()
    selection = models.ForeignKey('Behavior', 
                                  )
    transformation = models.ForeignKey('Behavior', 
                                       )


class InteractionFragment(NamedElement):
    """
    InteractionFragment is an abstract notion of the most general interaction unit.
    An InteractionFragment is a piece of an Interaction. Each InteractionFragment is
    conceptually like an Interaction by itself.
    """

    __package__ = 'UML.Interactions'

    covered = models.ForeignKey('Lifeline', 
                                )
    enclosing_interaction = models.ForeignKey('Interaction', 
                                              )
    enclosing_operand = models.ForeignKey('InteractionOperand', 
                                          )
    general_ordering = models.ForeignKey('GeneralOrdering', 
                                         )

    class Meta:
        abstract = True


class OccurrenceSpecification(InteractionFragment):
    """
    An OccurrenceSpecification is the basic semantic unit of Interactions. The
    sequences of occurrences specified by them are the meanings of Interactions.
    """

    __package__ = 'UML.Interactions'

    to_after = models.ForeignKey('GeneralOrdering', 
                                 )
    to_before = models.ForeignKey('GeneralOrdering', 
                                  )

    def __init__(self, *args, **kwargs):
        super(OccurrenceSpecification).__init__(*args, **kwargs)


class ExecutionOccurrenceSpecification(models.Model):
    """
    An ExecutionOccurrenceSpecification represents moments in time at which Actions
    or Behaviors start or finish.
    """

    __package__ = 'UML.Interactions'

    occurrence_specification = models.OneToOneField('OccurrenceSpecification')
    execution = models.ForeignKey('ExecutionSpecification', 
                                  )


class ExecutionSpecification(InteractionFragment):
    """
    An ExecutionSpecification is a specification of the execution of a unit of
    Behavior or Action within the Lifeline. The duration of an
    ExecutionSpecification is represented by two OccurrenceSpecifications, the start
    OccurrenceSpecification and the finish OccurrenceSpecification.
    """

    __package__ = 'UML.Interactions'

    finish = models.ForeignKey('OccurrenceSpecification', 
                               )
    start = models.ForeignKey('OccurrenceSpecification', 
                              )

    class Meta:
        abstract = True


class ActionExecutionSpecification(ExecutionSpecification):
    """
    An ActionExecutionSpecification is a kind of ExecutionSpecification representing
    the execution of an Action.
    """

    __package__ = 'UML.Interactions'

    action = models.ForeignKey('Action', help_text='Action whose execution is occurring.')


class Constraint(PackageableElement):
    """
    A Constraint is a condition or restriction expressed in natural language text or
    in a machine readable language for the purpose of declaring some of the
    semantics of an Element or set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    constrained_element = models.ForeignKey('Element', 
                                            )
    context = models.ForeignKey('Namespace', 
                                )
    specification = models.ForeignKey('ValueSpecification', 
                                      )


class Feature(RedefinableElement):
    """
    A Feature declares a behavioral or structural characteristic of Classifiers.
    """

    __package__ = 'UML.Classification'

    featuring_classifier = models.ForeignKey('Classifier', 
                                             )
    is_static = models.BooleanField()

    class Meta:
        abstract = True


class BehavioralFeature(Feature, Namespace):
    """
    A BehavioralFeature is a feature of a Classifier that specifies an aspect of the
    behavior of its instances.  A BehavioralFeature is implemented (realized) by a
    Behavior. A BehavioralFeature specifies that a Classifier will respond to a
    designated request by invoking its implementing method.
    """

    __package__ = 'UML.Classification'

    concurrency = models.ForeignKey('CallConcurrencyKind', 
                                    )
    is_abstract = models.BooleanField()
    method = models.ForeignKey('Behavior', 
                               )
    owned_parameter = models.ForeignKey('Parameter', 
                                        )
    owned_parameter_set = models.ForeignKey('ParameterSet', 
                                            )
    raised_exception = models.ForeignKey('Type', 
                                         )

    class Meta:
        abstract = True

    def input_parameters(self):
        """
        The ownedParameters with direction in and inout.
        """
        # OCL: "result = (ownedParameter->select(direction=ParameterDirectionKind::_'in' or direction=ParameterDirectionKind::inout))"
        pass


class Message(NamedElement):
    """
    A Message defines a particular communication between Lifelines of an
    Interaction.
    """

    __package__ = 'UML.Interactions'

    argument = models.ForeignKey('ValueSpecification', help_text='The arguments of the Message.')
    connector = models.ForeignKey('Connector', 
                                  )
    interaction = models.ForeignKey('Interaction', 
                                    )
    message_kind = models.ForeignKey('MessageKind', 
                                     )
    message_sort = models.ForeignKey('MessageSort', 
                                     )
    receive_event = models.ForeignKey('MessageEnd', 
                                      )
    send_event = models.ForeignKey('MessageEnd', 
                                   )
    signature = models.ForeignKey('NamedElement', 
                                  )

    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() specifies that any two Messages may coexist in
        the same Namespace, regardless of their names.
        """
        # OCL: "result = (true)"
        pass


class InteractionUse(InteractionFragment):
    """
    An InteractionUse refers to an Interaction. The InteractionUse is a shorthand
    for copying the contents of the referenced Interaction where the InteractionUse
    is. To be accurate the copying must take into account substituting parameters
    with arguments and connect the formal Gates with the actual ones.
    """

    __package__ = 'UML.Interactions'

    actual_gate = models.ForeignKey('Gate', 
                                    )
    argument = models.ForeignKey('ValueSpecification', 
                                 )
    refers_to = models.ForeignKey('Interaction', 
                                  )
    return_value = models.ForeignKey('ValueSpecification', 
                                     )
    return_value_recipient = models.ForeignKey('Property', 
                                               )


class PartDecomposition(models.Model):
    """
    A PartDecomposition is a description of the internal Interactions of one
    Lifeline relative to an Interaction.
    """

    __package__ = 'UML.Interactions'

    interaction_use = models.OneToOneField('InteractionUse')


class Package(PackageableElement, TemplateableElement, Namespace):
    """
    A package can have one or more profile applications to indicate which profiles
    have been applied. Because a profile is a package, it is possible to apply a
    profile not only to packages, but also to profiles. Package specializes
    TemplateableElement and PackageableElement specializes ParameterableElement to
    specify that a package can be used as a template and a PackageableElement as a
    template parameter. A package is used to group elements, and provides a
    namespace for the grouped elements.
    """

    __package__ = 'UML.Packages'

    uri = models.CharField(max_length=255, 
                           )
    nested_package = models.ForeignKey('self', 
                                       )
    nesting_package = models.ForeignKey('self', 
                                        )
    owned_stereotype = models.ForeignKey('Stereotype', 
                                         )
    owned_type = models.ForeignKey('Type', 
                                   )
    package_merge = models.ForeignKey('PackageMerge', 
                                      )
    packaged_element = models.ForeignKey('PackageableElement', 
                                         )
    profile_application = models.ForeignKey('ProfileApplication', 
                                            )

    def all_applicable_stereotypes(self):
        """
        The query allApplicableStereotypes() returns all the directly or indirectly
        owned stereotypes, including stereotypes contained in sub-profiles.
        """
        """
        .. ocl:
            result = (let ownedPackages : Bag(Package) = ownedMember->select(oclIsKindOf(Package))->collect(oclAsType(Package)) in
             ownedStereotype->union(ownedPackages.allApplicableStereotypes())->flatten()->asSet()
            )
        """
        pass


class ObjectNodeOrderingKind(models.Model):
    """
    ObjectNodeOrderingKind is an enumeration indicating queuing order for offering
    the tokens held by an ObjectNode.
    """

    __package__ = 'UML.Activities'

    enumeration = models.OneToOneField('Enumeration')
    LIFO = 'lifo'
    ORDERED = 'ordered'
    FIFO = 'fifo'
    UNORDERED = 'unordered'
    CHOICES = (
        (LIFO, 'Indicates that tokens are queued in a last in, first out manner.'),
        (ORDERED, 'Indicates that tokens are ordered.'),
        (FIFO, 'Indicates that tokens are queued in a first in, first out manner.'),
        (UNORDERED, 'Indicates that tokens are unordered.'),
    )

    object_node_ordering_kind = models.CharField(max_length=255, choices=CHOICES, default=UNORDERED)


class Deployment(models.Model):
    """
    A deployment is the allocation of an artifact or artifact instance to a
    deployment target. A component deployment is the deployment of one or more
    artifacts or artifact instances to a deployment target, optionally parameterized
    by a deployment specification. Examples are executables and configuration files.
    """

    __package__ = 'UML.Deployments'

    dependency = models.OneToOneField('Dependency')
    configuration = models.ForeignKey('DeploymentSpecification', 
                                      )
    deployed_artifact = models.ForeignKey('DeployedArtifact', 
                                          )
    location = models.ForeignKey('DeploymentTarget', 
                                 )


class Behavior(models.Model):
    """
    Behavior is a specification of how its context BehavioredClassifier changes
    state over time. This specification may be either a definition of possible
    behavior execution or emergent behavior, or a selective illustration of an
    interesting subset of possible executions. The latter form is typically used for
    capturing examples, such as a trace of a particular execution.
    """

    __package__ = 'UML.CommonBehavior'

    class_ = models.OneToOneField('Class')
    context = models.ForeignKey('BehavioredClassifier', 
                                )
    is_reentrant = models.BooleanField()
    owned_parameter = models.ForeignKey('Parameter', 
                                        )
    owned_parameter_set = models.ForeignKey('ParameterSet', 
                                            )
    postcondition = models.ForeignKey('Constraint', 
                                      )
    precondition = models.ForeignKey('Constraint', 
                                     )
    redefined_behavior = models.ForeignKey('self', 
                                           )
    specification = models.ForeignKey('BehavioralFeature', 
                                      )

    class Meta:
        abstract = True

    def input_parameters(self):
        """
        The in and inout ownedParameters of the Behavior.
        """
        # OCL: "result = (ownedParameter->select(direction=ParameterDirectionKind::_'in' or direction=ParameterDirectionKind::inout))"
        pass


class OpaqueBehavior(Behavior):
    """
    An OpaqueBehavior is a Behavior whose specification is given in a textual
    language other than UML.
    """

    __package__ = 'UML.CommonBehavior'

    body = models.CharField(max_length=255, 
                            )
    language = models.CharField(max_length=255, 
                                )


class FunctionBehavior(models.Model):
    """
    A FunctionBehavior is an OpaqueBehavior that does not access or modify any
    objects or other external data.
    """

    __package__ = 'UML.CommonBehavior'

    opaque_behavior = models.OneToOneField('OpaqueBehavior')

    def has_all_data_type_attributes(self):
        """
        The hasAllDataTypeAttributes query tests whether the types of the attributes of
        the given DataType are all DataTypes, and similarly for all those DataTypes.
        """
        """
        .. ocl:
            result = (d.ownedAttribute->forAll(a |
                a.type.oclIsKindOf(DataType) and
                  hasAllDataTypeAttributes(a.type.oclAsType(DataType))))
        """
        pass


class Vertex(NamedElement):
    """
    A Vertex is an abstraction of a node in a StateMachine graph. It can be the
    source or destination of any number of Transitions.
    """

    __package__ = 'UML.StateMachines'

    container = models.ForeignKey('Region', 
                                  )
    incoming = models.ForeignKey('Transition', 
                                 )
    outgoing = models.ForeignKey('Transition', 
                                 )

    class Meta:
        abstract = True

    def containing_state_machine(self):
        """
        The operation containingStateMachine() returns the StateMachine in which this
        Vertex is defined.
        """
        """
        .. ocl:
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


class Pseudostate(Vertex):
    """
    A Pseudostate is an abstraction that encompasses different types of transient
    Vertices in the StateMachine graph. A StateMachine instance never comes to rest
    in a Pseudostate, instead, it will exit and enter the Pseudostate within a
    single run-to-completion step.
    """

    __package__ = 'UML.StateMachines'

    kind = models.ForeignKey('PseudostateKind', 
                             )
    state = models.ForeignKey('State', 
                              )
    state_machine = models.ForeignKey('StateMachine', 
                                      )


class UnmarshallAction(Action):
    """
    An UnmarshallAction is an Action that retrieves the values of the
    StructuralFeatures of an object and places them on OutputPins.
    """

    __package__ = 'UML.Actions'

    object_ = models.ForeignKey('InputPin', 
                                )
    result = models.ForeignKey('OutputPin', 
                               )
    unmarshall_type = models.ForeignKey('Classifier', 
                                        )


class ExpansionRegion(models.Model):
    """
    An ExpansionRegion is a StructuredActivityNode that executes its content
    multiple times corresponding to elements of input collection(s).
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode')
    input_element = models.ForeignKey('ExpansionNode', 
                                      )
    mode = models.ForeignKey('ExpansionKind', 
                             )
    output_element = models.ForeignKey('ExpansionNode', 
                                       )


class LinkAction(Action):
    """
    LinkAction is an abstract class for all Actions that identify the links to be
    acted on using LinkEndData.
    """

    __package__ = 'UML.Actions'

    end_data = models.ForeignKey('LinkEndData', 
                                 )
    input_value = models.ForeignKey('InputPin', 
                                    )

    class Meta:
        abstract = True

    def association(self):
        """
        Returns the Association acted on by this LinkAction.
        """
        # OCL: "result = (endData->asSequence()->first().end.association)"
        pass


class WriteLinkAction(LinkAction):
    """
    WriteLinkAction is an abstract class for LinkActions that create and destroy
    links.
    """

    __package__ = 'UML.Actions'


    class Meta:
        abstract = True


class CreateLinkAction(WriteLinkAction):
    """
    A CreateLinkAction is a WriteLinkAction for creating links.
    """

    __package__ = 'UML.Actions'


    def __init__(self, *args, **kwargs):
        super(CreateLinkAction).__init__(*args, **kwargs)


class CreateLinkObjectAction(models.Model):
    """
    A CreateLinkObjectAction is a CreateLinkAction for creating link objects
    (AssociationClasse instances).
    """

    __package__ = 'UML.Actions'

    create_link_action = models.OneToOneField('CreateLinkAction')
    result = models.ForeignKey('OutputPin', 
                               )


class CombinedFragment(InteractionFragment):
    """
    A CombinedFragment defines an expression of InteractionFragments. A
    CombinedFragment is defined by an interaction operator and corresponding
    InteractionOperands. Through the use of CombinedFragments the user will be able
    to describe a number of traces in a compact and concise manner.
    """

    __package__ = 'UML.Interactions'

    cfragment_gate = models.ForeignKey('Gate', 
                                       )
    interaction_operator = models.ForeignKey('InteractionOperatorKind', 
                                             )
    operand = models.ForeignKey('InteractionOperand', 
                                )


class Usage(models.Model):
    """
    A Usage is a Dependency in which the client Element requires the supplier
    Element (or set of Elements) for its full implementation or operation.
    """

    __package__ = 'UML.CommonStructure'

    dependency = models.OneToOneField('Dependency')


class PackageMerge(DirectedRelationship):
    """
    A package merge defines how the contents of one package are extended by the
    contents of another package.
    """

    __package__ = 'UML.Packages'

    merged_package = models.ForeignKey('Package', 
                                       )
    receiving_package = models.ForeignKey('Package', 
                                          )


class Continuation(InteractionFragment):
    """
    A Continuation is a syntactic way to define continuations of different branches
    of an alternative CombinedFragment. Continuations are intuitively similar to
    labels representing intermediate points in a flow of control.
    """

    __package__ = 'UML.Interactions'

    setting = models.BooleanField()


class InvocationAction(Action):
    """
    InvocationAction is an abstract class for the various actions that request
    Behavior invocation.
    """

    __package__ = 'UML.Actions'

    argument = models.ForeignKey('InputPin', 
                                 )
    on_port = models.ForeignKey('Port', 
                                )

    class Meta:
        abstract = True


class CallAction(InvocationAction):
    """
    CallAction is an abstract class for Actions that invoke a Behavior with given
    argument values and (if the invocation is synchronous) receive reply values.
    """

    __package__ = 'UML.Actions'

    is_synchronous = models.BooleanField()
    result = models.ForeignKey('OutputPin', 
                               )

    class Meta:
        abstract = True

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior or Operation being
        called. (This operation is abstract and should be overridden by subclasses of
        CallAction.)
        """
        pass


class FinalNode(ControlNode):
    """
    A FinalNode is an abstract ControlNode at which a flow in an Activity stops.
    """

    __package__ = 'UML.Activities'


    class Meta:
        abstract = True


class FlowFinalNode(FinalNode):
    """
    A FlowFinalNode is a FinalNode that terminates a flow by consuming the tokens
    offered to it.
    """

    __package__ = 'UML.Activities'



class ValueSpecificationAction(Action):
    """
    A ValueSpecificationAction is an Action that evaluates a ValueSpecification and
    provides a result.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )
    value = models.ForeignKey('ValueSpecification', help_text='The ValueSpecification to be evaluated.')


class ParameterDirectionKind(models.Model):
    """
    ParameterDirectionKind is an Enumeration that defines literals used to specify
    direction of parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration')
    RETURN = 'return'
    IN = 'in'
    INOUT = 'inout'
    OUT = 'out'
    CHOICES = (
        (RETURN, 'Indicates that Parameter values are passed as return values back to ' +
                 'the caller.'),
        (IN, 'Indicates that Parameter values are passed in by the caller.'),
        (INOUT, 'Indicates that Parameter values are passed in by the caller and ' +
                '(possibly different) values passed out to the caller.'),
        (OUT, 'Indicates that Parameter values are passed out to the caller.'),
    )

    parameter_direction_kind = models.CharField(max_length=255, choices=CHOICES, default=OUT)


class ReadLinkAction(LinkAction):
    """
    A ReadLinkAction is a LinkAction that navigates across an Association to
    retrieve the objects on one end.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )

    def open_end(self):
        """
        Returns the ends corresponding to endData with no value InputPin. (A well-formed
        ReadLinkAction is constrained to have only one of these.)
        """
        # OCL: "result = (endData->select(value=null).end->asOrderedSet())"
        pass


class PseudostateKind(models.Model):
    """
    PseudostateKind is an Enumeration type that is used to differentiate various
    kinds of Pseudostates.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration')
    JOIN = 0
    CHOICE = 1
    JUNCTION = 2
    EXITPOINT = 3
    SHALLOWHISTORY = 4
    FORK = 5
    ENTRYPOINT = 6
    DEEPHISTORY = 7
    INITIAL = 8
    TERMINATE = 9
    CHOICES = (
        (JOIN, 'join'),
        (CHOICE, 'choice'),
        (JUNCTION, 'junction'),
        (EXITPOINT, 'exitPoint'),
        (SHALLOWHISTORY, 'shallowHistory'),
        (FORK, 'fork'),
        (ENTRYPOINT, 'entryPoint'),
        (DEEPHISTORY, 'deepHistory'),
        (INITIAL, 'initial'),
        (TERMINATE, 'terminate'),
    )

    pseudostate_kind = models.IntegerField(choices=CHOICES, default=TERMINATE)


class SendSignalAction(InvocationAction):
    """
    A SendSignalAction is an InvocationAction that creates a Signal instance and
    transmits it to the target object. Values from the argument InputPins are used
    to provide values for the attributes of the Signal. The requestor continues
    execution immediately after the Signal instance is sent out and cannot receive
    reply values.
    """

    __package__ = 'UML.Actions'

    signal = models.ForeignKey('Signal', 
                               )
    target = models.ForeignKey('InputPin', 
                               )


class ReduceAction(Action):
    """
    A ReduceAction is an Action that reduces a collection to a single value by
    repeatedly combining the elements of the collection using a reducer Behavior.
    """

    __package__ = 'UML.Actions'

    collection = models.ForeignKey('InputPin', 
                                   )
    is_ordered = models.BooleanField()
    reducer = models.ForeignKey('Behavior', 
                                )
    result = models.ForeignKey('OutputPin', 
                               )


class Event(PackageableElement):
    """
    An Event is the specification of some occurrence that may potentially trigger
    effects by an object.
    """

    __package__ = 'UML.CommonBehavior'


    class Meta:
        abstract = True


class MessageEvent(Event):
    """
    A MessageEvent specifies the receipt by an object of either an Operation call or
    a Signal instance.
    """

    __package__ = 'UML.CommonBehavior'


    class Meta:
        abstract = True


class AnyReceiveEvent(MessageEvent):
    """
    A trigger for an AnyReceiveEvent is triggered by the receipt of any message that
    is not explicitly handled by any related trigger.
    """

    __package__ = 'UML.CommonBehavior'



class Generalization(DirectedRelationship):
    """
    A Generalization is a taxonomic relationship between a more general Classifier
    and a more specific Classifier. Each instance of the specific Classifier is also
    an instance of the general Classifier. The specific Classifier inherits the
    features of the more general Classifier. A Generalization is owned by the
    specific Classifier.
    """

    __package__ = 'UML.Classification'

    general = models.ForeignKey('Classifier', 
                                )
    generalization_set = models.ForeignKey('GeneralizationSet', 
                                           )
    is_substitutable = models.BooleanField()
    specific = models.ForeignKey('Classifier', 
                                 )


class State(RedefinableElement, Namespace, Vertex):
    """
    A State models a situation during which some (usually implicit) invariant
    condition holds.
    """

    __package__ = 'UML.StateMachines'

    connection = models.ForeignKey('ConnectionPointReference', 
                                   )
    connection_point = models.ForeignKey('Pseudostate', 
                                         )
    deferrable_trigger = models.ForeignKey('Trigger', 
                                           )
    do_activity = models.ForeignKey('Behavior', 
                                    )
    entry = models.ForeignKey('Behavior', 
                              )
    exit = models.ForeignKey('Behavior', 
                             )
    is_composite = models.BooleanField()
    is_orthogonal = models.BooleanField()
    is_simple = models.BooleanField()
    is_submachine_state = models.BooleanField()
    redefined_state = models.ForeignKey('self', 
                                        )
    region = models.ForeignKey('Region', 
                               )
    state_invariant = models.ForeignKey('Constraint', 
                                        )
    submachine = models.ForeignKey('StateMachine', 
                                   )

    def __init__(self, *args, **kwargs):
        super(State).__init__(*args, **kwargs)

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the
        State either directly or transitively.
        """
        # OCL: "result = (container.containingStateMachine())"
        pass


class InformationFlow(DirectedRelationship, PackageableElement):
    """
    InformationFlows describe circulation of information through a system in a
    general manner. They do not specify the nature of the information, mechanisms by
    which it is conveyed, sequences of exchange or any control conditions. During
    more detailed modeling, representation and realization links may be added to
    specify which model elements implement an InformationFlow and to show how
    information is conveyed.  InformationFlows require some kind of 'information
    channel' for unidirectional transmission of information items from sources to
    targets.' They specify the information channel's realizations, if any, and
    identify the information that flows along them.' Information moving along the
    information channel may be represented by abstract InformationItems and by
    concrete Classifiers.
    """

    __package__ = 'UML.InformationFlows'

    conveyed = models.ForeignKey('Classifier', 
                                 )
    information_source = models.ForeignKey('NamedElement', 
                                           )
    information_target = models.ForeignKey('NamedElement', 
                                           )
    realization = models.ForeignKey('Relationship', 
                                    )
    realizing_activity_edge = models.ForeignKey('ActivityEdge', 
                                                )
    realizing_connector = models.ForeignKey('Connector', 
                                            )
    realizing_message = models.ForeignKey('Message', 
                                          )


class ParameterSet(NamedElement):
    """
    A ParameterSet designates alternative sets of inputs or outputs that a Behavior
    may use.
    """

    __package__ = 'UML.Classification'

    condition = models.ForeignKey('Constraint', 
                                  )
    parameter = models.ForeignKey('Parameter', help_text='Parameters in the ParameterSet.')


class MultiplicityElement(Element):
    """
    A multiplicity is a definition of an inclusive interval of non-negative integers
    beginning with a lower bound and ending with a (possibly infinite) upper bound.
    A MultiplicityElement embeds this information to specify the allowable
    cardinalities for an instantiation of the Element.
    """

    __package__ = 'UML.CommonStructure'

    is_ordered = models.BooleanField()
    is_unique = models.BooleanField()
    lower = models.ForeignKey('Integer', 
                              )
    lower_value = models.ForeignKey('ValueSpecification', 
                                    )
    upper = models.ForeignKey('UnlimitedNatural', 
                              )
    upper_value = models.ForeignKey('ValueSpecification', 
                                    )

    class Meta:
        abstract = True

    def compatible_with(self):
        """
        The operation compatibleWith takes another multiplicity as input. It returns
        true if the other multiplicity is wider than, or the same as, self.
        """
        # OCL: "result = ((other.lowerBound() <= self.lowerBound()) and ((other.upperBound() = *) or (self.upperBound() <= other.upperBound())))"
        pass


class StructuralFeature(MultiplicityElement, TypedElement, Feature):
    """
    A StructuralFeature is a typed feature of a Classifier that specifies the
    structure of instances of the Classifier.
    """

    __package__ = 'UML.Classification'

    is_read_only = models.BooleanField()

    class Meta:
        abstract = True


class ConnectableElement(TypedElement, ParameterableElement):
    """
    ConnectableElement is an abstract metaclass representing a set of instances that
    play roles of a StructuredClassifier. ConnectableElements may be joined by
    attached Connectors and specify configurations of linked instances to be created
    within an instance of the containing StructuredClassifier.
    """

    __package__ = 'UML.StructuredClassifiers'

    end = models.ForeignKey('ConnectorEnd', 
                            )

    def __init__(self, *args, **kwargs):
        super(ConnectableElement).__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def end_operation(self):
        """
        Derivation for ConnectableElement::/end : ConnectorEnd
        """
        # OCL: "result = (ConnectorEnd.allInstances()->select(role = self))"
        pass


class Property(ConnectableElement, DeploymentTarget, StructuralFeature):
    """
    A Property is a StructuralFeature. A Property related by ownedAttribute to a
    Classifier (other than an association) represents an attribute and might also
    represent an association end. It relates an instance of the Classifier to a
    value or set of values of the type of the attribute. A Property related by
    memberEnd to an Association represents an end of the Association. The type of
    the Property is the type of the end of the Association. A Property has the
    capability of being a DeploymentTarget in a Deployment relationship. This
    enables modeling the deployment to hierarchical nodes that have Properties
    functioning as internal parts.  Property specializes ParameterableElement to
    specify that a Property can be exposed as a formal template parameter, and
    provided as an actual parameter in a binding of a template.
    """

    __package__ = 'UML.Classification'

    aggregation = models.ForeignKey('AggregationKind', 
                                    )
    association = models.ForeignKey('Association', 
                                    )
    association_end = models.ForeignKey('self', 
                                        )
    class_ = models.ForeignKey('Class', 
                               )
    datatype = models.ForeignKey('DataType', 
                                 )
    default_value = models.ForeignKey('ValueSpecification', 
                                      )
    interface = models.ForeignKey('Interface', 
                                  )
    is_composite = models.BooleanField()
    is_derived = models.BooleanField()
    is_derived_union = models.BooleanField()
    is_id = models.BooleanField()
    opposite = models.ForeignKey('self', 
                                 )
    owning_association = models.ForeignKey('Association', 
                                           )
    qualifier = models.ForeignKey('self', 
                                  )
    redefined_property = models.ForeignKey('self', 
                                           )
    subsetted_property = models.ForeignKey('self', 
                                           )

    def opposite_operation(self):
        """
        If this property is a memberEnd of a binary association, then opposite gives the
        other end.
        """
        """
        .. ocl:
            result = (if association <> null and association.memberEnd->size() = 2
            then
                association.memberEnd->any(e | e <> self)
            else
                null
            endif)
        """
        pass


class ExtensionEnd(models.Model):
    """
    An extension end is used to tie an extension to a stereotype when extending a
    metaclass. The default multiplicity of an extension end is 0..1.
    """

    __package__ = 'UML.Packages'

    property_ = models.OneToOneField('Property')

    def __init__(self, *args, **kwargs):
        super(ExtensionEnd).__init__(*args, **kwargs)

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an
        Integer. This is a redefinition of the default lower bound, which normally, for
        MultiplicityElements, evaluates to 1 if empty.
        """
        # OCL: "result = (if lowerValue=null then 0 else lowerValue.integerValue() endif)"
        pass


class IntervalConstraint(models.Model):
    """
    An IntervalConstraint is a Constraint that is specified by an Interval.
    """

    __package__ = 'UML.Values'

    constraint = models.OneToOneField('Constraint')

    def __init__(self, *args, **kwargs):
        super(IntervalConstraint).__init__(*args, **kwargs)


class DurationConstraint(models.Model):
    """
    A DurationConstraint is a Constraint that refers to a DurationInterval.
    """

    __package__ = 'UML.Values'

    interval_constraint = models.OneToOneField('IntervalConstraint')
    first_event = models.BooleanField()

    def __init__(self, *args, **kwargs):
        super(DurationConstraint).__init__(*args, **kwargs)


class LiteralString(LiteralSpecification):
    """
    A LiteralString is a specification of a String value.
    """

    __package__ = 'UML.Values'

    value = models.CharField(max_length=255, help_text='The specified String value.')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL: "result = (true)"
        pass


class Device(models.Model):
    """
    A device is a physical computational resource with processing capability upon
    which artifacts may be deployed for execution. Devices may be complex (i.e.,
    they may consist of other devices).
    """

    __package__ = 'UML.Deployments'

    node = models.OneToOneField('Node')


class Parameter(MultiplicityElement, ConnectableElement):
    """
    A Parameter is a specification of an argument used to pass information into or
    out of an invocation of a BehavioralFeature.  Parameters can be treated as
    ConnectableElements within Collaborations.
    """

    __package__ = 'UML.Classification'

    default = models.CharField(max_length=255, 
                               )
    default_value = models.ForeignKey('ValueSpecification', 
                                      )
    direction = models.ForeignKey('ParameterDirectionKind', 
                                  )
    effect = models.ForeignKey('ParameterEffectKind', 
                               )
    is_exception = models.BooleanField()
    is_stream = models.BooleanField()
    operation = models.ForeignKey('Operation', 
                                  )
    parameter_set = models.ForeignKey('ParameterSet', 
                                      )

    def default_operation(self):
        """
        Derivation for Parameter::/default
        """
        # OCL: "result = (if self.type = String then defaultValue.stringValue() else null endif)"
        pass


class SendObjectAction(InvocationAction):
    """
    A SendObjectAction is an InvocationAction that transmits an input object to the
    target object, which is handled as a request message by the target object. The
    requestor continues execution immediately after the object is sent out and
    cannot receive reply values.
    """

    __package__ = 'UML.Actions'

    target = models.ForeignKey('InputPin', 
                               )

    def __init__(self, *args, **kwargs):
        super(SendObjectAction).__init__(*args, **kwargs)


class Include(DirectedRelationship, NamedElement):
    """
    An Include relationship specifies that a UseCase contains the behavior defined
    in another UseCase.
    """

    __package__ = 'UML.UseCases'

    addition = models.ForeignKey('UseCase', help_text='The UseCase that is to be included.')
    including_case = models.ForeignKey('UseCase', 
                                       )


class Interval(ValueSpecification):
    """
    An Interval defines the range between two ValueSpecifications.
    """

    __package__ = 'UML.Values'

    max_ = models.ForeignKey('ValueSpecification', 
                             )
    min_ = models.ForeignKey('ValueSpecification', 
                             )


class InformationItem(Classifier):
    """
    InformationItems represent many kinds of information that can flow from sources
    to targets in very abstract ways.' They represent the kinds of information that
    may move within a system, but do not elaborate details of the transferred
    information.' Details of transferred information are the province of other
    Classifiers that may ultimately define InformationItems.' Consequently,
    InformationItems cannot be instantiated and do not themselves have features,
    generalizations, or associations.'An important use of InformationItems is to
    represent information during early design stages, possibly before the detailed
    modeling decisions that will ultimately define them have been made. Another
    purpose of InformationItems is to abstract portions of complex models in less
    precise, but perhaps more general and communicable, ways.
    """

    __package__ = 'UML.InformationFlows'

    represented = models.ForeignKey('Classifier', 
                                    )


class MessageSort(models.Model):
    """
    This is an enumerated type that identifies the type of communication action that
    was used to generate the Message.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration')
    CREATEMESSAGE = 'createmessage'
    REPLY = 'reply'
    DELETEMESSAGE = 'deletemessage'
    SYNCHCALL = 'synchcall'
    ASYNCHCALL = 'asynchcall'
    ASYNCHSIGNAL = 'asynchsignal'
    CHOICES = (
        (CREATEMESSAGE, 'The message designating the creation of another lifeline ' +
                        'object.'),
        (REPLY, 'The message is a reply message to an operation call.'),
        (DELETEMESSAGE, 'The message designating the termination of another lifeline.'),
        (SYNCHCALL, 'The message was generated by a synchronous call to an operation.'),
        (ASYNCHCALL, 'The message was generated by an asynchronous call to an operation; ' +
                     'i.e., a CallAction with isSynchronous = false.'),
        (ASYNCHSIGNAL, 'The message was generated by an asynchronous send action.'),
    )

    message_sort = models.CharField(max_length=255, choices=CHOICES, default=ASYNCHSIGNAL)


class ConnectionPointReference(Vertex):
    """
    A ConnectionPointReference represents a usage (as part of a submachine State) of
    an entry/exit point Pseudostate defined in the StateMachine referenced by the
    submachine State.
    """

    __package__ = 'UML.StateMachines'

    entry = models.ForeignKey('Pseudostate', 
                              )
    exit = models.ForeignKey('Pseudostate', 
                             )
    state = models.ForeignKey('State', 
                              )


class GeneralizationSet(PackageableElement):
    """
    A GeneralizationSet is a PackageableElement whose instances represent sets of
    Generalization relationships.
    """

    __package__ = 'UML.Classification'

    generalization = models.ForeignKey('Generalization', 
                                       )
    is_covering = models.BooleanField()
    is_disjoint = models.BooleanField()
    powertype = models.ForeignKey('Classifier', 
                                  )


class ForkNode(ControlNode):
    """
    A ForkNode is a ControlNode that splits a flow into multiple concurrent flows.
    """

    __package__ = 'UML.Activities'



class InteractionOperand(InteractionFragment, Namespace):
    """
    An InteractionOperand is contained in a CombinedFragment. An InteractionOperand
    represents one operand of the expression given by the enclosing
    CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    fragment = models.ForeignKey('InteractionFragment', help_text='The fragments of the operand.')
    guard = models.ForeignKey('InteractionConstraint', help_text='Constraint of the operand.')


class WriteVariableAction(VariableAction):
    """
    WriteVariableAction is an abstract class for VariableActions that change
    Variable values.
    """

    __package__ = 'UML.Actions'

    value = models.ForeignKey('InputPin', 
                              )

    class Meta:
        abstract = True


class RemoveVariableValueAction(WriteVariableAction):
    """
    A RemoveVariableValueAction is a WriteVariableAction that removes values from a
    Variables.
    """

    __package__ = 'UML.Actions'

    is_remove_duplicates = models.BooleanField()
    remove_at = models.ForeignKey('InputPin', 
                                  )


class Expression(ValueSpecification):
    """
    An Expression represents a node in an expression tree, which may be non-terminal
    or terminal. It defines a symbol, and has a possibly empty sequence of operands
    that are ValueSpecifications. It denotes a (possibly empty) set of values when
    evaluated in a context.
    """

    __package__ = 'UML.Values'

    operand = models.ForeignKey('ValueSpecification', 
                                )
    symbol = models.CharField(max_length=255, 
                              )


class StringExpression(TemplateableElement):
    """
    A StringExpression is an Expression that specifies a String value that is
    derived by concatenating a sequence of operands with String values or a sequence
    of subExpressions, some of which might be template parameters.
    """

    __package__ = 'UML.Values'

    expression = models.OneToOneField('Expression')
    owning_expression = models.ForeignKey('self', 
                                          )
    sub_expression = models.ForeignKey('self', 
                                       )

    def string_value(self):
        """
        The query stringValue() returns the String resulting from concatenating, in
        order, all the component String values of all the operands or subExpressions
        that are part of the StringExpression.
        """
        """
        .. ocl:
            result = (if subExpression->notEmpty()
            then subExpression->iterate(se; stringValue: String = '' | stringValue.concat(se.stringValue()))
            else operand->iterate(op; stringValue: String = '' | stringValue.concat(op.stringValue()))
            endif)
        """
        pass


class Clause(Element):
    """
    A Clause is an Element that represents a single branch of a ConditionalNode,
    including a test and a body section. The body section is executed only if (but
    not necessarily if) the test section evaluates to true.
    """

    __package__ = 'UML.Actions'

    body = models.ForeignKey('ExecutableNode', 
                             )
    body_output = models.ForeignKey('OutputPin', 
                                    )
    decider = models.ForeignKey('OutputPin', 
                                )
    predecessor_clause = models.ForeignKey('self', 
                                           )
    successor_clause = models.ForeignKey('self', 
                                         )
    test = models.ForeignKey('ExecutableNode', 
                             )


class WriteStructuralFeatureAction(StructuralFeatureAction):
    """
    WriteStructuralFeatureAction is an abstract class for StructuralFeatureActions
    that change StructuralFeature values.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )
    value = models.ForeignKey('InputPin', 
                              )

    class Meta:
        abstract = True


class AddStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """
    An AddStructuralFeatureValueAction is a WriteStructuralFeatureAction for adding
    values to a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    insert_at = models.ForeignKey('InputPin', 
                                  )
    is_replace_all = models.BooleanField()


class Port(models.Model):
    """
    A Port is a property of an EncapsulatedClassifier that specifies a distinct
    interaction point between that EncapsulatedClassifier and its environment or
    between the (behavior of the) EncapsulatedClassifier and its internal parts.
    Ports are connected to Properties of the EncapsulatedClassifier by Connectors
    through which requests can be made to invoke BehavioralFeatures. A Port may
    specify the services an EncapsulatedClassifier provides (offers) to its
    environment as well as the services that an EncapsulatedClassifier expects
    (requires) of its environment.  A Port may have an associated
    ProtocolStateMachine.
    """

    __package__ = 'UML.StructuredClassifiers'

    property_ = models.OneToOneField('Property')
    is_behavior = models.BooleanField()
    is_conjugated = models.BooleanField()
    is_service = models.BooleanField()
    protocol = models.ForeignKey('ProtocolStateMachine', 
                                 )
    provided = models.ForeignKey('Interface', 
                                 )
    redefined_port = models.ForeignKey('self', 
                                       )
    required = models.ForeignKey('Interface', 
                                 )

    def provided_operation(self):
        """
        Derivation for Port::/provided
        """
        # OCL: "result = (if isConjugated then basicRequired() else basicProvided() endif)"
        pass


class ObjectNode(TypedElement, ActivityNode):
    """
    An ObjectNode is an abstract ActivityNode that may hold tokens within the object
    flow in an Activity. ObjectNodes also support token selection, limitation on the
    number of tokens held, specification of the state required for tokens being
    held, and carrying control values.
    """

    __package__ = 'UML.Activities'

    in_state = models.ForeignKey('State', 
                                 )
    is_control_type = models.BooleanField()
    ordering = models.ForeignKey('ObjectNodeOrderingKind', 
                                 )
    selection = models.ForeignKey('Behavior', 
                                  )
    upper_bound = models.ForeignKey('ValueSpecification', 
                                    )

    class Meta:
        abstract = True


class Pin(ObjectNode, MultiplicityElement):
    """
    A Pin is an ObjectNode and MultiplicityElement that provides input values to an
    Action or accepts output values from an Action.
    """

    __package__ = 'UML.Actions'

    is_control = models.BooleanField()

    class Meta:
        abstract = True


class OutputPin(Pin):
    """
    An OutputPin is a Pin that holds output values produced by an Action.
    """

    __package__ = 'UML.Actions'



class SequenceNode(models.Model):
    """
    A SequenceNode is a StructuredActivityNode that executes a sequence of
    ExecutableNodes in order.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode')

    def __init__(self, *args, **kwargs):
        super(SequenceNode).__init__(*args, **kwargs)


class LiteralInteger(LiteralSpecification):
    """
    A LiteralInteger is a specification of an Integer value.
    """

    __package__ = 'UML.Values'

    value = models.ForeignKey('Integer', help_text='The specified Integer value.')

    def integer_value(self):
        """
        The query integerValue() gives the value.
        """
        # OCL: "result = (value)"
        pass


class Operation(TemplateableElement, ParameterableElement, BehavioralFeature):
    """
    An Operation is a BehavioralFeature of a Classifier that specifies the name,
    type, parameters, and constraints for invoking an associated Behavior. An
    Operation may invoke both the execution of method behaviors as well as other
    behavioral responses. Operation specializes TemplateableElement in order to
    support specification of template operations and bound operations. Operation
    specializes ParameterableElement to specify that an operation can be exposed as
    a formal template parameter, and provided as an actual parameter in a binding of
    a template.
    """

    __package__ = 'UML.Classification'

    body_condition = models.ForeignKey('Constraint', 
                                       )
    class_ = models.ForeignKey('Class', 
                               )
    datatype = models.ForeignKey('DataType', 
                                 )
    interface = models.ForeignKey('Interface', 
                                  )
    is_ordered = models.BooleanField()
    is_query = models.BooleanField()
    is_unique = models.BooleanField()
    lower = models.ForeignKey('Integer', 
                              )
    postcondition = models.ForeignKey('Constraint', 
                                      )
    precondition = models.ForeignKey('Constraint', 
                                     )
    redefined_operation = models.ForeignKey('self', 
                                            )
    type_ = models.ForeignKey('Type', 
                              )
    upper = models.ForeignKey('UnlimitedNatural', 
                              )

    def __init__(self, *args, **kwargs):
        super(Operation).__init__(*args, **kwargs)

    def is_consistent_with(self):
        """
        The query isConsistentWith() specifies, for any two Operations in a context in
        which redefinition is possible, whether redefinition would be consistent. A
        redefining operation is consistent with a redefined operation if  it has the
        same number of owned parameters, and for each parameter the following holds:
        - Direction, ordering and uniqueness are the same.  - The corresponding types
        are covariant, contravariant or invariant.  - The multiplicities are compatible,
        depending on the parameter direction.
        """
        pass


class InteractionConstraint(models.Model):
    """
    An InteractionConstraint is a Boolean expression that guards an operand in a
    CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    constraint = models.OneToOneField('Constraint')
    maxint = models.ForeignKey('ValueSpecification', 
                               )
    minint = models.ForeignKey('ValueSpecification', 
                               )


class BehaviorExecutionSpecification(ExecutionSpecification):
    """
    A BehaviorExecutionSpecification is a kind of ExecutionSpecification
    representing the execution of a Behavior.
    """

    __package__ = 'UML.Interactions'

    behavior = models.ForeignKey('Behavior', 
                                 )


class TemplateParameter(Element):
    """
    A TemplateParameter exposes a ParameterableElement as a formal parameter of a
    template.
    """

    __package__ = 'UML.CommonStructure'

    default = models.ForeignKey('ParameterableElement', 
                                )
    owned_default = models.ForeignKey('ParameterableElement', 
                                      )
    owned_parametered_element = models.ForeignKey('ParameterableElement', 
                                                  )
    parametered_element = models.ForeignKey('ParameterableElement', 
                                            )
    signature = models.ForeignKey('TemplateSignature', 
                                  )


class ActivityParameterNode(ObjectNode):
    """
    An ActivityParameterNode is an ObjectNode for accepting values from the input
    Parameters or providing values to the output Parameters of an Activity.
    """

    __package__ = 'UML.Activities'

    parameter = models.ForeignKey('Parameter', 
                                  )


class CollaborationUse(NamedElement):
    """
    A CollaborationUse is used to specify the application of a pattern specified by
    a Collaboration to a specific situation.
    """

    __package__ = 'UML.StructuredClassifiers'

    role_binding = models.ForeignKey('Dependency', 
                                     )
    type_ = models.ForeignKey('Collaboration', 
                              )


class InterruptibleActivityRegion(ActivityGroup):
    """
    An InterruptibleActivityRegion is an ActivityGroup that supports the termination
    of tokens flowing in the portions of an activity within it.
    """

    __package__ = 'UML.Activities'

    interrupting_edge = models.ForeignKey('ActivityEdge', 
                                          )
    node = models.ForeignKey('ActivityNode', 
                             )


class ExpansionKind(models.Model):
    """
    ExpansionKind is an enumeration type used to specify how an ExpansionRegion
    executes its contents.
    """

    __package__ = 'UML.Actions'

    enumeration = models.OneToOneField('Enumeration')
    STREAM = 'stream'
    PARALLEL = 'parallel'
    ITERATIVE = 'iterative'
    CHOICES = (
        (STREAM, 'A stream of input collection elements flows into a single execution of ' +
                 'the content of the ExpansionRegion, in the order of the collection elements if ' +
                 'the input collections are ordered.'),
        (PARALLEL, 'The content of the ExpansionRegion is executed concurrently for the ' +
                   'elements of the input collections.'),
        (ITERATIVE, 'The content of the ExpansionRegion is executed iteratively for the ' +
                    'elements of the input collections, in the order of the input elements, if the ' +
                    'collections are ordered.'),
    )

    expansion_kind = models.CharField(max_length=255, choices=CHOICES, default=ITERATIVE)


class OpaqueExpression(ValueSpecification):
    """
    An OpaqueExpression is a ValueSpecification that specifies the computation of a
    collection of values either in terms of a UML Behavior or based on a textual
    statement in a language other than UML
    """

    __package__ = 'UML.Values'

    behavior = models.ForeignKey('Behavior', 
                                 )
    body = models.CharField(max_length=255, 
                            )
    language = models.CharField(max_length=255, 
                                )
    result = models.ForeignKey('Parameter', 
                               )

    def is_positive(self):
        """
        The query isPositive() tells whether an integer expression has a positive value.
        """
        pass


class CallEvent(MessageEvent):
    """
    A CallEvent models the receipt by an object of a message invoking a call of an
    Operation.
    """

    __package__ = 'UML.CommonBehavior'

    operation = models.ForeignKey('Operation', 
                                  )


class ConnectableElementTemplateParameter(models.Model):
    """
    A ConnectableElementTemplateParameter exposes a ConnectableElement as a formal
    parameter for a template.
    """

    __package__ = 'UML.StructuredClassifiers'

    template_parameter = models.OneToOneField('TemplateParameter')

    def __init__(self, *args, **kwargs):
        super(ConnectableElementTemplateParameter).__init__(*args, **kwargs)


class ExtensionPoint(RedefinableElement):
    """
    An ExtensionPoint identifies a point in the behavior of a UseCase where that
    behavior can be extended by the behavior of some other (extending) UseCase, as
    specified by an Extend relationship.
    """

    __package__ = 'UML.UseCases'

    use_case = models.ForeignKey('UseCase', 
                                 )


class StartClassifierBehaviorAction(Action):
    """
    A StartClassifierBehaviorAction is an Action that starts the classifierBehavior
    of the input object.
    """

    __package__ = 'UML.Actions'

    object_ = models.ForeignKey('InputPin', 
                                )


class ReadExtentAction(Action):
    """
    A ReadExtentAction is an Action that retrieves the current instances of a
    Classifier.
    """

    __package__ = 'UML.Actions'

    classifier = models.ForeignKey('Classifier', 
                                   )
    result = models.ForeignKey('OutputPin', 
                               )


class UseCase(BehavioredClassifier):
    """
    A UseCase specifies a set of actions performed by its subjects, which yields an
    observable result that is of value for one or more Actors or other stakeholders
    of each subject.
    """

    __package__ = 'UML.UseCases'

    extend = models.ForeignKey('Extend', 
                               )
    extension_point = models.ForeignKey('ExtensionPoint', 
                                        )
    include = models.ForeignKey('Include', 
                                )
    subject = models.ForeignKey('Classifier', 
                                )

    def all_included_use_cases(self):
        """
        The query allIncludedUseCases() returns the transitive closure of all UseCases
        (directly or indirectly) included by this UseCase.
        """
        # OCL: "result = (self.include.addition->union(self.include.addition->collect(uc | uc.allIncludedUseCases()))->asSet())"
        pass


class Extend(NamedElement, DirectedRelationship):
    """
    A relationship from an extending UseCase to an extended UseCase that specifies
    how and when the behavior defined in the extending UseCase can be inserted into
    the behavior defined in the extended UseCase.
    """

    __package__ = 'UML.UseCases'

    condition = models.ForeignKey('Constraint', 
                                  )
    extended_case = models.ForeignKey('UseCase', 
                                      )
    extension = models.ForeignKey('UseCase', 
                                  )
    extension_location = models.ForeignKey('ExtensionPoint', 
                                           )


class ClassifierTemplateParameter(models.Model):
    """
    A ClassifierTemplateParameter exposes a Classifier as a formal template
    parameter.
    """

    __package__ = 'UML.Classification'

    template_parameter = models.OneToOneField('TemplateParameter')
    allow_substitutable = models.BooleanField()
    constraining_classifier = models.ForeignKey('Classifier', 
                                                )

    def __init__(self, *args, **kwargs):
        super(ClassifierTemplateParameter).__init__(*args, **kwargs)


class ReadIsClassifiedObjectAction(Action):
    """
    A ReadIsClassifiedObjectAction is an Action that determines whether an object is
    classified by a given Classifier.
    """

    __package__ = 'UML.Actions'

    classifier = models.ForeignKey('Classifier', 
                                   )
    is_direct = models.BooleanField()
    object_ = models.ForeignKey('InputPin', 
                                )
    result = models.ForeignKey('OutputPin', 
                               )


class OperationTemplateParameter(models.Model):
    """
    An OperationTemplateParameter exposes an Operation as a formal parameter for a
    template.
    """

    __package__ = 'UML.Classification'

    template_parameter = models.OneToOneField('TemplateParameter')

    def __init__(self, *args, **kwargs):
        super(OperationTemplateParameter).__init__(*args, **kwargs)


class Association(Relationship, Classifier):
    """
    A link is a tuple of values that refer to typed objects.  An Association
    classifies a set of links, each of which is an instance of the Association.
    Each value in the link refers to an instance of the type of the corresponding
    end of the Association.
    """

    __package__ = 'UML.StructuredClassifiers'

    end_type = models.ForeignKey('Type', 
                                 )
    is_derived = models.BooleanField()
    member_end = models.ForeignKey('Property', 
                                   )
    navigable_owned_end = models.ForeignKey('Property', 
                                            )
    owned_end = models.ForeignKey('Property', 
                                  )

    def end_type_operation(self):
        """
        endType is derived from the types of the member ends.
        """
        # OCL: "result = (memberEnd->collect(type)->asSet())"
        pass


class Extension(models.Model):
    """
    An extension is used to indicate that the properties of a metaclass are extended
    through a stereotype, and gives the ability to flexibly add (and later remove)
    stereotypes to classes.
    """

    __package__ = 'UML.Packages'

    association = models.OneToOneField('Association')
    is_required = models.BooleanField()
    metaclass = models.ForeignKey('Class', 
                                  )

    def __init__(self, *args, **kwargs):
        super(Extension).__init__(*args, **kwargs)

    def metaclass_operation(self):
        """
        The query metaclass() returns the metaclass that is being extended (as opposed
        to the extending stereotype).
        """
        # OCL: "result = (metaclassEnd().type.oclAsType(Class))"
        pass


class MessageEnd(NamedElement):
    """
    MessageEnd is an abstract specialization of NamedElement that represents what
    can occur at the end of a Message.
    """

    __package__ = 'UML.Interactions'

    message = models.ForeignKey('Message', help_text='References a Message.')

    class Meta:
        abstract = True

    def enclosing_fragment(self):
        """
        This query returns a set including the enclosing InteractionFragment this
        MessageEnd is enclosed within.
        """
        """
        .. ocl:
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


class MessageOccurrenceSpecification(MessageEnd):
    """
    A MessageOccurrenceSpecification specifies the occurrence of Message events,
    such as sending and receiving of Signals or invoking or receiving of Operation
    calls. A MessageOccurrenceSpecification is a kind of MessageEnd. Messages are
    generated either by synchronous Operation calls or asynchronous Signal sends.
    They are received by the execution of corresponding AcceptEventActions.
    """

    __package__ = 'UML.Interactions'

    occurrence_specification = models.OneToOneField('OccurrenceSpecification')


class DestructionOccurrenceSpecification(models.Model):
    """
    A DestructionOccurenceSpecification models the destruction of an object.
    """

    __package__ = 'UML.Interactions'

    message_occurrence_specification = models.OneToOneField('MessageOccurrenceSpecification')


class Manifestation(models.Model):
    """
    A manifestation is the concrete physical rendering of one or more model elements
    by an artifact.
    """

    __package__ = 'UML.Deployments'

    abstraction = models.OneToOneField('Abstraction')
    utilized_element = models.ForeignKey('PackageableElement', 
                                         )


class ElementImport(DirectedRelationship):
    """
    An ElementImport identifies a NamedElement in a Namespace other than the one
    that owns that NamedElement and allows the NamedElement to be referenced using
    an unqualified name in the Namespace owning the ElementImport.
    """

    __package__ = 'UML.CommonStructure'

    alias = models.CharField(max_length=255, 
                             )
    imported_element = models.ForeignKey('PackageableElement', 
                                         )
    importing_namespace = models.ForeignKey('Namespace', 
                                            )
    visibility = models.ForeignKey('VisibilityKind', 
                                   )

    def get_name(self):
        """
        The query getName() returns the name under which the imported PackageableElement
        will be known in the importing namespace.
        """
        """
        .. ocl:
            result = (if alias->notEmpty() then
              alias
            else
              importedElement.name
            endif)
        """
        pass


class InputPin(Pin):
    """
    An InputPin is a Pin that holds input values to be consumed by an Action.
    """

    __package__ = 'UML.Actions'



class ValuePin(models.Model):
    """
    A ValuePin is an InputPin that provides a value by evaluating a
    ValueSpecification.
    """

    __package__ = 'UML.Actions'

    input_pin = models.OneToOneField('InputPin')
    value = models.ForeignKey('ValueSpecification', 
                              )


class CallBehaviorAction(CallAction):
    """
    A CallBehaviorAction is a CallAction that invokes a Behavior directly. The
    argument values of the CallBehaviorAction are passed on the input Parameters of
    the invoked Behavior. If the call is synchronous, the execution of the
    CallBehaviorAction waits until the execution of the invoked Behavior completes
    and the values of output Parameters of the Behavior are placed on the result
    OutputPins. If the call is asynchronous, the CallBehaviorAction completes
    immediately and no results values can be provided.
    """

    __package__ = 'UML.Actions'

    behavior = models.ForeignKey('Behavior', help_text='The Behavior being invoked.')

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior being called.
        """
        # OCL: "result = (behavior.inputParameters())"
        pass


class AddVariableValueAction(WriteVariableAction):
    """
    An AddVariableValueAction is a WriteVariableAction for adding values to a
    Variable.
    """

    __package__ = 'UML.Actions'

    insert_at = models.ForeignKey('InputPin', 
                                  )
    is_replace_all = models.BooleanField()


class ActivityPartition(ActivityGroup):
    """
    An ActivityPartition is a kind of ActivityGroup for identifying ActivityNodes
    that have some characteristic in common.
    """

    __package__ = 'UML.Activities'

    edge = models.ForeignKey('ActivityEdge', 
                             )
    is_dimension = models.BooleanField()
    is_external = models.BooleanField()
    node = models.ForeignKey('ActivityNode', 
                             )
    represents = models.ForeignKey('Element', 
                                   )
    subpartition = models.ForeignKey('self', 
                                     )
    super_partition = models.ForeignKey('self', 
                                        )


class Substitution(models.Model):
    """
    A substitution is a relationship between two classifiers signifying that the
    substituting classifier complies with the contract specified by the contract
    classifier. This implies that instances of the substituting classifier are
    runtime substitutable where instances of the contract classifier are expected.
    """

    __package__ = 'UML.Classification'

    realization = models.OneToOneField('Realization')
    contract = models.ForeignKey('Classifier', 
                                 )
    substituting_classifier = models.ForeignKey('Classifier', 
                                                )


class ProfileApplication(DirectedRelationship):
    """
    A profile application is used to show which profiles have been applied to a
    package.
    """

    __package__ = 'UML.Packages'

    applied_profile = models.ForeignKey('Profile', 
                                        )
    applying_package = models.ForeignKey('Package', 
                                         )
    is_strict = models.BooleanField()


class PackageImport(DirectedRelationship):
    """
    A PackageImport is a Relationship that imports all the non-private members of a
    Package into the Namespace owning the PackageImport, so that those Elements may
    be referred to by their unqualified names in the importingNamespace.
    """

    __package__ = 'UML.CommonStructure'

    imported_package = models.ForeignKey('Package', 
                                         )
    importing_namespace = models.ForeignKey('Namespace', 
                                            )
    visibility = models.ForeignKey('VisibilityKind', 
                                   )


class DestroyObjectAction(Action):
    """
    A DestroyObjectAction is an Action that destroys objects.
    """

    __package__ = 'UML.Actions'

    is_destroy_links = models.BooleanField()
    is_destroy_owned_objects = models.BooleanField()
    target = models.ForeignKey('InputPin', 
                               )


class ExpansionNode(ObjectNode):
    """
    An ExpansionNode is an ObjectNode used to indicate a collection input or output
    for an ExpansionRegion. A collection input of an ExpansionRegion contains a
    collection that is broken into its individual elements inside the region, whose
    content is executed once per element. A collection output of an ExpansionRegion
    combines individual elements produced by the execution of the region into a
    collection for use outside the region.
    """

    __package__ = 'UML.Actions'

    region_as_input = models.ForeignKey('ExpansionRegion', 
                                        )
    region_as_output = models.ForeignKey('ExpansionRegion', 
                                         )


class ParameterEffectKind(models.Model):
    """
    ParameterEffectKind is an Enumeration that indicates the effect of a Behavior on
    values passed in or out of its parameters.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration')
    UPDATE = 'update'
    READ = 'read'
    DELETE = 'delete'
    CREATE = 'create'
    CHOICES = (
        (UPDATE, 'Indicates objects that are values of the parameter have values of ' +
                 'their properties, or links in which they participate, or their classification ' +
                 'changed during executions of the behavior.'),
        (READ, 'Indicates objects that are values of the parameter have values of their ' +
               'properties, or links in which they participate, or their classifiers retrieved ' +
               'during executions of the behavior.'),
        (DELETE, 'Indicates objects that are values of the parameter do not exist after ' +
                 'executions of the behavior are finished.'),
        (CREATE, 'Indicates that the behavior creates values.'),
    )

    parameter_effect_kind = models.CharField(max_length=255, choices=CHOICES, default=CREATE)


class Trigger(NamedElement):
    """
    A Trigger specifies a specific point  at which an Event occurrence may trigger
    an effect in a Behavior. A Trigger may be qualified by the Port on which the
    Event occurred.
    """

    __package__ = 'UML.CommonBehavior'

    event = models.ForeignKey('Event', help_text='The Event that detected by the Trigger.')
    port = models.ForeignKey('Port', 
                             )


class Component(models.Model):
    """
    A Component represents a modular part of a system that encapsulates its contents
    and whose manifestation is replaceable within its environment.
    """

    __package__ = 'UML.StructuredClassifiers'

    class_ = models.OneToOneField('Class')
    is_indirectly_instantiated = models.BooleanField()
    packaged_element = models.ForeignKey('PackageableElement', 
                                         )
    provided = models.ForeignKey('Interface', 
                                 )
    realization = models.ForeignKey('ComponentRealization', 
                                    )
    required = models.ForeignKey('Interface', 
                                 )

    def provided_operation(self):
        """
        Derivation for Component::/provided
        """
        """
        .. ocl:
            result = (let 	ris : Set(Interface) = allRealizedInterfaces(),
                    realizingClassifiers : Set(Classifier) =  self.realization.realizingClassifier->union(self.allParents()->collect(realization.realizingClassifier))->asSet(),
                    allRealizingClassifiers : Set(Classifier) = realizingClassifiers->union(realizingClassifiers.allParents())->asSet(),
                    realizingClassifierInterfaces : Set(Interface) = allRealizingClassifiers->iterate(c; rci : Set(Interface) = Set{} | rci->union(c.allRealizedInterfaces())),
                    ports : Set(Port) = self.ownedPort->union(allParents()->collect(ownedPort))->asSet(),
                    providedByPorts : Set(Interface) = ports.provided->asSet()
            in     ris->union(realizingClassifierInterfaces) ->union(providedByPorts)->asSet())
        """
        pass


class ConditionalNode(models.Model):
    """
    A ConditionalNode is a StructuredActivityNode that chooses one among some number
    of alternative collections of ExecutableNodes to execute.
    """

    __package__ = 'UML.Actions'

    structured_activity_node = models.OneToOneField('StructuredActivityNode')
    clause = models.ForeignKey('Clause', 
                               )
    is_assured = models.BooleanField()
    is_determinate = models.BooleanField()

    def __init__(self, *args, **kwargs):
        super(ConditionalNode).__init__(*args, **kwargs)

    def all_actions(self):
        """
        Return only this ConditionalNode. This prevents Actions within the
        ConditionalNode from having their OutputPins used as bodyOutputs or decider Pins
        in containing LoopNodes or ConditionalNodes.
        """
        # OCL: "result = (self->asSet())"
        pass


class InterfaceRealization(models.Model):
    """
    An InterfaceRealization is a specialized realization relationship between a
    BehavioredClassifier and an Interface. This relationship signifies that the
    realizing BehavioredClassifier conforms to the contract specified by the
    Interface.
    """

    __package__ = 'UML.SimpleClassifiers'

    realization = models.OneToOneField('Realization')
    contract = models.ForeignKey('Interface', 
                                 )
    implementing_classifier = models.ForeignKey('BehavioredClassifier', 
                                                )


class Signal(Classifier):
    """
    A Signal is a specification of a kind of communication between objects in which
    a reaction is asynchronously triggered in the receiver without a reply.
    """

    __package__ = 'UML.SimpleClassifiers'

    owned_attribute = models.ForeignKey('Property', 
                                        )


class StateInvariant(InteractionFragment):
    """
    A StateInvariant is a runtime constraint on the participants of the Interaction.
    It may be used to specify a variety of different kinds of Constraints, such as
    values of Attributes or Variables, internal or external States, and so on. A
    StateInvariant is an InteractionFragment and it is placed on a Lifeline.
    """

    __package__ = 'UML.Interactions'

    invariant = models.ForeignKey('Constraint', 
                                  )

    def __init__(self, *args, **kwargs):
        super(StateInvariant).__init__(*args, **kwargs)


class Slot(Element):
    """
    A Slot designates that an entity modeled by an InstanceSpecification has a value
    or values for a specific StructuralFeature.
    """

    __package__ = 'UML.Classification'

    defining_feature = models.ForeignKey('StructuralFeature', 
                                         )
    owning_instance = models.ForeignKey('InstanceSpecification', 
                                        )
    value = models.ForeignKey('ValueSpecification', help_text='The value or values held by the Slot.')


class PrimitiveType(models.Model):
    """
    A PrimitiveType defines a predefined DataType, without any substructure. A
    PrimitiveType may have an algebra and operations defined outside of UML, for
    example, mathematically.
    """

    __package__ = 'UML.SimpleClassifiers'

    data_type = models.OneToOneField('DataType')


class TimeEvent(Event):
    """
    A TimeEvent is an Event that occurs at a specific point in time.
    """

    __package__ = 'UML.CommonBehavior'

    is_relative = models.BooleanField()
    when = models.ForeignKey('TimeExpression', help_text='Specifies the time of the TimeEvent.')


class TimeExpression(ValueSpecification):
    """
    A TimeExpression is a ValueSpecification that represents a time value.
    """

    __package__ = 'UML.Values'

    expr = models.ForeignKey('ValueSpecification', 
                             )
    observation = models.ForeignKey('Observation', 
                                    )


class Actor(BehavioredClassifier):
    """
    An Actor specifies a role played by a user or any other system that interacts
    with the subject.
    """

    __package__ = 'UML.UseCases'



class CommunicationPath(models.Model):
    """
    A communication path is an association between two deployment targets, through
    which they are able to exchange signals and messages.
    """

    __package__ = 'UML.Deployments'

    association = models.OneToOneField('Association')


class LiteralUnlimitedNatural(LiteralSpecification):
    """
    A LiteralUnlimitedNatural is a specification of an UnlimitedNatural number.
    """

    __package__ = 'UML.Values'

    value = models.ForeignKey('UnlimitedNatural', help_text='The specified UnlimitedNatural value.')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL: "result = (true)"
        pass


class Interaction(InteractionFragment, Behavior):
    """
    An Interaction is a unit of Behavior that focuses on the observable exchange of
    information between connectable elements.
    """

    __package__ = 'UML.Interactions'

    action = models.ForeignKey('Action', help_text='Actions owned by the Interaction.')
    formal_gate = models.ForeignKey('Gate', 
                                    )
    fragment = models.ForeignKey('InteractionFragment', 
                                 )
    lifeline = models.ForeignKey('Lifeline', 
                                 )
    message = models.ForeignKey('Message', 
                                )


class JoinNode(ControlNode):
    """
    A JoinNode is a ControlNode that synchronizes multiple flows.
    """

    __package__ = 'UML.Activities'

    is_combine_duplicate = models.BooleanField()
    join_spec = models.ForeignKey('ValueSpecification', 
                                  )


class ReadLinkObjectEndAction(Action):
    """
    A ReadLinkObjectEndAction is an Action that retrieves an end object from a link
    object.
    """

    __package__ = 'UML.Actions'

    end = models.ForeignKey('Property', help_text='The Association end to be read.')
    object_ = models.ForeignKey('InputPin', 
                                )
    result = models.ForeignKey('OutputPin', 
                               )


class BroadcastSignalAction(InvocationAction):
    """
    A BroadcastSignalAction is an InvocationAction that transmits a Signal instance
    to all the potential target objects in the system. Values from the argument
    InputPins are used to provide values for the attributes of the Signal. The
    requestor continues execution immediately after the Signal instances are sent
    out and cannot receive reply values.
    """

    __package__ = 'UML.Actions'

    signal = models.ForeignKey('Signal', 
                               )


class CentralBufferNode(ObjectNode):
    """
    A CentralBufferNode is an ObjectNode for managing flows from multiple sources
    and targets.
    """

    __package__ = 'UML.Activities'



class DataStoreNode(models.Model):
    """
    A DataStoreNode is a CentralBufferNode for persistent data.
    """

    __package__ = 'UML.Activities'

    central_buffer_node = models.OneToOneField('CentralBufferNode')


class SignalEvent(MessageEvent):
    """
    A SignalEvent represents the receipt of an asynchronous Signal instance.
    """

    __package__ = 'UML.CommonBehavior'

    signal = models.ForeignKey('Signal', 
                               )


class Comment(Element):
    """
    A Comment is a textual annotation that can be attached to a set of Elements.
    """

    __package__ = 'UML.CommonStructure'

    annotated_element = models.ForeignKey('Element', 
                                          )
    body = models.CharField(max_length=255, help_text='Specifies a string that is the comment.')


class Activity(Behavior):
    """
    An Activity is the specification of parameterized Behavior as the coordinated
    sequencing of subordinate units.
    """

    __package__ = 'UML.Activities'

    edge = models.ForeignKey('ActivityEdge', 
                             )
    group = models.ForeignKey('ActivityGroup', 
                              )
    is_read_only = models.BooleanField()
    is_single_execution = models.BooleanField()
    node = models.ForeignKey('ActivityNode', 
                             )
    partition = models.ForeignKey('ActivityPartition', 
                                  )
    structured_node = models.ForeignKey('StructuredActivityNode', 
                                        )
    variable = models.ForeignKey('Variable', 
                                 )


class ProtocolTransition(models.Model):
    """
    A ProtocolTransition specifies a legal Transition for an Operation. Transitions
    of ProtocolStateMachines have the following information: a pre-condition
    (guard), a Trigger, and a post-condition. Every ProtocolTransition is associated
    with at most one BehavioralFeature belonging to the context Classifier of the
    ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    transition = models.OneToOneField('Transition')
    post_condition = models.ForeignKey('Constraint', 
                                       )
    pre_condition = models.ForeignKey('Constraint', 
                                      )
    referred = models.ForeignKey('Operation', 
                                 )

    def referred_operation(self):
        """
        Derivation for ProtocolTransition::/referred
        """
        # OCL: "result = (trigger->collect(event)->select(oclIsKindOf(CallEvent))->collect(oclAsType(CallEvent).operation)->asSet())"
        pass


class TimeInterval(models.Model):
    """
    A TimeInterval defines the range between two TimeExpressions.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval')

    def __init__(self, *args, **kwargs):
        super(TimeInterval).__init__(*args, **kwargs)


class Reception(BehavioralFeature):
    """
    A Reception is a declaration stating that a Classifier is prepared to react to
    the receipt of a Signal.
    """

    __package__ = 'UML.SimpleClassifiers'

    signal = models.ForeignKey('Signal', 
                               )


class ClearVariableAction(VariableAction):
    """
    A ClearVariableAction is a VariableAction that removes all values of a Variable.
    """

    __package__ = 'UML.Actions'



class ActionInputPin(models.Model):
    """
    An ActionInputPin is a kind of InputPin that executes an Action to determine the
    values to input to another Action.
    """

    __package__ = 'UML.Actions'

    input_pin = models.OneToOneField('InputPin')
    from_action = models.ForeignKey('Action', 
                                    )


class LiteralReal(LiteralSpecification):
    """
    A LiteralReal is a specification of a Real value.
    """

    __package__ = 'UML.Values'

    value = models.ForeignKey('Real', help_text='The specified Real value.')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL: "result = (true)"
        pass


class Image(Element):
    """
    Physical definition of a graphical image.
    """

    __package__ = 'UML.Packages'

    content = models.CharField(max_length=255, 
                               )
    format_ = models.CharField(max_length=255, 
                               )
    location = models.CharField(max_length=255, 
                                )


class ControlFlow(ActivityEdge):
    """
    A ControlFlow is an ActivityEdge traversed by control tokens or object tokens of
    control type, which are use to control the execution of ExecutableNodes.
    """

    __package__ = 'UML.Activities'



class InteractionOperatorKind(models.Model):
    """
    InteractionOperatorKind is an enumeration designating the different kinds of
    operators of CombinedFragments. The InteractionOperand defines the type of
    operator of a CombinedFragment.
    """

    __package__ = 'UML.Interactions'

    enumeration = models.OneToOneField('Enumeration')
    STRICT = 'strict'
    OPT = 'opt'
    ASSERT = 'assert'
    NEG = 'neg'
    IGNORE = 'ignore'
    BREAK = 'break'
    LOOP = 'loop'
    CRITICAL = 'critical'
    ALT = 'alt'
    CONSIDER = 'consider'
    PAR = 'par'
    SEQ = 'seq'
    CHOICES = (
        (STRICT, 'The InteractionOperatorKind strict designates that the ' +
                 'CombinedFragment represents a strict sequencing between the behaviors of the ' +
                 'operands. The semantics of strict sequencing defines a strict ordering of the ' +
                 'operands on the first level within the CombinedFragment with interactionOperator ' +
                 'strict. Therefore OccurrenceSpecifications within contained CombinedFragment ' +
                 'will not directly be compared with other OccurrenceSpecifications of the ' +
                 'enclosing CombinedFragment.'),
        (OPT, 'The InteractionOperatorKind opt designates that the CombinedFragment ' +
              'represents a choice of behavior where either the (sole) operand happens or ' +
              'nothing happens. An option is semantically equivalent to an alternative ' +
              'CombinedFragment where there is one operand with non-empty content and the ' +
              'second operand is empty.'),
        (ASSERT, 'The InteractionOperatorKind assert designates that the ' +
                 'CombinedFragment represents an assertion. The sequences of the operand of the ' +
                 'assertion are the only valid continuations. All other continuations result in an ' +
                 'invalid trace.'),
        (NEG, 'The InteractionOperatorKind neg designates that the CombinedFragment ' +
              'represents traces that are defined to be invalid.'),
        (IGNORE, 'The InteractionOperatorKind ignore designates that there are some ' +
                 'message types that are not shown within this combined fragment. These message ' +
                 'types can be considered insignificant and are implicitly ignored if they appear ' +
                 'in a corresponding execution. Alternatively, one can understand ignore to mean ' +
                 'that the message types that are ignored can appear anywhere in the traces.'),
        (BREAK, 'The InteractionOperatorKind break designates that the CombinedFragment ' +
                'represents a breaking scenario in the sense that the operand is a scenario that ' +
                'is performed instead of the remainder of the enclosing InteractionFragment. A ' +
                'break operator with a guard is chosen when the guard is true and the rest of the ' +
                'enclosing Interaction Fragment is ignored. When the guard of the break operand ' +
                'is false, the break operand is ignored and the rest of the enclosing ' +
                'InteractionFragment is chosen. The choice between a break operand without a ' +
                'guard and the rest of the enclosing InteractionFragment is done non- ' +
                'deterministically.'),
        (LOOP, 'The InteractionOperatorKind loop designates that the CombinedFragment ' +
               'represents a loop. The loop operand will be repeated a number of times.'),
        (CRITICAL, 'The InteractionOperatorKind critical designates that the ' +
                   'CombinedFragment represents a critical region. A critical region means that the ' +
                   'traces of the region cannot be interleaved by other OccurrenceSpecifications (on ' +
                   'those Lifelines covered by the region). This means that the region is treated ' +
                   'atomically by the enclosing fragment when determining the set of valid traces. ' +
                   'Even though enclosing CombinedFragments may imply that some ' +
                   'OccurrenceSpecifications may interleave into the region, such as with par- ' +
                   'operator, this is prevented by defining a region.'),
        (ALT, 'The InteractionOperatorKind alt designates that the CombinedFragment ' +
              'represents a choice of behavior. At most one of the operands will be chosen. The ' +
              'chosen operand must have an explicit or implicit guard expression that evaluates ' +
              'to true at this point in the interaction. An implicit true guard is implied if ' +
              'the operand has no guard.'),
        (CONSIDER, 'The InteractionOperatorKind consider designates which messages ' +
                   'should be considered within this combined fragment. This is equivalent to ' +
                   'defining every other message to be ignored.'),
        (PAR, 'The InteractionOperatorKind par designates that the CombinedFragment ' +
              'represents a parallel merge between the behaviors of the operands. The ' +
              'OccurrenceSpecifications of the different operands can be interleaved in any way ' +
              'as long as the ordering imposed by each operand as such is preserved.'),
        (SEQ, 'The InteractionOperatorKind seq designates that the CombinedFragment ' +
              'represents a weak sequencing between the behaviors of the operands.'),
    )

    interaction_operator_kind = models.CharField(max_length=255, choices=CHOICES, default=SEQ)


class TemplateBinding(DirectedRelationship):
    """
    A TemplateBinding is a DirectedRelationship between a TemplateableElement and a
    template. A TemplateBinding specifies the TemplateParameterSubstitutions of
    actual parameters for the formal parameters of the template.
    """

    __package__ = 'UML.CommonStructure'

    bound_element = models.ForeignKey('TemplateableElement', 
                                      )
    parameter_substitution = models.ForeignKey('TemplateParameterSubstitution', 
                                               )
    signature = models.ForeignKey('TemplateSignature', 
                                  )


class AssociationClass(models.Model):
    """
    A model element that has both Association and Class properties. An
    AssociationClass can be seen as an Association that also has Class properties,
    or as a Class that also has Association properties. It not only connects a set
    of Classifiers but also defines a set of Features that belong to the Association
    itself and not to any of the associated Classifiers.
    """

    __package__ = 'UML.StructuredClassifiers'

    class_ = models.OneToOneField('Class')
    association = models.OneToOneField('Association')


class TimeObservation(Observation):
    """
    A TimeObservation is a reference to a time instant during an execution. It
    points out the NamedElement in the model to observe and whether the observation
    is when this NamedElement is entered or when it is exited.
    """

    __package__ = 'UML.Values'

    event = models.ForeignKey('NamedElement', 
                              )
    first_event = models.BooleanField()


class ProtocolConformance(DirectedRelationship):
    """
    A ProtocolStateMachine can be redefined into a more specific
    ProtocolStateMachine or into behavioral StateMachine. ProtocolConformance
    declares that the specific ProtocolStateMachine specifies a protocol that
    conforms to the general ProtocolStateMachine or that the specific behavioral
    StateMachine abides by the protocol of the general ProtocolStateMachine.
    """

    __package__ = 'UML.StateMachines'

    general_machine = models.ForeignKey('ProtocolStateMachine', 
                                        )
    specific_machine = models.ForeignKey('ProtocolStateMachine', 
                                         )


class FinalState(models.Model):
    """
    A special kind of State, which, when entered, signifies that the enclosing
    Region has completed. If the enclosing Region is directly contained in a
    StateMachine and all other Regions in that StateMachine also are completed, then
    it means that the entire StateMachine behavior is completed.
    """

    __package__ = 'UML.StateMachines'

    state = models.OneToOneField('State')


class ConsiderIgnoreFragment(models.Model):
    """
    A ConsiderIgnoreFragment is a kind of CombinedFragment that is used for the
    consider and ignore cases, which require lists of pertinent Messages to be
    specified.
    """

    __package__ = 'UML.Interactions'

    combined_fragment = models.OneToOneField('CombinedFragment')
    message = models.ForeignKey('NamedElement', 
                                )


class StateMachine(Behavior):
    """
    StateMachines can be used to express event-driven behaviors of parts of a
    system. Behavior is modeled as a traversal of a graph of Vertices interconnected
    by one or more joined Transition arcs that are triggered by the dispatching of
    successive Event occurrences. During this traversal, the StateMachine may
    execute a sequence of Behaviors associated with various elements of the
    StateMachine.
    """

    __package__ = 'UML.StateMachines'

    connection_point = models.ForeignKey('Pseudostate', 
                                         )
    region = models.ForeignKey('Region', 
                               )
    submachine_state = models.ForeignKey('State', 
                                         )

    def __init__(self, *args, **kwargs):
        super(StateMachine).__init__(*args, **kwargs)

    def lca(self):
        """
        The operation LCA(s1,s2) returns the Region that is the least common ancestor of
        Vertices s1 and s2, based on the StateMachine containment hierarchy.
        """
        """
        .. ocl:
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


class Gate(MessageEnd):
    """
    A Gate is a MessageEnd which serves as a connection point for relating a Message
    which has a MessageEnd (sendEvent / receiveEvent) outside an InteractionFragment
    with another Message which has a MessageEnd (receiveEvent / sendEvent)  inside
    that InteractionFragment.
    """

    __package__ = 'UML.Interactions'


    def is_actual(self):
        """
        This query returns true value if this Gate is an actualGate of an
        InteractionUse.
        """
        # OCL: "result = (interactionUse->notEmpty())"
        pass


class ExceptionHandler(Element):
    """
    An ExceptionHandler is an Element that specifies a handlerBody ExecutableNode to
    execute in case the specified exception occurs during the execution of the
    protected ExecutableNode.
    """

    __package__ = 'UML.Activities'

    exception_input = models.ForeignKey('ObjectNode', 
                                        )
    exception_type = models.ForeignKey('Classifier', 
                                       )
    handler_body = models.ForeignKey('ExecutableNode', 
                                     )
    protected_node = models.ForeignKey('ExecutableNode', 
                                       )


class TransitionKind(models.Model):
    """
    TransitionKind is an Enumeration type used to differentiate the various kinds of
    Transitions.
    """

    __package__ = 'UML.StateMachines'

    enumeration = models.OneToOneField('Enumeration')
    INTERNAL = 'internal'
    LOCAL = 'local'
    EXTERNAL = 'external'
    CHOICES = (
        (INTERNAL, 'Implies that the Transition, if triggered, occurs without exiting or ' +
                   'entering the source State (i.e., it does not cause a state change). This means ' +
                   'that the entry or exit condition of the source State will not be invoked. An ' +
                   'internal Transition can be taken even if the SateMachine is in one or more ' +
                   'Regions nested within the associated State.'),
        (LOCAL, 'Implies that the Transition, if triggered, will not exit the composite ' +
                '(source) State, but it will exit and re-enter any state within the composite ' +
                'State that is in the current state configuration.'),
        (EXTERNAL, 'Implies that the Transition, if triggered, will exit the composite ' +
                   '(source) State.'),
    )

    transition_kind = models.CharField(max_length=255, choices=CHOICES, default=EXTERNAL)


class InstanceSpecification(DeploymentTarget, PackageableElement, DeployedArtifact):
    """
    An InstanceSpecification is a model element that represents an instance in a
    modeled system. An InstanceSpecification can act as a DeploymentTarget in a
    Deployment relationship, in the case that it represents an instance of a Node.
    It can also act as a DeployedArtifact, if it represents an instance of an
    Artifact.
    """

    __package__ = 'UML.Classification'

    classifier = models.ForeignKey('Classifier', 
                                   )
    slot = models.ForeignKey('Slot', 
                             )
    specification = models.ForeignKey('ValueSpecification', 
                                      )


class QualifierValue(Element):
    """
    A QualifierValue is an Element that is used as part of LinkEndData to provide
    the value for a single qualifier of the end given by the LinkEndData.
    """

    __package__ = 'UML.Actions'

    qualifier = models.ForeignKey('Property', 
                                  )
    value = models.ForeignKey('InputPin', 
                              )


class EnumerationLiteral(models.Model):
    """
    An EnumerationLiteral is a user-defined data value for an Enumeration.
    """

    __package__ = 'UML.SimpleClassifiers'

    instance_specification = models.OneToOneField('InstanceSpecification')
    enumeration = models.ForeignKey('Enumeration', 
                                    )

    def __init__(self, *args, **kwargs):
        super(EnumerationLiteral).__init__(*args, **kwargs)

    def classifier_operation(self):
        """
        Derivation of Enumeration::/classifier
        """
        # OCL: "result = (enumeration)"
        pass


class TimeConstraint(models.Model):
    """
    A TimeConstraint is a Constraint that refers to a TimeInterval.
    """

    __package__ = 'UML.Values'

    interval_constraint = models.OneToOneField('IntervalConstraint')
    first_event = models.BooleanField()

    def __init__(self, *args, **kwargs):
        super(TimeConstraint).__init__(*args, **kwargs)


class ReplyAction(Action):
    """
    A ReplyAction is an Action that accepts a set of reply values and a value
    containing return information produced by a previous AcceptCallAction. The
    ReplyAction returns the values to the caller of the previous call, completing
    execution of the call.
    """

    __package__ = 'UML.Actions'

    reply_to_call = models.ForeignKey('Trigger', 
                                      )
    reply_value = models.ForeignKey('InputPin', 
                                    )
    return_information = models.ForeignKey('InputPin', 
                                           )


class RaiseExceptionAction(Action):
    """
    A RaiseExceptionAction is an Action that causes an exception to occur. The input
    value becomes the exception object.
    """

    __package__ = 'UML.Actions'

    exception = models.ForeignKey('InputPin', 
                                  )


class LiteralNull(LiteralSpecification):
    """
    A LiteralNull specifies the lack of a value.
    """

    __package__ = 'UML.Values'


    def is_null(self):
        """
        The query isNull() returns true.
        """
        # OCL: "result = (true)"
        pass


class GeneralOrdering(NamedElement):
    """
    A GeneralOrdering represents a binary relation between two
    OccurrenceSpecifications, to describe that one OccurrenceSpecification must
    occur before the other in a valid trace. This mechanism provides the ability to
    define partial orders of OccurrenceSpecifications that may otherwise not have a
    specified order.
    """

    __package__ = 'UML.Interactions'

    after = models.ForeignKey('OccurrenceSpecification', 
                              )
    before = models.ForeignKey('OccurrenceSpecification', 
                               )


class Interface(Classifier):
    """
    Interfaces declare coherent services that are implemented by
    BehavioredClassifiers that implement the Interfaces via InterfaceRealizations.
    """

    __package__ = 'UML.SimpleClassifiers'

    nested_classifier = models.ForeignKey('Classifier', 
                                          )
    owned_attribute = models.ForeignKey('Property', 
                                        )
    owned_operation = models.ForeignKey('Operation', 
                                        )
    owned_reception = models.ForeignKey('Reception', 
                                        )
    protocol = models.ForeignKey('ProtocolStateMachine', 
                                 )
    redefined_interface = models.ForeignKey('self', 
                                            )


class Collaboration(StructuredClassifier, BehavioredClassifier):
    """
    A Collaboration describes a structure of collaborating elements (roles), each
    performing a specialized function, which collectively accomplish some desired
    functionality.
    """

    __package__ = 'UML.StructuredClassifiers'

    collaboration_role = models.ForeignKey('ConnectableElement', 
                                           )


class ProtocolStateMachine(models.Model):
    """
    A ProtocolStateMachine is always defined in the context of a Classifier. It
    specifies which BehavioralFeatures of the Classifier can be called in which
    State and under which conditions, thus specifying the allowed invocation
    sequences on the Classifier's BehavioralFeatures. A ProtocolStateMachine
    specifies the possible and permitted Transitions on the instances of its context
    Classifier, together with the BehavioralFeatures that carry the Transitions. In
    this manner, an instance lifecycle can be specified for a Classifier, by
    defining the order in which the BehavioralFeatures can be activated and the
    States through which an instance progresses during its existence.
    """

    __package__ = 'UML.StateMachines'

    state_machine = models.OneToOneField('StateMachine')
    conformance = models.ForeignKey('ProtocolConformance', 
                                    )


class OpaqueAction(Action):
    """
    An OpaqueAction is an Action whose functionality is not specified within UML.
    """

    __package__ = 'UML.Actions'

    body = models.CharField(max_length=255, 
                            )
    input_value = models.ForeignKey('InputPin', 
                                    )
    language = models.CharField(max_length=255, 
                                )
    output_value = models.ForeignKey('OutputPin', 
                                     )


class Model(models.Model):
    """
    A model captures a view of a physical system. It is an abstraction of the
    physical system, with a certain purpose. This purpose determines what is to be
    included in the model and what is irrelevant. Thus the model completely
    describes those aspects of the physical system that are relevant to the purpose
    of the model, at the appropriate level of detail.
    """

    __package__ = 'UML.Packages'

    package = models.OneToOneField('Package')
    viewpoint = models.CharField(max_length=255, 
                                 )


class Duration(ValueSpecification):
    """
    A Duration is a ValueSpecification that specifies the temporal distance between
    two time instants.
    """

    __package__ = 'UML.Values'

    expr = models.ForeignKey('ValueSpecification', 
                             )
    observation = models.ForeignKey('Observation', 
                                    )


class Variable(ConnectableElement, MultiplicityElement):
    """
    A Variable is a ConnectableElement that may store values during the execution of
    an Activity. Reading and writing the values of a Variable provides an
    alternative means for passing data than the use of ObjectFlows. A Variable may
    be owned directly by an Activity, in which case it is accessible from anywhere
    within that activity, or it may be owned by a StructuredActivityNode, in which
    case it is only accessible within that node.
    """

    __package__ = 'UML.Activities'

    activity_scope = models.ForeignKey('Activity', 
                                       )
    scope = models.ForeignKey('StructuredActivityNode', 
                              )

    def is_accessible_by(self):
        """
        A Variable is accessible by Actions within its scope (the Activity or
        StructuredActivityNode that owns it).
        """
        """
        .. ocl:
            result = (if scope<>null then scope.allOwnedNodes()->includes(a)
            else a.containingActivity()=activityScope
            endif)
        """
        pass


class TestIdentityAction(Action):
    """
    A TestIdentityAction is an Action that tests if two values are identical
    objects.
    """

    __package__ = 'UML.Actions'

    first = models.ForeignKey('InputPin', 
                              )
    result = models.ForeignKey('OutputPin', 
                               )
    second = models.ForeignKey('InputPin', 
                               )


class RemoveStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """
    A RemoveStructuralFeatureValueAction is a WriteStructuralFeatureAction that
    removes values from a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    is_remove_duplicates = models.BooleanField()
    remove_at = models.ForeignKey('InputPin', 
                                  )


class CreateObjectAction(Action):
    """
    A CreateObjectAction is an Action that creates an instance of the specified
    Classifier.
    """

    __package__ = 'UML.Actions'

    classifier = models.ForeignKey('Classifier', help_text='The Classifier to be instantiated.')
    result = models.ForeignKey('OutputPin', 
                               )


class InitialNode(ControlNode):
    """
    An InitialNode is a ControlNode that offers a single control token when
    initially enabled.
    """

    __package__ = 'UML.Activities'



class ConnectorEnd(MultiplicityElement):
    """
    A ConnectorEnd is an endpoint of a Connector, which attaches the Connector to a
    ConnectableElement.
    """

    __package__ = 'UML.StructuredClassifiers'

    defining_end = models.ForeignKey('Property', 
                                     )
    part_with_port = models.ForeignKey('Property', 
                                       )
    role = models.ForeignKey('ConnectableElement', 
                             )

    def defining_end_operation(self):
        """
        Derivation for ConnectorEnd::/definingEnd : Property
        """
        """
        .. ocl:
            result = (if connector.type = null 
            then
              null 
            else
              let index : Integer = connector.end->indexOf(self) in
                connector.type.memberEnd->at(index)
            endif)
        """
        pass


class DurationInterval(models.Model):
    """
    A DurationInterval defines the range between two Durations.
    """

    __package__ = 'UML.Values'

    interval = models.OneToOneField('Interval')

    def __init__(self, *args, **kwargs):
        super(DurationInterval).__init__(*args, **kwargs)


class DeploymentSpecification(models.Model):
    """
    A deployment specification specifies a set of properties that determine
    execution parameters of a component artifact that is deployed on a node. A
    deployment specification can be aimed at a specific type of container. An
    artifact that reifies or implements deployment specification properties is a
    deployment descriptor.
    """

    __package__ = 'UML.Deployments'

    artifact = models.OneToOneField('Artifact')
    deployment = models.ForeignKey('Deployment', 
                                   )
    deployment_location = models.CharField(max_length=255, 
                                           )
    execution_location = models.CharField(max_length=255, 
                                          )


class AcceptCallAction(models.Model):
    """
    An AcceptCallAction is an AcceptEventAction that handles the receipt of a
    synchronous call request. In addition to the values from the Operation input
    parameters, the Action produces an output that is needed later to supply the
    information to the ReplyAction necessary to return control to the caller. An
    AcceptCallAction is for synchronous calls. If it is used to handle an
    asynchronous call, execution of the subsequent ReplyAction will complete
    immediately with no effect.
    """

    __package__ = 'UML.Actions'

    accept_event_action = models.OneToOneField('AcceptEventAction')
    return_information = models.ForeignKey('OutputPin', 
                                           )


class LinkEndDestructionData(models.Model):
    """
    LinkEndDestructionData is LinkEndData used to provide values for one end of a
    link to be destroyed by a DestroyLinkAction.
    """

    __package__ = 'UML.Actions'

    link_end_data = models.OneToOneField('LinkEndData')
    destroy_at = models.ForeignKey('InputPin', 
                                   )
    is_destroy_duplicates = models.BooleanField()

    def all_pins(self):
        """
        Adds the destroyAt InputPin (if any) to the set of all Pins.
        """
        # OCL: "result = (self.LinkEndData::allPins()->including(destroyAt))"
        pass


class Region(Namespace, RedefinableElement):
    """
    A Region is a top-level part of a StateMachine or a composite State, that serves
    as a container for the Vertices and Transitions of the StateMachine. A
    StateMachine or composite State may contain multiple Regions representing
    behaviors that may occur in parallel.
    """

    __package__ = 'UML.StateMachines'

    extended_region = models.ForeignKey('self', 
                                        )
    state = models.ForeignKey('State', 
                              )
    state_machine = models.ForeignKey('StateMachine', 
                                      )
    subvertex = models.ForeignKey('Vertex', 
                                  )
    transition = models.ForeignKey('Transition', 
                                   )

    def __init__(self, *args, **kwargs):
        super(Region).__init__(*args, **kwargs)

    def containing_state_machine(self):
        """
        The operation containingStateMachine() returns the StateMachine in which this
        Region is defined.
        """
        """
        .. ocl:
            result = (if stateMachine = null 
            then
              state.containingStateMachine()
            else
              stateMachine
            endif)
        """
        pass


class DecisionNode(ControlNode):
    """
    A DecisionNode is a ControlNode that chooses between outgoing ActivityEdges for
    the routing of tokens.
    """

    __package__ = 'UML.Activities'

    decision_input = models.ForeignKey('Behavior', 
                                       )
    decision_input_flow = models.ForeignKey('ObjectFlow', 
                                            )


class Connector(Feature):
    """
    A Connector specifies links that enables communication between two or more
    instances. In contrast to Associations, which specify links between any instance
    of the associated Classifiers, Connectors specify links between instances
    playing the connected parts only.
    """

    __package__ = 'UML.StructuredClassifiers'

    contract = models.ForeignKey('Behavior', 
                                 )
    end = models.ForeignKey('ConnectorEnd', 
                            )
    kind = models.ForeignKey('ConnectorKind', 
                             )
    redefined_connector = models.ForeignKey('self', 
                                            )
    type_ = models.ForeignKey('Association', 
                              )

    def kind_operation(self):
        """
        Derivation for Connector::/kind : ConnectorKind
        """
        """
        .. ocl:
            result = (if end->exists(
            		role.oclIsKindOf(Port) 
            		and partWithPort->isEmpty()
            		and not role.oclAsType(Port).isBehavior)
            then ConnectorKind::delegation 
            else ConnectorKind::assembly 
            endif)
        """
        pass


class ChangeEvent(Event):
    """
    A ChangeEvent models a change in the system configuration that makes a condition
    true.
    """

    __package__ = 'UML.CommonBehavior'

    change_expression = models.ForeignKey('ValueSpecification', 
                                          )


class CallOperationAction(CallAction):
    """
    A CallOperationAction is a CallAction that transmits an Operation call request
    to the target object, where it may cause the invocation of associated Behavior.
    The argument values of the CallOperationAction are passed on the input
    Parameters of the Operation. If call is synchronous, the execution of the
    CallOperationAction waits until the execution of the invoked Operation completes
    and the values of output Parameters of the Operation are placed on the result
    OutputPins. If the call is asynchronous, the CallOperationAction completes
    immediately and no results values can be provided.
    """

    __package__ = 'UML.Actions'

    operation = models.ForeignKey('Operation', help_text='The Operation being invoked.')
    target = models.ForeignKey('InputPin', 
                               )

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Operation being called.
        """
        # OCL: "result = (operation.inputParameters())"
        pass


class ReadSelfAction(Action):
    """
    A ReadSelfAction is an Action that retrieves the context object of the Behavior
    execution within which the ReadSelfAction execution is taking place.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )


class ClearStructuralFeatureAction(StructuralFeatureAction):
    """
    A ClearStructuralFeatureAction is a StructuralFeatureAction that removes all
    values of a StructuralFeature.
    """

    __package__ = 'UML.Actions'

    result = models.ForeignKey('OutputPin', 
                               )


class ClearAssociationAction(Action):
    """
    A ClearAssociationAction is an Action that destroys all links of an Association
    in which a particular object participates.
    """

    __package__ = 'UML.Actions'

    association = models.ForeignKey('Association', help_text='The Association to be cleared.')
    object_ = models.ForeignKey('InputPin', 
                                )


class ReadLinkObjectEndQualifierAction(Action):
    """
    A ReadLinkObjectEndQualifierAction is an Action that retrieves a qualifier end
    value from a link object.
    """

    __package__ = 'UML.Actions'

    object_ = models.ForeignKey('InputPin', 
                                )
    qualifier = models.ForeignKey('Property', help_text='The qualifier Property to be read.')
    result = models.ForeignKey('OutputPin', 
                               )


class StartObjectBehaviorAction(CallAction):
    """
    A StartObjectBehaviorAction is an InvocationAction that starts the execution
    either of a directly instantiated Behavior or of the classifierBehavior of an
    object. Argument values may be supplied for the input Parameters of the
    Behavior. If the Behavior is invoked synchronously, then output values may be
    obtained for output Parameters.
    """

    __package__ = 'UML.Actions'

    object_ = models.ForeignKey('InputPin', 
                                )

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior being called.
        """
        # OCL: "result = (self.behavior().inputParameters())"
        pass


class ActivityFinalNode(FinalNode):
    """
    An ActivityFinalNode is a FinalNode that terminates the execution of its owning
    Activity or StructuredActivityNode.
    """

    __package__ = 'UML.Activities'



class AggregationKind(models.Model):
    """
    AggregationKind is an Enumeration for specifying the kind of aggregation of a
    Property.
    """

    __package__ = 'UML.Classification'

    enumeration = models.OneToOneField('Enumeration')
    COMPOSITE = 'composite'
    SHARED = 'shared'
    NONE = 'none'
    CHOICES = (
        (COMPOSITE, 'Indicates that the Property is aggregated compositely, i.e., the ' +
                    'composite object has responsibility for the existence and storage of the ' +
                    'composed objects (parts).'),
        (SHARED, 'Indicates that the Property has shared aggregation.'),
        (NONE, 'Indicates that the Property has no aggregation.'),
    )

    aggregation_kind = models.CharField(max_length=255, choices=CHOICES, default=NONE)


class Profile(models.Model):
    """
    A profile defines limited extensions to a reference metamodel with the purpose
    of adapting the metamodel to a specific platform or domain.
    """

    __package__ = 'UML.Packages'

    package = models.OneToOneField('Package')
    metaclass_reference = models.ForeignKey('ElementImport', 
                                            )
    metamodel_reference = models.ForeignKey('PackageImport', 
                                            )


class DestroyLinkAction(WriteLinkAction):
    """
    A DestroyLinkAction is a WriteLinkAction that destroys links (including link
    objects).
    """

    __package__ = 'UML.Actions'


    def __init__(self, *args, **kwargs):
        super(DestroyLinkAction).__init__(*args, **kwargs)
