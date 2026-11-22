/// <reference types="react" />
import { PanelInfo } from "@foxglove/studio-base/context/PanelCatalogContext";
import { PanelSelection } from "./types";
type Props = {
    filteredPanels: PanelInfo[];
    onPanelSelect: (arg0: PanelSelection) => void;
    searchQuery?: string;
};
export declare function PanelGrid(props: Props): JSX.Element;
export {};
