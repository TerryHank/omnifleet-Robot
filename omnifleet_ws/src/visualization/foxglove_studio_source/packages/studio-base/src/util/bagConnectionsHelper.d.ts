import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
type DatatypeDescription = {
    messageDefinition: string;
    type: string;
};
export declare function bagConnectionsToDatatypes(connections: readonly DatatypeDescription[], { ros2 }: {
    ros2: boolean;
}): RosDatatypes;
export {};
