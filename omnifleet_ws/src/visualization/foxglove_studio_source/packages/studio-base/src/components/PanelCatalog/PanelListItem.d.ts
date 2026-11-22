/// <reference types="react" />
import { MosaicPath } from "react-mosaic-component";
import { MosaicDropTargetPosition } from "react-mosaic-component/lib/internalTypes";
import { PanelInfo } from "@foxglove/studio-base/context/PanelCatalogContext";
import { PanelConfig } from "@foxglove/studio-base/types/panels";
export type DropDescription = {
    type: string;
    config?: PanelConfig;
    position?: MosaicDropTargetPosition;
    path?: MosaicPath;
    tabId?: string;
};
type Props = {
    panel: PanelInfo;
    searchQuery: string;
    checked?: boolean;
    highlighted?: boolean;
    onClick: () => void;
    mosaicId: string;
    onDragStart?: () => void;
    onDrop: (arg0: DropDescription) => void;
};
export declare function PanelListItem(props: Props): JSX.Element;
export {};
