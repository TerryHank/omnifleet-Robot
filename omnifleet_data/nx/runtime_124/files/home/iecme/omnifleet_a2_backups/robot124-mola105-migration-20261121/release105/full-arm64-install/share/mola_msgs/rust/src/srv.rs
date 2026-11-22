#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to mola_msgs__srv__MapLoad_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapLoad_Request {
    /// Request.
    /// File relative or absolute path. Do not add any file extension, since maps
    /// may be loaded/saved to several files depending on implementation.
    pub map_path: std::string::String,

}



impl Default for MapLoad_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapLoad_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MapLoad_Request {
  type RmwMsg = super::srv::rmw::MapLoad_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        map_path: msg.map_path.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        map_path: msg.map_path.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      map_path: msg.map_path.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MapLoad_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapLoad_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: std::string::String,

}



impl Default for MapLoad_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapLoad_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MapLoad_Response {
  type RmwMsg = super::srv::rmw::MapLoad_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        error_message: msg.error_message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        error_message: msg.error_message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      error_message: msg.error_message.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MapSave_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapSave_Request {
    /// Request.
    /// File relative or absolute path. Do not add any file extension, since maps
    /// may be loaded/saved to several files depending on implementation.
    pub map_path: std::string::String,

}



impl Default for MapSave_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapSave_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MapSave_Request {
  type RmwMsg = super::srv::rmw::MapSave_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        map_path: msg.map_path.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        map_path: msg.map_path.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      map_path: msg.map_path.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MapSave_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapSave_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: std::string::String,

}



impl Default for MapSave_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapSave_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MapSave_Response {
  type RmwMsg = super::srv::rmw::MapSave_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        error_message: msg.error_message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        error_message: msg.error_message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      error_message: msg.error_message.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MolaRuntimeParamGet_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamGet_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for MolaRuntimeParamGet_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MolaRuntimeParamGet_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamGet_Request {
  type RmwMsg = super::srv::rmw::MolaRuntimeParamGet_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to mola_msgs__srv__MolaRuntimeParamGet_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamGet_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub parameters: std::string::String,

}



impl Default for MolaRuntimeParamGet_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MolaRuntimeParamGet_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamGet_Response {
  type RmwMsg = super::srv::rmw::MolaRuntimeParamGet_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        parameters: msg.parameters.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        parameters: msg.parameters.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      parameters: msg.parameters.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MolaRuntimeParamSet_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    pub parameters: std::string::String,

}



impl Default for MolaRuntimeParamSet_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MolaRuntimeParamSet_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamSet_Request {
  type RmwMsg = super::srv::rmw::MolaRuntimeParamSet_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        parameters: msg.parameters.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        parameters: msg.parameters.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      parameters: msg.parameters.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__MolaRuntimeParamSet_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MolaRuntimeParamSet_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

    /// In case of no success, here is a human-readable error reason.
    pub error_message: std::string::String,

}



impl Default for MolaRuntimeParamSet_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MolaRuntimeParamSet_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MolaRuntimeParamSet_Response {
  type RmwMsg = super::srv::rmw::MolaRuntimeParamSet_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        error_message: msg.error_message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        error_message: msg.error_message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      error_message: msg.error_message.to_string(),
    }
  }
}


// Corresponds to mola_msgs__srv__RelocalizeFromStateEstimator_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeFromStateEstimator_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for RelocalizeFromStateEstimator_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::RelocalizeFromStateEstimator_Request::default())
  }
}

impl rosidl_runtime_rs::Message for RelocalizeFromStateEstimator_Request {
  type RmwMsg = super::srv::rmw::RelocalizeFromStateEstimator_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to mola_msgs__srv__RelocalizeFromStateEstimator_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeFromStateEstimator_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,

}



impl Default for RelocalizeFromStateEstimator_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::RelocalizeFromStateEstimator_Response::default())
  }
}

impl rosidl_runtime_rs::Message for RelocalizeFromStateEstimator_Response {
  type RmwMsg = super::srv::rmw::RelocalizeFromStateEstimator_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
    }
  }
}


// Corresponds to mola_msgs__srv__RelocalizeNearPose_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeNearPose_Request {
    /// Request
    pub pose: geometry_msgs::msg::PoseWithCovarianceStamped,

}



impl Default for RelocalizeNearPose_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::RelocalizeNearPose_Request::default())
  }
}

impl rosidl_runtime_rs::Message for RelocalizeNearPose_Request {
  type RmwMsg = super::srv::rmw::RelocalizeNearPose_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovarianceStamped::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovarianceStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      pose: geometry_msgs::msg::PoseWithCovarianceStamped::from_rmw_message(msg.pose),
    }
  }
}


// Corresponds to mola_msgs__srv__RelocalizeNearPose_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RelocalizeNearPose_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,

}



impl Default for RelocalizeNearPose_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::RelocalizeNearPose_Response::default())
  }
}

impl rosidl_runtime_rs::Message for RelocalizeNearPose_Response {
  type RmwMsg = super::srv::rmw::RelocalizeNearPose_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
    }
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


