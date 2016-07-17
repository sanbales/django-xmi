from django.db import models
from .uml import *


class Expose(Stereotype):
    base__dependency = models.ForeignKey('Dependency')


class Requirement(Stereotype):
    """
    A requirement specifies a capability or condition that must (or should) be
    satisfied. A requirement may specify a function that a system must perform or a
    performance condition that a system must satisfy. Requirements are used to
    establish a contract between the customer (or other stakeholder) and those
    responsible for designing and implementing the system.
    """
    text = models.CharField(max_length=255, help_text="The textual representation or a reference to the textual representation of the requirement.")
    satisfied_by = models.ForeignKey('NamedElement', help_text="Derived from all elements that are the client of a 'satisfy' relationship for which this requirement is a supplier.")
    refined_by = models.ForeignKey('NamedElement', help_text="Derived from all elements that are the client of a 'refine' relationship for which this requirement is a supplier.")
    master = models.ForeignKey('self', help_text="This is a derived property that lists the master requirement for this slave requirement. The master attribute is derived from the supplier of the Copy dependency that has this requirement as the slave.")
    id = models.CharField(max_length=255, help_text="The unique id of the requirement.")
    derived_from = models.ForeignKey('self', help_text="Derived from all requirements that are the supplier of a 'deriveReqt' relationship for which this requirement is a client.")
    base__class = models.ForeignKey('Class')
    verified_by = models.ForeignKey('NamedElement', help_text="Derived from all elements that are the client of a 'verify' relationship for which this requirement is a supplier.")
    derived = models.ForeignKey('self', help_text="Derived from all requirements that are the client of a 'deriveReqt' relationship for which this requirement is a supplier.")
    traced_to = models.ForeignKey('NamedElement', help_text="Derived from all elements that are the client of a 'trace' relationship for which this requirement is a supplier.")


class ElementPropertyPath(Stereotype):
    property_path = models.ForeignKey('Property', help_text="The propertyPath list of the NestedConnectorEnd stereotype must identify a path of containing properties that identify the connected property in the context of the block that owns the connector. The ordering of properties is from a property of the block that owns the connector, through a property of each intermediate block that types the preceding property, until a property is reached that contains a connector end property within its type. The connector end property is not included in the propertyPath list, but instead is held by the role property of the UML ConnectorEnd metaclass.")
    base__element = models.ForeignKey('Element')

    class Meta:
        abstract = True


class TriggerOnNestedPort(ElementPropertyPath):
    on_nested_port = models.ForeignKey('Port')
    base__trigger = models.ForeignKey('Trigger')


class ControlValues(Package):
    pass


class View(Stereotype):
    """
    A View is a representation of a whole system or subsystem from the perspective
    of a single viewpoint. Views are allowed to import other elements including
    other packages and other views that conform to the viewpoint.
    """
    view_point = models.ForeignKey('Viewpoint', help_text="The viewpoint for this View, derived from the supplier of the 'conform' dependency whose client is this View.")
    stakeholder = models.ForeignKey('Stakeholder')
    base__class = models.ForeignKey('Class')


class PropertySpecificType(Stereotype):
    """
    The PropertySpecificType stereotype should automatically be applied to the
    classifier which types a property with a propertyspecific type. This classifier
    can contain definitions of new or redefined features which extend the original
    classifier referenced by the property-specific type.
    """
    base__classifier = models.ForeignKey('Classifier')


class FeatureDirection(Enumeration):
    PROVIDEDREQUIRED = 0
    REQUIRED = 1
    PROVIDED = 2
    CHOICES = (
        (PROVIDEDREQUIRED, 'providedRequired'),
        (REQUIRED, 'required'),
        (PROVIDED, 'provided'),
    )

    feature_direction = models.IntegerField(choices=CHOICES, default=PROVIDED)


class NestedConnectorEnd(ElementPropertyPath):
    """
    The NestedConnectorEnd stereotype of UML ConnectorEnd extends a UML ConnectorEnd
    so that the connected property may be identified by a multi-level path of
    accessible properties from the block that owns the connector.
    """
    base__connector_end = models.ForeignKey('ConnectorEnd')


class FlowProperty(Stereotype):
    """
    A FlowProperty signifies a single flow element that can flow to/from a block. A
    flow property's values are either received from or transmitted to an external
    block. Flow properties are defined directly on blocks or flow specifications
    that are those specifications which type the flow ports. Flow properties enable
    item flows across connectors connecting parts of the corresponding block types,
    either directly (in case of the property is defined on the block) or via
    flowPorts. For Block, Data Type, and Value Type properties, setting an 'out'
    FlowProperty value of a block usage on one end of a connector will result in
    assigning the same value of an 'in' FlowProperty of a block usage at the other
    end of the connector, provided the flow properties are matched. Flow properties
    of type Signal imply sending and/or receiving of a signal usage. An 'out'
    FlowProperty of type Signal means that the owning Block may broadcast the signal
    via connectors and an 'in' FlowProperty means that the owning block is able to
    receive the Signal.
    """
    direction = models.ForeignKey('FlowDirection', help_text="Specifies if the property value is received from an external block (direction='in'), transmitted to an external Block (direction='out') or both (direction='inout').")
    base__property = models.ForeignKey('Property')


class FlowPort(Stereotype):
    """
    A FlowPort is an interaction point through which input and/or output of items
    such as data, material, or energy may flow. This enables the owning block to
    declare which items it may exchange with its environment and the interaction
    points through which the exchange is made. We distinguish between atomic flow
    port and a nonatomic flow port. Atomic flow ports relay items that are
    classified by a single Block, ValueType, DataType, or Signal classifier. A
    nonatomic flow port relays items of several types as specified by a
    FlowSpecification. Flow ports and associated flow specifications define 'what
    can flow' between the block and its environment, whereas item flows specify
    'what does flow' in a specific usage context. Flow ports relay items to their
    owning block or to a connector that connects them with their owner's internal
    parts (internal connector).
    """
    direction = models.ForeignKey('FlowDirection', help_text="Indicates the direction in which an atomic flow port relays its items. If the direction is set to 'in,' then the items are relayed from an external connector via the flow port into the flow port's owner (or one of its parts). If the direction is set to 'out,' then the items are relayed from the flow port's owner, via the flow port, through an external connector attached to the flow port. If the direction is set to 'inout,' then items can flow both ways. By default, the value is inout.")
    base__port = models.ForeignKey('Port')
    is_atomic = models.BooleanField(help_text="This is a derived attribute (derived from the flow port's type). For a flow port typed by a flow specification the value of this attribute is False, otherwise the value is True.")


class DirectedRelationshipPropertyPath(Stereotype):
    source_property_path = models.ForeignKey('Property')
    base__directed_relationship = models.ForeignKey('DirectedRelationship')
    target_context = models.ForeignKey('Classifier')
    target_property_path = models.ForeignKey('Property')
    source_context = models.ForeignKey('Classifier')

    class Meta:
        abstract = True


class Allocate(DirectedRelationshipPropertyPath):
    """
    Allocate is a dependency based on UML::abstraction. It is a mechanism for
    associating elements of different types, or in different hierarchies, at an
    abstract level. Allocate is used for assessing user model consistency and
    directing future design activity. It is expected that an 'allocate' relationship
    between model elements is a precursor to a more concrete relationship between
    the elements, their properties, operations, attributes, or sub-classes.
    """
    base__abstraction = models.ForeignKey('Abstraction')


class UnitAndQuantityKind(Package):
    pass


class VerdictKind(Enumeration):
    """
    Type of a return parameter of a TestCase must be VerdictKind, consistent with
    the UML Testing Profile.
    """
    FAIL = 0
    ERROR = 1
    INCONCLUSIVE = 2
    PASS = 3
    CHOICES = (
        (FAIL, 'fail'),
        (ERROR, 'error'),
        (INCONCLUSIVE, 'inconclusive'),
        (PASS, 'pass'),
    )

    verdict_kind = models.IntegerField(choices=CHOICES, default=PASS)


class DirectedFeature(Stereotype):
    base__feature = models.ForeignKey('Feature')
    feature_direction = models.ForeignKey('FeatureDirection')


class BindingConnector(Stereotype):
    """
    A Binding Connector is a connector which specifies that the properties at both
    ends of the connector have equal values. If the properties at the ends of a
    binding connector are typed by a DataType or ValueType, the connector specifies
    that the instances of the properties must hold equal values, recursively through
    any nested properties within the connected properties. If the properties at the
    ends of a binding connector are typed by a Block, the connector specifies that
    the instances of the properties must refer to the same block instance. As with
    any connector owned by a SysML Block, the ends of a binding connector may be
    nested within a multi-level path of properties accessible from the owning block.
    The NestedConnectorEnd stereotype is used to represent such nested ends just as
    for nested ends of other SysML connectors.
    """
    base__connector = models.ForeignKey('Connector')


class Optional(Stereotype):
    """
    When the 'optional' stereotype is applied to parameters, the lower multiplicity
    must be equal to zero. This means the parameter is not required to have a value
    for the activity or any behavior to begin or end execution. Otherwise, the lower
    multiplicity must be greater than zero, which is called 'required.'
    """
    base__parameter = models.ForeignKey('Parameter')


class ProxyPort(Stereotype):
    base__port = models.ForeignKey('Port')


class EndPathMultiplicity(Stereotype):
    upper = models.ForeignKey('UnlimitedNatural', help_text="Gives the maximum number of values of the property at the end of the related bindingPath, for each object reached by navigation along the bindingPath from an instance of the block owning the property to which EndPathMultiplicity is applied.")
    lower = models.ForeignKey('Integer', help_text="Gives the minimum number of values of the property at the end of the related bindingPath, for each object reached by navigation along the bindingPath from an instance of the block owning the property to which EndPathMultiplicity is applied")
    base__property = models.ForeignKey('Property')


class Rationale(Stereotype):
    """
    A Rationale documents the justification for decisions and the requirements,
    design, and other decisions. A Rationale can be attached to any model element
    including relationships. It allows the user, for example, to specify a rationale
    that may reference more detailed documentation such as a trade study or analysis
    report. Rationale is a stereotype of comment and may be attached to any other
    model element in the same manner as a comment.
    """
    base__comment = models.ForeignKey('Comment')


class Block(Stereotype):
    """
    A Block is a modular unit that describes the structure of a system or element.
    It may include both structural and behavioral features, such as properties and
    operations, that represent the state of the system and behavior that the system
    may exhibit. Some of these properties may hold parts of a system, which can also
    be described by blocks. A block may include a structure of connectors between
    its properties to indicate how its parts or other properties relate to one
    another. SysML blocks provide a general-purpose capability to describe the
    architecture of a system. They provide the ability to represent a system
    hierarchy, in which a system at one level is composed of systems at a more basic
    level. They can describe not only the connectivity relationships between the
    systems at any level, but also quantitative values or other information about a
    system. SysML does not restrict the kind of system or system element that may be
    described by a block. Any reusable form of description that may be applied to a
    system or a set of system characteristics may be described by a block. Such
    reusable descriptions, for example, may be applied to purely conceptual aspects
    of a system design, such as relationships that hold between parts or properties
    of a system. Connectors owned by SysML blocks may be used to define
    relationships between parts or other properties of the same containing block.
    The type of a connector or its connected ends may specify the semantic
    interpretation of a specific connector.
    """
    is_encapsulated = models.BooleanField(help_text="If true, then the block is treated as a black box; a part typed by this black box can only be connected via its ports or directly to its outer boundary. If false, or if a value is not present, then connections can be established to elements of its internal structure via deep-nested connector ends.")
    base__class = models.ForeignKey('Class')


class InterfaceBlock(Block):
    pass


class Rate(Stereotype):
    """
    When the 'rate' stereotype is applied to an activity edge, it specifies the
    expected value of the number of objects and values that traverse the edge per
    time interval, that is, the expected value rate at which they leave the source
    node and arrive at the target node. It does not refer to the rate at which a
    value changes over time. When the stereotype is applied to a parameter, the
    parameter must be streaming, and the stereotype gives the number of objects or
    values that flow in or out of the parameter per time interval while the behavior
    or operation is executing. Streaming is a characteristic of UML behavior
    parameters that supports the input and output of items while a behavior is
    executing, rather than only when the behavior starts and stops. The flow may be
    continuous or discrete. The 'rate' stereotype has a rate property of type
    InstanceSpecification. The values of this property must be instances of
    classifiers stereotyped by 'valueType' or 'distributionDefinition'. In
    particular, the denominator for units used in the rate property must be time
    units.
    """
    base__activity_edge = models.ForeignKey('ActivityEdge')
    base__parameter = models.ForeignKey('Parameter')
    base__object_node = models.ForeignKey('ObjectNode')
    rate = models.ForeignKey('InstanceSpecification')


class Continuous(Rate):
    """
    Continuous rate is a special case of rate of flow (see Rate) where the increment
    of time between items approaches zero. It is intended to represent continuous
    flows that may correspond to water flowing through a pipe, a time continuous
    signal, or continuous energy flow. It is independent from UML streaming. A
    streaming parameter may or may not apply to continuous flow, and a continuous
    flow may or may not apply to streaming parameters.
    """
    pass


class Stakeholder(Stereotype):
    concern_list = models.ForeignKey('Comment')
    base__classifier = models.ForeignKey('Classifier')
    concern = models.CharField(max_length=255)


class TestCase(Stereotype):
    """
    A test case is a method for verifying a requirement is satisfied.
    """
    base__behavior = models.ForeignKey('Behavior')
    base__operation = models.ForeignKey('Operation')


class ClassifierBehaviorProperty(Stereotype):
    """
    The ClassifierBehaviorProperty stereotype can be applied to properties to
    constrain their values to be the executions of classifier behaviors.  The value
    of properties with ClassifierBehaviorProperty  applied are the executions of
    classifier behaviors invoked by instantiation of the block that owns the
    stereotyped property or one of its specializations.
    """
    base__property = models.ForeignKey('Property')


class Trace(DirectedRelationshipPropertyPath):
    base__abstraction = models.ForeignKey('Abstraction')


class Copy(Trace):
    """
    A Copy relationship is a dependency between a supplier requirement and a client
    requirement that specifies that the text of the client requirement is a read-
    only copy of the text of the supplier requirement.
    """
    pass


class NoBuffer(Stereotype):
    """
    When this stereotype is applied to object nodes, tokens arriving at the node are
    discarded if they are refused by outgoing edges, or refused by actions for
    object nodes that are input pins. This is typically used with fast or
    continuously flowing data values, to prevent buffer overrun, or to model
    transient values, such as electrical signals. For object nodes that are the
    target of continuous flows, 'nobuffer' and 'overwrite' have the same effect. The
    stereotype does not override UML token offering semantics; it just indicates
    what happens to the token when it is accepted. When the stereotype is not
    applied, the semantics are as in UML, specifically, tokens arriving at an object
    node that are refused by outgoing edges, or action for input pins, are held
    until they can leave the object node.
    """
    base__object_node = models.ForeignKey('ObjectNode')


class Overwrite(Stereotype):
    """
    When the 'overwrite' stereotype is applied to object nodes, a token arriving at
    a full object node replaces the ones already there (a full object node has as
    many tokens as allowed by its upper bound). This is typically used on an input
    pin with an upper bound of 1 to ensure that stale data is overridden at an input
    pin. For upper bounds greater than one, the token replaced is the one that would
    be the last to be selected according to the ordering kind for the node. For FIFO
    ordering, this is the most recently added token, for LIFO it is the least
    recently added token. A null token removes all the tokens already there. The
    number of tokens replaced is equal to the weight of the incoming edge, which
    defaults to 1. For object nodes that are the target of continuous flows,
    'overwrite' and 'nobuffer' have the same effect. The stereotype does not
    override UML token offering semantics, just indicates what happens to the token
    when it is accepted. When the stereotype is not applied, the semantics is as in
    UML, specifically, tokens arriving at object nodes do not replace ones that are
    already there.
    """
    base__object_node = models.ForeignKey('ObjectNode')


class PrimitiveValueTypes(Package):
    pass


class Satisfy(Trace):
    """
    A Satisfy relationship is a dependency between a requirement and a model element
    that fulfills the requirement. As with other dependencies, the arrow direction
    points from the satisfying (client) model element to the (supplier) requirement
    that is satisfied.
    """
    pass


class ControlOperator(Stereotype):
    """
    A control operator is a behavior that is intended to represent an arbitrarily
    complex logical operator that can be used to enable and disable other actions.
    When this stereotype is applied to behaviors, the behavior takes control values
    as inputs or provides them as outputs, that is, it treats control as data. When
    this stereotype is not applied, the behavior may not have a parameter typed by
    ControlValue. This stereotype also applies to operations with the same
    semantics.
    """
    base__behavior = models.ForeignKey('Behavior')
    base__operation = models.ForeignKey('Operation')


class ChangeStructuralFeatureEvent(Stereotype):
    structural_feature = models.ForeignKey('StructuralFeature')
    base__change_event = models.ForeignKey('ChangeEvent')


class ConstraintBlock(Block):
    """
    A constraint block is a block that packages the statement of a constraint so it
    may be applied in a reusable way to constrain properties of other blocks. A
    constraint block typically defines one or more constraint parameters, which are
    bound to properties of other blocks in a surrounding context where the
    constraint is used. Binding connectors, as defined in Chapter 8: Blocks, are
    used to bind each parameter of the constraint block to a property in the
    surrounding context. All properties of a constraint block are constraint
    parameters, with the exception of constraint properties that hold internally
    nested usages of other constraint blocks.
    """
    base__class = models.ForeignKey('Class')


class FlowDirection(Enumeration):
    """
    FlowDirection is an enumeration type that defines literals used for specifying
    input and output directions. FlowDirection is used by flow properties to
    indicate if a property is an input or an output with respect to its owner.
    """
    OUT = 0
    IN = 1
    INOUT = 2
    CHOICES = (
        (OUT, 'out'),
        (IN, 'in'),
        (INOUT, 'inout'),
    )

    flow_direction = models.IntegerField(choices=CHOICES, default=INOUT)


class ItemFlow(Stereotype):
    """
    An ItemFlow describes the flow of items across a connector or an association. It
    may constrain the item exchange between blocks, block usages, or flow ports as
    specified by their flow properties. For example, a pump connected to a tank: the
    pump has an 'out' flow property of type Liquid and the tank has an 'in'
    FlowProperty of type Liquid. To signify that only water flows between the pump
    and the tank, we can specify an ItemFlow of type Water on the connector.
    """
    item_property = models.ForeignKey('Property', help_text="An optional property that relates the flowing item to the instances of the connector's enclosing block. This property is applicable only for item flows assigned to connectors. The multiplicity is zero if the item flow is assigned to an Association.")
    base__information_flow = models.ForeignKey('InformationFlow')


class Problem(Stereotype):
    """
    A Problem documents a deficiency, limitation, or failure of one or more model
    elements to satisfy a requirement or need, or other undesired outcome. It may be
    used to capture problems identified during analysis, design, verification, or
    manufacture and associate the problem with the relevant model elements. Problem
    is a stereotype of comment and may be attached to any other model element in the
    same manner as a comment.
    """
    base__comment = models.ForeignKey('Comment')


class ParticipantProperty(Stereotype):
    """
    The Block stereotype extends Class, so it can be applied to any specialization
    of Class, including Association Classes. These are informally called
    'association blocks.' An association block can own properties and connectors,
    like any other block. Each instance of an association block can link together
    instances of the end classifiers of the association. To refer to linked objects
    and values of an instance of an association block, it is necessary for the
    modeler to specify which (participant) properties of the association block
    identify the instances being linked at which end of the association. The value
    of a participant property on an instance (link) of the association block is the
    value or object at the end of the link corresponding to this end of the
    association.
    """
    end = models.ForeignKey('Property', help_text="A member end of the association block owning the property on which the stereotype is applied.")
    base__property = models.ForeignKey('Property')


class Conform(Stereotype):
    """
    A Conform relationship is a dependency between a view and a viewpoint. The view
    conforms to the specified rules and conventions detailed in the viewpoint.
    Conform is a specialization of the UML dependency, and as with other
    dependencies the arrow direction points from the (client/source) to the
    (supplier/target).
    """
    base__generalization = models.ForeignKey('Generalization')


class Verify(Trace):
    """
    A Verify relationship is a dependency between a requirement and a test case or
    other model element that can determine whether a system fulfills the
    requirement. As with other dependencies, the arrow direction points from the
    (client) element to the (supplier) requirement.
    """
    pass


class AcceptChangeStructuralFeatureEventAction(Stereotype):
    base__accept_event_action = models.ForeignKey('AcceptEventAction')


class Discrete(Rate):
    """
    Discrete rate is a special case of rate of flow (see Rate) where the increment
    of time between items is non-zero.
    """
    pass


class DistributedProperty(Stereotype):
    """
    DistributedProperty is a stereotype of Property used to apply a probability
    distribution to the values of the property. Specific distributions should be
    defined as subclasses of the DistributedProperty stereotype with the operands of
    the distributions represented by properties of those stereotype subclasses.
    """
    base__property = models.ForeignKey('Property')


class FlowSpecification(Stereotype):
    """
    A FlowSpecification specifies inputs and outputs as a set of flow properties. A
    flow specification is used by flow ports to specify what items can flow via the
    port.
    """
    base__interface = models.ForeignKey('Interface')


class FullPort(Stereotype):
    base__port = models.ForeignKey('Port')


class AllocateActivityPartition(Stereotype):
    """
    AllocateActivityPartition is used to depict an 'allocate' relationship on an
    Activity diagram. The AllocateActivityPartition is a standard
    UML2::ActivityPartition, with modified constraints as stated in the paragraph
    below.
    """
    base__activity_partition = models.ForeignKey('ActivityPartition')


class BoundReference(EndPathMultiplicity):
    bound_end = models.ForeignKey('ConnectorEnd', help_text="Gives a connector end of a binding connector opposite to the end linked to the stereotyped property, or linked to a property that generalizes the stereotyped one through redefinition.")
    binding_path = models.ForeignKey('Property', help_text="Gives the propertyPath of the NestedConnectorEnd applied, if any, to the boundEnd, appended to the role of the boundEnd.")


class Viewpoint(Stereotype):
    """
    A Viewpoint is a specification of the conventions and rules for constructing and
    using a view for the purpose of addressing a set of stakeholder concerns. The
    languages and methods for specifying a view may reference languages and methods
    in another viewpoint. They specify the elements expected to be represented in
    the view, and may be formally or informally defined. For example, the security
    viewpoint may require the security requirements, security functional and
    physical architecture, and security test cases.
    """
    concern_list = models.ForeignKey('Comment', help_text="The interest of the stakeholders.")
    language = models.CharField(max_length=255, help_text="The languages used to construct the viewpoint.")
    stakeholder = models.ForeignKey('Stakeholder', help_text="Set of stakeholders.")
    purpose = models.CharField(max_length=255, help_text="The purpose addresses the stakeholder concerns.")
    concern = models.CharField(max_length=255)
    method = models.ForeignKey('Behavior', help_text="The methods used to construct the views for this viewpoint.")
    base__class = models.ForeignKey('Class')
    presentation = models.CharField(max_length=255)


class Refine(DirectedRelationshipPropertyPath):
    base__abstraction = models.ForeignKey('Abstraction')


class DeriveReqt(Trace):
    """
    A DeriveReqt relationship is a dependency between two requirements in which a
    client requirement can be derived from the supplier requirement. As with other
    dependencies, the arrow direction points from the derived (client) requirement
    to the (supplier) requirement from which it is derived.
    """
    pass


class Probability(Stereotype):
    """
    When the 'probability' stereotype is applied to edges coming out of decision
    nodes and object nodes, it provides an expression for the probability that the
    edge will be traversed. These must be between zero and one inclusive, and add up
    to one for edges with same source at the time the probabilities are used. When
    the 'probability' stereotype is applied to output parameter sets, it gives the
    probability the parameter set will be given values at runtime. These must be
    between zero and one inclusive, and add up to one for output parameter sets of
    the same behavior at the time the probabilities are used.
    """
    base__parameter_set = models.ForeignKey('ParameterSet')
    base__activity_edge = models.ForeignKey('ActivityEdge')
    probability = models.ForeignKey('ValueSpecification')


class AdjunctProperty(Stereotype):
    """
    The AdjunctProperty stereotype can be applied to properties to constrain their
    values to the values of connectors typed by association blocks, call actions,
    object nodes, variables, or parameters, interaction uses, and submachine states.
    The values of connectors typed by association blocks are the instances of the
    association block typing a connector in the block having the stereotyped
    property.  The values of call actions are the executions of behaviors invoked by
    the behavior having the call action and the stereotyped property (see Subclause
    11.3.1.1.1 for more about this use of the stereotype).  The values of object
    nodes are the values of tokens in the object nodes of the behavior having the
    stereotyped property (see Subclause 11.3.1.4.1 for more about this use of the
    stereotype).  The values of variables are those assigned by executions of
    activities that have the stereotyped property.  The values of parameters are
    those assigned by executions of behaviors that have the stereotyped property.
    The keyword 'adjunct' before a property name indicates the property is
    stereotyped by AdjunctProperty.
    """
    principal = models.ForeignKey('Element', help_text="Gives the element that determines the values of the property. Must be a connector, call action, object node, variable, or parameter.")
    base__property = models.ForeignKey('Property')


class ElementGroup(Stereotype):
    member = models.ForeignKey('Element')
    base__comment = models.ForeignKey('Comment')
    size = models.ForeignKey('Integer')
    ordered_memeber = models.ForeignKey('Element')
    criterion = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


class InvocationOnNestedPortAction(ElementPropertyPath):
    base__invocation_action = models.ForeignKey('InvocationAction')
    on_nested_port = models.ForeignKey('Port')


class ValueType(Stereotype):
    """
    A ValueType defines types of values that may be used to express information
    about a system, but cannot be identified as the target of any reference. Since a
    value cannot be identified except by means of the value itself, each such value
    within a model is independent of any other, unless other forms of constraints
    are imposed. Value types may be used to type properties, operation parameters,
    or potentially other elements within SysML. SysML defines ValueType as a
    stereotype of UML DataType to establish a more neutral term for system values
    that may never be given a concrete data representation.
    """
    base__data_type = models.ForeignKey('DataType')
    quantity_kind = models.ForeignKey('InstanceSpecification', help_text="A kind of quantity that may be stated by means of defined units, as identified by an instance of the Dimension stereotype. A value type may optionally specify a dimension without any unit. Such a value has no concrete representation, but may be used to express a value in an abstract form independent of any specific units.")
    unit = models.ForeignKey('InstanceSpecification', help_text="A quantity in terms of which the magnitudes of other quantities that have the same dimension can be stated, as identified by an instance of the Unit stereotype.")


class ConnectorProperty(Stereotype):
    """
    Connectors can be typed by association classes that are stereotyped by Block
    (association blocks). These connectors specify instances (links) of the
    association block that exist due to instantiation of the block owning or
    inheriting the connector. The value of a connector property on an instance of a
    block will be exactly those link objects that are instances of the association
    block typing the connector referred to by the connector property.
    """
    connector = models.ForeignKey('Connector', help_text="A connector of the block owning the property on which the stereotype is applied.")
    base__property = models.ForeignKey('Property')
