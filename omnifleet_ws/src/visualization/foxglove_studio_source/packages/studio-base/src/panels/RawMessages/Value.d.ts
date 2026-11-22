/// <reference types="react" />
import { OpenSiblingPanel } from "@foxglove/studio-base/types/panels";
import { ValueAction } from "./getValueActionForValue";
type ValueProps = {
    arrLabel: string;
    basePath: string;
    itemLabel: string;
    itemValue: unknown;
    valueAction: ValueAction | undefined;
    onTopicPathChange: (arg0: string) => void;
    openSiblingPanel: OpenSiblingPanel;
};
declare function Value(props: ValueProps): JSX.Element;
declare const _default: import("react").MemoExoticComponent<typeof Value>;
export default _default;
