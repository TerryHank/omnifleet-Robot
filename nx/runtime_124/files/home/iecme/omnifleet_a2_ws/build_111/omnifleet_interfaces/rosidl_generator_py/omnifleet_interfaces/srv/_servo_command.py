# generated from rosidl_generator_py/resource/_idl.py.em
# with input from omnifleet_interfaces:srv/ServoCommand.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ServoCommand_Request(type):
    """Metaclass of message 'ServoCommand_Request'."""

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
                'omnifleet_interfaces.srv.ServoCommand_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__servo_command__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__servo_command__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__servo_command__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__servo_command__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__servo_command__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ServoCommand_Request(metaclass=Metaclass_ServoCommand_Request):
    """Message class 'ServoCommand_Request'."""

    __slots__ = [
        '_operation',
        '_id',
        '_arg0',
        '_arg1',
        '_arg2',
    ]

    _fields_and_field_types = {
        'operation': 'uint8',
        'id': 'uint8',
        'arg0': 'int32',
        'arg1': 'int32',
        'arg2': 'int32',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.operation = kwargs.get('operation', int())
        self.id = kwargs.get('id', int())
        self.arg0 = kwargs.get('arg0', int())
        self.arg1 = kwargs.get('arg1', int())
        self.arg2 = kwargs.get('arg2', int())

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
        if self.operation != other.operation:
            return False
        if self.id != other.id:
            return False
        if self.arg0 != other.arg0:
            return False
        if self.arg1 != other.arg1:
            return False
        if self.arg2 != other.arg2:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def operation(self):
        """Message field 'operation'."""
        return self._operation

    @operation.setter
    def operation(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'operation' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'operation' field must be an unsigned integer in [0, 255]"
        self._operation = value

    @builtins.property  # noqa: A003
    def id(self):  # noqa: A003
        """Message field 'id'."""
        return self._id

    @id.setter  # noqa: A003
    def id(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'id' field must be an unsigned integer in [0, 255]"
        self._id = value

    @builtins.property
    def arg0(self):
        """Message field 'arg0'."""
        return self._arg0

    @arg0.setter
    def arg0(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'arg0' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'arg0' field must be an integer in [-2147483648, 2147483647]"
        self._arg0 = value

    @builtins.property
    def arg1(self):
        """Message field 'arg1'."""
        return self._arg1

    @arg1.setter
    def arg1(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'arg1' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'arg1' field must be an integer in [-2147483648, 2147483647]"
        self._arg1 = value

    @builtins.property
    def arg2(self):
        """Message field 'arg2'."""
        return self._arg2

    @arg2.setter
    def arg2(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'arg2' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'arg2' field must be an integer in [-2147483648, 2147483647]"
        self._arg2 = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ServoCommand_Response(type):
    """Metaclass of message 'ServoCommand_Response'."""

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
                'omnifleet_interfaces.srv.ServoCommand_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__servo_command__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__servo_command__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__servo_command__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__servo_command__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__servo_command__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ServoCommand_Response(metaclass=Metaclass_ServoCommand_Response):
    """Message class 'ServoCommand_Response'."""

    __slots__ = [
        '_success',
        '_value0',
        '_value1',
        '_value2',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'value0': 'int32',
        'value1': 'int32',
        'value2': 'int32',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.value0 = kwargs.get('value0', int())
        self.value1 = kwargs.get('value1', int())
        self.value2 = kwargs.get('value2', int())
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
        if self.value0 != other.value0:
            return False
        if self.value1 != other.value1:
            return False
        if self.value2 != other.value2:
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
    def value0(self):
        """Message field 'value0'."""
        return self._value0

    @value0.setter
    def value0(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'value0' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'value0' field must be an integer in [-2147483648, 2147483647]"
        self._value0 = value

    @builtins.property
    def value1(self):
        """Message field 'value1'."""
        return self._value1

    @value1.setter
    def value1(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'value1' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'value1' field must be an integer in [-2147483648, 2147483647]"
        self._value1 = value

    @builtins.property
    def value2(self):
        """Message field 'value2'."""
        return self._value2

    @value2.setter
    def value2(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'value2' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'value2' field must be an integer in [-2147483648, 2147483647]"
        self._value2 = value

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


class Metaclass_ServoCommand(type):
    """Metaclass of service 'ServoCommand'."""

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
                'omnifleet_interfaces.srv.ServoCommand')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__servo_command

            from omnifleet_interfaces.srv import _servo_command
            if _servo_command.Metaclass_ServoCommand_Request._TYPE_SUPPORT is None:
                _servo_command.Metaclass_ServoCommand_Request.__import_type_support__()
            if _servo_command.Metaclass_ServoCommand_Response._TYPE_SUPPORT is None:
                _servo_command.Metaclass_ServoCommand_Response.__import_type_support__()


class ServoCommand(metaclass=Metaclass_ServoCommand):
    from omnifleet_interfaces.srv._servo_command import ServoCommand_Request as Request
    from omnifleet_interfaces.srv._servo_command import ServoCommand_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
