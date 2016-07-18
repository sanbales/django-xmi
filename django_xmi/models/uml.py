from django.db import models


class Element(models.Model):
    """
    An Element is a constituent of a model. As such, it has the capability of owning
    other Elements.
    """

    owned_comment = models.ForeignKey('Comment', help_text="The Comments owned by this Element.")
    owned_element = models.ForeignKey('self', help_text="The Elements owned by this Element.")
    owner = models.ForeignKey('self', help_text="The Element that owns this Element.")

    class Meta:
        abstract = True

    def all_owned_elements(self):
        """
        The query allOwnedElements() gives all of the direct and indirect ownedElements
        of an Element.
        """
        # OCL:
        #     result = (ownedElement->union(ownedElement->collect(e | e.allOwnedElements()))->asSet())
        pass


class NamedElement(Element):
    """
    A NamedElement is an Element in a model that may have a name. The name may be
    given directly and/or via the use of a StringExpression.
    """

    client_dependency = models.ForeignKey('Dependency', help_text="Indicates the Dependencies that reference this NamedElement as a client.")
    name = models.CharField(max_length=255, help_text="The name of the NamedElement.")
    name_expression = models.ForeignKey('StringExpression', help_text="The StringExpression used to define the name of this NamedElement.")
    namespace = models.ForeignKey('Namespace', help_text="Specifies the Namespace that owns the NamedElement.")
    qualified_name = models.CharField(max_length=255, help_text="A name that allows the NamedElement to be identified within a hierarchy of nested Namespaces. It is constructed from the names of the containing Namespaces starting at the root of the hierarchy and ending with the name of the NamedElement itself.")
    visibility = models.ForeignKey('VisibilityKind', help_text="Determines whether and how the NamedElement is visible outside its owning Namespace.")

    class Meta:
        abstract = True

    def all_namespaces(self):
        """
        The query allNamespaces() gives the sequence of Namespaces in which the
        NamedElement is nested, working outwards.
        """
        # OCL:
        """    result = (if owner.oclIsKindOf(TemplateParameter) and
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
            endif)"""
        pass


class RedefinableElement(NamedElement):
    """
    A RedefinableElement is an element that, when defined in the context of a
    Classifier, can be redefined more specifically or differently in the context of
    another Classifier that specializes (directly or indirectly) the context
    Classifier.
    """

    is_leaf = models.BooleanField(help_text="Indicates whether it is possible to further redefine a RedefinableElement. If the value is true, then it is not possible to further redefine the RedefinableElement.")
    redefined_element = models.ForeignKey('self', help_text="The RedefinableElement that is being redefined by this element.")
    redefinition_context = models.ForeignKey('Classifier', help_text="The contexts that this element may be redefined from.")

    class Meta:
        abstract = True

    def is_redefinition_context_valid(self):
        """
        The query isRedefinitionContextValid() specifies whether the redefinition
        contexts of this RedefinableElement are properly related to the redefinition
        contexts of the specified RedefinableElement to allow this element to redefine
        the other. By default at least one of the redefinition contexts of this element
        must be a specialization of at least one of the redefinition contexts of the
        specified element.
        """
        # OCL:
        #     result = (redefinitionContext->exists(c | c.allParents()->includesAll(redefinedElement.redefinitionContext)))
        pass


class ActivityNode(RedefinableElement):
    """
    ActivityNode is an abstract class for points in the flow of an Activity
    connected by ActivityEdges.
    """

    activity = models.ForeignKey('Activity', help_text="The Activity containing the ActivityNode, if it is directly owned by an Activity.")
    in_group = models.ForeignKey('ActivityGroup', help_text="ActivityGroups containing the ActivityNode.")
    in_interruptible_region = models.ForeignKey('InterruptibleActivityRegion', help_text="InterruptibleActivityRegions containing the ActivityNode.")
    in_partition = models.ForeignKey('ActivityPartition', help_text="ActivityPartitions containing the ActivityNode.")
    in_structured_node = models.ForeignKey('StructuredActivityNode', help_text="The StructuredActivityNode containing the ActvityNode, if it is directly owned by a StructuredActivityNode.")
    incoming = models.ForeignKey('ActivityEdge', help_text="ActivityEdges that have the ActivityNode as their target.")
    outgoing = models.ForeignKey('ActivityEdge', help_text="ActivityEdges that have the ActivityNode as their source.")
    redefined_node = models.ForeignKey('self', help_text="ActivityNodes from a generalization of the Activity containining this ActivityNode that are redefined by this ActivityNode.")

    class Meta:
        abstract = True

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityNode.
        """
        # OCL:
        """    result = (if inStructuredNode<>null then inStructuredNode.containingActivity()
            else activity
            endif)"""
        pass


class ControlNode(ActivityNode):
    """
    A ControlNode is an abstract ActivityNode that coordinates flows in an Activity.
    """


    class Meta:
        abstract = True


class MergeNode(ControlNode):
    """
    A merge node is a control node that brings together multiple alternate flows. It
    is not used to synchronize concurrent flows but to accept one among several
    alternate flows.
    """

    pass


class LinkEndData(Element):
    """
    LinkEndData is an Element that identifies on end of a link to be read or written
    by a LinkAction. As a link (that is not a link object) cannot be passed as a
    runtime value to or from an Action, it is instead identified by its end objects
    and qualifier values, if any. A LinkEndData instance provides these values for a
    single Association end.
    """

    end = models.ForeignKey('Property', help_text="The Association'end'for'which'this'LinkEndData'specifies'values.")
    qualifier = models.ForeignKey('QualifierValue', help_text="A set of QualifierValues used to provide values for the qualifiers of the end.")
    value = models.ForeignKey('InputPin', help_text="""The InputPin that provides the specified value for the given end. This InputPin is omitted if the LinkEndData specifies the "open" end for a ReadLinkAction.""")

    def all_pins(self):
        """
        Returns all the InputPins referenced by this LinkEndData. By default this
        includes the value and qualifier InputPins, but subclasses may override the
        operation to add other InputPins.
        """
        # OCL:
        #     result = (value->asBag()->union(qualifier.value))
        pass


class LinkEndDestructionData(LinkEndData):
    """
    LinkEndDestructionData is LinkEndData used to provide values for one end of a
    link to be destroyed by a DestroyLinkAction.
    """

    destroy_at = models.ForeignKey('InputPin', help_text="The InputPin that provides the position of an existing link to be destroyed in an ordered, nonunique Association end. The type of the destroyAt InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.")
    is_destroy_duplicates = models.BooleanField(help_text="Specifies whether to destroy duplicates of the value in nonunique Association ends.")

    def all_pins(self):
        """
        Adds the destroyAt InputPin (if any) to the set of all Pins.
        """
        # OCL:
        #     result = (self.LinkEndData::allPins()->including(destroyAt))
        pass


class TemplateParameter(Element):
    """
    A TemplateParameter exposes a ParameterableElement as a formal parameter of a
    template.
    """

    default = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement that is the default for this formal TemplateParameter.")
    owned_default = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement that is owned by this TemplateParameter for the purpose of providing a default.")
    owned_parametered_element = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement that is owned by this TemplateParameter for the purpose of exposing it as the parameteredElement.")
    parametered_element = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement exposed by this TemplateParameter.")
    signature = models.ForeignKey('TemplateSignature', help_text="The TemplateSignature that owns this TemplateParameter.")


class Namespace(NamedElement):
    """
    A Namespace is an Element in a model that owns and/or imports a set of
    NamedElements that can be identified by name.
    """

    element_import = models.ForeignKey('ElementImport', help_text="References the ElementImports owned by the Namespace.")
    imported_member = models.ForeignKey('PackageableElement', help_text="References the PackageableElements that are members of this Namespace as a result of either PackageImports or ElementImports.")
    member = models.ForeignKey('NamedElement', help_text="A collection of NamedElements identifiable within the Namespace, either by being owned or by being introduced by importing or inheritance.")
    owned_member = models.ForeignKey('NamedElement', help_text="A collection of NamedElements owned by the Namespace.")
    owned_rule = models.ForeignKey('Constraint', help_text="Specifies a set of Constraints owned by this Namespace.")
    package_import = models.ForeignKey('PackageImport', help_text="References the PackageImports owned by the Namespace.")

    class Meta:
        abstract = True

    def get_names_of_member(self):
        """
        The query getNamesOfMember() gives a set of all of the names that a member would
        have in a Namespace, taking importing into account. In general a member can have
        multiple names in a Namespace if it is imported more than once with different
        aliases.
        """
        # OCL:
        """    result = (if self.ownedMember ->includes(element)
            then Set{element.name}
            else let elementImports : Set(ElementImport) = self.elementImport->select(ei | ei.importedElement = element) in
              if elementImports->notEmpty()
              then
                 elementImports->collect(el | el.getName())->asSet()
              else 
                 self.packageImport->select(pi | pi.importedPackage.visibleMembers().oclAsType(NamedElement)->includes(element))-> collect(pi | pi.importedPackage.getNamesOfMember(element))->asSet()
              endif
            endif)"""
        pass


class TemplateableElement(Element):
    """
    A TemplateableElement is an Element that can optionally be defined as a template
    and bound to other templates.
    """

    owned_template_signature = models.ForeignKey('TemplateSignature', help_text="The optional TemplateSignature specifying the formal TemplateParameters for this TemplateableElement. If a TemplateableElement has a TemplateSignature, then it is a template.")
    template_binding = models.ForeignKey('TemplateBinding', help_text="The optional TemplateBindings from this TemplateableElement to one or more templates.")

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
        # OCL:
        #     result = (self.allOwnedElements()->select(oclIsKindOf(ParameterableElement)).oclAsType(ParameterableElement)->asSet())
        pass


class ParameterableElement(Element):
    """
    A ParameterableElement is an Element that can be exposed as a formal
    TemplateParameter for a template, or specified as an actual parameter in a
    binding of a template.
    """

    owning_template_parameter = models.ForeignKey('TemplateParameter', help_text="The formal TemplateParameter that owns this ParameterableElement.")
    template_parameter = models.ForeignKey('TemplateParameter', help_text="The TemplateParameter that exposes this ParameterableElement as a formal parameter.")

    class Meta:
        abstract = True

    def is_compatible_with(self):
        """
        The query isCompatibleWith() determines if this ParameterableElement is
        compatible with the specified ParameterableElement. By default, this
        ParameterableElement is compatible with another ParameterableElement p if the
        kind of this ParameterableElement is the same as or a subtype of the kind of p.
        Subclasses of ParameterableElement should override this operation to specify
        different compatibility constraints.
        """
        # OCL:
        #     result = (self.oclIsKindOf(p.oclType()))
        pass


class PackageableElement(ParameterableElement, NamedElement):
    """
    A PackageableElement is a NamedElement that may be owned directly by a Package.
    A PackageableElement is also able to serve as the parameteredElement of a
    TemplateParameter.
    """


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

    package = models.ForeignKey('Package')

    class Meta:
        abstract = True

    def conforms_to(self):
        """
        The query conformsTo() gives true for a Type that conforms to another. By
        default, two Types do not conform to each other. This query is intended to be
        redefined for specific conformance situations.
        """
        # OCL:
        #     result = (false)
        pass


class Classifier(Namespace, Type, TemplateableElement, RedefinableElement):
    """
    A Classifier represents a classification of instances according to their
    Features.
    """

    attribute = models.ForeignKey('Property', help_text="All of the Properties that are direct (i.e., not inherited or imported) attributes of the Classifier.")
    collaboration_use = models.ForeignKey('CollaborationUse', help_text="The CollaborationUses owned by the Classifier.")
    feature = models.ForeignKey('Feature', help_text="Specifies each Feature directly defined in the classifier. Note that there may be members of the Classifier that are of the type Feature but are not included, e.g., inherited features.")
    general = models.ForeignKey('self', help_text="The generalizing Classifiers for this Classifier.")
    generalization = models.ForeignKey('Generalization', help_text="The Generalization relationships for this Classifier. These Generalizations navigate to more general Classifiers in the generalization hierarchy.")
    inherited_member = models.ForeignKey('NamedElement', help_text="All elements inherited by this Classifier from its general Classifiers.")
    is_abstract = models.BooleanField(help_text="If true, the Classifier can only be instantiated by instantiating one of its specializations. An abstract Classifier is intended to be used by other Classifiers e.g., as the target of Associations or Generalizations.")
    is_final_specialization = models.BooleanField(help_text="If true, the Classifier cannot be specialized.")
    owned_use_case = models.ForeignKey('UseCase', help_text="The UseCases owned by this classifier.")
    powertype_extent = models.ForeignKey('GeneralizationSet', help_text="The GeneralizationSet of which this Classifier is a power type.")
    redefined_classifier = models.ForeignKey('self', help_text="The Classifiers redefined by this Classifier.")
    representation = models.ForeignKey('CollaborationUse', help_text="A CollaborationUse which indicates the Collaboration that represents this Classifier.")
    substitution = models.ForeignKey('Substitution', help_text="The Substitutions owned by this Classifier.")
    use_case = models.ForeignKey('UseCase', help_text="The set of UseCases for which this Classifier is the subject.")

    def __init__(self, *args, **kwargs):
        super(Classifier).__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def all_parents(self):
        """
        The query allParents() gives all of the direct and indirect ancestors of a
        generalized Classifier.
        """
        # OCL:
        #     result = (parents()->union(parents()->collect(allParents())->asSet()))
        pass


class DataType(Classifier):
    """
    A DataType is a type whose instances are identified only by their value.
    """

    owned_attribute = models.ForeignKey('Property', help_text="The attributes owned by the DataType.")
    owned_operation = models.ForeignKey('Operation', help_text="The Operations owned by the DataType.")


class DeploymentTarget(NamedElement):
    """
    A deployment target is the location for a deployed artifact.
    """

    deployed_element = models.ForeignKey('PackageableElement', help_text="The set of elements that are manifested in an Artifact that is involved in Deployment to a DeploymentTarget.")
    deployment = models.ForeignKey('Deployment', help_text="The set of Deployments for a DeploymentTarget.")

    class Meta:
        abstract = True

    def deployed_element_operation(self):
        """
        Derivation for DeploymentTarget::/deployedElement
        """
        # OCL:
        #     result = (deployment.deployedArtifact->select(oclIsKindOf(Artifact))->collect(oclAsType(Artifact).manifestation)->collect(utilizedElement)->asSet())
        pass


class StructuredClassifier(Classifier):
    """
    StructuredClassifiers may contain an internal structure of connected elements
    each of which plays a role in the overall Behavior modeled by the
    StructuredClassifier.
    """

    owned_attribute = models.ForeignKey('Property', help_text="The Properties owned by the StructuredClassifier.")
    owned_connector = models.ForeignKey('Connector', help_text="The connectors owned by the StructuredClassifier.")
    part = models.ForeignKey('Property', help_text="The Properties specifying instances that the StructuredClassifier owns by composition. This collection is derived, selecting those owned Properties where isComposite is true.")
    role = models.ForeignKey('ConnectableElement', help_text="The roles that instances may play in this StructuredClassifier.")

    class Meta:
        abstract = True

    def all_roles(self):
        """
        All features of type ConnectableElement, equivalent to all direct and inherited
        roles.
        """
        # OCL:
        #     result = (allFeatures()->select(oclIsKindOf(ConnectableElement))->collect(oclAsType(ConnectableElement))->asSet())
        pass


class EncapsulatedClassifier(StructuredClassifier):
    """
    An EncapsulatedClassifier may own Ports to specify typed interaction points.
    """

    owned_port = models.ForeignKey('Port')

    class Meta:
        abstract = True

    def owned_port_operation(self):
        """
        Derivation for EncapsulatedClassifier::/ownedPort : Port
        """
        # OCL:
        #     result = (ownedAttribute->select(oclIsKindOf(Port))->collect(oclAsType(Port))->asOrderedSet())
        pass


class BehavioredClassifier(Classifier):
    """
    A BehavioredClassifier may have InterfaceRealizations, and owns a set of
    Behaviors one of which may specify the behavior of the BehavioredClassifier
    itself.
    """

    classifier_behavior = models.ForeignKey('Behavior', help_text="A Behavior that specifies the behavior of the BehavioredClassifier itself.")
    interface_realization = models.ForeignKey('InterfaceRealization', help_text="The set of InterfaceRealizations owned by the BehavioredClassifier. Interface realizations reference the Interfaces of which the BehavioredClassifier is an implementation.")
    owned_behavior = models.ForeignKey('Behavior', help_text="Behaviors owned by a BehavioredClassifier.")

    class Meta:
        abstract = True


class Class(BehavioredClassifier, EncapsulatedClassifier):
    """
    A Class classifies a set of objects and specifies the features that characterize
    the structure and behavior of those objects.  A Class may have an internal
    structure and Ports.
    """

    extension = models.ForeignKey('Extension', help_text="This property is used when the Class is acting as a metaclass. It references the Extensions that specify additional properties of the metaclass. The property is derived from the Extensions whose memberEnds are typed by the Class.")
    is_active = models.BooleanField(help_text="Determines whether an object specified by this Class is active or not. If true, then the owning Class is referred to as an active Class. If false, then such a Class is referred to as a passive Class.")
    nested_classifier = models.ForeignKey('Classifier', help_text="The Classifiers owned by the Class that are not ownedBehaviors.")
    owned_operation = models.ForeignKey('Operation', help_text="The Operations owned by the Class.")
    owned_reception = models.ForeignKey('Reception', help_text="The Receptions owned by the Class.")

    def __init__(self, *args, **kwargs):
        super(Class).__init__(*args, **kwargs)

    def super_class_operation(self):
        """
        Derivation for Class::/superClass : Class
        """
        # OCL:
        #     result = (self.general()->select(oclIsKindOf(Class))->collect(oclAsType(Class))->asSet())
        pass


class Node(Class, DeploymentTarget):
    """
    A Node is computational resource upon which artifacts may be deployed for
    execution. Nodes can be interconnected through communication paths to define
    network structures.
    """

    nested_node = models.ForeignKey('self')


class MessageEnd(NamedElement):
    """
    MessageEnd is an abstract specialization of NamedElement that represents what
    can occur at the end of a Message.
    """

    message = models.ForeignKey('Message')

    class Meta:
        abstract = True

    def is_send(self):
        """
        This query returns value true if this MessageEnd is a sendEvent.
        """
        pass


class Gate(MessageEnd):
    """
    A Gate is a MessageEnd which serves as a connection point for relating a Message
    which has a MessageEnd (sendEvent / receiveEvent) outside an InteractionFragment
    with another Message which has a MessageEnd (receiveEvent / sendEvent)  inside
    that InteractionFragment.
    """


    def is_distinguishable_from(self):
        """
        The query isDistinguishableFrom() specifies that two Gates may coexist in the
        same Namespace, without an explicit name property. The association end
        formalGate subsets ownedElement, and since the Gate name attribute  is optional,
        it is allowed to have two formal gates without an explicit name, but having
        derived names which are distinct.
        """
        # OCL:
        #     result = (true)
        pass


class InteractionFragment(NamedElement):
    """
    InteractionFragment is an abstract notion of the most general interaction unit.
    An InteractionFragment is a piece of an Interaction. Each InteractionFragment is
    conceptually like an Interaction by itself.
    """

    covered = models.ForeignKey('Lifeline', help_text="References the Lifelines that the InteractionFragment involves.")
    enclosing_interaction = models.ForeignKey('Interaction', help_text="The Interaction enclosing this InteractionFragment.")
    enclosing_operand = models.ForeignKey('InteractionOperand', help_text="The operand enclosing this InteractionFragment (they may nest recursively).")
    general_ordering = models.ForeignKey('GeneralOrdering', help_text="The general ordering relationships contained in this fragment.")

    class Meta:
        abstract = True


class InteractionOperand(InteractionFragment, Namespace):
    """
    An InteractionOperand is contained in a CombinedFragment. An InteractionOperand
    represents one operand of the expression given by the enclosing
    CombinedFragment.
    """

    fragment = models.ForeignKey('InteractionFragment', help_text="The fragments of the operand.")
    guard = models.ForeignKey('InteractionConstraint', help_text="Constraint of the operand.")


class Behavior(Class):
    """
    Behavior is a specification of how its context BehavioredClassifier changes
    state over time. This specification may be either a definition of possible
    behavior execution or emergent behavior, or a selective illustration of an
    interesting subset of possible executions. The latter form is typically used for
    capturing examples, such as a trace of a particular execution.
    """

    context = models.ForeignKey('BehavioredClassifier', help_text="The BehavioredClassifier that is the context for the execution of the Behavior. A Behavior that is directly owned as a nestedClassifier does not have a context. Otherwise, to determine the context of a Behavior, find the first BehavioredClassifier reached by following the chain of owner relationships from the Behavior, if any. If there is such a BehavioredClassifier, then it is the context, unless it is itself a Behavior with a non-empty context, in which case that is also the context for the original Behavior. For example, following this algorithm, the context of an entry Behavior in a StateMachine is the BehavioredClassifier that owns the StateMachine. The features of the context BehavioredClassifier as well as the Elements visible to the context Classifier are visible to the Behavior.")
    is_reentrant = models.BooleanField(help_text="Tells whether the Behavior can be invoked while it is still executing from a previous invocation.")
    owned_parameter = models.ForeignKey('Parameter', help_text="References a list of Parameters to the Behavior which describes the order and type of arguments that can be given when the Behavior is invoked and of the values which will be returned when the Behavior completes its execution.")
    owned_parameter_set = models.ForeignKey('ParameterSet', help_text="The ParameterSets owned by this Behavior.")
    postcondition = models.ForeignKey('Constraint', help_text="An optional set of Constraints specifying what is fulfilled after the execution of the Behavior is completed, if its precondition was fulfilled before its invocation.")
    precondition = models.ForeignKey('Constraint', help_text="An optional set of Constraints specifying what must be fulfilled before the Behavior is invoked.")
    redefined_behavior = models.ForeignKey('self', help_text="References the Behavior that this Behavior redefines. A subtype of Behavior may redefine any other subtype of Behavior. If the Behavior implements a BehavioralFeature, it replaces the redefined Behavior. If the Behavior is a classifierBehavior, it extends the redefined Behavior.")
    specification = models.ForeignKey('BehavioralFeature', help_text="Designates a BehavioralFeature that the Behavior implements. The BehavioralFeature must be owned by the BehavioredClassifier that owns the Behavior or be inherited by it. The Parameters of the BehavioralFeature and the implementing Behavior must match. A Behavior does not need to have a specification, in which case it either is the classifierBehavior of a BehavioredClassifier or it can only be invoked by another Behavior of the Classifier.")

    class Meta:
        abstract = True

    def behaviored_classifier(self):
        """
        The first BehavioredClassifier reached by following the chain of owner
        relationships from the Behavior, if any.
        """
        # OCL:
        """    if from.oclIsKindOf(BehavioredClassifier) then
                from.oclAsType(BehavioredClassifier)
            else if from.owner = null then
                null
            else
                self.behavioredClassifier(from.owner)
            endif
            endif"""
        pass


class OpaqueBehavior(Behavior):
    """
    An OpaqueBehavior is a Behavior whose specification is given in a textual
    language other than UML.
    """

    body = models.CharField(max_length=255, help_text="Specifies the behavior in one or more languages.")
    language = models.CharField(max_length=255, help_text="Languages the body strings use in the same order as the body strings.")


class Stereotype(Class):
    """
    A stereotype defines how an existing metaclass may be extended, and enables the
    use of platform or domain specific terminology or notation in place of, or in
    addition to, the ones used for the extended metaclass.
    """

    icon = models.ForeignKey('Image', help_text="Stereotype can change the graphical appearance of the extended model element by using attached icons. When this association is not null, it references the location of the icon content to be displayed within diagrams presenting the extended model elements.")
    profile = models.ForeignKey('Profile', help_text="The profile that directly or indirectly contains this stereotype.")

    def profile_operation(self):
        """
        A stereotype must be contained, directly or indirectly, in a profile.
        """
        # OCL:
        #     result = (self.containingProfile())
        pass


class ExecutableNode(ActivityNode):
    """
    An ExecutableNode is an abstract class for ActivityNodes whose execution may be
    controlled using ControlFlows and to which ExceptionHandlers may be attached.
    """

    handler = models.ForeignKey('ExceptionHandler')

    class Meta:
        abstract = True


class Action(ExecutableNode):
    """
    An Action is the fundamental unit of executable functionality. The execution of
    an Action represents some transformation or processing in the modeled system.
    Actions provide the ExecutableNodes within Activities and may also be used
    within Interactions.
    """

    context = models.ForeignKey('Classifier', help_text="The context Classifier of the Behavior that contains this Action, or the Behavior itself if it has no context.")
    input_ = models.ForeignKey('InputPin', help_text="The ordered set of InputPins representing the inputs to the Action.")
    is_locally_reentrant = models.BooleanField(help_text="If true, the Action can begin a new, concurrent execution, even if there is already another execution of the Action ongoing. If false, the Action cannot begin a new execution until any previous execution has completed.")
    local_postcondition = models.ForeignKey('Constraint', help_text="A Constraint that must be satisfied when execution of the Action is completed.")
    local_precondition = models.ForeignKey('Constraint', help_text="A Constraint that must be satisfied when execution of the Action is started.")
    output = models.ForeignKey('OutputPin', help_text="The ordered set of OutputPins representing outputs from the Action.")

    class Meta:
        abstract = True

    def all_actions(self):
        """
        Return this Action and all Actions contained directly or indirectly in it. By
        default only the Action itself is returned, but the operation is overridden for
        StructuredActivityNodes.
        """
        # OCL:
        #     result = (self->asSet())
        pass


class AcceptEventAction(Action):
    """
    An AcceptEventAction is an Action that waits for the occurrence of one or more
    specific Events.
    """

    is_unmarshall = models.BooleanField(help_text="Indicates whether there is a single OutputPin for a SignalEvent occurrence, or multiple OutputPins for attribute values of the instance of the Signal associated with a SignalEvent occurrence.")
    result = models.ForeignKey('OutputPin', help_text="OutputPins holding the values received from an Event occurrence.")
    trigger = models.ForeignKey('Trigger', help_text="The Triggers specifying the Events of which the AcceptEventAction waits for occurrences.")


class AcceptCallAction(AcceptEventAction):
    """
    An AcceptCallAction is an AcceptEventAction that handles the receipt of a
    synchronous call request. In addition to the values from the Operation input
    parameters, the Action produces an output that is needed later to supply the
    information to the ReplyAction necessary to return control to the caller. An
    AcceptCallAction is for synchronous calls. If it is used to handle an
    asynchronous call, execution of the subsequent ReplyAction will complete
    immediately with no effect.
    """

    return_information = models.ForeignKey('OutputPin')


class Enumeration(DataType):
    """
    An Enumeration is a DataType whose values are enumerated in the model as
    EnumerationLiterals.
    """

    owned_literal = models.ForeignKey('EnumerationLiteral')


class MessageKind(Enumeration):
    """
    This is an enumerated type that identifies the type of Message.
    """

    FOUND = 'found'
    LOST = 'lost'
    COMPLETE = 'complete'
    UNKNOWN = 'unknown'
    CHOICES = (
        (FOUND, 'sendEvent absent and receiveEvent present'),
        (LOST, 'sendEvent present and receiveEvent absent'),
        (COMPLETE, 'sendEvent and receiveEvent are present'),
        (UNKNOWN, 'sendEvent and receiveEvent absent (should not appear)'),
    )

    message_kind = models.CharField(max_length=255, choices=CHOICES, default=UNKNOWN)


class Event(PackageableElement):
    """
    An Event is the specification of some occurrence that may potentially trigger
    effects by an object.
    """


    class Meta:
        abstract = True


class GeneralOrdering(NamedElement):
    """
    A GeneralOrdering represents a binary relation between two
    OccurrenceSpecifications, to describe that one OccurrenceSpecification must
    occur before the other in a valid trace. This mechanism provides the ability to
    define partial orders of OccurrenceSpecifications that may otherwise not have a
    specified order.
    """

    after = models.ForeignKey('OccurrenceSpecification', help_text="The OccurrenceSpecification referenced comes after the OccurrenceSpecification referenced by before.")
    before = models.ForeignKey('OccurrenceSpecification', help_text="The OccurrenceSpecification referenced comes before the OccurrenceSpecification referenced by after.")


class LinkAction(Action):
    """
    LinkAction is an abstract class for all Actions that identify the links to be
    acted on using LinkEndData.
    """

    end_data = models.ForeignKey('LinkEndData', help_text="The LinkEndData identifying the values on the ends of the links acting on by this LinkAction.")
    input_value = models.ForeignKey('InputPin', help_text="InputPins used by the LinkEndData of the LinkAction.")

    class Meta:
        abstract = True

    def association(self):
        """
        Returns the Association acted on by this LinkAction.
        """
        # OCL:
        #     result = (endData->asSequence()->first().end.association)
        pass


class WriteLinkAction(LinkAction):
    """
    WriteLinkAction is an abstract class for LinkActions that create and destroy
    links.
    """


    class Meta:
        abstract = True


class DestroyLinkAction(WriteLinkAction):
    """
    A DestroyLinkAction is a WriteLinkAction that destroys links (including link
    objects).
    """


    def __init__(self, *args, **kwargs):
        super(DestroyLinkAction).__init__(*args, **kwargs)
    pass


class InvocationAction(Action):
    """
    InvocationAction is an abstract class for the various actions that request
    Behavior invocation.
    """

    argument = models.ForeignKey('InputPin', help_text="The InputPins that provide the argument values passed in the invocation request.")
    on_port = models.ForeignKey('Port', help_text="For CallOperationActions, SendSignalActions, and SendObjectActions, an optional Port of the target object through which the invocation request is sent.")

    class Meta:
        abstract = True


class FinalNode(ControlNode):
    """
    A FinalNode is an abstract ControlNode at which a flow in an Activity stops.
    """


    class Meta:
        abstract = True


class TypedElement(NamedElement):
    """
    A TypedElement is a NamedElement that may have a Type specified for it.
    """

    type_ = models.ForeignKey('Type')

    class Meta:
        abstract = True


class ValueSpecification(TypedElement, PackageableElement):
    """
    A ValueSpecification is the specification of a (possibly empty) set of values. A
    ValueSpecification is a ParameterableElement that may be exposed as a formal
    TemplateParameter and provided as the actual parameter in the binding of a
    template.
    """


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
        # OCL:
        #     result = (false)
        pass


class Expression(ValueSpecification):
    """
    An Expression represents a node in an expression tree, which may be non-terminal
    or terminal. It defines a symbol, and has a possibly empty sequence of operands
    that are ValueSpecifications. It denotes a (possibly empty) set of values when
    evaluated in a context.
    """

    operand = models.ForeignKey('ValueSpecification', help_text="Specifies a sequence of operand ValueSpecifications.")
    symbol = models.CharField(max_length=255, help_text="The symbol associated with this node in the expression tree.")


class StringExpression(TemplateableElement, Expression):
    """
    A StringExpression is an Expression that specifies a String value that is
    derived by concatenating a sequence of operands with String values or a sequence
    of subExpressions, some of which might be template parameters.
    """

    owning_expression = models.ForeignKey('self', help_text="The StringExpression of which this StringExpression is a subExpression.")
    sub_expression = models.ForeignKey('self', help_text="The StringExpressions that constitute this StringExpression.")

    def string_value(self):
        """
        The query stringValue() returns the String resulting from concatenating, in
        order, all the component String values of all the operands or subExpressions
        that are part of the StringExpression.
        """
        # OCL:
        """    result = (if subExpression->notEmpty()
            then subExpression->iterate(se; stringValue: String = '' | stringValue.concat(se.stringValue()))
            else operand->iterate(op; stringValue: String = '' | stringValue.concat(op.stringValue()))
            endif)"""
        pass


class Relationship(Element):
    """
    Relationship is an abstract concept that specifies some kind of relationship
    between Elements.
    """

    related_element = models.ForeignKey('Element')

    class Meta:
        abstract = True


class DirectedRelationship(Relationship):
    """
    A DirectedRelationship represents a relationship between a collection of source
    model Elements and a collection of target model Elements.
    """

    source = models.ForeignKey('Element', help_text="Specifies the source Element(s) of the DirectedRelationship.")
    target = models.ForeignKey('Element', help_text="Specifies the target Element(s) of the DirectedRelationship.")

    class Meta:
        abstract = True


class TemplateBinding(DirectedRelationship):
    """
    A TemplateBinding is a DirectedRelationship between a TemplateableElement and a
    template. A TemplateBinding specifies the TemplateParameterSubstitutions of
    actual parameters for the formal parameters of the template.
    """

    bound_element = models.ForeignKey('TemplateableElement', help_text="The TemplateableElement that is bound by this TemplateBinding.")
    parameter_substitution = models.ForeignKey('TemplateParameterSubstitution', help_text="The TemplateParameterSubstitutions owned by this TemplateBinding.")
    signature = models.ForeignKey('TemplateSignature', help_text="The TemplateSignature for the template that is the target of this TemplateBinding.")


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

    uri = models.CharField(max_length=255, help_text="Provides an identifier for the package that can be used for many purposes. A URI is the universally unique identification of the package following the IETF URI specification, RFC 2396 http://www.ietf.org/rfc/rfc2396.txt and it must comply with those syntax rules.")
    nested_package = models.ForeignKey('self', help_text="References the packaged elements that are Packages.")
    nesting_package = models.ForeignKey('self', help_text="References the Package that owns this Package.")
    owned_stereotype = models.ForeignKey('Stereotype', help_text="References the Stereotypes that are owned by the Package.")
    owned_type = models.ForeignKey('Type', help_text="References the packaged elements that are Types.")
    package_merge = models.ForeignKey('PackageMerge', help_text="References the PackageMerges that are owned by this Package.")
    packaged_element = models.ForeignKey('PackageableElement', help_text="Specifies the packageable elements that are owned by this Package.")
    profile_application = models.ForeignKey('ProfileApplication', help_text="References the ProfileApplications that indicate which profiles have been applied to the Package.")

    def containing_profile(self):
        """
        The query containingProfile() returns the closest profile directly or indirectly
        containing this package (or this package itself, if it is a profile).
        """
        # OCL:
        """    result = (if self.oclIsKindOf(Profile) then 
            	self.oclAsType(Profile)
            else
            	self.namespace.oclAsType(Package).containingProfile()
            endif)"""
        pass


class Model(Package):
    """
    A model captures a view of a physical system. It is an abstraction of the
    physical system, with a certain purpose. This purpose determines what is to be
    included in the model and what is irrelevant. Thus the model completely
    describes those aspects of the physical system that are relevant to the purpose
    of the model, at the appropriate level of detail.
    """

    viewpoint = models.CharField(max_length=255)


class SendSignalAction(InvocationAction):
    """
    A SendSignalAction is an InvocationAction that creates a Signal instance and
    transmits it to the target object. Values from the argument InputPins are used
    to provide values for the attributes of the Signal. The requestor continues
    execution immediately after the Signal instance is sent out and cannot receive
    reply values.
    """

    signal = models.ForeignKey('Signal', help_text="The Signal whose instance is transmitted to the target.")
    target = models.ForeignKey('InputPin', help_text="The InputPin that provides the target object to which the Signal instance is sent.")


class Constraint(PackageableElement):
    """
    A Constraint is a condition or restriction expressed in natural language text or
    in a machine readable language for the purpose of declaring some of the
    semantics of an Element or set of Elements.
    """

    constrained_element = models.ForeignKey('Element', help_text="The ordered set of Elements referenced by this Constraint.")
    context = models.ForeignKey('Namespace', help_text="Specifies the Namespace that owns the Constraint.")
    specification = models.ForeignKey('ValueSpecification', help_text="A condition that must be true when evaluated in order for the Constraint to be satisfied.")


class IntervalConstraint(Constraint):
    """
    An IntervalConstraint is a Constraint that is specified by an Interval.
    """


    def __init__(self, *args, **kwargs):
        super(IntervalConstraint).__init__(*args, **kwargs)
    pass


class DurationConstraint(IntervalConstraint):
    """
    A DurationConstraint is a Constraint that refers to a DurationInterval.
    """

    first_event = models.BooleanField(help_text="The value of firstEvent[i] is related to constrainedElement[i] (where i is 1 or 2). If firstEvent[i] is true, then the corresponding observation event is the first time instant the execution enters constrainedElement[i]. If firstEvent[i] is false, then the corresponding observation event is the last time instant the execution is within constrainedElement[i].")

    def __init__(self, *args, **kwargs):
        super(DurationConstraint).__init__(*args, **kwargs)


class ParameterEffectKind(Enumeration):
    """
    ParameterEffectKind is an Enumeration that indicates the effect of a Behavior on
    values passed in or out of its parameters.
    """

    CREATE = 'create'
    DELETE = 'delete'
    READ = 'read'
    UPDATE = 'update'
    CHOICES = (
        (CREATE, 'Indicates that the behavior creates values.'),
        (DELETE, 'Indicates objects that are values of the parameter do not exist after executions of the behavior are finished.'),
        (READ, 'Indicates objects that are values of the parameter have values of their properties, or links in which they participate, or their classifiers retrieved during executions of the behavior.'),
        (UPDATE, 'Indicates objects that are values of the parameter have values of their properties, or links in which they participate, or their classification changed during executions of the behavior.'),
    )

    parameter_effect_kind = models.CharField(max_length=255, choices=CHOICES, default=UPDATE)


class ObjectNode(TypedElement, ActivityNode):
    """
    An ObjectNode is an abstract ActivityNode that may hold tokens within the object
    flow in an Activity. ObjectNodes also support token selection, limitation on the
    number of tokens held, specification of the state required for tokens being
    held, and carrying control values.
    """

    in_state = models.ForeignKey('State', help_text="The States required to be associated with the values held by tokens on this ObjectNode.")
    is_control_type = models.BooleanField(help_text="Indicates whether the type of the ObjectNode is to be treated as representing control values that may traverse ControlFlows.")
    ordering = models.ForeignKey('ObjectNodeOrderingKind', help_text="Indicates how the tokens held by the ObjectNode are ordered for selection to traverse ActivityEdges outgoing from the ObjectNode.")
    selection = models.ForeignKey('Behavior', help_text="A Behavior used to select tokens to be offered on outgoing ActivityEdges.")
    upper_bound = models.ForeignKey('ValueSpecification', help_text="The maximum number of tokens that may be held by this ObjectNode. Tokens cannot flow into the ObjectNode if the upperBound is reached. If no upperBound is specified, then there is no limit on how many tokens the ObjectNode can hold.")

    class Meta:
        abstract = True


class MultiplicityElement(Element):
    """
    A multiplicity is a definition of an inclusive interval of non-negative integers
    beginning with a lower bound and ending with a (possibly infinite) upper bound.
    A MultiplicityElement embeds this information to specify the allowable
    cardinalities for an instantiation of the Element.
    """

    is_ordered = models.BooleanField(help_text="For a multivalued multiplicity, this attribute specifies whether the values in an instantiation of this MultiplicityElement are sequentially ordered.")
    is_unique = models.BooleanField(help_text="For a multivalued multiplicity, this attributes specifies whether the values in an instantiation of this MultiplicityElement are unique.")
    lower = models.ForeignKey('Integer', help_text="The lower bound of the multiplicity interval.")
    lower_value = models.ForeignKey('ValueSpecification', help_text="The specification of the lower bound for this multiplicity.")
    upper = models.ForeignKey('UnlimitedNatural', help_text="The upper bound of the multiplicity interval.")
    upper_value = models.ForeignKey('ValueSpecification', help_text="The specification of the upper bound for this multiplicity.")

    class Meta:
        abstract = True

    def is_multivalued(self):
        """
        The query isMultivalued() checks whether this multiplicity has an upper bound
        greater than one.
        """
        pass


class Pin(ObjectNode, MultiplicityElement):
    """
    A Pin is an ObjectNode and MultiplicityElement that provides input values to an
    Action or accepts output values from an Action.
    """

    is_control = models.BooleanField()

    class Meta:
        abstract = True


class OccurrenceSpecification(InteractionFragment):
    """
    An OccurrenceSpecification is the basic semantic unit of Interactions. The
    sequences of occurrences specified by them are the meanings of Interactions.
    """

    to_after = models.ForeignKey('GeneralOrdering', help_text="References the GeneralOrderings that specify EventOcurrences that must occur after this OccurrenceSpecification.")
    to_before = models.ForeignKey('GeneralOrdering', help_text="References the GeneralOrderings that specify EventOcurrences that must occur before this OccurrenceSpecification.")

    def __init__(self, *args, **kwargs):
        super(OccurrenceSpecification).__init__(*args, **kwargs)


class MessageOccurrenceSpecification(MessageEnd, OccurrenceSpecification):
    """
    A MessageOccurrenceSpecification specifies the occurrence of Message events,
    such as sending and receiving of Signals or invoking or receiving of Operation
    calls. A MessageOccurrenceSpecification is a kind of MessageEnd. Messages are
    generated either by synchronous Operation calls or asynchronous Signal sends.
    They are received by the execution of corresponding AcceptEventActions.
    """

    pass


class StructuralFeatureAction(Action):
    """
    StructuralFeatureAction is an abstract class for all Actions that operate on
    StructuralFeatures.
    """

    object_ = models.ForeignKey('InputPin', help_text="The InputPin from which the object whose StructuralFeature is to be read or written is obtained.")
    structural_feature = models.ForeignKey('StructuralFeature', help_text="The StructuralFeature to be read or written.")

    class Meta:
        abstract = True


class ClearStructuralFeatureAction(StructuralFeatureAction):
    """
    A ClearStructuralFeatureAction is a StructuralFeatureAction that removes all
    values of a StructuralFeature.
    """

    result = models.ForeignKey('OutputPin')


class ActivityGroup(NamedElement):
    """
    ActivityGroup is an abstract class for defining sets of ActivityNodes and
    ActivityEdges in an Activity.
    """

    contained_edge = models.ForeignKey('ActivityEdge', help_text="ActivityEdges immediately contained in the ActivityGroup.")
    contained_node = models.ForeignKey('ActivityNode', help_text="ActivityNodes immediately contained in the ActivityGroup.")
    in_activity = models.ForeignKey('Activity', help_text="The Activity containing the ActivityGroup, if it is directly owned by an Activity.")
    subgroup = models.ForeignKey('self', help_text="Other ActivityGroups immediately contained in this ActivityGroup.")
    super_group = models.ForeignKey('self', help_text="The ActivityGroup immediately containing this ActivityGroup, if it is directly owned by another ActivityGroup.")

    class Meta:
        abstract = True

    def containing_activity(self):
        """
        The Activity that directly or indirectly contains this ActivityGroup.
        """
        # OCL:
        """    result = (if superGroup<>null then superGroup.containingActivity()
            else inActivity
            endif)"""
        pass


class InterruptibleActivityRegion(ActivityGroup):
    """
    An InterruptibleActivityRegion is an ActivityGroup that supports the termination
    of tokens flowing in the portions of an activity within it.
    """

    interrupting_edge = models.ForeignKey('ActivityEdge', help_text="The ActivityEdges leaving the InterruptibleActivityRegion on which a traversing token will result in the termination of other tokens flowing in the InterruptibleActivityRegion.")
    node = models.ForeignKey('ActivityNode', help_text="ActivityNodes immediately contained in the InterruptibleActivityRegion.")


class TimeConstraint(IntervalConstraint):
    """
    A TimeConstraint is a Constraint that refers to a TimeInterval.
    """

    first_event = models.BooleanField(help_text="The value of firstEvent is related to the constrainedElement. If firstEvent is true, then the corresponding observation event is the first time instant the execution enters the constrainedElement. If firstEvent is false, then the corresponding observation event is the last time instant the execution is within the constrainedElement.")

    def __init__(self, *args, **kwargs):
        super(TimeConstraint).__init__(*args, **kwargs)


class Dependency(DirectedRelationship, PackageableElement):
    """
    A Dependency is a Relationship that signifies that a single model Element or a
    set of model Elements requires other model Elements for their specification or
    implementation. This means that the complete semantics of the client Element(s)
    are either semantically or structurally dependent on the definition of the
    supplier Element(s).
    """

    client = models.ForeignKey('NamedElement', help_text="The Element(s) dependent on the supplier Element(s). In some cases (such as a trace Abstraction) the assignment of direction (that is, the designation of the client Element) is at the discretion of the modeler and is a stipulation.")
    supplier = models.ForeignKey('NamedElement', help_text="The Element(s) on which the client Element(s) depend in some respect. The modeler may stipulate a sense of Dependency direction suitable for their domain.")


class Abstraction(Dependency):
    """
    An Abstraction is a Relationship that relates two Elements or sets of Elements
    that represent the same concept at different levels of abstraction or from
    different viewpoints.
    """

    mapping = models.ForeignKey('OpaqueExpression')


class Manifestation(Abstraction):
    """
    A manifestation is the concrete physical rendering of one or more model elements
    by an artifact.
    """

    utilized_element = models.ForeignKey('PackageableElement')


class CallAction(InvocationAction):
    """
    CallAction is an abstract class for Actions that invoke a Behavior with given
    argument values and (if the invocation is synchronous) receive reply values.
    """

    is_synchronous = models.BooleanField(help_text="If true, the call is synchronous and the caller waits for completion of the invoked Behavior. If false, the call is asynchronous and the caller proceeds immediately and cannot receive return values.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPins on which the reply values from the invocation are placed (if the call is synchronous).")

    class Meta:
        abstract = True

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior or Operation being
        called. (This operation is abstract and should be overridden by subclasses of
        CallAction.)
        """
        pass


class DeployedArtifact(NamedElement):
    """
    A deployed artifact is an artifact or artifact instance that has been deployed
    to a deployment target.
    """


    class Meta:
        abstract = True


class StateMachine(Behavior):
    """
    StateMachines can be used to express event-driven behaviors of parts of a
    system. Behavior is modeled as a traversal of a graph of Vertices interconnected
    by one or more joined Transition arcs that are triggered by the dispatching of
    successive Event occurrences. During this traversal, the StateMachine may
    execute a sequence of Behaviors associated with various elements of the
    StateMachine.
    """

    connection_point = models.ForeignKey('Pseudostate', help_text="The connection points defined for this StateMachine. They represent the interface of the StateMachine when used as part of submachine State")
    region = models.ForeignKey('Region', help_text="The Regions owned directly by the StateMachine.")
    submachine_state = models.ForeignKey('State', help_text="References the submachine(s) in case of a submachine State. Multiple machines are referenced in case of a concurrent State.")

    def __init__(self, *args, **kwargs):
        super(StateMachine).__init__(*args, **kwargs)

    def ancestor(self):
        """
        The query ancestor(s1, s2) checks whether Vertex s2 is an ancestor of Vertex s1.
        """
        # OCL:
        """    result = (if (s2 = s1) then 
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
            endif  )"""
        pass


class ProtocolStateMachine(StateMachine):
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

    conformance = models.ForeignKey('ProtocolConformance')


class ReclassifyObjectAction(Action):
    """
    A ReclassifyObjectAction is an Action that changes the Classifiers that classify
    an object.
    """

    is_replace_all = models.BooleanField(help_text="Specifies whether existing Classifiers should be removed before adding the new Classifiers.")
    new_classifier = models.ForeignKey('Classifier', help_text="A set of Classifiers to be added to the Classifiers of the given object.")
    object_ = models.ForeignKey('InputPin', help_text="The InputPin that holds the object to be reclassified.")
    old_classifier = models.ForeignKey('Classifier', help_text="A set of Classifiers to be removed from the Classifiers of the given object.")


class RaiseExceptionAction(Action):
    """
    A RaiseExceptionAction is an Action that causes an exception to occur. The input
    value becomes the exception object.
    """

    exception = models.ForeignKey('InputPin')


class TestIdentityAction(Action):
    """
    A TestIdentityAction is an Action that tests if two values are identical
    objects.
    """

    first = models.ForeignKey('InputPin', help_text="The InputPin on which the first input object is placed.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin whose Boolean value indicates whether the two input objects are identical.")
    second = models.ForeignKey('InputPin', help_text="The OutputPin on which the second input object is placed.")


class MessageEvent(Event):
    """
    A MessageEvent specifies the receipt by an object of either an Operation call or
    a Signal instance.
    """


    class Meta:
        abstract = True


class Feature(RedefinableElement):
    """
    A Feature declares a behavioral or structural characteristic of Classifiers.
    """

    featuring_classifier = models.ForeignKey('Classifier', help_text="The Classifiers that have this Feature as a feature.")
    is_static = models.BooleanField(help_text="Specifies whether this Feature characterizes individual instances classified by the Classifier (false) or the Classifier itself (true).")

    class Meta:
        abstract = True


class BehavioralFeature(Feature, Namespace):
    """
    A BehavioralFeature is a feature of a Classifier that specifies an aspect of the
    behavior of its instances.  A BehavioralFeature is implemented (realized) by a
    Behavior. A BehavioralFeature specifies that a Classifier will respond to a
    designated request by invoking its implementing method.
    """

    concurrency = models.ForeignKey('CallConcurrencyKind', help_text="Specifies the semantics of concurrent calls to the same passive instance (i.e., an instance originating from a Class with isActive being false). Active instances control access to their own BehavioralFeatures.")
    is_abstract = models.BooleanField(help_text="If true, then the BehavioralFeature does not have an implementation, and one must be supplied by a more specific Classifier. If false, the BehavioralFeature must have an implementation in the Classifier or one must be inherited.")
    method = models.ForeignKey('Behavior', help_text="A Behavior that implements the BehavioralFeature. There may be at most one Behavior for a particular pairing of a Classifier (as owner of the Behavior) and a BehavioralFeature (as specification of the Behavior).")
    owned_parameter = models.ForeignKey('Parameter', help_text="The ordered set of formal Parameters of this BehavioralFeature.")
    owned_parameter_set = models.ForeignKey('ParameterSet', help_text="The ParameterSets owned by this BehavioralFeature.")
    raised_exception = models.ForeignKey('Type', help_text="The Types representing exceptions that may be raised during an invocation of this BehavioralFeature.")

    class Meta:
        abstract = True

    def input_parameters(self):
        """
        The ownedParameters with direction in and inout.
        """
        # OCL:
        #     result = (ownedParameter->select(direction=ParameterDirectionKind::_'in' or direction=ParameterDirectionKind::inout))
        pass


class Reception(BehavioralFeature):
    """
    A Reception is a declaration stating that a Classifier is prepared to react to
    the receipt of a Signal.
    """

    signal = models.ForeignKey('Signal')


class CreateObjectAction(Action):
    """
    A CreateObjectAction is an Action that creates an instance of the specified
    Classifier.
    """

    classifier = models.ForeignKey('Classifier', help_text="The Classifier to be instantiated.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin on which the newly created object is placed.")


class TemplateParameterSubstitution(Element):
    """
    A TemplateParameterSubstitution relates the actual parameter to a formal
    TemplateParameter as part of a template binding.
    """

    actual = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement that is the actual parameter for this TemplateParameterSubstitution.")
    formal = models.ForeignKey('TemplateParameter', help_text="The formal TemplateParameter that is associated with this TemplateParameterSubstitution.")
    owned_actual = models.ForeignKey('ParameterableElement', help_text="The ParameterableElement that is owned by this TemplateParameterSubstitution as its actual parameter.")
    template_binding = models.ForeignKey('TemplateBinding', help_text="The TemplateBinding that owns this TemplateParameterSubstitution.")


class ConnectableElement(TypedElement, ParameterableElement):
    """
    ConnectableElement is an abstract metaclass representing a set of instances that
    play roles of a StructuredClassifier. ConnectableElements may be joined by
    attached Connectors and specify configurations of linked instances to be created
    within an instance of the containing StructuredClassifier.
    """

    end = models.ForeignKey('ConnectorEnd', help_text="A set of ConnectorEnds that attach to this ConnectableElement.")

    def __init__(self, *args, **kwargs):
        super(ConnectableElement).__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def end_operation(self):
        """
        Derivation for ConnectableElement::/end : ConnectorEnd
        """
        # OCL:
        #     result = (ConnectorEnd.allInstances()->select(role = self))
        pass


class StructuralFeature(MultiplicityElement, TypedElement, Feature):
    """
    A StructuralFeature is a typed feature of a Classifier that specifies the
    structure of instances of the Classifier.
    """

    is_read_only = models.BooleanField()

    class Meta:
        abstract = True


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

    aggregation = models.ForeignKey('AggregationKind', help_text="Specifies the kind of aggregation that applies to the Property.")
    association = models.ForeignKey('Association', help_text="The Association of which this Property is a member, if any.")
    association_end = models.ForeignKey('self', help_text="Designates the optional association end that owns a qualifier attribute.")
    class_ = models.ForeignKey('Class', help_text="The Class that owns this Property, if any.")
    datatype = models.ForeignKey('DataType', help_text="The DataType that owns this Property, if any.")
    default_value = models.ForeignKey('ValueSpecification', help_text="A ValueSpecification that is evaluated to give a default value for the Property when an instance of the owning Classifier is instantiated.")
    interface = models.ForeignKey('Interface', help_text="The Interface that owns this Property, if any.")
    is_composite = models.BooleanField(help_text="If isComposite is true, the object containing the attribute is a container for the object or value contained in the attribute. This is a derived value, indicating whether the aggregation of the Property is composite or not.")
    is_derived = models.BooleanField(help_text="Specifies whether the Property is derived, i.e., whether its value or values can be computed from other information.")
    is_derived_union = models.BooleanField(help_text="Specifies whether the property is derived as the union of all of the Properties that are constrained to subset it.")
    is_id = models.BooleanField(help_text="True indicates this property can be used to uniquely identify an instance of the containing Class.")
    opposite = models.ForeignKey('self', help_text="In the case where the Property is one end of a binary association this gives the other end.")
    owning_association = models.ForeignKey('Association', help_text="The owning association of this property, if any.")
    qualifier = models.ForeignKey('self', help_text="An optional list of ordered qualifier attributes for the end.")
    redefined_property = models.ForeignKey('self', help_text="The properties that are redefined by this property, if any.")
    subsetted_property = models.ForeignKey('self', help_text="The properties of which this Property is constrained to be a subset, if any.")

    def is_attribute(self):
        """
        The query isAttribute() is true if the Property is defined as an attribute of
        some Classifier.
        """
        # OCL:
        #     result = (not classifier->isEmpty())
        pass


class GeneralizationSet(PackageableElement):
    """
    A GeneralizationSet is a PackageableElement whose instances represent sets of
    Generalization relationships.
    """

    generalization = models.ForeignKey('Generalization', help_text="Designates the instances of Generalization that are members of this GeneralizationSet.")
    is_covering = models.BooleanField(help_text="Indicates (via the associated Generalizations) whether or not the set of specific Classifiers are covering for a particular general classifier. When isCovering is true, every instance of a particular general Classifier is also an instance of at least one of its specific Classifiers for the GeneralizationSet. When isCovering is false, there are one or more instances of the particular general Classifier that are not instances of at least one of its specific Classifiers defined for the GeneralizationSet.")
    is_disjoint = models.BooleanField(help_text="Indicates whether or not the set of specific Classifiers in a Generalization relationship have instance in common. If isDisjoint is true, the specific Classifiers for a particular GeneralizationSet have no members in common; that is, their intersection is empty. If isDisjoint is false, the specific Classifiers in a particular GeneralizationSet have one or more members in common; that is, their intersection is not empty.")
    powertype = models.ForeignKey('Classifier', help_text="Designates the Classifier that is defined as the power type for the associated GeneralizationSet, if there is one.")


class ElementImport(DirectedRelationship):
    """
    An ElementImport identifies a NamedElement in a Namespace other than the one
    that owns that NamedElement and allows the NamedElement to be referenced using
    an unqualified name in the Namespace owning the ElementImport.
    """

    alias = models.CharField(max_length=255, help_text="Specifies the name that should be added to the importing Namespace in lieu of the name of the imported PackagableElement. The alias must not clash with any other member in the importing Namespace. By default, no alias is used.")
    imported_element = models.ForeignKey('PackageableElement', help_text="Specifies the PackageableElement whose name is to be added to a Namespace.")
    importing_namespace = models.ForeignKey('Namespace', help_text="Specifies the Namespace that imports a PackageableElement from another Namespace.")
    visibility = models.ForeignKey('VisibilityKind', help_text="Specifies the visibility of the imported PackageableElement within the importingNamespace, i.e., whether the  importedElement will in turn be visible to other Namespaces. If the ElementImport is public, the importedElement will be visible outside the importingNamespace while, if the ElementImport is private, it will not.")

    def get_name(self):
        """
        The query getName() returns the name under which the imported PackageableElement
        will be known in the importing namespace.
        """
        # OCL:
        """    result = (if alias->notEmpty() then
              alias
            else
              importedElement.name
            endif)"""
        pass


class LinkEndCreationData(LinkEndData):
    """
    LinkEndCreationData is LinkEndData used to provide values for one end of a link
    to be created by a CreateLinkAction.
    """

    insert_at = models.ForeignKey('InputPin', help_text="For ordered Association ends, the InputPin that provides the position where the new link should be inserted or where an existing link should be moved to. The type of the insertAt InputPin is UnlimitedNatural, but the input cannot be zero. It is omitted for Association ends that are not ordered.")
    is_replace_all = models.BooleanField(help_text="Specifies whether the existing links emanating from the object on this end should be destroyed before creating a new link.")

    def all_pins(self):
        """
        Adds the insertAt InputPin (if any) to the set of all Pins.
        """
        # OCL:
        #     result = (self.LinkEndData::allPins()->including(insertAt))
        pass


class MessageSort(Enumeration):
    """
    This is an enumerated type that identifies the type of communication action that
    was used to generate the Message.
    """

    REPLY = 'reply'
    CREATEMESSAGE = 'createmessage'
    ASYNCHSIGNAL = 'asynchsignal'
    DELETEMESSAGE = 'deletemessage'
    ASYNCHCALL = 'asynchcall'
    SYNCHCALL = 'synchcall'
    CHOICES = (
        (REPLY, 'The message is a reply message to an operation call.'),
        (CREATEMESSAGE, 'The message designating the creation of another lifeline object.'),
        (ASYNCHSIGNAL, 'The message was generated by an asynchronous send action.'),
        (DELETEMESSAGE, 'The message designating the termination of another lifeline.'),
        (ASYNCHCALL, 'The message was generated by an asynchronous call to an operation; i.e., a CallAction with isSynchronous = false.'),
        (SYNCHCALL, 'The message was generated by a synchronous call to an operation.'),
    )

    message_sort = models.CharField(max_length=255, choices=CHOICES, default=SYNCHCALL)


class Lifeline(NamedElement):
    """
    A Lifeline represents an individual participant in the Interaction. While parts
    and structural features may have multiplicity greater than 1, Lifelines
    represent only one interacting entity.
    """

    covered_by = models.ForeignKey('InteractionFragment', help_text="References the InteractionFragments in which this Lifeline takes part.")
    decomposed_as = models.ForeignKey('PartDecomposition', help_text="References the Interaction that represents the decomposition.")
    interaction = models.ForeignKey('Interaction', help_text="References the Interaction enclosing this Lifeline.")
    represents = models.ForeignKey('ConnectableElement', help_text="References the ConnectableElement within the classifier that contains the enclosing interaction.")
    selector = models.ForeignKey('ValueSpecification', help_text="If the referenced ConnectableElement is multivalued, then this specifies the specific individual part within that set.")


class ClassifierTemplateParameter(TemplateParameter):
    """
    A ClassifierTemplateParameter exposes a Classifier as a formal template
    parameter.
    """

    allow_substitutable = models.BooleanField(help_text="Constrains the required relationship between an actual parameter and the parameteredElement for this formal parameter.")
    constraining_classifier = models.ForeignKey('Classifier', help_text="The classifiers that constrain the argument that can be used for the parameter. If the allowSubstitutable attribute is true, then any Classifier that is compatible with this constraining Classifier can be substituted; otherwise, it must be either this Classifier or one of its specializations. If this property is empty, there are no constraints on the Classifier that can be used as an argument.")

    def __init__(self, *args, **kwargs):
        super(ClassifierTemplateParameter).__init__(*args, **kwargs)


class ReduceAction(Action):
    """
    A ReduceAction is an Action that reduces a collection to a single value by
    repeatedly combining the elements of the collection using a reducer Behavior.
    """

    collection = models.ForeignKey('InputPin', help_text="The InputPin that provides the collection to be reduced.")
    is_ordered = models.BooleanField(help_text="Indicates whether the order of the input collection should determine the order in which the reducer Behavior is applied to its elements.")
    reducer = models.ForeignKey('Behavior', help_text="A Behavior that is repreatedly applied to two elements of the input collection to produce a value that is of the same type as elements of the collection.")
    result = models.ForeignKey('OutputPin', help_text="The output pin on which the result value is placed.")


class InteractionUse(InteractionFragment):
    """
    An InteractionUse refers to an Interaction. The InteractionUse is a shorthand
    for copying the contents of the referenced Interaction where the InteractionUse
    is. To be accurate the copying must take into account substituting parameters
    with arguments and connect the formal Gates with the actual ones.
    """

    actual_gate = models.ForeignKey('Gate', help_text="The actual gates of the InteractionUse.")
    argument = models.ForeignKey('ValueSpecification', help_text="The actual arguments of the Interaction.")
    refers_to = models.ForeignKey('Interaction', help_text="Refers to the Interaction that defines its meaning.")
    return_value = models.ForeignKey('ValueSpecification', help_text="The value of the executed Interaction.")
    return_value_recipient = models.ForeignKey('Property', help_text="The recipient of the return value.")


class PartDecomposition(InteractionUse):
    """
    A PartDecomposition is a description of the internal Interactions of one
    Lifeline relative to an Interaction.
    """

    pass


class ConnectableElementTemplateParameter(TemplateParameter):
    """
    A ConnectableElementTemplateParameter exposes a ConnectableElement as a formal
    parameter for a template.
    """


    def __init__(self, *args, **kwargs):
        super(ConnectableElementTemplateParameter).__init__(*args, **kwargs)
    pass


class Parameter(MultiplicityElement, ConnectableElement):
    """
    A Parameter is a specification of an argument used to pass information into or
    out of an invocation of a BehavioralFeature.  Parameters can be treated as
    ConnectableElements within Collaborations.
    """

    default = models.CharField(max_length=255, help_text="A String that represents a value to be used when no argument is supplied for the Parameter.")
    default_value = models.ForeignKey('ValueSpecification', help_text="Specifies a ValueSpecification that represents a value to be used when no argument is supplied for the Parameter.")
    direction = models.ForeignKey('ParameterDirectionKind', help_text="Indicates whether a parameter is being sent into or out of a behavioral element.")
    effect = models.ForeignKey('ParameterEffectKind', help_text="Specifies the effect that executions of the owner of the Parameter have on objects passed in or out of the parameter.")
    is_exception = models.BooleanField(help_text="Tells whether an output parameter may emit a value to the exclusion of the other outputs.")
    is_stream = models.BooleanField(help_text="Tells whether an input parameter may accept values while its behavior is executing, or whether an output parameter may post values while the behavior is executing.")
    operation = models.ForeignKey('Operation', help_text="The Operation owning this parameter.")
    parameter_set = models.ForeignKey('ParameterSet', help_text="The ParameterSets containing the parameter. See ParameterSet.")

    def default_operation(self):
        """
        Derivation for Parameter::/default
        """
        # OCL:
        #     result = (if self.type = String then defaultValue.stringValue() else null endif)
        pass


class Realization(Abstraction):
    """
    Realization is a specialized Abstraction relationship between two sets of model
    Elements, one representing a specification (the supplier) and the other
    represents an implementation of the latter (the client). Realization can be used
    to model stepwise refinement, optimizations, transformations, templates, model
    synthesis, framework composition, etc.
    """

    pass


class InterfaceRealization(Realization):
    """
    An InterfaceRealization is a specialized realization relationship between a
    BehavioredClassifier and an Interface. This relationship signifies that the
    realizing BehavioredClassifier conforms to the contract specified by the
    Interface.
    """

    contract = models.ForeignKey('Interface', help_text="References the Interface specifying the conformance contract.")
    implementing_classifier = models.ForeignKey('BehavioredClassifier', help_text="References the BehavioredClassifier that owns this InterfaceRealization, i.e., the BehavioredClassifier that realizes the Interface to which it refers.")


class Comment(Element):
    """
    A Comment is a textual annotation that can be attached to a set of Elements.
    """

    annotated_element = models.ForeignKey('Element', help_text="References the Element(s) being commented.")
    body = models.CharField(max_length=255, help_text="Specifies a string that is the comment.")


class ActivityEdge(RedefinableElement):
    """
    An ActivityEdge is an abstract class for directed connections between two
    ActivityNodes.
    """

    activity = models.ForeignKey('Activity', help_text="The Activity containing the ActivityEdge, if it is directly owned by an Activity.")
    guard = models.ForeignKey('ValueSpecification', help_text="A ValueSpecification that is evaluated to determine if a token can traverse the ActivityEdge. If an ActivityEdge has no guard, then there is no restriction on tokens traversing the edge.")
    in_group = models.ForeignKey('ActivityGroup', help_text="ActivityGroups containing the ActivityEdge.")
    in_partition = models.ForeignKey('ActivityPartition', help_text="ActivityPartitions containing the ActivityEdge.")
    in_structured_node = models.ForeignKey('StructuredActivityNode', help_text="The StructuredActivityNode containing the ActivityEdge, if it is owned by a StructuredActivityNode.")
    interrupts = models.ForeignKey('InterruptibleActivityRegion', help_text="The InterruptibleActivityRegion for which this ActivityEdge is an interruptingEdge.")
    redefined_edge = models.ForeignKey('self', help_text="ActivityEdges from a generalization of the Activity containing this ActivityEdge that are redefined by this ActivityEdge.")
    source = models.ForeignKey('ActivityNode', help_text="The ActivityNode from which tokens are taken when they traverse the ActivityEdge.")
    target = models.ForeignKey('ActivityNode', help_text="The ActivityNode to which tokens are put when they traverse the ActivityEdge.")
    weight = models.ForeignKey('ValueSpecification', help_text="The minimum number of tokens that must traverse the ActivityEdge at the same time. If no weight is specified, this is equivalent to specifying a constant value of 1.")

    class Meta:
        abstract = True

    def is_consistent_with(self):
        # OCL:
        #     result = (redefiningElement.oclIsKindOf(ActivityEdge))
        pass


class ObjectFlow(ActivityEdge):
    """
    An ObjectFlow is an ActivityEdge that is traversed by object tokens that may
    hold values. Object flows also support multicast/receive, token selection from
    object nodes, and transformation of tokens.
    """

    is_multicast = models.BooleanField(help_text="Indicates whether the objects in the ObjectFlow are passed by multicasting.")
    is_multireceive = models.BooleanField(help_text="Indicates whether the objects in the ObjectFlow are gathered from respondents to multicasting.")
    selection = models.ForeignKey('Behavior', help_text="A Behavior used to select tokens from a source ObjectNode.")
    transformation = models.ForeignKey('Behavior', help_text="A Behavior used to change or replace object tokens flowing along the ObjectFlow.")


class Connector(Feature):
    """
    A Connector specifies links that enables communication between two or more
    instances. In contrast to Associations, which specify links between any instance
    of the associated Classifiers, Connectors specify links between instances
    playing the connected parts only.
    """

    contract = models.ForeignKey('Behavior', help_text="The set of Behaviors that specify the valid interaction patterns across the Connector.")
    end = models.ForeignKey('ConnectorEnd', help_text="A Connector has at least two ConnectorEnds, each representing the participation of instances of the Classifiers typing the ConnectableElements attached to the end. The set of ConnectorEnds is ordered.")
    kind = models.ForeignKey('ConnectorKind', help_text="Indicates the kind of Connector. This is derived: a Connector with one or more ends connected to a Port which is not on a Part and which is not a behavior port is a delegation; otherwise it is an assembly.")
    redefined_connector = models.ForeignKey('self', help_text="A Connector may be redefined when its containing Classifier is specialized. The redefining Connector may have a type that specializes the type of the redefined Connector. The types of the ConnectorEnds of the redefining Connector may specialize the types of the ConnectorEnds of the redefined Connector. The properties of the ConnectorEnds of the redefining Connector may be replaced.")
    type_ = models.ForeignKey('Association', help_text="An optional Association that classifies links corresponding to this Connector.")

    def kind_operation(self):
        """
        Derivation for Connector::/kind : ConnectorKind
        """
        # OCL:
        """    result = (if end->exists(
            		role.oclIsKindOf(Port) 
            		and partWithPort->isEmpty()
            		and not role.oclAsType(Port).isBehavior)
            then ConnectorKind::delegation 
            else ConnectorKind::assembly 
            endif)"""
        pass


class ProtocolConformance(DirectedRelationship):
    """
    A ProtocolStateMachine can be redefined into a more specific
    ProtocolStateMachine or into behavioral StateMachine. ProtocolConformance
    declares that the specific ProtocolStateMachine specifies a protocol that
    conforms to the general ProtocolStateMachine or that the specific behavioral
    StateMachine abides by the protocol of the general ProtocolStateMachine.
    """

    general_machine = models.ForeignKey('ProtocolStateMachine', help_text="Specifies the ProtocolStateMachine to which the specific ProtocolStateMachine conforms.")
    specific_machine = models.ForeignKey('ProtocolStateMachine', help_text="Specifies the ProtocolStateMachine which conforms to the general ProtocolStateMachine.")


class Interval(ValueSpecification):
    """
    An Interval defines the range between two ValueSpecifications.
    """

    max_ = models.ForeignKey('ValueSpecification', help_text="Refers to the ValueSpecification denoting the maximum value of the range.")
    min_ = models.ForeignKey('ValueSpecification', help_text="Refers to the ValueSpecification denoting the minimum value of the range.")


class PseudostateKind(Enumeration):
    """
    PseudostateKind is an Enumeration type that is used to differentiate various
    kinds of Pseudostates.
    """

    SHALLOWHISTORY = 0
    DEEPHISTORY = 1
    JOIN = 2
    EXITPOINT = 3
    FORK = 4
    INITIAL = 5
    CHOICE = 6
    ENTRYPOINT = 7
    JUNCTION = 8
    TERMINATE = 9
    CHOICES = (
        (SHALLOWHISTORY, 'shallowHistory'),
        (DEEPHISTORY, 'deepHistory'),
        (JOIN, 'join'),
        (EXITPOINT, 'exitPoint'),
        (FORK, 'fork'),
        (INITIAL, 'initial'),
        (CHOICE, 'choice'),
        (ENTRYPOINT, 'entryPoint'),
        (JUNCTION, 'junction'),
        (TERMINATE, 'terminate'),
    )

    pseudostate_kind = models.IntegerField(choices=CHOICES, default=TERMINATE)


class CreateLinkAction(WriteLinkAction):
    """
    A CreateLinkAction is a WriteLinkAction for creating links.
    """


    def __init__(self, *args, **kwargs):
        super(CreateLinkAction).__init__(*args, **kwargs)
    pass


class CreateLinkObjectAction(CreateLinkAction):
    """
    A CreateLinkObjectAction is a CreateLinkAction for creating link objects
    (AssociationClasse instances).
    """

    result = models.ForeignKey('OutputPin')


class LiteralSpecification(ValueSpecification):
    """
    A LiteralSpecification identifies a literal constant being modeled.
    """


    class Meta:
        abstract = True


class LiteralString(LiteralSpecification):
    """
    A LiteralString is a specification of a String value.
    """

    value = models.CharField(max_length=255)

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


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

    represented = models.ForeignKey('Classifier')


class ExpansionNode(ObjectNode):
    """
    An ExpansionNode is an ObjectNode used to indicate a collection input or output
    for an ExpansionRegion. A collection input of an ExpansionRegion contains a
    collection that is broken into its individual elements inside the region, whose
    content is executed once per element. A collection output of an ExpansionRegion
    combines individual elements produced by the execution of the region into a
    collection for use outside the region.
    """

    region_as_input = models.ForeignKey('ExpansionRegion', help_text="The ExpansionRegion for which the ExpansionNode is an input.")
    region_as_output = models.ForeignKey('ExpansionRegion', help_text="The ExpansionRegion for which the ExpansionNode is an output.")


class ExecutionSpecification(InteractionFragment):
    """
    An ExecutionSpecification is a specification of the execution of a unit of
    Behavior or Action within the Lifeline. The duration of an
    ExecutionSpecification is represented by two OccurrenceSpecifications, the start
    OccurrenceSpecification and the finish OccurrenceSpecification.
    """

    finish = models.ForeignKey('OccurrenceSpecification', help_text="References the OccurrenceSpecification that designates the finish of the Action or Behavior.")
    start = models.ForeignKey('OccurrenceSpecification', help_text="References the OccurrenceSpecification that designates the start of the Action or Behavior.")

    class Meta:
        abstract = True


class ActionExecutionSpecification(ExecutionSpecification):
    """
    An ActionExecutionSpecification is a kind of ExecutionSpecification representing
    the execution of an Action.
    """

    action = models.ForeignKey('Action')


class Usage(Dependency):
    """
    A Usage is a Dependency in which the client Element requires the supplier
    Element (or set of Elements) for its full implementation or operation.
    """

    pass


class InstanceValue(ValueSpecification):
    """
    An InstanceValue is a ValueSpecification that identifies an instance.
    """

    instance = models.ForeignKey('InstanceSpecification')


class LiteralReal(LiteralSpecification):
    """
    A LiteralReal is a specification of a Real value.
    """

    value = models.ForeignKey('Real')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


class ExceptionHandler(Element):
    """
    An ExceptionHandler is an Element that specifies a handlerBody ExecutableNode to
    execute in case the specified exception occurs during the execution of the
    protected ExecutableNode.
    """

    exception_input = models.ForeignKey('ObjectNode', help_text="An ObjectNode within the handlerBody. When the ExceptionHandler catches an exception, the exception token is placed on this ObjectNode, causing the handlerBody to execute.")
    exception_type = models.ForeignKey('Classifier', help_text="The Classifiers whose instances the ExceptionHandler catches as exceptions. If an exception occurs whose type is any exceptionType, the ExceptionHandler catches the exception and executes the handlerBody.")
    handler_body = models.ForeignKey('ExecutableNode', help_text="An ExecutableNode that is executed if the ExceptionHandler catches an exception.")
    protected_node = models.ForeignKey('ExecutableNode', help_text="The ExecutableNode protected by the ExceptionHandler. If an exception propagates out of the protectedNode and has a type matching one of the exceptionTypes, then it is caught by this ExceptionHandler.")


class ControlFlow(ActivityEdge):
    """
    A ControlFlow is an ActivityEdge traversed by control tokens or object tokens of
    control type, which are use to control the execution of ExecutableNodes.
    """

    pass


class PrimitiveType(DataType):
    """
    A PrimitiveType defines a predefined DataType, without any substructure. A
    PrimitiveType may have an algebra and operations defined outside of UML, for
    example, mathematically.
    """

    pass


class Vertex(NamedElement):
    """
    A Vertex is an abstraction of a node in a StateMachine graph. It can be the
    source or destination of any number of Transitions.
    """

    container = models.ForeignKey('Region', help_text="The Region that contains this Vertex.")
    incoming = models.ForeignKey('Transition', help_text="Specifies the Transitions entering this Vertex.")
    outgoing = models.ForeignKey('Transition', help_text="Specifies the Transitions departing from this Vertex.")

    class Meta:
        abstract = True

    def is_contained_in_region(self):
        """
        This utility query returns true if the Vertex is contained in the Region r
        (input argument).
        """
        # OCL:
        """    result = (if (container = r) then
            	true
            else
            	if (r.state->isEmpty()) then
            		false
            	else
            		container.state.isContainedInRegion(r)
            	endif
            endif)"""
        pass


class Pseudostate(Vertex):
    """
    A Pseudostate is an abstraction that encompasses different types of transient
    Vertices in the StateMachine graph. A StateMachine instance never comes to rest
    in a Pseudostate, instead, it will exit and enter the Pseudostate within a
    single run-to-completion step.
    """

    kind = models.ForeignKey('PseudostateKind', help_text="Determines the precise type of the Pseudostate and can be one of: entryPoint, exitPoint, initial, deepHistory, shallowHistory, join, fork, junction, terminate or choice.")
    state = models.ForeignKey('State', help_text="The State that owns this Pseudostate and in which it appears.")
    state_machine = models.ForeignKey('StateMachine', help_text="The StateMachine in which this Pseudostate is defined. This only applies to Pseudostates of the kind entryPoint or exitPoint.")


class Activity(Behavior):
    """
    An Activity is the specification of parameterized Behavior as the coordinated
    sequencing of subordinate units.
    """

    edge = models.ForeignKey('ActivityEdge', help_text="ActivityEdges expressing flow between the nodes of the Activity.")
    group = models.ForeignKey('ActivityGroup', help_text="Top-level ActivityGroups in the Activity.")
    is_read_only = models.BooleanField(help_text="If true, this Activity must not make any changes to objects. The default is false (an Activity may make nonlocal changes). (This is an assertion, not an executable property. It may be used by an execution engine to optimize model execution. If the assertion is violated by the Activity, then the model is ill-formed.)")
    is_single_execution = models.BooleanField(help_text="If true, all invocations of the Activity are handled by the same execution.")
    node = models.ForeignKey('ActivityNode', help_text="ActivityNodes coordinated by the Activity.")
    partition = models.ForeignKey('ActivityPartition', help_text="Top-level ActivityPartitions in the Activity.")
    structured_node = models.ForeignKey('StructuredActivityNode', help_text="Top-level StructuredActivityNodes in the Activity.")
    variable = models.ForeignKey('Variable', help_text="Top-level Variables defined by the Activity.")


class UseCase(BehavioredClassifier):
    """
    A UseCase specifies a set of actions performed by its subjects, which yields an
    observable result that is of value for one or more Actors or other stakeholders
    of each subject.
    """

    extend = models.ForeignKey('Extend', help_text="The Extend relationships owned by this UseCase.")
    extension_point = models.ForeignKey('ExtensionPoint', help_text="The ExtensionPoints owned by this UseCase.")
    include = models.ForeignKey('Include', help_text="The Include relationships owned by this UseCase.")
    subject = models.ForeignKey('Classifier', help_text="The subjects to which this UseCase applies. Each subject or its parts realize all the UseCases that apply to it.")

    def all_included_use_cases(self):
        """
        The query allIncludedUseCases() returns the transitive closure of all UseCases
        (directly or indirectly) included by this UseCase.
        """
        # OCL:
        #     result = (self.include.addition->union(self.include.addition->collect(uc | uc.allIncludedUseCases()))->asSet())
        pass


class WriteStructuralFeatureAction(StructuralFeatureAction):
    """
    WriteStructuralFeatureAction is an abstract class for StructuralFeatureActions
    that change StructuralFeature values.
    """

    result = models.ForeignKey('OutputPin', help_text="The OutputPin on which is put the input object as modified by the WriteStructuralFeatureAction.")
    value = models.ForeignKey('InputPin', help_text="The InputPin that provides the value to be added or removed from the StructuralFeature.")

    class Meta:
        abstract = True


class AddStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """
    An AddStructuralFeatureValueAction is a WriteStructuralFeatureAction for adding
    values to a StructuralFeature.
    """

    insert_at = models.ForeignKey('InputPin', help_text="The InputPin that gives the position at which to insert the value in an ordered StructuralFeature. The type of the insertAt InputPin is UnlimitedNatural, but the value cannot be zero. It is omitted for unordered StructuralFeatures.")
    is_replace_all = models.BooleanField(help_text="Specifies whether existing values of the StructuralFeature should be removed before adding the new value.")


class JoinNode(ControlNode):
    """
    A JoinNode is a ControlNode that synchronizes multiple flows.
    """

    is_combine_duplicate = models.BooleanField(help_text="Indicates whether incoming tokens having objects with the same identity are combined into one by the JoinNode.")
    join_spec = models.ForeignKey('ValueSpecification', help_text="""A ValueSpecification giving the condition under which the JoinNode will offer a token on its outgoing ActivityEdge. If no joinSpec is specified, then the JoinNode will offer an outgoing token if tokens are offered on all of its incoming ActivityEdges (an "and" condition).""")


class LiteralUnlimitedNatural(LiteralSpecification):
    """
    A LiteralUnlimitedNatural is a specification of an UnlimitedNatural number.
    """

    value = models.ForeignKey('UnlimitedNatural')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


class AnyReceiveEvent(MessageEvent):
    """
    A trigger for an AnyReceiveEvent is triggered by the receipt of any message that
    is not explicitly handled by any related trigger.
    """

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

    body_condition = models.ForeignKey('Constraint', help_text="An optional Constraint on the result values of an invocation of this Operation.")
    class_ = models.ForeignKey('Class', help_text="The Class that owns this operation, if any.")
    datatype = models.ForeignKey('DataType', help_text="The DataType that owns this Operation, if any.")
    interface = models.ForeignKey('Interface', help_text="The Interface that owns this Operation, if any.")
    is_ordered = models.BooleanField(help_text="Specifies whether the return parameter is ordered or not, if present.  This information is derived from the return result for this Operation.")
    is_query = models.BooleanField(help_text="Specifies whether an execution of the BehavioralFeature leaves the state of the system unchanged (isQuery=true) or whether side effects may occur (isQuery=false).")
    is_unique = models.BooleanField(help_text="Specifies whether the return parameter is unique or not, if present. This information is derived from the return result for this Operation.")
    lower = models.ForeignKey('Integer', help_text="Specifies the lower multiplicity of the return parameter, if present. This information is derived from the return result for this Operation.")
    postcondition = models.ForeignKey('Constraint', help_text="An optional set of Constraints specifying the state of the system when the Operation is completed.")
    precondition = models.ForeignKey('Constraint', help_text="An optional set of Constraints on the state of the system when the Operation is invoked.")
    redefined_operation = models.ForeignKey('self', help_text="The Operations that are redefined by this Operation.")
    type_ = models.ForeignKey('Type', help_text="The return type of the operation, if present. This information is derived from the return result for this Operation.")
    upper = models.ForeignKey('UnlimitedNatural', help_text="The upper multiplicity of the return parameter, if present. This information is derived from the return result for this Operation.")

    def __init__(self, *args, **kwargs):
        super(Operation).__init__(*args, **kwargs)

    def type_operation(self):
        """
        If this operation has a return parameter, type equals the value of type for that
        parameter. Otherwise type has no value.
        """
        # OCL:
        #     result = (if returnResult()->notEmpty() then returnResult()->any(true).type else null endif)
        pass


class InstanceSpecification(DeploymentTarget, PackageableElement, DeployedArtifact):
    """
    An InstanceSpecification is a model element that represents an instance in a
    modeled system. An InstanceSpecification can act as a DeploymentTarget in a
    Deployment relationship, in the case that it represents an instance of a Node.
    It can also act as a DeployedArtifact, if it represents an instance of an
    Artifact.
    """

    classifier = models.ForeignKey('Classifier', help_text="The Classifier or Classifiers of the represented instance. If multiple Classifiers are specified, the instance is classified by all of them.")
    slot = models.ForeignKey('Slot', help_text="A Slot giving the value or values of a StructuralFeature of the instance. An InstanceSpecification can have one Slot per StructuralFeature of its Classifiers, including inherited features. It is not necessary to model a Slot for every StructuralFeature, in which case the InstanceSpecification is a partial description.")
    specification = models.ForeignKey('ValueSpecification', help_text="A specification of how to compute, derive, or construct the instance.")


class StructuredActivityNode(Namespace, ActivityGroup, Action):
    """
    A StructuredActivityNode is an Action that is also an ActivityGroup and whose
    behavior is specified by the ActivityNodes and ActivityEdges it so contains.
    Unlike other kinds of ActivityGroup, a StructuredActivityNode owns the
    ActivityNodes and ActivityEdges it contains, and so a node or edge can only be
    directly contained in one StructuredActivityNode, though StructuredActivityNodes
    may be nested.
    """

    edge = models.ForeignKey('ActivityEdge', help_text="The ActivityEdges immediately contained in the StructuredActivityNode.")
    must_isolate = models.BooleanField(help_text="If true, then any object used by an Action within the StructuredActivityNode cannot be accessed by any Action outside the node until the StructuredActivityNode as a whole completes. Any concurrent Actions that would result in accessing such objects are required to have their execution deferred until the completion of the StructuredActivityNode.")
    node = models.ForeignKey('ActivityNode', help_text="The ActivityNodes immediately contained in the StructuredActivityNode.")
    structured_node_input = models.ForeignKey('InputPin', help_text="The InputPins owned by the StructuredActivityNode.")
    structured_node_output = models.ForeignKey('OutputPin', help_text="The OutputPins owned by the StructuredActivityNode.")
    variable = models.ForeignKey('Variable', help_text="The Variables defined in the scope of the StructuredActivityNode.")

    def __init__(self, *args, **kwargs):
        super(StructuredActivityNode).__init__(*args, **kwargs)

    def source_nodes(self):
        """
        Return those ActivityNodes contained immediately within the
        StructuredActivityNode that may act as sources of edges owned by the
        StructuredActivityNode.
        """
        # OCL:
        """    result = (node->union(input.oclAsType(ActivityNode)->asSet())->
              union(node->select(oclIsKindOf(Action)).oclAsType(Action).output)->asSet())"""
        pass


class BehaviorExecutionSpecification(ExecutionSpecification):
    """
    A BehaviorExecutionSpecification is a kind of ExecutionSpecification
    representing the execution of a Behavior.
    """

    behavior = models.ForeignKey('Behavior')


class RemoveStructuralFeatureValueAction(WriteStructuralFeatureAction):
    """
    A RemoveStructuralFeatureValueAction is a WriteStructuralFeatureAction that
    removes values from a StructuralFeature.
    """

    is_remove_duplicates = models.BooleanField(help_text="Specifies whether to remove duplicates of the value in nonunique StructuralFeatures.")
    remove_at = models.ForeignKey('InputPin', help_text="An InputPin that provides the position of an existing value to remove in ordered, nonunique structural features. The type of the removeAt InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.")


class SequenceNode(StructuredActivityNode):
    """
    A SequenceNode is a StructuredActivityNode that executes a sequence of
    ExecutableNodes in order.
    """


    def __init__(self, *args, **kwargs):
        super(SequenceNode).__init__(*args, **kwargs)
    pass


class Association(Relationship, Classifier):
    """
    A link is a tuple of values that refer to typed objects.  An Association
    classifies a set of links, each of which is an instance of the Association.
    Each value in the link refers to an instance of the type of the corresponding
    end of the Association.
    """

    end_type = models.ForeignKey('Type', help_text="The Classifiers that are used as types of the ends of the Association.")
    is_derived = models.BooleanField(help_text="Specifies whether the Association is derived from other model elements such as other Associations.")
    member_end = models.ForeignKey('Property', help_text="Each end represents participation of instances of the Classifier connected to the end in links of the Association.")
    navigable_owned_end = models.ForeignKey('Property', help_text="The navigable ends that are owned by the Association itself.")
    owned_end = models.ForeignKey('Property', help_text="The ends that are owned by the Association itself.")

    def end_type_operation(self):
        """
        endType is derived from the types of the member ends.
        """
        # OCL:
        #     result = (memberEnd->collect(type)->asSet())
        pass


class CommunicationPath(Association):
    """
    A communication path is an association between two deployment targets, through
    which they are able to exchange signals and messages.
    """

    pass


class AggregationKind(Enumeration):
    """
    AggregationKind is an Enumeration for specifying the kind of aggregation of a
    Property.
    """

    NONE = 'none'
    COMPOSITE = 'composite'
    SHARED = 'shared'
    CHOICES = (
        (NONE, 'Indicates that the Property has no aggregation.'),
        (COMPOSITE, 'Indicates that the Property is aggregated compositely, i.e., the composite object has responsibility for the existence and storage of the composed objects (parts).'),
        (SHARED, 'Indicates that the Property has shared aggregation.'),
    )

    aggregation_kind = models.CharField(max_length=255, choices=CHOICES, default=SHARED)


class InteractionOperatorKind(Enumeration):
    """
    InteractionOperatorKind is an enumeration designating the different kinds of
    operators of CombinedFragments. The InteractionOperand defines the type of
    operator of a CombinedFragment.
    """

    CRITICAL = 'critical'
    SEQ = 'seq'
    LOOP = 'loop'
    STRICT = 'strict'
    BREAK = 'break'
    ASSERT = 'assert'
    PAR = 'par'
    ALT = 'alt'
    CONSIDER = 'consider'
    IGNORE = 'ignore'
    OPT = 'opt'
    NEG = 'neg'
    CHOICES = (
        (CRITICAL, 'The InteractionOperatorKind critical designates that the CombinedFragment represents a critical region. A critical region means that the traces of the region cannot be interleaved by other OccurrenceSpecifications (on those Lifelines covered by the region). This means that the region is treated atomically by the enclosing fragment when determining the set of valid traces. Even though enclosing CombinedFragments may imply that some OccurrenceSpecifications may interleave into the region, such as with par-operator, this is prevented by defining a region.'),
        (SEQ, 'The InteractionOperatorKind seq designates that the CombinedFragment represents a weak sequencing between the behaviors of the operands.'),
        (LOOP, 'The InteractionOperatorKind loop designates that the CombinedFragment represents a loop. The loop operand will be repeated a number of times.'),
        (STRICT, 'The InteractionOperatorKind strict designates that the CombinedFragment represents a strict sequencing between the behaviors of the operands. The semantics of strict sequencing defines a strict ordering of the operands on the first level within the CombinedFragment with interactionOperator strict. Therefore OccurrenceSpecifications within contained CombinedFragment will not directly be compared with other OccurrenceSpecifications of the enclosing CombinedFragment.'),
        (BREAK, 'The InteractionOperatorKind break designates that the CombinedFragment represents a breaking scenario in the sense that the operand is a scenario that is performed instead of the remainder of the enclosing InteractionFragment. A break operator with a guard is chosen when the guard is true and the rest of the enclosing Interaction Fragment is ignored. When the guard of the break operand is false, the break operand is ignored and the rest of the enclosing InteractionFragment is chosen. The choice between a break operand without a guard and the rest of the enclosing InteractionFragment is done non-deterministically.'),
        (ASSERT, 'The InteractionOperatorKind assert designates that the CombinedFragment represents an assertion. The sequences of the operand of the assertion are the only valid continuations. All other continuations result in an invalid trace.'),
        (PAR, 'The InteractionOperatorKind par designates that the CombinedFragment represents a parallel merge between the behaviors of the operands. The OccurrenceSpecifications of the different operands can be interleaved in any way as long as the ordering imposed by each operand as such is preserved.'),
        (ALT, 'The InteractionOperatorKind alt designates that the CombinedFragment represents a choice of behavior. At most one of the operands will be chosen. The chosen operand must have an explicit or implicit guard expression that evaluates to true at this point in the interaction. An implicit true guard is implied if the operand has no guard.'),
        (CONSIDER, 'The InteractionOperatorKind consider designates which messages should be considered within this combined fragment. This is equivalent to defining every other message to be ignored.'),
        (IGNORE, 'The InteractionOperatorKind ignore designates that there are some message types that are not shown within this combined fragment. These message types can be considered insignificant and are implicitly ignored if they appear in a corresponding execution. Alternatively, one can understand ignore to mean that the message types that are ignored can appear anywhere in the traces.'),
        (OPT, 'The InteractionOperatorKind opt designates that the CombinedFragment represents a choice of behavior where either the (sole) operand happens or nothing happens. An option is semantically equivalent to an alternative CombinedFragment where there is one operand with non-empty content and the second operand is empty.'),
        (NEG, 'The InteractionOperatorKind neg designates that the CombinedFragment represents traces that are defined to be invalid.'),
    )

    interaction_operator_kind = models.CharField(max_length=255, choices=CHOICES, default=NEG)


class ReadExtentAction(Action):
    """
    A ReadExtentAction is an Action that retrieves the current instances of a
    Classifier.
    """

    classifier = models.ForeignKey('Classifier', help_text="The Classifier whose instances are to be retrieved.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin on which the Classifier instances are placed.")


class State(RedefinableElement, Namespace, Vertex):
    """
    A State models a situation during which some (usually implicit) invariant
    condition holds.
    """

    connection = models.ForeignKey('ConnectionPointReference', help_text="The entry and exit connection points used in conjunction with this (submachine) State, i.e., as targets and sources, respectively, in the Region with the submachine State. A connection point reference references the corresponding definition of a connection point Pseudostate in the StateMachine referenced by the submachine State.")
    connection_point = models.ForeignKey('Pseudostate', help_text="The entry and exit Pseudostates of a composite State. These can only be entry or exit Pseudostates, and they must have different names. They can only be defined for composite States.")
    deferrable_trigger = models.ForeignKey('Trigger', help_text="A list of Triggers that are candidates to be retained by the StateMachine if they trigger no Transitions out of the State (not consumed). A deferred Trigger is retained until the StateMachine reaches a State configuration where it is no longer deferred.")
    do_activity = models.ForeignKey('Behavior', help_text="An optional Behavior that is executed while being in the State. The execution starts when this State is entered, and ceases either by itself when done, or when the State is exited, whichever comes first.")
    entry = models.ForeignKey('Behavior', help_text="An optional Behavior that is executed whenever this State is entered regardless of the Transition taken to reach the State. If defined, entry Behaviors are always executed to completion prior to any internal Behavior or Transitions performed within the State.")
    exit = models.ForeignKey('Behavior', help_text="An optional Behavior that is executed whenever this State is exited regardless of which Transition was taken out of the State. If defined, exit Behaviors are always executed to completion only after all internal and transition Behaviors have completed execution.")
    is_composite = models.BooleanField(help_text="A state with isComposite=true is said to be a composite State. A composite State is a State that contains at least one Region.")
    is_orthogonal = models.BooleanField(help_text="A State with isOrthogonal=true is said to be an orthogonal composite State An orthogonal composite State contains two or more Regions.")
    is_simple = models.BooleanField(help_text="A State with isSimple=true is said to be a simple State A simple State does not have any Regions and it does not refer to any submachine StateMachine.")
    is_submachine_state = models.BooleanField(help_text="A State with isSubmachineState=true is said to be a submachine State Such a State refers to another StateMachine(submachine).")
    redefined_state = models.ForeignKey('self', help_text="The State of which this State is a redefinition.")
    region = models.ForeignKey('Region', help_text="The Regions owned directly by the State.")
    state_invariant = models.ForeignKey('Constraint', help_text="Specifies conditions that are always true when this State is the current State. In ProtocolStateMachines state invariants are additional conditions to the preconditions of the outgoing Transitions, and to the postcondition of the incoming Transitions.")
    submachine = models.ForeignKey('StateMachine', help_text="The StateMachine that is to be inserted in place of the (submachine) State.")

    def __init__(self, *args, **kwargs):
        super(State).__init__(*args, **kwargs)

    def is_orthogonal_operation(self):
        """
        An orthogonal State is a composite state with at least 2 regions.
        """
        # OCL:
        #     result = (region->size () > 1)
        pass


class FinalState(State):
    """
    A special kind of State, which, when entered, signifies that the enclosing
    Region has completed. If the enclosing Region is directly contained in a
    StateMachine and all other Regions in that StateMachine also are completed, then
    it means that the entire StateMachine behavior is completed.
    """

    pass


class DestructionOccurrenceSpecification(MessageOccurrenceSpecification):
    """
    A DestructionOccurenceSpecification models the destruction of an object.
    """

    pass


class BroadcastSignalAction(InvocationAction):
    """
    A BroadcastSignalAction is an InvocationAction that transmits a Signal instance
    to all the potential target objects in the system. Values from the argument
    InputPins are used to provide values for the attributes of the Signal. The
    requestor continues execution immediately after the Signal instances are sent
    out and cannot receive reply values.
    """

    signal = models.ForeignKey('Signal')


class Artifact(Classifier, DeployedArtifact):
    """
    An artifact is the specification of a physical piece of information that is used
    or produced by a software development process, or by deployment and operation of
    a system. Examples of artifacts include model files, source files, scripts, and
    binary executable files, a table in a database system, a development
    deliverable, or a word-processing document, a mail message. An artifact is the
    source of a deployment to a node.
    """

    file_name = models.CharField(max_length=255, help_text="A concrete name that is used to refer to the Artifact in a physical context. Example: file system name, universal resource locator.")
    manifestation = models.ForeignKey('Manifestation', help_text="The set of model elements that are manifested in the Artifact. That is, these model elements are utilized in the construction (or generation) of the artifact.")
    nested_artifact = models.ForeignKey('self', help_text="The Artifacts that are defined (nested) within the Artifact. The association is a specialization of the ownedMember association from Namespace to NamedElement.")
    owned_attribute = models.ForeignKey('Property', help_text="The attributes or association ends defined for the Artifact. The association is a specialization of the ownedMember association.")
    owned_operation = models.ForeignKey('Operation', help_text="The Operations defined for the Artifact. The association is a specialization of the ownedMember association.")


class Interface(Classifier):
    """
    Interfaces declare coherent services that are implemented by
    BehavioredClassifiers that implement the Interfaces via InterfaceRealizations.
    """

    nested_classifier = models.ForeignKey('Classifier', help_text="References all the Classifiers that are defined (nested) within the Interface.")
    owned_attribute = models.ForeignKey('Property', help_text="The attributes (i.e., the Properties) owned by the Interface.")
    owned_operation = models.ForeignKey('Operation', help_text="The Operations owned by the Interface.")
    owned_reception = models.ForeignKey('Reception', help_text="Receptions that objects providing this Interface are willing to accept.")
    protocol = models.ForeignKey('ProtocolStateMachine', help_text="References a ProtocolStateMachine specifying the legal sequences of the invocation of the BehavioralFeatures described in the Interface.")
    redefined_interface = models.ForeignKey('self', help_text="References all the Interfaces redefined by this Interface.")


class ProfileApplication(DirectedRelationship):
    """
    A profile application is used to show which profiles have been applied to a
    package.
    """

    applied_profile = models.ForeignKey('Profile', help_text="References the Profiles that are applied to a Package through this ProfileApplication.")
    applying_package = models.ForeignKey('Package', help_text="The package that owns the profile application.")
    is_strict = models.BooleanField(help_text="Specifies that the Profile filtering rules for the metaclasses of the referenced metamodel shall be strictly applied.")


class Message(NamedElement):
    """
    A Message defines a particular communication between Lifelines of an
    Interaction.
    """

    argument = models.ForeignKey('ValueSpecification', help_text="The arguments of the Message.")
    connector = models.ForeignKey('Connector', help_text="The Connector on which this Message is sent.")
    interaction = models.ForeignKey('Interaction', help_text="The enclosing Interaction owning the Message.")
    message_kind = models.ForeignKey('MessageKind', help_text="The derived kind of the Message (complete, lost, found, or unknown).")
    message_sort = models.ForeignKey('MessageSort', help_text="The sort of communication reflected by the Message.")
    receive_event = models.ForeignKey('MessageEnd', help_text="References the Receiving of the Message.")
    send_event = models.ForeignKey('MessageEnd', help_text="References the Sending of the Message.")
    signature = models.ForeignKey('NamedElement', help_text="The signature of the Message is the specification of its content. It refers either an Operation or a Signal.")

    def message_kind_operation(self):
        """
        This query returns the MessageKind value for this Message.
        """
        # OCL:
        #     result = (messageKind)
        pass


class Extend(NamedElement, DirectedRelationship):
    """
    A relationship from an extending UseCase to an extended UseCase that specifies
    how and when the behavior defined in the extending UseCase can be inserted into
    the behavior defined in the extended UseCase.
    """

    condition = models.ForeignKey('Constraint', help_text="References the condition that must hold when the first ExtensionPoint is reached for the extension to take place. If no constraint is associated with the Extend relationship, the extension is unconditional.")
    extended_case = models.ForeignKey('UseCase', help_text="The UseCase that is being extended.")
    extension = models.ForeignKey('UseCase', help_text="The UseCase that represents the extension and owns the Extend relationship.")
    extension_location = models.ForeignKey('ExtensionPoint', help_text="An ordered list of ExtensionPoints belonging to the extended UseCase, specifying where the respective behavioral fragments of the extending UseCase are to be inserted. The first fragment in the extending UseCase is associated with the first extension point in the list, the second fragment with the second point, and so on. Note that, in most practical cases, the extending UseCase has just a single behavior fragment, so that the list of ExtensionPoints is trivial.")


class Observation(PackageableElement):
    """
    Observation specifies a value determined by observing an event or events that
    occur relative to other model Elements.
    """


    class Meta:
        abstract = True


class TimeObservation(Observation):
    """
    A TimeObservation is a reference to a time instant during an execution. It
    points out the NamedElement in the model to observe and whether the observation
    is when this NamedElement is entered or when it is exited.
    """

    event = models.ForeignKey('NamedElement', help_text="The TimeObservation is determined by the entering or exiting of the event Element during execution.")
    first_event = models.BooleanField(help_text="The value of firstEvent is related to the event. If firstEvent is true, then the corresponding observation event is the first time instant the execution enters the event Element. If firstEvent is false, then the corresponding observation event is the time instant the execution exits the event Element.")


class TemplateSignature(Element):
    """
    A Template Signature bundles the set of formal TemplateParameters for a
    template.
    """

    owned_parameter = models.ForeignKey('TemplateParameter', help_text="The formal parameters that are owned by this TemplateSignature.")
    parameter = models.ForeignKey('TemplateParameter', help_text="The ordered set of all formal TemplateParameters for this TemplateSignature.")
    template = models.ForeignKey('TemplateableElement', help_text="The TemplateableElement that owns this TemplateSignature.")


class RedefinableTemplateSignature(RedefinableElement, TemplateSignature):
    """
    A RedefinableTemplateSignature supports the addition of formal template
    parameters in a specialization of a template classifier.
    """

    extended_signature = models.ForeignKey('self', help_text="The signatures extended by this RedefinableTemplateSignature.")
    inherited_parameter = models.ForeignKey('TemplateParameter', help_text="The formal template parameters of the extended signatures.")

    def __init__(self, *args, **kwargs):
        super(RedefinableTemplateSignature).__init__(*args, **kwargs)

    def inherited_parameter_operation(self):
        """
        Derivation for RedefinableTemplateSignature::/inheritedParameter
        """
        # OCL:
        #     result = (if extendedSignature->isEmpty() then Set{} else extendedSignature.parameter->asSet() endif)
        pass


class DurationInterval(Interval):
    """
    A DurationInterval defines the range between two Durations.
    """


    def __init__(self, *args, **kwargs):
        super(DurationInterval).__init__(*args, **kwargs)
    pass


class ReadLinkObjectEndAction(Action):
    """
    A ReadLinkObjectEndAction is an Action that retrieves an end object from a link
    object.
    """

    end = models.ForeignKey('Property', help_text="The Association end to be read.")
    object_ = models.ForeignKey('InputPin', help_text="The input pin from which the link object is obtained.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin where the result value is placed.")


class Deployment(Dependency):
    """
    A deployment is the allocation of an artifact or artifact instance to a
    deployment target. A component deployment is the deployment of one or more
    artifacts or artifact instances to a deployment target, optionally parameterized
    by a deployment specification. Examples are executables and configuration files.
    """

    configuration = models.ForeignKey('DeploymentSpecification', help_text="The specification of properties that parameterize the deployment and execution of one or more Artifacts.")
    deployed_artifact = models.ForeignKey('DeployedArtifact', help_text="The Artifacts that are deployed onto a Node. This association specializes the supplier association.")
    location = models.ForeignKey('DeploymentTarget', help_text="The DeployedTarget which is the target of a Deployment.")


class PackageMerge(DirectedRelationship):
    """
    A package merge defines how the contents of one package are extended by the
    contents of another package.
    """

    merged_package = models.ForeignKey('Package', help_text="References the Package that is to be merged with the receiving package of the PackageMerge.")
    receiving_package = models.ForeignKey('Package', help_text="References the Package that is being extended with the contents of the merged package of the PackageMerge.")


class LiteralNull(LiteralSpecification):
    """
    A LiteralNull specifies the lack of a value.
    """


    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


class VariableAction(Action):
    """
    VariableAction is an abstract class for Actions that operate on a specified
    Variable.
    """

    variable = models.ForeignKey('Variable')

    class Meta:
        abstract = True


class WriteVariableAction(VariableAction):
    """
    WriteVariableAction is an abstract class for VariableActions that change
    Variable values.
    """

    value = models.ForeignKey('InputPin')

    class Meta:
        abstract = True


class AddVariableValueAction(WriteVariableAction):
    """
    An AddVariableValueAction is a WriteVariableAction for adding values to a
    Variable.
    """

    insert_at = models.ForeignKey('InputPin', help_text="The InputPin that gives the position at which to insert a new value or move an existing value in ordered Variables. The type of the insertAt InputPin is UnlimitedNatural, but the value cannot be zero. It is omitted for unordered Variables.")
    is_replace_all = models.BooleanField(help_text="Specifies whether existing values of the Variable should be removed before adding the new value.")


class StartClassifierBehaviorAction(Action):
    """
    A StartClassifierBehaviorAction is an Action that starts the classifierBehavior
    of the input object.
    """

    object_ = models.ForeignKey('InputPin')


class ReadVariableAction(VariableAction):
    """
    A ReadVariableAction is a VariableAction that retrieves the values of a
    Variable.
    """

    result = models.ForeignKey('OutputPin')


class ReadSelfAction(Action):
    """
    A ReadSelfAction is an Action that retrieves the context object of the Behavior
    execution within which the ReadSelfAction execution is taking place.
    """

    result = models.ForeignKey('OutputPin')


class Collaboration(StructuredClassifier, BehavioredClassifier):
    """
    A Collaboration describes a structure of collaborating elements (roles), each
    performing a specialized function, which collectively accomplish some desired
    functionality.
    """

    collaboration_role = models.ForeignKey('ConnectableElement')


class ExtensionEnd(Property):
    """
    An extension end is used to tie an extension to a stereotype when extending a
    metaclass. The default multiplicity of an extension end is 0..1.
    """


    def __init__(self, *args, **kwargs):
        super(ExtensionEnd).__init__(*args, **kwargs)

    def lower_bound(self):
        """
        The query lowerBound() returns the lower bound of the multiplicity as an
        Integer. This is a redefinition of the default lower bound, which normally, for
        MultiplicityElements, evaluates to 1 if empty.
        """
        # OCL:
        #     result = (if lowerValue=null then 0 else lowerValue.integerValue() endif)
        pass


class TransitionKind(Enumeration):
    """
    TransitionKind is an Enumeration type used to differentiate the various kinds of
    Transitions.
    """

    EXTERNAL = 'external'
    INTERNAL = 'internal'
    LOCAL = 'local'
    CHOICES = (
        (EXTERNAL, 'Implies that the Transition, if triggered, will exit the composite (source) State.'),
        (INTERNAL, 'Implies that the Transition, if triggered, occurs without exiting or entering the source State (i.e., it does not cause a state change). This means that the entry or exit condition of the source State will not be invoked. An internal Transition can be taken even if the SateMachine is in one or more Regions nested within the associated State.'),
        (LOCAL, 'Implies that the Transition, if triggered, will not exit the composite (source) State, but it will exit and re-enter any state within the composite State that is in the current state configuration.'),
    )

    transition_kind = models.CharField(max_length=255, choices=CHOICES, default=LOCAL)


class ExecutionOccurrenceSpecification(OccurrenceSpecification):
    """
    An ExecutionOccurrenceSpecification represents moments in time at which Actions
    or Behaviors start or finish.
    """

    execution = models.ForeignKey('ExecutionSpecification')


class Trigger(NamedElement):
    """
    A Trigger specifies a specific point  at which an Event occurrence may trigger
    an effect in a Behavior. A Trigger may be qualified by the Port on which the
    Event occurred.
    """

    event = models.ForeignKey('Event', help_text="The Event that detected by the Trigger.")
    port = models.ForeignKey('Port', help_text="A optional Port of through which the given effect is detected.")


class CombinedFragment(InteractionFragment):
    """
    A CombinedFragment defines an expression of InteractionFragments. A
    CombinedFragment is defined by an interaction operator and corresponding
    InteractionOperands. Through the use of CombinedFragments the user will be able
    to describe a number of traces in a compact and concise manner.
    """

    cfragment_gate = models.ForeignKey('Gate', help_text="Specifies the gates that form the interface between this CombinedFragment and its surroundings")
    interaction_operator = models.ForeignKey('InteractionOperatorKind', help_text="Specifies the operation which defines the semantics of this combination of InteractionFragments.")
    operand = models.ForeignKey('InteractionOperand', help_text="The set of operands of the combined fragment.")


class Clause(Element):
    """
    A Clause is an Element that represents a single branch of a ConditionalNode,
    including a test and a body section. The body section is executed only if (but
    not necessarily if) the test section evaluates to true.
    """

    body = models.ForeignKey('ExecutableNode', help_text="The set of ExecutableNodes that are executed if the test evaluates to true and the Clause is chosen over other Clauses within the ConditionalNode that also have tests that evaluate to true.")
    body_output = models.ForeignKey('OutputPin', help_text="The OutputPins on Actions within the body section whose values are moved to the result OutputPins of the containing ConditionalNode after execution of the body.")
    decider = models.ForeignKey('OutputPin', help_text="An OutputPin on an Action in the test section whose Boolean value determines the result of the test.")
    predecessor_clause = models.ForeignKey('self', help_text="A set of Clauses whose tests must all evaluate to false before this Clause can evaluate its test.")
    successor_clause = models.ForeignKey('self', help_text="A set of Clauses that may not evaluate their tests unless the test for this Clause evaluates to false.")
    test = models.ForeignKey('ExecutableNode', help_text="The set of ExecutableNodes that are executed in order to provide a test result for the Clause.")


class Signal(Classifier):
    """
    A Signal is a specification of a kind of communication between objects in which
    a reaction is asynchronously triggered in the receiver without a reply.
    """

    owned_attribute = models.ForeignKey('Property')


class InteractionConstraint(Constraint):
    """
    An InteractionConstraint is a Boolean expression that guards an operand in a
    CombinedFragment.
    """

    maxint = models.ForeignKey('ValueSpecification', help_text="The maximum number of iterations of a loop")
    minint = models.ForeignKey('ValueSpecification', help_text="The minimum number of iterations of a loop")


class LoopNode(StructuredActivityNode):
    """
    A LoopNode is a StructuredActivityNode that represents an iterative loop with
    setup, test, and body sections.
    """

    body_output = models.ForeignKey('OutputPin', help_text="The OutputPins on Actions within the bodyPart, the values of which are moved to the loopVariable OutputPins after the completion of each execution of the bodyPart, before the next iteration of the loop begins or before the loop exits.")
    body_part = models.ForeignKey('ExecutableNode', help_text="The set of ExecutableNodes that perform the repetitive computations of the loop. The bodyPart is executed as long as the test section produces a true value.")
    decider = models.ForeignKey('OutputPin', help_text="An OutputPin on an Action in the test section whose Boolean value determines whether to continue executing the loop bodyPart.")
    is_tested_first = models.BooleanField(help_text="If true, the test is performed before the first execution of the bodyPart. If false, the bodyPart is executed once before the test is performed.")
    loop_variable = models.ForeignKey('OutputPin', help_text="A list of OutputPins that hold the values of the loop variables during an execution of the loop. When the test fails, the values are moved to the result OutputPins of the loop.")
    setup_part = models.ForeignKey('ExecutableNode', help_text="The set of ExecutableNodes executed before the first iteration of the loop, in order to initialize values or perform other setup computations.")
    test = models.ForeignKey('ExecutableNode', help_text="The set of ExecutableNodes executed in order to provide the test result for the loop.")

    def __init__(self, *args, **kwargs):
        super(LoopNode).__init__(*args, **kwargs)

    def source_nodes(self):
        """
        Return the loopVariable OutputPins in addition to other source nodes for the
        LoopNode as a StructuredActivityNode.
        """
        # OCL:
        #     result = (self.StructuredActivityNode::sourceNodes()->union(loopVariable))
        pass


class ClearAssociationAction(Action):
    """
    A ClearAssociationAction is an Action that destroys all links of an Association
    in which a particular object participates.
    """

    association = models.ForeignKey('Association', help_text="The Association to be cleared.")
    object_ = models.ForeignKey('InputPin', help_text="The InputPin that gives the object whose participation in the Association is to be cleared.")


class ActivityFinalNode(FinalNode):
    """
    An ActivityFinalNode is a FinalNode that terminates the execution of its owning
    Activity or StructuredActivityNode.
    """

    pass


class ReadIsClassifiedObjectAction(Action):
    """
    A ReadIsClassifiedObjectAction is an Action that determines whether an object is
    classified by a given Classifier.
    """

    classifier = models.ForeignKey('Classifier', help_text="The Classifier against which the classification of the input object is tested.")
    is_direct = models.BooleanField(help_text="Indicates whether the input object must be directly classified by the given Classifier or whether it may also be an instance of a specialization of the given Classifier.")
    object_ = models.ForeignKey('InputPin', help_text="The InputPin that holds the object whose classification is to be tested.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin that holds the Boolean result of the test.")


class LiteralInteger(LiteralSpecification):
    """
    A LiteralInteger is a specification of an Integer value.
    """

    value = models.ForeignKey('Integer')

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


class ConnectorKind(Enumeration):
    """
    ConnectorKind is an enumeration that defines whether a Connector is an assembly
    or a delegation.
    """

    DELEGATION = 'delegation'
    ASSEMBLY = 'assembly'
    CHOICES = (
        (DELEGATION, 'Indicates that the Connector is a delegation Connector.'),
        (ASSEMBLY, 'Indicates that the Connector is an assembly Connector.'),
    )

    connector_kind = models.CharField(max_length=255, choices=CHOICES, default=ASSEMBLY)


class StartObjectBehaviorAction(CallAction):
    """
    A StartObjectBehaviorAction is an InvocationAction that starts the execution
    either of a directly instantiated Behavior or of the classifierBehavior of an
    object. Argument values may be supplied for the input Parameters of the
    Behavior. If the Behavior is invoked synchronously, then output values may be
    obtained for output Parameters.
    """

    object_ = models.ForeignKey('InputPin')

    def behavior(self):
        """
        If the type of the object InputPin is a Behavior, then that Behavior. Otherwise,
        if the type of the object InputPin is a BehavioredClassifier, then the
        classifierBehavior of that BehavioredClassifier.
        """
        # OCL:
        """    result = (if object.type.oclIsKindOf(Behavior) then
              object.type.oclAsType(Behavior)
            else if object.type.oclIsKindOf(BehavioredClassifier) then
              object.type.oclAsType(BehavioredClassifier).classifierBehavior
            else
              null
            endif
            endif)"""
        pass


class CallEvent(MessageEvent):
    """
    A CallEvent models the receipt by an object of a message invoking a call of an
    Operation.
    """

    operation = models.ForeignKey('Operation')


class OutputPin(Pin):
    """
    An OutputPin is a Pin that holds output values produced by an Action.
    """

    pass


class LiteralBoolean(LiteralSpecification):
    """
    A LiteralBoolean is a specification of a Boolean value.
    """

    value = models.BooleanField()

    def is_computable(self):
        """
        The query isComputable() is redefined to be true.
        """
        # OCL:
        #     result = (true)
        pass


class QualifierValue(Element):
    """
    A QualifierValue is an Element that is used as part of LinkEndData to provide
    the value for a single qualifier of the end given by the LinkEndData.
    """

    qualifier = models.ForeignKey('Property', help_text="The qualifier Property for which the value is to be specified.")
    value = models.ForeignKey('InputPin', help_text="The InputPin from which the specified value for the qualifier is taken.")


class EnumerationLiteral(InstanceSpecification):
    """
    An EnumerationLiteral is a user-defined data value for an Enumeration.
    """

    enumeration = models.ForeignKey('Enumeration', help_text="The Enumeration that this EnumerationLiteral is a member of.")

    def __init__(self, *args, **kwargs):
        super(EnumerationLiteral).__init__(*args, **kwargs)

    def classifier_operation(self):
        """
        Derivation of Enumeration::/classifier
        """
        # OCL:
        #     result = (enumeration)
        pass


class ParameterDirectionKind(Enumeration):
    """
    ParameterDirectionKind is an Enumeration that defines literals used to specify
    direction of parameters.
    """

    RETURN = 'return'
    INOUT = 'inout'
    OUT = 'out'
    IN = 'in'
    CHOICES = (
        (RETURN, 'Indicates that Parameter values are passed as return values back to the caller.'),
        (INOUT, 'Indicates that Parameter values are passed in by the caller and (possibly different) values passed out to the caller.'),
        (OUT, 'Indicates that Parameter values are passed out to the caller.'),
        (IN, 'Indicates that Parameter values are passed in by the caller.'),
    )

    parameter_direction_kind = models.CharField(max_length=255, choices=CHOICES, default=IN)


class ConnectorEnd(MultiplicityElement):
    """
    A ConnectorEnd is an endpoint of a Connector, which attaches the Connector to a
    ConnectableElement.
    """

    defining_end = models.ForeignKey('Property', help_text="A derived property referencing the corresponding end on the Association which types the Connector owing this ConnectorEnd, if any. It is derived by selecting the end at the same place in the ordering of Association ends as this ConnectorEnd.")
    part_with_port = models.ForeignKey('Property', help_text="Indicates the role of the internal structure of a Classifier with the Port to which the ConnectorEnd is attached.")
    role = models.ForeignKey('ConnectableElement', help_text="The ConnectableElement attached at this ConnectorEnd. When an instance of the containing Classifier is created, a link may (depending on the multiplicities) be created to an instance of the Classifier that types this ConnectableElement.")

    def defining_end_operation(self):
        """
        Derivation for ConnectorEnd::/definingEnd : Property
        """
        # OCL:
        """    result = (if connector.type = null 
            then
              null 
            else
              let index : Integer = connector.end->indexOf(self) in
                connector.type.memberEnd->at(index)
            endif)"""
        pass


class Image(Element):
    """
    Physical definition of a graphical image.
    """

    content = models.CharField(max_length=255, help_text="This contains the serialization of the image according to the format. The value could represent a bitmap, image such as a GIF file, or drawing 'instructions' using a standard such as Scalable Vector Graphic (SVG) (which is XML based).")
    format_ = models.CharField(max_length=255, help_text="""This indicates the format of the content, which is how the string content should be interpreted. The following values are reserved: SVG, GIF, PNG, JPG, WMF, EMF, BMP. In addition the prefix 'MIME: ' is also reserved. This option can be used as an alternative to express the reserved values above, for example "SVG" could instead be expressed as "MIME: image/svg+xml".""")
    location = models.CharField(max_length=255, help_text="This contains a location that can be used by a tool to locate the image as an alternative to embedding it in the stereotype.")


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

    operation = models.ForeignKey('Operation', help_text="The Operation being invoked.")
    target = models.ForeignKey('InputPin', help_text="The InputPin that provides the target object to which the Operation call request is sent.")

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Operation being called.
        """
        # OCL:
        #     result = (operation.inputParameters())
        pass


class ReadStructuralFeatureAction(StructuralFeatureAction):
    """
    A ReadStructuralFeatureAction is a StructuralFeatureAction that retrieves the
    values of a StructuralFeature.
    """

    result = models.ForeignKey('OutputPin')


class Component(Class):
    """
    A Component represents a modular part of a system that encapsulates its contents
    and whose manifestation is replaceable within its environment.
    """

    is_indirectly_instantiated = models.BooleanField(help_text="If true, the Component is defined at design-time, but at run-time (or execution-time) an object specified by the Component does not exist, that is, the Component is instantiated indirectly, through the instantiation of its realizing Classifiers or parts.")
    packaged_element = models.ForeignKey('PackageableElement', help_text="The set of PackageableElements that a Component owns. In the namespace of a Component, all model elements that are involved in or related to its definition may be owned or imported explicitly. These may include e.g., Classes, Interfaces, Components, Packages, UseCases, Dependencies (e.g., mappings), and Artifacts.")
    provided = models.ForeignKey('Interface', help_text="The Interfaces that the Component exposes to its environment. These Interfaces may be Realized by the Component or any of its realizingClassifiers, or they may be the Interfaces that are provided by its public Ports.")
    realization = models.ForeignKey('ComponentRealization', help_text="The set of Realizations owned by the Component. Realizations reference the Classifiers of which the Component is an abstraction; i.e., that realize its behavior.")
    required = models.ForeignKey('Interface', help_text="The Interfaces that the Component requires from other Components in its environment in order to be able to offer its full set of provided functionality. These Interfaces may be used by the Component or any of its realizingClassifiers, or they may be the Interfaces that are required by its public Ports.")

    def required_operation(self):
        """
        Derivation for Component::/required
        """
        # OCL:
        """    result = (let 	uis : Set(Interface) = allUsedInterfaces(),
                    realizingClassifiers : Set(Classifier) = self.realization.realizingClassifier->union(self.allParents()->collect(realization.realizingClassifier))->asSet(),
                    allRealizingClassifiers : Set(Classifier) = realizingClassifiers->union(realizingClassifiers.allParents())->asSet(),
                    realizingClassifierInterfaces : Set(Interface) = allRealizingClassifiers->iterate(c; rci : Set(Interface) = Set{} | rci->union(c.allUsedInterfaces())),
                    ports : Set(Port) = self.ownedPort->union(allParents()->collect(ownedPort))->asSet(),
                    usedByPorts : Set(Interface) = ports.required->asSet()
            in	    uis->union(realizingClassifierInterfaces)->union(usedByPorts)->asSet()
            )"""
        pass


class Port(Property):
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

    is_behavior = models.BooleanField(help_text="Specifies whether requests arriving at this Port are sent to the classifier behavior of this EncapsulatedClassifier. Such a Port is referred to as a behavior Port. Any invocation of a BehavioralFeature targeted at a behavior Port will be handled by the instance of the owning EncapsulatedClassifier itself, rather than by any instances that it may contain.")
    is_conjugated = models.BooleanField(help_text="Specifies the way that the provided and required Interfaces are derived from the Port's Type.")
    is_service = models.BooleanField(help_text="If true, indicates that this Port is used to provide the published functionality of an EncapsulatedClassifier.  If false, this Port is used to implement the EncapsulatedClassifier but is not part of the essential externally-visible functionality of the EncapsulatedClassifier and can, therefore, be altered or deleted along with the internal implementation of the EncapsulatedClassifier and other properties that are considered part of its implementation.")
    protocol = models.ForeignKey('ProtocolStateMachine', help_text="An optional ProtocolStateMachine which describes valid interactions at this interaction point.")
    provided = models.ForeignKey('Interface', help_text="The Interfaces specifying the set of Operations and Receptions that the EncapsulatedCclassifier offers to its environment via this Port, and which it will handle either directly or by forwarding it to a part of its internal structure. This association is derived according to the value of isConjugated. If isConjugated is false, provided is derived as the union of the sets of Interfaces realized by the type of the port and its supertypes, or directly from the type of the Port if the Port is typed by an Interface. If isConjugated is true, it is derived as the union of the sets of Interfaces used by the type of the Port and its supertypes.")
    redefined_port = models.ForeignKey('self', help_text="A Port may be redefined when its containing EncapsulatedClassifier is specialized. The redefining Port may have additional Interfaces to those that are associated with the redefined Port or it may replace an Interface by one of its subtypes.")
    required = models.ForeignKey('Interface', help_text="The Interfaces specifying the set of Operations and Receptions that the EncapsulatedCassifier expects its environment to handle via this port. This association is derived according to the value of isConjugated. If isConjugated is false, required is derived as the union of the sets of Interfaces used by the type of the Port and its supertypes. If isConjugated is true, it is derived as the union of the sets of Interfaces realized by the type of the Port and its supertypes, or directly from the type of the Port if the Port is typed by an Interface.")

    def basic_provided(self):
        """
        The union of the sets of Interfaces realized by the type of the Port and its
        supertypes, or directly the type of the Port if the Port is typed by an
        Interface.
        """
        # OCL:
        """    result = (if type.oclIsKindOf(Interface) 
            then type.oclAsType(Interface)->asSet() 
            else type.oclAsType(Classifier).allRealizedInterfaces() 
            endif)"""
        pass


class DeploymentSpecification(Artifact):
    """
    A deployment specification specifies a set of properties that determine
    execution parameters of a component artifact that is deployed on a node. A
    deployment specification can be aimed at a specific type of container. An
    artifact that reifies or implements deployment specification properties is a
    deployment descriptor.
    """

    deployment = models.ForeignKey('Deployment', help_text="The deployment with which the DeploymentSpecification is associated.")
    deployment_location = models.CharField(max_length=255, help_text="The location where an Artifact is deployed onto a Node. This is typically a 'directory' or 'memory address.'")
    execution_location = models.CharField(max_length=255, help_text="The location where a component Artifact executes. This may be a local or remote location.")


class Device(Node):
    """
    A device is a physical computational resource with processing capability upon
    which artifacts may be deployed for execution. Devices may be complex (i.e.,
    they may consist of other devices).
    """

    pass


class Region(Namespace, RedefinableElement):
    """
    A Region is a top-level part of a StateMachine or a composite State, that serves
    as a container for the Vertices and Transitions of the StateMachine. A
    StateMachine or composite State may contain multiple Regions representing
    behaviors that may occur in parallel.
    """

    extended_region = models.ForeignKey('self', help_text="The region of which this region is an extension.")
    state = models.ForeignKey('State', help_text="The State that owns the Region. If a Region is owned by a State, then it cannot also be owned by a StateMachine.")
    state_machine = models.ForeignKey('StateMachine', help_text="The StateMachine that owns the Region. If a Region is owned by a StateMachine, then it cannot also be owned by a State.")
    subvertex = models.ForeignKey('Vertex', help_text="The set of Vertices that are owned by this Region.")
    transition = models.ForeignKey('Transition', help_text="The set of Transitions owned by the Region.")

    def __init__(self, *args, **kwargs):
        super(Region).__init__(*args, **kwargs)

    def belongs_to_psm(self):
        """
        The operation belongsToPSM () checks if the Region belongs to a
        ProtocolStateMachine.
        """
        # OCL:
        """    result = (if  stateMachine <> null 
            then
              stateMachine.oclIsKindOf(ProtocolStateMachine)
            else 
              state <> null  implies  state.container.belongsToPSM()
            endif )"""
        pass


class ConsiderIgnoreFragment(CombinedFragment):
    """
    A ConsiderIgnoreFragment is a kind of CombinedFragment that is used for the
    consider and ignore cases, which require lists of pertinent Messages to be
    specified.
    """

    message = models.ForeignKey('NamedElement')


class Generalization(DirectedRelationship):
    """
    A Generalization is a taxonomic relationship between a more general Classifier
    and a more specific Classifier. Each instance of the specific Classifier is also
    an instance of the general Classifier. The specific Classifier inherits the
    features of the more general Classifier. A Generalization is owned by the
    specific Classifier.
    """

    general = models.ForeignKey('Classifier', help_text="The general classifier in the Generalization relationship.")
    generalization_set = models.ForeignKey('GeneralizationSet', help_text="Represents a set of instances of Generalization.  A Generalization may appear in many GeneralizationSets.")
    is_substitutable = models.BooleanField(help_text="Indicates whether the specific Classifier can be used wherever the general Classifier can be used. If true, the execution traces of the specific Classifier shall be a superset of the execution traces of the general Classifier. If false, there is no such constraint on execution traces. If unset, the modeler has not stated whether there is such a constraint or not.")
    specific = models.ForeignKey('Classifier', help_text="The specializing Classifier in the Generalization relationship.")


class InitialNode(ControlNode):
    """
    An InitialNode is a ControlNode that offers a single control token when
    initially enabled.
    """

    pass


class CollaborationUse(NamedElement):
    """
    A CollaborationUse is used to specify the application of a pattern specified by
    a Collaboration to a specific situation.
    """

    role_binding = models.ForeignKey('Dependency', help_text="A mapping between features of the Collaboration and features of the owning Classifier. This mapping indicates which ConnectableElement of the Classifier plays which role(s) in the Collaboration. A ConnectableElement may be bound to multiple roles in the same CollaborationUse (that is, it may play multiple roles).")
    type_ = models.ForeignKey('Collaboration', help_text="The Collaboration which is used in this CollaborationUse. The Collaboration defines the cooperation between its roles which are mapped to ConnectableElements relating to the Classifier owning the CollaborationUse.")


class Duration(ValueSpecification):
    """
    A Duration is a ValueSpecification that specifies the temporal distance between
    two time instants.
    """

    expr = models.ForeignKey('ValueSpecification', help_text="A ValueSpecification that evaluates to the value of the Duration.")
    observation = models.ForeignKey('Observation', help_text="Refers to the Observations that are involved in the computation of the Duration value")


class Continuation(InteractionFragment):
    """
    A Continuation is a syntactic way to define continuations of different branches
    of an alternative CombinedFragment. Continuations are intuitively similar to
    labels representing intermediate points in a flow of control.
    """

    setting = models.BooleanField()


class ExpansionRegion(StructuredActivityNode):
    """
    An ExpansionRegion is a StructuredActivityNode that executes its content
    multiple times corresponding to elements of input collection(s).
    """

    input_element = models.ForeignKey('ExpansionNode', help_text="The ExpansionNodes that hold the input collections for the ExpansionRegion.")
    mode = models.ForeignKey('ExpansionKind', help_text="The mode in which the ExpansionRegion executes its contents. If parallel, executions are concurrent. If iterative, executions are sequential. If stream, a stream of values flows into a single execution.")
    output_element = models.ForeignKey('ExpansionNode', help_text="The ExpansionNodes that form the output collections of the ExpansionRegion.")


class FunctionBehavior(OpaqueBehavior):
    """
    A FunctionBehavior is an OpaqueBehavior that does not access or modify any
    objects or other external data.
    """


    def has_all_data_type_attributes(self):
        """
        The hasAllDataTypeAttributes query tests whether the types of the attributes of
        the given DataType are all DataTypes, and similarly for all those DataTypes.
        """
        # OCL:
        """    result = (d.ownedAttribute->forAll(a |
                a.type.oclIsKindOf(DataType) and
                  hasAllDataTypeAttributes(a.type.oclAsType(DataType))))"""
        pass


class OperationTemplateParameter(TemplateParameter):
    """
    An OperationTemplateParameter exposes an Operation as a formal parameter for a
    template.
    """


    def __init__(self, *args, **kwargs):
        super(OperationTemplateParameter).__init__(*args, **kwargs)
    pass


class DurationObservation(Observation):
    """
    A DurationObservation is a reference to a duration during an execution. It
    points out the NamedElement(s) in the model to observe and whether the
    observations are when this NamedElement is entered or when it is exited.
    """

    event = models.ForeignKey('NamedElement', help_text="The DurationObservation is determined as the duration between the entering or exiting of a single event Element during execution, or the entering/exiting of one event Element and the entering/exiting of a second.")
    first_event = models.BooleanField(help_text="The value of firstEvent[i] is related to event[i] (where i is 1 or 2). If firstEvent[i] is true, then the corresponding observation event is the first time instant the execution enters event[i]. If firstEvent[i] is false, then the corresponding observation event is the time instant the execution exits event[i].")


class AssociationClass(Class, Association):
    """
    A model element that has both Association and Class properties. An
    AssociationClass can be seen as an Association that also has Class properties,
    or as a Class that also has Association properties. It not only connects a set
    of Classifiers but also defines a set of Features that belong to the Association
    itself and not to any of the associated Classifiers.
    """

    pass


class Actor(BehavioredClassifier):
    """
    An Actor specifies a role played by a user or any other system that interacts
    with the subject.
    """

    pass


class Extension(Association):
    """
    An extension is used to indicate that the properties of a metaclass are extended
    through a stereotype, and gives the ability to flexibly add (and later remove)
    stereotypes to classes.
    """

    is_required = models.BooleanField(help_text="Indicates whether an instance of the extending stereotype must be created when an instance of the extended class is created. The attribute value is derived from the value of the lower property of the ExtensionEnd referenced by Extension::ownedEnd; a lower value of 1 means that isRequired is true, but otherwise it is false. Since the default value of ExtensionEnd::lower is 0, the default value of isRequired is false.")
    metaclass = models.ForeignKey('Class', help_text="References the Class that is extended through an Extension. The property is derived from the type of the memberEnd that is not the ownedEnd.")

    def __init__(self, *args, **kwargs):
        super(Extension).__init__(*args, **kwargs)

    def metaclass_operation(self):
        """
        The query metaclass() returns the metaclass that is being extended (as opposed
        to the extending stereotype).
        """
        # OCL:
        #     result = (metaclassEnd().type.oclAsType(Class))
        pass


class DestroyObjectAction(Action):
    """
    A DestroyObjectAction is an Action that destroys objects.
    """

    is_destroy_links = models.BooleanField(help_text="Specifies whether links in which the object participates are destroyed along with the object.")
    is_destroy_owned_objects = models.BooleanField(help_text="Specifies whether objects owned by the object (via composition) are destroyed along with the object.")
    target = models.ForeignKey('InputPin', help_text="The InputPin providing the object to be destroyed.")


class ConditionalNode(StructuredActivityNode):
    """
    A ConditionalNode is a StructuredActivityNode that chooses one among some number
    of alternative collections of ExecutableNodes to execute.
    """

    clause = models.ForeignKey('Clause', help_text="The set of Clauses composing the ConditionalNode.")
    is_assured = models.BooleanField(help_text="If true, the modeler asserts that the test for at least one Clause of the ConditionalNode will succeed.")
    is_determinate = models.BooleanField(help_text="If true, the modeler asserts that the test for at most one Clause of the ConditionalNode will succeed.")

    def __init__(self, *args, **kwargs):
        super(ConditionalNode).__init__(*args, **kwargs)

    def all_actions(self):
        """
        Return only this ConditionalNode. This prevents Actions within the
        ConditionalNode from having their OutputPins used as bodyOutputs or decider Pins
        in containing LoopNodes or ConditionalNodes.
        """
        # OCL:
        #     result = (self->asSet())
        pass


class ReadLinkAction(LinkAction):
    """
    A ReadLinkAction is a LinkAction that navigates across an Association to
    retrieve the objects on one end.
    """

    result = models.ForeignKey('OutputPin')

    def open_end(self):
        """
        Returns the ends corresponding to endData with no value InputPin. (A well-formed
        ReadLinkAction is constrained to have only one of these.)
        """
        # OCL:
        #     result = (endData->select(value=null).end->asOrderedSet())
        pass


class CallConcurrencyKind(Enumeration):
    """
    CallConcurrencyKind is an Enumeration used to specify the semantics of
    concurrent calls to a BehavioralFeature.
    """

    SEQUENTIAL = 'sequential'
    GUARDED = 'guarded'
    CONCURRENT = 'concurrent'
    CHOICES = (
        (SEQUENTIAL, 'No concurrency management mechanism is associated with the BehavioralFeature and, therefore, concurrency conflicts may occur. Instances that invoke a BehavioralFeature need to coordinate so that only one invocation to a target on any BehavioralFeature occurs at once.'),
        (GUARDED, 'Multiple invocations of a BehavioralFeature that overlap in time may occur to one instance, but only one is allowed to commence. The others are blocked until the performance of the currently executing BehavioralFeature is complete. It is the responsibility of the system designer to ensure that deadlocks do not occur due to simultaneous blocking.'),
        (CONCURRENT, 'Multiple invocations of a BehavioralFeature that overlap in time may occur to one instance and all of them may proceed concurrently.'),
    )

    call_concurrency_kind = models.CharField(max_length=255, choices=CHOICES, default=CONCURRENT)


class ReplyAction(Action):
    """
    A ReplyAction is an Action that accepts a set of reply values and a value
    containing return information produced by a previous AcceptCallAction. The
    ReplyAction returns the values to the caller of the previous call, completing
    execution of the call.
    """

    reply_to_call = models.ForeignKey('Trigger', help_text="The Trigger specifying the Operation whose call is being replied to.")
    reply_value = models.ForeignKey('InputPin', help_text="A list of InputPins providing the values for the output (inout, out, and return) Parameters of the Operation. These values are returned to the caller.")
    return_information = models.ForeignKey('InputPin', help_text="An InputPin that holds the return information value produced by an earlier AcceptCallAction.")


class ReadLinkObjectEndQualifierAction(Action):
    """
    A ReadLinkObjectEndQualifierAction is an Action that retrieves a qualifier end
    value from a link object.
    """

    object_ = models.ForeignKey('InputPin', help_text="The InputPin from which the link object is obtained.")
    qualifier = models.ForeignKey('Property', help_text="The qualifier Property to be read.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPin where the result value is placed.")


class SendObjectAction(InvocationAction):
    """
    A SendObjectAction is an InvocationAction that transmits an input object to the
    target object, which is handled as a request message by the target object. The
    requestor continues execution immediately after the object is sent out and
    cannot receive reply values.
    """

    target = models.ForeignKey('InputPin', help_text="The target object to which the object is sent.")

    def __init__(self, *args, **kwargs):
        super(SendObjectAction).__init__(*args, **kwargs)


class ExtensionPoint(RedefinableElement):
    """
    An ExtensionPoint identifies a point in the behavior of a UseCase where that
    behavior can be extended by the behavior of some other (extending) UseCase, as
    specified by an Extend relationship.
    """

    use_case = models.ForeignKey('UseCase')


class UnmarshallAction(Action):
    """
    An UnmarshallAction is an Action that retrieves the values of the
    StructuralFeatures of an object and places them on OutputPins.
    """

    object_ = models.ForeignKey('InputPin', help_text="The InputPin that gives the object to be unmarshalled.")
    result = models.ForeignKey('OutputPin', help_text="The OutputPins on which are placed the values of the StructuralFeatures of the input object.")
    unmarshall_type = models.ForeignKey('Classifier', help_text="The type of the object to be unmarshalled.")


class Interaction(InteractionFragment, Behavior):
    """
    An Interaction is a unit of Behavior that focuses on the observable exchange of
    information between connectable elements.
    """

    action = models.ForeignKey('Action', help_text="Actions owned by the Interaction.")
    formal_gate = models.ForeignKey('Gate', help_text="Specifies the gates that form the message interface between this Interaction and any InteractionUses which reference it.")
    fragment = models.ForeignKey('InteractionFragment', help_text="The ordered set of fragments in the Interaction.")
    lifeline = models.ForeignKey('Lifeline', help_text="Specifies the participants in this Interaction.")
    message = models.ForeignKey('Message', help_text="The Messages contained in this Interaction.")


class PackageImport(DirectedRelationship):
    """
    A PackageImport is a Relationship that imports all the non-private members of a
    Package into the Namespace owning the PackageImport, so that those Elements may
    be referred to by their unqualified names in the importingNamespace.
    """

    imported_package = models.ForeignKey('Package', help_text="Specifies the Package whose members are imported into a Namespace.")
    importing_namespace = models.ForeignKey('Namespace', help_text="Specifies the Namespace that imports the members from a Package.")
    visibility = models.ForeignKey('VisibilityKind', help_text="Specifies the visibility of the imported PackageableElements within the importingNamespace, i.e., whether imported Elements will in turn be visible to other Namespaces. If the PackageImport is public, the imported Elements will be visible outside the importingNamespace, while, if the PackageImport is private, they will not.")


class ChangeEvent(Event):
    """
    A ChangeEvent models a change in the system configuration that makes a condition
    true.
    """

    change_expression = models.ForeignKey('ValueSpecification')


class OpaqueExpression(ValueSpecification):
    """
    An OpaqueExpression is a ValueSpecification that specifies the computation of a
    collection of values either in terms of a UML Behavior or based on a textual
    statement in a language other than UML
    """

    behavior = models.ForeignKey('Behavior', help_text="Specifies the behavior of the OpaqueExpression as a UML Behavior.")
    body = models.CharField(max_length=255, help_text="A textual definition of the behavior of the OpaqueExpression, possibly in multiple languages.")
    language = models.CharField(max_length=255, help_text="Specifies the languages used to express the textual bodies of the OpaqueExpression.  Languages are matched to body Strings by order. The interpretation of the body depends on the languages. If the languages are unspecified, they may be implicit from the expression body or the context.")
    result = models.ForeignKey('Parameter', help_text="If an OpaqueExpression is specified using a UML Behavior, then this refers to the single required return Parameter of that Behavior. When the Behavior completes execution, the values on this Parameter give the result of evaluating the OpaqueExpression.")

    def is_integral(self):
        """
        The query isIntegral() tells whether an expression is intended to produce an
        Integer.
        """
        # OCL:
        #     result = (false)
        pass


class TimeEvent(Event):
    """
    A TimeEvent is an Event that occurs at a specific point in time.
    """

    is_relative = models.BooleanField(help_text="Specifies whether the TimeEvent is specified as an absolute or relative time.")
    when = models.ForeignKey('TimeExpression', help_text="Specifies the time of the TimeEvent.")


class RemoveVariableValueAction(WriteVariableAction):
    """
    A RemoveVariableValueAction is a WriteVariableAction that removes values from a
    Variables.
    """

    is_remove_duplicates = models.BooleanField(help_text="Specifies whether to remove duplicates of the value in nonunique Variables.")
    remove_at = models.ForeignKey('InputPin', help_text="An InputPin that provides the position of an existing value to remove in ordered, nonunique Variables. The type of the removeAt InputPin is UnlimitedNatural, but the value cannot be zero or unlimited.")


class InputPin(Pin):
    """
    An InputPin is a Pin that holds input values to be consumed by an Action.
    """

    pass


class TimeExpression(ValueSpecification):
    """
    A TimeExpression is a ValueSpecification that represents a time value.
    """

    expr = models.ForeignKey('ValueSpecification', help_text="A ValueSpecification that evaluates to the value of the TimeExpression.")
    observation = models.ForeignKey('Observation', help_text="Refers to the Observations that are involved in the computation of the TimeExpression value.")


class ClearVariableAction(VariableAction):
    """
    A ClearVariableAction is a VariableAction that removes all values of a Variable.
    """

    pass


class Transition(Namespace, RedefinableElement):
    """
    A Transition represents an arc between exactly one source Vertex and exactly one
    Target vertex (the source and targets may be the same Vertex). It may form part
    of a compound transition, which takes the StateMachine from one steady State
    configuration to another, representing the full response of the StateMachine to
    an occurrence of an Event that triggered it.
    """

    container = models.ForeignKey('Region', help_text="Designates the Region that owns this Transition.")
    effect = models.ForeignKey('Behavior', help_text="Specifies an optional behavior to be performed when the Transition fires.")
    guard = models.ForeignKey('Constraint', help_text="A guard is a Constraint that provides a fine-grained control over the firing of the Transition. The guard is evaluated when an Event occurrence is dispatched by the StateMachine. If the guard is true at that time, the Transition may be enabled, otherwise, it is disabled. Guards should be pure expressions without side effects. Guard expressions with side effects are ill formed.")
    kind = models.ForeignKey('TransitionKind', help_text="Indicates the precise type of the Transition.")
    redefined_transition = models.ForeignKey('self', help_text="The Transition that is redefined by this Transition.")
    source = models.ForeignKey('Vertex', help_text="Designates the originating Vertex (State or Pseudostate) of the Transition.")
    target = models.ForeignKey('Vertex', help_text="Designates the target Vertex that is reached when the Transition is taken.")
    trigger = models.ForeignKey('Trigger', help_text="Specifies the Triggers that may fire the transition.")

    def __init__(self, *args, **kwargs):
        super(Transition).__init__(*args, **kwargs)

    def containing_state_machine(self):
        """
        The query containingStateMachine() returns the StateMachine that contains the
        Transition either directly or transitively.
        """
        # OCL:
        #     result = (container.containingStateMachine())
        pass


class ActivityPartition(ActivityGroup):
    """
    An ActivityPartition is a kind of ActivityGroup for identifying ActivityNodes
    that have some characteristic in common.
    """

    edge = models.ForeignKey('ActivityEdge', help_text="ActivityEdges immediately contained in the ActivityPartition.")
    is_dimension = models.BooleanField(help_text="Indicates whether the ActivityPartition groups other ActivityPartitions along a dimension.")
    is_external = models.BooleanField(help_text="Indicates whether the ActivityPartition represents an entity to which the partitioning structure does not apply.")
    node = models.ForeignKey('ActivityNode', help_text="ActivityNodes immediately contained in the ActivityPartition.")
    represents = models.ForeignKey('Element', help_text="An Element represented by the functionality modeled within the ActivityPartition.")
    subpartition = models.ForeignKey('self', help_text="Other ActivityPartitions immediately contained in this ActivityPartition (as its subgroups).")
    super_partition = models.ForeignKey('self', help_text="Other ActivityPartitions immediately containing this ActivityPartition (as its superGroups).")


class FlowFinalNode(FinalNode):
    """
    A FlowFinalNode is a FinalNode that terminates a flow by consuming the tokens
    offered to it.
    """

    pass


class ActivityParameterNode(ObjectNode):
    """
    An ActivityParameterNode is an ObjectNode for accepting values from the input
    Parameters or providing values to the output Parameters of an Activity.
    """

    parameter = models.ForeignKey('Parameter')


class ParameterSet(NamedElement):
    """
    A ParameterSet designates alternative sets of inputs or outputs that a Behavior
    may use.
    """

    condition = models.ForeignKey('Constraint', help_text="A constraint that should be satisfied for the owner of the Parameters in an input ParameterSet to start execution using the values provided for those Parameters, or the owner of the Parameters in an output ParameterSet to end execution providing the values for those Parameters, if all preconditions and conditions on input ParameterSets were satisfied.")
    parameter = models.ForeignKey('Parameter', help_text="Parameters in the ParameterSet.")


class VisibilityKind(Enumeration):
    """
    VisibilityKind is an enumeration type that defines literals to determine the
    visibility of Elements in a model.
    """

    PACKAGE = 'package'
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'
    CHOICES = (
        (PACKAGE, 'A NamedElement with package visibility is visible to all Elements within the nearest enclosing Package (given that other owning Elements have proper visibility). Outside the nearest enclosing Package, a NamedElement marked as having package visibility is not visible.  Only NamedElements that are not owned by Packages can be marked as having package visibility.'),
        (PUBLIC, 'A Named Element with public visibility is visible to all elements that can access the contents of the Namespace that owns it.'),
        (PRIVATE, 'A NamedElement with private visibility is only visible inside the Namespace that owns it.'),
        (PROTECTED, 'A NamedElement with protected visibility is visible to Elements that have a generalization relationship to the Namespace that owns it.'),
    )

    visibility_kind = models.CharField(max_length=255, choices=CHOICES, default=PROTECTED)


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

    behavior = models.ForeignKey('Behavior')

    def input_parameters(self):
        """
        Return the in and inout ownedParameters of the Behavior being called.
        """
        # OCL:
        #     result = (behavior.inputParameters())
        pass


class Include(DirectedRelationship, NamedElement):
    """
    An Include relationship specifies that a UseCase contains the behavior defined
    in another UseCase.
    """

    addition = models.ForeignKey('UseCase', help_text="The UseCase that is to be included.")
    including_case = models.ForeignKey('UseCase', help_text="The UseCase which includes the addition and owns the Include relationship.")


class TimeInterval(Interval):
    """
    A TimeInterval defines the range between two TimeExpressions.
    """


    def __init__(self, *args, **kwargs):
        super(TimeInterval).__init__(*args, **kwargs)
    pass


class ConnectionPointReference(Vertex):
    """
    A ConnectionPointReference represents a usage (as part of a submachine State) of
    an entry/exit point Pseudostate defined in the StateMachine referenced by the
    submachine State.
    """

    entry = models.ForeignKey('Pseudostate', help_text="The entryPoint Pseudostates corresponding to this connection point.")
    exit = models.ForeignKey('Pseudostate', help_text="The exitPoints kind Pseudostates corresponding to this connection point.")
    state = models.ForeignKey('State', help_text="The State in which the ConnectionPointReference is defined.")


class ExpansionKind(Enumeration):
    """
    ExpansionKind is an enumeration type used to specify how an ExpansionRegion
    executes its contents.
    """

    ITERATIVE = 'iterative'
    PARALLEL = 'parallel'
    STREAM = 'stream'
    CHOICES = (
        (ITERATIVE, 'The content of the ExpansionRegion is executed iteratively for the elements of the input collections, in the order of the input elements, if the collections are ordered.'),
        (PARALLEL, 'The content of the ExpansionRegion is executed concurrently for the elements of the input collections.'),
        (STREAM, 'A stream of input collection elements flows into a single execution of the content of the ExpansionRegion, in the order of the collection elements if the input collections are ordered.'),
    )

    expansion_kind = models.CharField(max_length=255, choices=CHOICES, default=STREAM)


class Slot(Element):
    """
    A Slot designates that an entity modeled by an InstanceSpecification has a value
    or values for a specific StructuralFeature.
    """

    defining_feature = models.ForeignKey('StructuralFeature', help_text="The StructuralFeature that specifies the values that may be held by the Slot.")
    owning_instance = models.ForeignKey('InstanceSpecification', help_text="The InstanceSpecification that owns this Slot.")
    value = models.ForeignKey('ValueSpecification', help_text="The value or values held by the Slot.")


class ComponentRealization(Realization):
    """
    Realization is specialized to (optionally) define the Classifiers that realize
    the contract offered by a Component in terms of its provided and required
    Interfaces. The Component forms an abstraction from these various Classifiers.
    """

    abstraction = models.ForeignKey('Component', help_text="The Component that owns this ComponentRealization and which is implemented by its realizing Classifiers.")
    realizing_classifier = models.ForeignKey('Classifier', help_text="The Classifiers that are involved in the implementation of the Component that owns this Realization.")


class OpaqueAction(Action):
    """
    An OpaqueAction is an Action whose functionality is not specified within UML.
    """

    body = models.CharField(max_length=255, help_text="Provides a textual specification of the functionality of the Action, in one or more languages other than UML.")
    input_value = models.ForeignKey('InputPin', help_text="The InputPins providing inputs to the OpaqueAction.")
    language = models.CharField(max_length=255, help_text="If provided, a specification of the language used for each of the body Strings.")
    output_value = models.ForeignKey('OutputPin', help_text="The OutputPins on which the OpaqueAction provides outputs.")


class ObjectNodeOrderingKind(Enumeration):
    """
    ObjectNodeOrderingKind is an enumeration indicating queuing order for offering
    the tokens held by an ObjectNode.
    """

    LIFO = 'lifo'
    UNORDERED = 'unordered'
    FIFO = 'fifo'
    ORDERED = 'ordered'
    CHOICES = (
        (LIFO, 'Indicates that tokens are queued in a last in, first out manner.'),
        (UNORDERED, 'Indicates that tokens are unordered.'),
        (FIFO, 'Indicates that tokens are queued in a first in, first out manner.'),
        (ORDERED, 'Indicates that tokens are ordered.'),
    )

    object_node_ordering_kind = models.CharField(max_length=255, choices=CHOICES, default=ORDERED)


class CentralBufferNode(ObjectNode):
    """
    A CentralBufferNode is an ObjectNode for managing flows from multiple sources
    and targets.
    """

    pass


class DataStoreNode(CentralBufferNode):
    """
    A DataStoreNode is a CentralBufferNode for persistent data.
    """

    pass


class ValueSpecificationAction(Action):
    """
    A ValueSpecificationAction is an Action that evaluates a ValueSpecification and
    provides a result.
    """

    result = models.ForeignKey('OutputPin', help_text="The OutputPin on which the result value is placed.")
    value = models.ForeignKey('ValueSpecification', help_text="The ValueSpecification to be evaluated.")


class SignalEvent(MessageEvent):
    """
    A SignalEvent represents the receipt of an asynchronous Signal instance.
    """

    signal = models.ForeignKey('Signal')


class StateInvariant(InteractionFragment):
    """
    A StateInvariant is a runtime constraint on the participants of the Interaction.
    It may be used to specify a variety of different kinds of Constraints, such as
    values of Attributes or Variables, internal or external States, and so on. A
    StateInvariant is an InteractionFragment and it is placed on a Lifeline.
    """

    invariant = models.ForeignKey('Constraint', help_text="A Constraint that should hold at runtime for this StateInvariant.")

    def __init__(self, *args, **kwargs):
        super(StateInvariant).__init__(*args, **kwargs)


class Variable(ConnectableElement, MultiplicityElement):
    """
    A Variable is a ConnectableElement that may store values during the execution of
    an Activity. Reading and writing the values of a Variable provides an
    alternative means for passing data than the use of ObjectFlows. A Variable may
    be owned directly by an Activity, in which case it is accessible from anywhere
    within that activity, or it may be owned by a StructuredActivityNode, in which
    case it is only accessible within that node.
    """

    activity_scope = models.ForeignKey('Activity', help_text="An Activity that owns the Variable.")
    scope = models.ForeignKey('StructuredActivityNode', help_text="A StructuredActivityNode that owns the Variable.")

    def is_accessible_by(self):
        """
        A Variable is accessible by Actions within its scope (the Activity or
        StructuredActivityNode that owns it).
        """
        # OCL:
        """    result = (if scope<>null then scope.allOwnedNodes()->includes(a)
            else a.containingActivity()=activityScope
            endif)"""
        pass


class Profile(Package):
    """
    A profile defines limited extensions to a reference metamodel with the purpose
    of adapting the metamodel to a specific platform or domain.
    """

    metaclass_reference = models.ForeignKey('ElementImport', help_text="References a metaclass that may be extended.")
    metamodel_reference = models.ForeignKey('PackageImport', help_text="References a package containing (directly or indirectly) metaclasses that may be extended.")


class DecisionNode(ControlNode):
    """
    A DecisionNode is a ControlNode that chooses between outgoing ActivityEdges for
    the routing of tokens.
    """

    decision_input = models.ForeignKey('Behavior', help_text="A Behavior that is executed to provide an input to guard ValueSpecifications on ActivityEdges outgoing from the DecisionNode.")
    decision_input_flow = models.ForeignKey('ObjectFlow', help_text="An additional ActivityEdge incoming to the DecisionNode that provides a decision input value for the guards ValueSpecifications on ActivityEdges outgoing from the DecisionNode.")


class ForkNode(ControlNode):
    """
    A ForkNode is a ControlNode that splits a flow into multiple concurrent flows.
    """

    pass


class Substitution(Realization):
    """
    A substitution is a relationship between two classifiers signifying that the
    substituting classifier complies with the contract specified by the contract
    classifier. This implies that instances of the substituting classifier are
    runtime substitutable where instances of the contract classifier are expected.
    """

    contract = models.ForeignKey('Classifier', help_text="The contract with which the substituting classifier complies.")
    substituting_classifier = models.ForeignKey('Classifier', help_text="Instances of the substituting classifier are runtime substitutable where instances of the contract classifier are expected.")


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

    conveyed = models.ForeignKey('Classifier', help_text="Specifies the information items that may circulate on this information flow.")
    information_source = models.ForeignKey('NamedElement', help_text="Defines from which source the conveyed InformationItems are initiated.")
    information_target = models.ForeignKey('NamedElement', help_text="Defines to which target the conveyed InformationItems are directed.")
    realization = models.ForeignKey('Relationship', help_text="Determines which Relationship will realize the specified flow.")
    realizing_activity_edge = models.ForeignKey('ActivityEdge', help_text="Determines which ActivityEdges will realize the specified flow.")
    realizing_connector = models.ForeignKey('Connector', help_text="Determines which Connectors will realize the specified flow.")
    realizing_message = models.ForeignKey('Message', help_text="Determines which Messages will realize the specified flow.")


class ProtocolTransition(Transition):
    """
    A ProtocolTransition specifies a legal Transition for an Operation. Transitions
    of ProtocolStateMachines have the following information: a pre-condition
    (guard), a Trigger, and a post-condition. Every ProtocolTransition is associated
    with at most one BehavioralFeature belonging to the context Classifier of the
    ProtocolStateMachine.
    """

    post_condition = models.ForeignKey('Constraint', help_text="Specifies the post condition of the Transition which is the Condition that should be obtained once the Transition is triggered. This post condition is part of the post condition of the Operation connected to the Transition.")
    pre_condition = models.ForeignKey('Constraint', help_text="Specifies the precondition of the Transition. It specifies the Condition that should be verified before triggering the Transition. This guard condition added to the source State will be evaluated as part of the precondition of the Operation referred by the Transition if any.")
    referred = models.ForeignKey('Operation', help_text="This association refers to the associated Operation. It is derived from the Operation of the CallEvent Trigger when applicable.")

    def referred_operation(self):
        """
        Derivation for ProtocolTransition::/referred
        """
        # OCL:
        #     result = (trigger->collect(event)->select(oclIsKindOf(CallEvent))->collect(oclAsType(CallEvent).operation)->asSet())
        pass


class ExecutionEnvironment(Node):
    """
    An execution environment is a node that offers an execution environment for
    specific types of components that are deployed on it in the form of executable
    artifacts.
    """

    pass


class ValuePin(InputPin):
    """
    A ValuePin is an InputPin that provides a value by evaluating a
    ValueSpecification.
    """

    value = models.ForeignKey('ValueSpecification')


class ActionInputPin(InputPin):
    """
    An ActionInputPin is a kind of InputPin that executes an Action to determine the
    values to input to another Action.
    """

    from_action = models.ForeignKey('Action')
