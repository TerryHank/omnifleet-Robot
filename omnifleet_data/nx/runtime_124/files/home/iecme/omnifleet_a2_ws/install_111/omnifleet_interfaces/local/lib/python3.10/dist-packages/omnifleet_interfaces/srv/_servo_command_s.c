// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "omnifleet_interfaces/srv/detail/servo_command__struct.h"
#include "omnifleet_interfaces/srv/detail/servo_command__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool omnifleet_interfaces__srv__servo_command__request__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[61];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("omnifleet_interfaces.srv._servo_command.ServoCommand_Request", full_classname_dest, 60) == 0);
  }
  omnifleet_interfaces__srv__ServoCommand_Request * ros_message = _ros_message;
  {  // operation
    PyObject * field = PyObject_GetAttrString(_pymsg, "operation");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->operation = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // id
    PyObject * field = PyObject_GetAttrString(_pymsg, "id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->id = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // arg0
    PyObject * field = PyObject_GetAttrString(_pymsg, "arg0");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->arg0 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // arg1
    PyObject * field = PyObject_GetAttrString(_pymsg, "arg1");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->arg1 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // arg2
    PyObject * field = PyObject_GetAttrString(_pymsg, "arg2");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->arg2 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * omnifleet_interfaces__srv__servo_command__request__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of ServoCommand_Request */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("omnifleet_interfaces.srv._servo_command");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "ServoCommand_Request");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  omnifleet_interfaces__srv__ServoCommand_Request * ros_message = (omnifleet_interfaces__srv__ServoCommand_Request *)raw_ros_message;
  {  // operation
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->operation);
    {
      int rc = PyObject_SetAttrString(_pymessage, "operation", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // arg0
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->arg0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "arg0", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // arg1
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->arg1);
    {
      int rc = PyObject_SetAttrString(_pymessage, "arg1", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // arg2
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->arg2);
    {
      int rc = PyObject_SetAttrString(_pymessage, "arg2", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
// already included above
// #include <Python.h>
// already included above
// #include <stdbool.h>
// already included above
// #include "numpy/ndarrayobject.h"
// already included above
// #include "rosidl_runtime_c/visibility_control.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/servo_command__struct.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/servo_command__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool omnifleet_interfaces__srv__servo_command__response__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[62];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("omnifleet_interfaces.srv._servo_command.ServoCommand_Response", full_classname_dest, 61) == 0);
  }
  omnifleet_interfaces__srv__ServoCommand_Response * ros_message = _ros_message;
  {  // success
    PyObject * field = PyObject_GetAttrString(_pymsg, "success");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->success = (Py_True == field);
    Py_DECREF(field);
  }
  {  // value0
    PyObject * field = PyObject_GetAttrString(_pymsg, "value0");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->value0 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // value1
    PyObject * field = PyObject_GetAttrString(_pymsg, "value1");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->value1 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // value2
    PyObject * field = PyObject_GetAttrString(_pymsg, "value2");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->value2 = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // message
    PyObject * field = PyObject_GetAttrString(_pymsg, "message");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->message, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * omnifleet_interfaces__srv__servo_command__response__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of ServoCommand_Response */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("omnifleet_interfaces.srv._servo_command");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "ServoCommand_Response");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  omnifleet_interfaces__srv__ServoCommand_Response * ros_message = (omnifleet_interfaces__srv__ServoCommand_Response *)raw_ros_message;
  {  // success
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->success ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "success", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // value0
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->value0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "value0", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // value1
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->value1);
    {
      int rc = PyObject_SetAttrString(_pymessage, "value1", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // value2
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->value2);
    {
      int rc = PyObject_SetAttrString(_pymessage, "value2", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // message
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->message.data,
      strlen(ros_message->message.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "message", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
