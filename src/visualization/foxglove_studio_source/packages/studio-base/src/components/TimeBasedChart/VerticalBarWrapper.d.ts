/// <reference types="react" />
import { RpcScales } from "@foxglove/studio-base/components/Chart/types";
type VerticalBarWrapperProps = {
    scales?: RpcScales;
    xValue?: number;
};
export declare function VerticalBarWrapper({ children, scales, xValue, }: React.PropsWithChildren<VerticalBarWrapperProps>): JSX.Element;
export {};
