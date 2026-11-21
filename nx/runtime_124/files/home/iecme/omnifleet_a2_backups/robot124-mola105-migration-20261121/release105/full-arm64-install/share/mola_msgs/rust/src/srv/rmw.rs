#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapLoad_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MapLoad_Request__init(msg: *mut MapLoad_Request) -> bool;
    fn mola_msgs__srv__MapLoad_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Request>, size: usize) -> bool;
    fn mola_msgs__srv__MapLoad_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Request>);
    fn mola_msgs__srv__MapLoad_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapLoad_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__MapLoad_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapLoad_Request {
    /// Request.
    /// File relative or absolute path. Do not add any file extension, since maps
    /// may be loaded/saved to several files depending on implementation.
    pub map_path: rosidl_runtime_rs::String,

}



impl Default for MapLoad_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MapLoad_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MapLoad_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapLoad_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapLoad_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapLoad_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MapLoad_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapLoad_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapLoad_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MapLoad_Response__init(msg: *mut MapLoad_Response) -> bool;
    fn mola_msgs__srv__MapLoad_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Response>, size: usize) -> bool;
    fn mola_msgs__srv__MapLoad_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Response>);
    fn mola_msgs__srv__MapLoad_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapLoad_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MapLoad_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__MapLoad_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapLoad_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: rosidl_runtime_rs::String,

}



impl Default for MapLoad_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MapLoad_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MapLoad_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapLoad_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapLoad_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapLoad_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapLoad_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MapLoad_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapLoad_Response() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapSave_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MapSave_Request__init(msg: *mut MapSave_Request) -> bool;
    fn mola_msgs__srv__MapSave_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapSave_Request>, size: usize) -> bool;
    fn mola_msgs__srv__MapSave_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapSave_Request>);
    fn mola_msgs__srv__MapSave_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapSave_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MapSave_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__MapSave_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapSave_Request {
    /// Request.
    /// File relative or absolute path. Do not add any file extension, since maps
    /// may be loaded/saved to several files depending on implementation.
    pub map_path: rosidl_runtime_rs::String,

}



impl Default for MapSave_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MapSave_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MapSave_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapSave_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapSave_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapSave_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MapSave_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapSave_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapSave_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MapSave_Response__init(msg: *mut MapSave_Response) -> bool;
    fn mola_msgs__srv__MapSave_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapSave_Response>, size: usize) -> bool;
    fn mola_msgs__srv__MapSave_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapSave_Response>);
    fn mola_msgs__srv__MapSave_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapSave_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MapSave_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__MapSave_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapSave_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: rosidl_runtime_rs::String,

}



impl Default for MapSave_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MapSave_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MapSave_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapSave_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MapSave_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapSave_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapSave_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MapSave_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MapSave_Response() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MolaRuntimeParamGet_Request__init(msg: *mut MolaRuntimeParamGet_Request) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Request>, size: usize) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Request>);
    fn mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamGet_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamGet_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for MolaRuntimeParamGet_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MolaRuntimeParamGet_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MolaRuntimeParamGet_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MolaRuntimeParamGet_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamGet_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MolaRuntimeParamGet_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MolaRuntimeParamGet_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MolaRuntimeParamGet_Response__init(msg: *mut MolaRuntimeParamGet_Response) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Response>, size: usize) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Response>);
    fn mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamGet_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamGet_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamGet_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub parameters: rosidl_runtime_rs::String,

}



impl Default for MolaRuntimeParamGet_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MolaRuntimeParamGet_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MolaRuntimeParamGet_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MolaRuntimeParamGet_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamGet_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MolaRuntimeParamGet_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MolaRuntimeParamGet_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet_Response() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MolaRuntimeParamSet_Request__init(msg: *mut MolaRuntimeParamSet_Request) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Request>, size: usize) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Request>);
    fn mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamSet_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamSet_Request {
    /// Request: a multiline string in YAML format with all parameters that need to be changed, in this format:
    /// ---
    /// module1:
    ///   var: value
    /// module2:
    ///   var: value
    /// ...
    /// ---
    pub parameters: rosidl_runtime_rs::String,

}



impl Default for MolaRuntimeParamSet_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MolaRuntimeParamSet_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MolaRuntimeParamSet_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MolaRuntimeParamSet_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamSet_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MolaRuntimeParamSet_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MolaRuntimeParamSet_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__MolaRuntimeParamSet_Response__init(msg: *mut MolaRuntimeParamSet_Response) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Response>, size: usize) -> bool;
    fn mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Response>);
    fn mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MolaRuntimeParamSet_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamSet_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamSet_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: rosidl_runtime_rs::String,

}



impl Default for MolaRuntimeParamSet_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__MolaRuntimeParamSet_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__MolaRuntimeParamSet_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MolaRuntimeParamSet_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamSet_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MolaRuntimeParamSet_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/MolaRuntimeParamSet_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet_Response() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Request__init(msg: *mut RelocalizeFromStateEstimator_Request) -> bool;
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Request>, size: usize) -> bool;
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Request>);
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__RelocalizeFromStateEstimator_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeFromStateEstimator_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for RelocalizeFromStateEstimator_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__RelocalizeFromStateEstimator_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__RelocalizeFromStateEstimator_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RelocalizeFromStateEstimator_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RelocalizeFromStateEstimator_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RelocalizeFromStateEstimator_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/RelocalizeFromStateEstimator_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Response__init(msg: *mut RelocalizeFromStateEstimator_Response) -> bool;
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Response>, size: usize) -> bool;
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Response>);
    fn mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<RelocalizeFromStateEstimator_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__RelocalizeFromStateEstimator_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeFromStateEstimator_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,

}



impl Default for RelocalizeFromStateEstimator_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__RelocalizeFromStateEstimator_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__RelocalizeFromStateEstimator_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RelocalizeFromStateEstimator_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RelocalizeFromStateEstimator_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RelocalizeFromStateEstimator_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/RelocalizeFromStateEstimator_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator_Response() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeNearPose_Request() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__RelocalizeNearPose_Request__init(msg: *mut RelocalizeNearPose_Request) -> bool;
    fn mola_msgs__srv__RelocalizeNearPose_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Request>, size: usize) -> bool;
    fn mola_msgs__srv__RelocalizeNearPose_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Request>);
    fn mola_msgs__srv__RelocalizeNearPose_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RelocalizeNearPose_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Request>) -> bool;
}

// Corresponds to mola_msgs__srv__RelocalizeNearPose_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeNearPose_Request {
    /// Request
    pub pose: geometry_msgs::msg::rmw::PoseWithCovarianceStamped,

}



impl Default for RelocalizeNearPose_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__RelocalizeNearPose_Request__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__RelocalizeNearPose_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RelocalizeNearPose_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RelocalizeNearPose_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RelocalizeNearPose_Request where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/RelocalizeNearPose_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeNearPose_Request() }
  }
}


#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeNearPose_Response() -> *const std::ffi::c_void;
}

#[link(name = "mola_msgs__rosidl_generator_c")]
extern "C" {
    fn mola_msgs__srv__RelocalizeNearPose_Response__init(msg: *mut RelocalizeNearPose_Response) -> bool;
    fn mola_msgs__srv__RelocalizeNearPose_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Response>, size: usize) -> bool;
    fn mola_msgs__srv__RelocalizeNearPose_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Response>);
    fn mola_msgs__srv__RelocalizeNearPose_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RelocalizeNearPose_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<RelocalizeNearPose_Response>) -> bool;
}

// Corresponds to mola_msgs__srv__RelocalizeNearPose_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeNearPose_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,

}



impl Default for RelocalizeNearPose_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !mola_msgs__srv__RelocalizeNearPose_Response__init(&mut msg as *mut _) {
        panic!("Call to mola_msgs__srv__RelocalizeNearPose_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RelocalizeNearPose_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { mola_msgs__srv__RelocalizeNearPose_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RelocalizeNearPose_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RelocalizeNearPose_Response where Self: Sized {
  const TYPE_NAME: &'static str = "mola_msgs/srv/RelocalizeNearPose_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__mola_msgs__srv__RelocalizeNearPose_Response() }
  }
}






#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MapLoad() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__MapLoad
#[allow(missing_docs, non_camel_case_types)]
pub struct MapLoad;

impl rosidl_runtime_rs::Service for MapLoad {
    type Request = MapLoad_Request;
    type Response = MapLoad_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MapLoad() }
    }
}




#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MapSave() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__MapSave
#[allow(missing_docs, non_camel_case_types)]
pub struct MapSave;

impl rosidl_runtime_rs::Service for MapSave {
    type Request = MapSave_Request;
    type Response = MapSave_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MapSave() }
    }
}




#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamGet
#[allow(missing_docs, non_camel_case_types)]
pub struct MolaRuntimeParamGet;

impl rosidl_runtime_rs::Service for MolaRuntimeParamGet {
    type Request = MolaRuntimeParamGet_Request;
    type Response = MolaRuntimeParamGet_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MolaRuntimeParamGet() }
    }
}




#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__MolaRuntimeParamSet
#[allow(missing_docs, non_camel_case_types)]
pub struct MolaRuntimeParamSet;

impl rosidl_runtime_rs::Service for MolaRuntimeParamSet {
    type Request = MolaRuntimeParamSet_Request;
    type Response = MolaRuntimeParamSet_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__MolaRuntimeParamSet() }
    }
}




#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__RelocalizeFromStateEstimator
#[allow(missing_docs, non_camel_case_types)]
pub struct RelocalizeFromStateEstimator;

impl rosidl_runtime_rs::Service for RelocalizeFromStateEstimator {
    type Request = RelocalizeFromStateEstimator_Request;
    type Response = RelocalizeFromStateEstimator_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__RelocalizeFromStateEstimator() }
    }
}




#[link(name = "mola_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__RelocalizeNearPose() -> *const std::ffi::c_void;
}

// Corresponds to mola_msgs__srv__RelocalizeNearPose
#[allow(missing_docs, non_camel_case_types)]
pub struct RelocalizeNearPose;

impl rosidl_runtime_rs::Service for RelocalizeNearPose {
    type Request = RelocalizeNearPose_Request;
    type Response = RelocalizeNearPose_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__mola_msgs__srv__RelocalizeNearPose() }
    }
}


