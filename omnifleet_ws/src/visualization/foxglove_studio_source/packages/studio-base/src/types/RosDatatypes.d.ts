import { MessageDefinition, MessageDefinitionField } from "@foxglove/message-definition";
/**
 * Extend the standard ROS message definition with an optional flag.
 */
type OptionalMessageDefinitionField = MessageDefinitionField & {
    optional?: boolean;
};
export type OptionalMessageDefinition = MessageDefinition & {
    definitions: OptionalMessageDefinitionField[];
};
/** RosDatatypes is a map of datatype name to the datatype definition */
export type RosDatatypes = Map<string, OptionalMessageDefinition>;
export {};
