# generated from rosidl_generator_py/resource/_idl.py.em
# with input from omnifleet_interfaces:srv/LoadMission.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_LoadMission_Request(type):
    """Metaclass of message 'LoadMission_Request'."""

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
            module = import_type_support('omnifleet_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_interfaces.srv.LoadMission_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__load_mission__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__load_mission__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__load_mission__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__load_mission__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__load_mission__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LoadMission_Request(metaclass=Metaclass_LoadMission_Request):
    """Message class 'LoadMission_Request'."""

    __slots__ = [
        '_mission_id',
    ]

    _fields_and_field_types = {
        'mission_id': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.mission_id = kwargs.get('mission_id', str())

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
        if self.mission_id != other.mission_id:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def mission_id(self):
        """Message field 'mission_id'."""
        return self._mission_id

    @mission_id.setter
    def mission_id(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'mission_id' field must be of type 'str'"
        self._mission_id = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_LoadMission_Response(type):
    """Metaclass of message 'LoadMission_Response'."""

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
            module = import_type_support('omnifleet_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_interfaces.srv.LoadMission_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__load_mission__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__load_mission__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__load_mission__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__load_mission__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__load_mission__response

            from geometry_msgs.msg import Pose
            if Pose.__class__._TYPE_SUPPORT is None:
                Pose.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LoadMission_Response(metaclass=Metaclass_LoadMission_Response):
    """Message class 'LoadMission_Response'."""

    __slots__ = [
        '_accepted',
        '_revision',
        '_map_id',
        '_map_sha256',
        '_frame',
        '_poses',
        '_loop',
        '_message',
    ]

    _fields_and_field_types = {
        'accepted': 'boolean',
        'revision': 'uint64',
        'map_id': 'string',
        'map_sha256': 'string',
        'frame': 'string',
        'poses': 'sequence<geometry_msgs/Pose>',
        'loop': 'boolean',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Pose')),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.accepted = kwargs.get('accepted', bool())
        self.revision = kwargs.get('revision', int())
        self.map_id = kwargs.get('map_id', str())
        self.map_sha256 = kwargs.get('map_sha256', str())
        self.frame = kwargs.get('frame', str())
        self.poses = kwargs.get('poses', [])
        self.loop = kwargs.get('loop', bool())
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
        if self.accepted != other.accepted:
            return False
        if self.revision != other.revision:
            return False
        if self.map_id != other.map_id:
            return False
        if self.map_sha256 != other.map_sha256:
            return False
        if self.frame != other.frame:
            return False
        if self.poses != other.poses:
            return False
        if self.loop != other.loop:
            return False
        if self.message != other.message:
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
    def map_id(self):
        """Message field 'map_id'."""
        return self._map_id

    @map_id.setter
    def map_id(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'map_id' field must be of type 'str'"
        self._map_id = value

    @builtins.property
    def map_sha256(self):
        """Message field 'map_sha256'."""
        return self._map_sha256

    @map_sha256.setter
    def map_sha256(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'map_sha256' field must be of type 'str'"
        self._map_sha256 = value

    @builtins.property
    def frame(self):
        """Message field 'frame'."""
        return self._frame

    @frame.setter
    def frame(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'frame' field must be of type 'str'"
        self._frame = value

    @builtins.property
    def poses(self):
        """Message field 'poses'."""
        return self._poses

    @poses.setter
    def poses(self, value):
        if __debug__:
            from geometry_msgs.msg import Pose
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
                 all(isinstance(v, Pose) for v in value) and
                 True), \
                "The 'poses' field must be a set or sequence and each value of type 'Pose'"
        self._poses = value

    @builtins.property
    def loop(self):
        """Message field 'loop'."""
        return self._loop

    @loop.setter
    def loop(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'loop' field must be of type 'bool'"
        self._loop = value

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


class Metaclass_LoadMission(type):
    """Metaclass of service 'LoadMission'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('omnifleet_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'omnifleet_interfaces.srv.LoadMission')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__load_mission

            from omnifleet_interfaces.srv import _load_mission
            if _load_mission.Metaclass_LoadMission_Request._TYPE_SUPPORT is None:
                _load_mission.Metaclass_LoadMission_Request.__import_type_support__()
            if _load_mission.Metaclass_LoadMission_Response._TYPE_SUPPORT is None:
                _load_mission.Metaclass_LoadMission_Response.__import_type_support__()


class LoadMission(metaclass=Metaclass_LoadMission):
    from omnifleet_interfaces.srv._load_mission import LoadMission_Request as Request
    from omnifleet_interfaces.srv._load_mission import LoadMission_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
