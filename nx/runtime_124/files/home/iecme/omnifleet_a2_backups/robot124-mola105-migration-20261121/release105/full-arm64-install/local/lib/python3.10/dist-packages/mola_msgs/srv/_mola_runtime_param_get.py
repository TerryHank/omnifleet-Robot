# generated from rosidl_generator_py/resource/_idl.py.em
# with input from mola_msgs:srv/MolaRuntimeParamGet.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MolaRuntimeParamGet_Request(type):
    """Metaclass of message 'MolaRuntimeParamGet_Request'."""

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
            module = import_type_support('mola_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'mola_msgs.srv.MolaRuntimeParamGet_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__mola_runtime_param_get__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__mola_runtime_param_get__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__mola_runtime_param_get__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__mola_runtime_param_get__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__mola_runtime_param_get__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MolaRuntimeParamGet_Request(metaclass=Metaclass_MolaRuntimeParamGet_Request):
    """Message class 'MolaRuntimeParamGet_Request'."""

    __slots__ = [
    ]

    _fields_and_field_types = {
    }

    SLOT_TYPES = (
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))

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
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)


# Import statements for member types

import builtins  # noqa: E402, I100

# already imported above
# import rosidl_parser.definition


class Metaclass_MolaRuntimeParamGet_Response(type):
    """Metaclass of message 'MolaRuntimeParamGet_Response'."""

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
            module = import_type_support('mola_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'mola_msgs.srv.MolaRuntimeParamGet_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__mola_runtime_param_get__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__mola_runtime_param_get__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__mola_runtime_param_get__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__mola_runtime_param_get__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__mola_runtime_param_get__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MolaRuntimeParamGet_Response(metaclass=Metaclass_MolaRuntimeParamGet_Response):
    """Message class 'MolaRuntimeParamGet_Response'."""

    __slots__ = [
        '_parameters',
    ]

    _fields_and_field_types = {
        'parameters': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.parameters = kwargs.get('parameters', str())

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
        if self.parameters != other.parameters:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def parameters(self):
        """Message field 'parameters'."""
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'parameters' field must be of type 'str'"
        self._parameters = value


class Metaclass_MolaRuntimeParamGet(type):
    """Metaclass of service 'MolaRuntimeParamGet'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('mola_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'mola_msgs.srv.MolaRuntimeParamGet')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__mola_runtime_param_get

            from mola_msgs.srv import _mola_runtime_param_get
            if _mola_runtime_param_get.Metaclass_MolaRuntimeParamGet_Request._TYPE_SUPPORT is None:
                _mola_runtime_param_get.Metaclass_MolaRuntimeParamGet_Request.__import_type_support__()
            if _mola_runtime_param_get.Metaclass_MolaRuntimeParamGet_Response._TYPE_SUPPORT is None:
                _mola_runtime_param_get.Metaclass_MolaRuntimeParamGet_Response.__import_type_support__()


class MolaRuntimeParamGet(metaclass=Metaclass_MolaRuntimeParamGet):
    from mola_msgs.srv._mola_runtime_param_get import MolaRuntimeParamGet_Request as Request
    from mola_msgs.srv._mola_runtime_param_get import MolaRuntimeParamGet_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
