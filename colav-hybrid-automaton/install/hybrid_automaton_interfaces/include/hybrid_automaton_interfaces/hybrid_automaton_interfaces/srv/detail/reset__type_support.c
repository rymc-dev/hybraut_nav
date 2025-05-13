// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:srv/Reset.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/srv/detail/reset__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/srv/detail/reset__functions.h"
#include "hybrid_automaton_interfaces/srv/detail/reset__struct.h"


// Include directives for member types
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `reset_name`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__srv__Reset_Request__init(message_memory);
}

void hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__srv__Reset_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_member_array[2] = {
  {
    "transition_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Request, transition_uuid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "reset_name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Request, reset_name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_members = {
  "hybrid_automaton_interfaces__srv",  // message namespace
  "Reset_Request",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__srv__Reset_Request),
  hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_member_array,  // message members
  hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Request)() {
  hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  if (!hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__srv__Reset_Request__rosidl_typesupport_introspection_c__Reset_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/srv/detail/reset__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/srv/detail/reset__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/srv/detail/reset__struct.h"


// Include directives for member types
// Member `transition_uuid`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `transition_uuid`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `reset_name`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__srv__Reset_Response__init(message_memory);
}

void hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__srv__Reset_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_member_array[4] = {
  {
    "transition_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Response, transition_uuid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "reset_name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Response, reset_name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__srv__Reset_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_members = {
  "hybrid_automaton_interfaces__srv",  // message namespace
  "Reset_Response",  // message name
  4,  // number of fields
  sizeof(hybrid_automaton_interfaces__srv__Reset_Response),
  hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_member_array,  // message members
  hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Response)() {
  hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  if (!hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__srv__Reset_Response__rosidl_typesupport_introspection_c__Reset_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "hybrid_automaton_interfaces/srv/detail/reset__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_members = {
  "hybrid_automaton_interfaces__srv",  // service namespace
  "Reset",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_Request_message_type_support_handle,
  NULL  // response message
  // hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_Response_message_type_support_handle
};

static rosidl_service_type_support_t hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset)() {
  if (!hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, srv, Reset_Response)()->data;
  }

  return &hybrid_automaton_interfaces__srv__detail__reset__rosidl_typesupport_introspection_c__Reset_service_type_support_handle;
}
