import { PropsWithChildren } from "react";
import { Immutable } from "@foxglove/studio";
export type TimeBasedChartTooltipData = {
    configIndex: number;
    value: number | bigint | boolean | string;
    constantName?: string;
};
type Props = Immutable<{
    colorsByConfigIndex?: Record<string, undefined | string>;
    content: TimeBasedChartTooltipData[];
    labelsByConfigIndex?: Record<string, undefined | string>;
    multiDataset: boolean;
}>;
export default function TimeBasedChartTooltipContent(props: PropsWithChildren<Props>): React.ReactElement;
export {};
