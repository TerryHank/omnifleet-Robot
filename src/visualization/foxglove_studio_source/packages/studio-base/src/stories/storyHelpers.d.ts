import { CSSProperties, PropsWithChildren } from "react";
type ExpectedResultProps = {
    top?: CSSProperties["top"];
    left?: CSSProperties["left"];
};
export declare function ExpectedResult(props: PropsWithChildren<ExpectedResultProps>): React.ReactElement;
export {};
