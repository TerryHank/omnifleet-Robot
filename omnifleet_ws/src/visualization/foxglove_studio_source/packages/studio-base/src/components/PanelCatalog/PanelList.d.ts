/// <reference types="react" />
import { PanelInfo } from "@foxglove/studio-base/context/PanelCatalogContext";
import { PanelSelection } from "./types";
type Props = {
    filteredPanels: PanelInfo[];
    onPanelSelect: (arg0: PanelSelection) => void;
    onDragStart?: () => void;
    selectedPanelType?: string;
    highlightedPanelIdx?: number;
    searchQuery?: string;
};
export declare function PanelList(props: Props): JSX.Element;
export {};
