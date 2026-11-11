import { Topic } from "@foxglove/studio";
/**
 * Determines whether `topic` has a supported schema from the set of `supportedSchemaNames`, either
 * as the original schema or one of the `convertibleTo` schemas.
 */
export declare function topicIsConvertibleToSchema(topic: Topic, supportedSchemaNames: Set<string>): boolean;
