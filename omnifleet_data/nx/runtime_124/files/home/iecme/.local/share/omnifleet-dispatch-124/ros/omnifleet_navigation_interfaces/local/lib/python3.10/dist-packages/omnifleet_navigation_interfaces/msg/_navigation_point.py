# generated from rosidl_generator_py/resource/_idl.py.em
# with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_NavigationPoint(type):
    """Metaclass of message 'NavigationPoint'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'PASS': 0,
        'STOP': 1,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('omnifleet_navigation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_navigation_interfaces.msg.NavigationPoint')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__navigation_point
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__navigation_point
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__navigation_point
            cls._TYPE_SUPPORT = module.type_support_msg__msg__navigation_point
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__navigation_point

            from geometry_msgs.msg import PoseStamped
            if PoseStamped.__class__._TYPE_SUPPORT is None:
                PoseStamped.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'PASS': cls.__constants['PASS'],
            'STOP': cls.__constants['STOP'],
        }

    @property
    def PASS(self):
        """Message constant 'PASS'."""
        return Metaclass_NavigationPoint.__constants['PASS']

    @property
    def STOP(self):
        """Message constant 'STOP'."""
        return Metaclass_NavigationPoint.__constants['STOP']


class NavigationPoint(metaclass=Metaclass_NavigationPoint):
    """
    Message class 'NavigationPoint'.

    Constants:
      PASS
      STOP
    """

    __slots__ = [
        '_name',
        '_pose',
        '_kind',
        '_dwell_seconds',
    ]

    _fields_and_field_types = {
        'name': 'string',
        'pose': 'geometry_msgs/PoseStamped',
        'kind': 'uint8',
        'dwell_seconds': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'PoseStamped'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.name = kwargs.get('name', str())
        from geometry_msgs.msg import PoseStamped
        self.pose = kwargs.get('pose', PoseStamped())
        self.kind = kwargs.get('kind', int())
        self.dwell_seconds = kwargs.get('dwell_seconds', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.name != other.name:
            return False
        if self.pose != other.pose:
            return False
        if self.kind != other.kind:
            return False
        if self.dwell_seconds != other.dwell_seconds:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def name(self):
        """Message field 'name'."""
        return self._name

    @name.setter
    def name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'name' field must be of type 'str'"
        self._name = value

    @builtins.property
    def pose(self):
        """Message field 'pose'."""
        return self._pose

    @pose.setter
    def pose(self, value):
        if __debug__:
            from geometry_msgs.msg import PoseStamped
            assert \
                isinstance(value, PoseStamped), \
                "The 'pose' field must be a sub message of type 'PoseStamped'"
        self._pose = value

    @builtins.property
    def kind(self):
        """Message field 'kind'."""
        return self._kind

    @kind.setter
    def kind(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'kind' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'kind' field must be an unsigned integer in [0, 255]"
        self._kind = value

    @builtins.property
    def dwell_seconds(self):
        """Message field 'dwell_seconds'."""
        return self._dwell_seconds

    @dwell_seconds.setter
    def dwell_seconds(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'dwell_seconds' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'dwell_seconds' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._dwell_seconds = value
