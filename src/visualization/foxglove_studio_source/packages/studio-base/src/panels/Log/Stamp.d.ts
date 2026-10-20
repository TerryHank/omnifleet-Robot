/// <reference types="react" />
import { Time } from "@foxglove/studio";
import { TimeDisplayMethod } from "@foxglove/studio-base/types/panels";
type Props = {
    stamp: Time;
    timestampFormat: TimeDisplayMethod;
    timeZone: string | undefined;
};
declare function Stamp(props: Props): JSX.Element;
export default Stamp;
