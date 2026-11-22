import { MosaicNode } from "react-mosaic-component";
export type TabConfig = {
    title: string;
    layout?: MosaicNode<string>;
};
export type TabPanelConfig = {
    activeTabIdx: number;
    tabs: Array<TabConfig>;
};
export type TabLocation = {
    panelId: string;
    tabIndex?: number;
};
