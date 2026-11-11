/// <reference types="react" />
import { Immutable } from "@foxglove/studio";
import { Range } from "@foxglove/studio-base/util/ranges";
type ProgressProps = Immutable<{
    loading: boolean;
    availableRanges?: Range[];
}>;
export declare function ProgressPlot(props: ProgressProps): JSX.Element;
export {};
