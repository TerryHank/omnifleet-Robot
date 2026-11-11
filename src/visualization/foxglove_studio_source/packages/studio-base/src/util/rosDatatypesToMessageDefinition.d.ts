import { MessageDefinition } from "@foxglove/message-definition";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
export default function rosDatatypesToMessageDefinition(datatypes: RosDatatypes, rootDatatypeName: string): MessageDefinition[];
