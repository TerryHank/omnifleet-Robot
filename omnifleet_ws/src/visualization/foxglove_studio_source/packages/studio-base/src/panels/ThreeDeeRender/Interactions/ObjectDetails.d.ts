/// <reference types="react" />
import { RosValue } from "@foxglove/studio-base/players/types";
import { InteractionData } from "./types";
type Props = {
    readonly interactionData?: InteractionData;
    readonly selectedObject?: RosValue;
    readonly timezone: string | undefined;
};
declare function ObjectDetails({ interactionData, selectedObject, timezone }: Props): JSX.Element;
export default ObjectDetails;
