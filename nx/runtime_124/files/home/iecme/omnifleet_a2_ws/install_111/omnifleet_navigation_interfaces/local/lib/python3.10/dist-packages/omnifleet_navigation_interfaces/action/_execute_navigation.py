# generated from rosidl_generator_py/resource/_idl.py.em
# with input from omnifleet_navigation_interfaces:action/ExecuteNavigation.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ExecuteNavigation_Goal(type):
    """Metaclass of message 'ExecuteNavigation_Goal'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'LOCAL': 0,
        'FLEET': 1,
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_Goal')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__goal
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__goal
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__goal
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__goal
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__goal

            from omnifleet_navigation_interfaces.msg import NavigationPoint
            if NavigationPoint.__class__._TYPE_SUPPORT is None:
                NavigationPoint.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'LOCAL': cls.__constants['LOCAL'],
            'FLEET': cls.__constants['FLEET'],
            'PASS_RADIUS__DEFAULT': 0.25,
        }

    @property
    def LOCAL(self):
        """Message constant 'LOCAL'."""
        return Metaclass_ExecuteNavigation_Goal.__constants['LOCAL']

    @property
    def FLEET(self):
        """Message constant 'FLEET'."""
        return Metaclass_ExecuteNavigation_Goal.__constants['FLEET']

    @property
    def PASS_RADIUS__DEFAULT(cls):
        """Return default value for message field 'pass_radius'."""
        return 0.25


class ExecuteNavigation_Goal(metaclass=Metaclass_ExecuteNavigation_Goal):
    """
    Message class 'ExecuteNavigation_Goal'.

    Constants:
      LOCAL
      FLEET
    """

    __slots__ = [
        '_task_id',
        '_command_epoch',
        '_revision',
        '_source',
        '_single_point',
        '_follow_trail',
        '_waypoints',
        '_pass_radius',
    ]

    _fields_and_field_types = {
        'task_id': 'string',
        'command_epoch': 'string',
        'revision': 'uint64',
        'source': 'uint8',
        'single_point': 'boolean',
        'follow_trail': 'boolean',
        'waypoints': 'sequence<omnifleet_navigation_interfaces/NavigationPoint>',
        'pass_radius': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['omnifleet_navigation_interfaces', 'msg'], 'NavigationPoint')),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.task_id = kwargs.get('task_id', str())
        self.command_epoch = kwargs.get('command_epoch', str())
        self.revision = kwargs.get('revision', int())
        self.source = kwargs.get('source', int())
        self.single_point = kwargs.get('single_point', bool())
        self.follow_trail = kwargs.get('follow_trail', bool())
        self.waypoints = kwargs.get('waypoints', [])
        self.pass_radius = kwargs.get(
            'pass_radius', ExecuteNavigation_Goal.PASS_RADIUS__DEFAULT)

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
        if self.task_id != other.task_id:
            return False
        if self.command_epoch != other.command_epoch:
            return False
        if self.revision != other.revision:
            return False
        if self.source != other.source:
            return False
        if self.single_point != other.single_point:
            return False
        if self.follow_trail != other.follow_trail:
            return False
        if self.waypoints != other.waypoints:
            return False
        if self.pass_radius != other.pass_radius:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def task_id(self):
        """Message field 'task_id'."""
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'task_id' field must be of type 'str'"
        self._task_id = value

    @builtins.property
    def command_epoch(self):
        """Message field 'command_epoch'."""
        return self._command_epoch

    @command_epoch.setter
    def command_epoch(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'command_epoch' field must be of type 'str'"
        self._command_epoch = value

    @builtins.property
    def revision(self):
        """Message field 'revision'."""
        return self._revision

    @revision.setter
    def revision(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'revision' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'revision' field must be an unsigned integer in [0, 18446744073709551615]"
        self._revision = value

    @builtins.property
    def source(self):
        """Message field 'source'."""
        return self._source

    @source.setter
    def source(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'source' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'source' field must be an unsigned integer in [0, 255]"
        self._source = value

    @builtins.property
    def single_point(self):
        """Message field 'single_point'."""
        return self._single_point

    @single_point.setter
    def single_point(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'single_point' field must be of type 'bool'"
        self._single_point = value

    @builtins.property
    def follow_trail(self):
        """Message field 'follow_trail'."""
        return self._follow_trail

    @follow_trail.setter
    def follow_trail(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'follow_trail' field must be of type 'bool'"
        self._follow_trail = value

    @builtins.property
    def waypoints(self):
        """Message field 'waypoints'."""
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value):
        if __debug__:
            from omnifleet_navigation_interfaces.msg import NavigationPoint
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, NavigationPoint) for v in value) and
                 True), \
                "The 'waypoints' field must be a set or sequence and each value of type 'NavigationPoint'"
        self._waypoints = value

    @builtins.property
    def pass_radius(self):
        """Message field 'pass_radius'."""
        return self._pass_radius

    @pass_radius.setter
    def pass_radius(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'pass_radius' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'pass_radius' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._pass_radius = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_Result(type):
    """Metaclass of message 'ExecuteNavigation_Result'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_Result')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__result
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__result

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_Result(metaclass=Metaclass_ExecuteNavigation_Result):
    """Message class 'ExecuteNavigation_Result'."""

    __slots__ = [
        '_success',
        '_code',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'code': 'string',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.code = kwargs.get('code', str())
        self.message = kwargs.get('message', str())

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
        if self.success != other.success:
            return False
        if self.code != other.code:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def code(self):
        """Message field 'code'."""
        return self._code

    @code.setter
    def code(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'code' field must be of type 'str'"
        self._code = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import math

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_Feedback(type):
    """Metaclass of message 'ExecuteNavigation_Feedback'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_Feedback')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__feedback
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__feedback
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__feedback
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__feedback
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__feedback

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_Feedback(metaclass=Metaclass_ExecuteNavigation_Feedback):
    """Message class 'ExecuteNavigation_Feedback'."""

    __slots__ = [
        '_task_id',
        '_phase',
        '_message',
        '_passed_points',
        '_tf_age_ms',
    ]

    _fields_and_field_types = {
        'task_id': 'string',
        'phase': 'string',
        'message': 'string',
        'passed_points': 'uint32',
        'tf_age_ms': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.task_id = kwargs.get('task_id', str())
        self.phase = kwargs.get('phase', str())
        self.message = kwargs.get('message', str())
        self.passed_points = kwargs.get('passed_points', int())
        self.tf_age_ms = kwargs.get('tf_age_ms', float())

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
        if self.task_id != other.task_id:
            return False
        if self.phase != other.phase:
            return False
        if self.message != other.message:
            return False
        if self.passed_points != other.passed_points:
            return False
        if self.tf_age_ms != other.tf_age_ms:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def task_id(self):
        """Message field 'task_id'."""
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'task_id' field must be of type 'str'"
        self._task_id = value

    @builtins.property
    def phase(self):
        """Message field 'phase'."""
        return self._phase

    @phase.setter
    def phase(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'phase' field must be of type 'str'"
        self._phase = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value

    @builtins.property
    def passed_points(self):
        """Message field 'passed_points'."""
        return self._passed_points

    @passed_points.setter
    def passed_points(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'passed_points' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'passed_points' field must be an unsigned integer in [0, 4294967295]"
        self._passed_points = value

    @builtins.property
    def tf_age_ms(self):
        """Message field 'tf_age_ms'."""
        return self._tf_age_ms

    @tf_age_ms.setter
    def tf_age_ms(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'tf_age_ms' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'tf_age_ms' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._tf_age_ms = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_SendGoal_Request(type):
    """Metaclass of message 'ExecuteNavigation_SendGoal_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_SendGoal_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__send_goal__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__send_goal__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__send_goal__request
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__send_goal__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__send_goal__request

            from omnifleet_navigation_interfaces.action import ExecuteNavigation
            if ExecuteNavigation.Goal.__class__._TYPE_SUPPORT is None:
                ExecuteNavigation.Goal.__class__.__import_type_support__()

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_SendGoal_Request(metaclass=Metaclass_ExecuteNavigation_SendGoal_Request):
    """Message class 'ExecuteNavigation_SendGoal_Request'."""

    __slots__ = [
        '_goal_id',
        '_goal',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
        'goal': 'omnifleet_navigation_interfaces/ExecuteNavigation_Goal',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['omnifleet_navigation_interfaces', 'action'], 'ExecuteNavigation_Goal'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Goal
        self.goal = kwargs.get('goal', ExecuteNavigation_Goal())

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
        if self.goal_id != other.goal_id:
            return False
        if self.goal != other.goal:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value

    @builtins.property
    def goal(self):
        """Message field 'goal'."""
        return self._goal

    @goal.setter
    def goal(self, value):
        if __debug__:
            from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Goal
            assert \
                isinstance(value, ExecuteNavigation_Goal), \
                "The 'goal' field must be a sub message of type 'ExecuteNavigation_Goal'"
        self._goal = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_SendGoal_Response(type):
    """Metaclass of message 'ExecuteNavigation_SendGoal_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_SendGoal_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__send_goal__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__send_goal__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__send_goal__response
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__send_goal__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__send_goal__response

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_SendGoal_Response(metaclass=Metaclass_ExecuteNavigation_SendGoal_Response):
    """Message class 'ExecuteNavigation_SendGoal_Response'."""

    __slots__ = [
        '_accepted',
        '_stamp',
    ]

    _fields_and_field_types = {
        'accepted': 'boolean',
        'stamp': 'builtin_interfaces/Time',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.accepted = kwargs.get('accepted', bool())
        from builtin_interfaces.msg import Time
        self.stamp = kwargs.get('stamp', Time())

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
        if self.accepted != other.accepted:
            return False
        if self.stamp != other.stamp:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def accepted(self):
        """Message field 'accepted'."""
        return self._accepted

    @accepted.setter
    def accepted(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'accepted' field must be of type 'bool'"
        self._accepted = value

    @builtins.property
    def stamp(self):
        """Message field 'stamp'."""
        return self._stamp

    @stamp.setter
    def stamp(self, value):
        if __debug__:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'stamp' field must be a sub message of type 'Time'"
        self._stamp = value


class Metaclass_ExecuteNavigation_SendGoal(type):
    """Metaclass of service 'ExecuteNavigation_SendGoal'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('omnifleet_navigation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_SendGoal')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__action__execute_navigation__send_goal

            from omnifleet_navigation_interfaces.action import _execute_navigation
            if _execute_navigation.Metaclass_ExecuteNavigation_SendGoal_Request._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_SendGoal_Request.__import_type_support__()
            if _execute_navigation.Metaclass_ExecuteNavigation_SendGoal_Response._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_SendGoal_Response.__import_type_support__()


class ExecuteNavigation_SendGoal(metaclass=Metaclass_ExecuteNavigation_SendGoal):
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_SendGoal_Request as Request
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_SendGoal_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_GetResult_Request(type):
    """Metaclass of message 'ExecuteNavigation_GetResult_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_GetResult_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__get_result__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__get_result__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__get_result__request
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__get_result__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__get_result__request

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_GetResult_Request(metaclass=Metaclass_ExecuteNavigation_GetResult_Request):
    """Message class 'ExecuteNavigation_GetResult_Request'."""

    __slots__ = [
        '_goal_id',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())

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
        if self.goal_id != other.goal_id:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_GetResult_Response(type):
    """Metaclass of message 'ExecuteNavigation_GetResult_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_GetResult_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__get_result__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__get_result__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__get_result__response
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__get_result__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__get_result__response

            from omnifleet_navigation_interfaces.action import ExecuteNavigation
            if ExecuteNavigation.Result.__class__._TYPE_SUPPORT is None:
                ExecuteNavigation.Result.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_GetResult_Response(metaclass=Metaclass_ExecuteNavigation_GetResult_Response):
    """Message class 'ExecuteNavigation_GetResult_Response'."""

    __slots__ = [
        '_status',
        '_result',
    ]

    _fields_and_field_types = {
        'status': 'int8',
        'result': 'omnifleet_navigation_interfaces/ExecuteNavigation_Result',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['omnifleet_navigation_interfaces', 'action'], 'ExecuteNavigation_Result'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.status = kwargs.get('status', int())
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Result
        self.result = kwargs.get('result', ExecuteNavigation_Result())

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
        if self.status != other.status:
            return False
        if self.result != other.result:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def status(self):
        """Message field 'status'."""
        return self._status

    @status.setter
    def status(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'status' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'status' field must be an integer in [-128, 127]"
        self._status = value

    @builtins.property
    def result(self):
        """Message field 'result'."""
        return self._result

    @result.setter
    def result(self, value):
        if __debug__:
            from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Result
            assert \
                isinstance(value, ExecuteNavigation_Result), \
                "The 'result' field must be a sub message of type 'ExecuteNavigation_Result'"
        self._result = value


class Metaclass_ExecuteNavigation_GetResult(type):
    """Metaclass of service 'ExecuteNavigation_GetResult'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('omnifleet_navigation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_GetResult')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__action__execute_navigation__get_result

            from omnifleet_navigation_interfaces.action import _execute_navigation
            if _execute_navigation.Metaclass_ExecuteNavigation_GetResult_Request._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_GetResult_Request.__import_type_support__()
            if _execute_navigation.Metaclass_ExecuteNavigation_GetResult_Response._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_GetResult_Response.__import_type_support__()


class ExecuteNavigation_GetResult(metaclass=Metaclass_ExecuteNavigation_GetResult):
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_GetResult_Request as Request
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_GetResult_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ExecuteNavigation_FeedbackMessage(type):
    """Metaclass of message 'ExecuteNavigation_FeedbackMessage'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'omnifleet_navigation_interfaces.action.ExecuteNavigation_FeedbackMessage')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__execute_navigation__feedback_message
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__execute_navigation__feedback_message
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__execute_navigation__feedback_message
            cls._TYPE_SUPPORT = module.type_support_msg__action__execute_navigation__feedback_message
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__execute_navigation__feedback_message

            from omnifleet_navigation_interfaces.action import ExecuteNavigation
            if ExecuteNavigation.Feedback.__class__._TYPE_SUPPORT is None:
                ExecuteNavigation.Feedback.__class__.__import_type_support__()

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ExecuteNavigation_FeedbackMessage(metaclass=Metaclass_ExecuteNavigation_FeedbackMessage):
    """Message class 'ExecuteNavigation_FeedbackMessage'."""

    __slots__ = [
        '_goal_id',
        '_feedback',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
        'feedback': 'omnifleet_navigation_interfaces/ExecuteNavigation_Feedback',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['omnifleet_navigation_interfaces', 'action'], 'ExecuteNavigation_Feedback'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Feedback
        self.feedback = kwargs.get('feedback', ExecuteNavigation_Feedback())

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
        if self.goal_id != other.goal_id:
            return False
        if self.feedback != other.feedback:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value

    @builtins.property
    def feedback(self):
        """Message field 'feedback'."""
        return self._feedback

    @feedback.setter
    def feedback(self, value):
        if __debug__:
            from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Feedback
            assert \
                isinstance(value, ExecuteNavigation_Feedback), \
                "The 'feedback' field must be a sub message of type 'ExecuteNavigation_Feedback'"
        self._feedback = value


class Metaclass_ExecuteNavigation(type):
    """Metaclass of action 'ExecuteNavigation'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('omnifleet_navigation_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_navigation_interfaces.action.ExecuteNavigation')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_action__action__execute_navigation

            from action_msgs.msg import _goal_status_array
            if _goal_status_array.Metaclass_GoalStatusArray._TYPE_SUPPORT is None:
                _goal_status_array.Metaclass_GoalStatusArray.__import_type_support__()
            from action_msgs.srv import _cancel_goal
            if _cancel_goal.Metaclass_CancelGoal._TYPE_SUPPORT is None:
                _cancel_goal.Metaclass_CancelGoal.__import_type_support__()

            from omnifleet_navigation_interfaces.action import _execute_navigation
            if _execute_navigation.Metaclass_ExecuteNavigation_SendGoal._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_SendGoal.__import_type_support__()
            if _execute_navigation.Metaclass_ExecuteNavigation_GetResult._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_GetResult.__import_type_support__()
            if _execute_navigation.Metaclass_ExecuteNavigation_FeedbackMessage._TYPE_SUPPORT is None:
                _execute_navigation.Metaclass_ExecuteNavigation_FeedbackMessage.__import_type_support__()


class ExecuteNavigation(metaclass=Metaclass_ExecuteNavigation):

    # The goal message defined in the action definition.
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Goal as Goal
    # The result message defined in the action definition.
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Result as Result
    # The feedback message defined in the action definition.
    from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_Feedback as Feedback

    class Impl:

        # The send_goal service using a wrapped version of the goal message as a request.
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_SendGoal as SendGoalService
        # The get_result service using a wrapped version of the result message as a response.
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_GetResult as GetResultService
        # The feedback message with generic fields which wraps the feedback message.
        from omnifleet_navigation_interfaces.action._execute_navigation import ExecuteNavigation_FeedbackMessage as FeedbackMessage

        # The generic service to cancel a goal.
        from action_msgs.srv._cancel_goal import CancelGoal as CancelGoalService
        # The generic message for get the status of a goal.
        from action_msgs.msg._goal_status_array import GoalStatusArray as GoalStatusMessage

    def __init__(self):
        raise NotImplementedError('Action classes can not be instantiated')
