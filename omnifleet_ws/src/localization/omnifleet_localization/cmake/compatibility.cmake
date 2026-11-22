# Preserve the library target exported before the sensing extraction.
if(NOT TARGET omnifleet_localization::omnifleet_sensor_conversions)
  add_library(omnifleet_localization::omnifleet_sensor_conversions INTERFACE IMPORTED)
  set_property(TARGET omnifleet_localization::omnifleet_sensor_conversions PROPERTY
    INTERFACE_LINK_LIBRARIES omnifleet_sensor_processing::omnifleet_sensor_conversions)
endif()
