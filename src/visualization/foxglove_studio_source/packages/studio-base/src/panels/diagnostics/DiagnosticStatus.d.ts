/// <reference types="react" />
import { OpenSiblingPanel } from "@foxglove/studio-base/types/panels";
import { DiagnosticInfo } from "./util";
type Props = {
    info: DiagnosticInfo;
    splitFraction: number | undefined;
    onChangeSplitFraction: (arg0: number) => void;
    topicToRender: string;
    numericPrecision: number | undefined;
    openSiblingPanel: OpenSiblingPanel;
};
export default function DiagnosticStatus(props: Props): JSX.Element;
export {};
