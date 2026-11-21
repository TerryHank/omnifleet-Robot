# generated from rosidl_generator_py/resource/_idl.py.em
# with input from omnifleet_interfaces:srv/Capability.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Capability_Request(type):
    """Metaclass of message 'Capability_Request'."""

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
                'omnifleet_interfaces.srv.Capability_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__capability__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__capability__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__capability__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__capability__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__capability__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Capability_Request(metaclass=Metaclass_Capability_Request):
    """Message class 'Capability_Request'."""

    __slots__ = [
        '_capability',
    ]

    _fields_and_field_types = {
        'capability': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.capability = kwargs.get('capability', str())

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
        if self.capability != other.capability:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def capability(self):
        """Message field 'capability'."""
        return self._capability

    @capability.setter
    def capability(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'capability' field must be of type 'str'"
        self._capability = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_Capability_Response(type):
    """Metaclass of message 'Capability_Response'."""

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
                'omnifleet_interfaces.srv.Capability_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__capability__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__capability__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__capability__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__capability__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__capability__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Capability_Response(metaclass=Metaclass_Capability_Response):
    """Message class 'Capability_Response'."""

    __slots__ = [
        '_available',
        '_accepted',
        '_transaction_id',
        '_message',
    ]

    _fields_and_field_types = {
        'available': 'boolean',
        'accepted': 'boolean',
        'transaction_id': 'string',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.available = kwargs.get('available', bool())
        self.accepted = kwargs.get('accepted', bool())
        self.transaction_id = kwargs.get('transaction_id', str())
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
        if self.available != other.available:
            return False
        if self.accepted != other.accepted:
            return False
        if self.transaction_id != other.transaction_id:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def available(self):
        """Message field 'available'."""
        return self._available

    @available.setter
    def available(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'available' field must be of type 'bool'"
        self._available = value

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
    def transaction_id(self):
        """Message field 'transaction_id'."""
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'transaction_id' field must be of type 'str'"
        self._transaction_id = value

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


class Metaclass_Capability(type):
    """Metaclass of service 'Capability'."""

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
                'omnifleet_interfaces.srv.Capability')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__capability

            from omnifleet_interfaces.srv import _capability
            if _capability.Metaclass_Capability_Request._TYPE_SUPPORT is None:
                _capability.Metaclass_Capability_Request.__import_type_support__()
            if _capability.Metaclass_Capability_Response._TYPE_SUPPORT is None:
                _capability.Metaclass_Capability_Response.__import_type_support__()


class Capability(metaclass=Metaclass_Capability):
    from omnifleet_interfaces.srv._capability import Capability_Request as Request
    from omnifleet_interfaces.srv._capability import Capability_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
