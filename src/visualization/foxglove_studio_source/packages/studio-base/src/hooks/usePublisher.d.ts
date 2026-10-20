import { Immutable } from "@foxglove/studio";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
type Props = Immutable<{
    topic: string;
    schemaName?: string;
    datatypes: RosDatatypes;
    name: string;
}>;
export default function usePublisher({ topic, schemaName, datatypes, name, }: Props): (msg: Record<string, unknown>) => void;
export {};
