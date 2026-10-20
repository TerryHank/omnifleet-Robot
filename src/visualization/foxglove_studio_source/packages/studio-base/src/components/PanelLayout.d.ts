import React from "react";
import { MosaicNode } from "react-mosaic-component";
import "react-mosaic-component/react-mosaic-component.css";
type Props = {
    layout?: MosaicNode<string>;
    onChange: (panels: MosaicNode<string> | undefined) => void;
    tabId?: string;
};
export declare function UnconnectedPanelLayout(props: Props): React.ReactElement;
export default function PanelLayout(): JSX.Element;
export {};
