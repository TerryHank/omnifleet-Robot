/// <reference types="react" />
import { ChartOptions } from "chart.js";
import { TypedChartData, ChartData, RpcElement, RpcScales } from "./types";
export type OnClickArg = {
    datalabel?: unknown;
    x: number | undefined;
    y: number | undefined;
};
type Props = {
    data?: ChartData;
    typedData?: TypedChartData;
    options: ChartOptions;
    isBoundsReset: boolean;
    type: "scatter";
    height: number;
    width: number;
    onClick?: (params: OnClickArg) => void;
    onScalesUpdate?: (scales: RpcScales, opt: {
        userInteraction: boolean;
    }) => void;
    onStartRender?: () => void;
    onFinishRender?: () => void;
    onHover?: (elements: RpcElement[]) => void;
};
declare function Chart(props: Props): JSX.Element;
export default Chart;
