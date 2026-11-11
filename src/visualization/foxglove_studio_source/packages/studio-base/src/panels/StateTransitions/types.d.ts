import { TimestampMethod } from "@foxglove/studio-base/util/time";
export type StateTransitionPath = {
    color?: string;
    value: string;
    label?: string;
    enabled?: boolean;
    timestampMethod: TimestampMethod;
};
export type StateTransitionConfig = {
    isSynced: boolean;
    paths: StateTransitionPath[];
    xAxisMaxValue?: number;
    xAxisMinValue?: number;
    xAxisRange?: number;
    showPoints?: boolean;
};
