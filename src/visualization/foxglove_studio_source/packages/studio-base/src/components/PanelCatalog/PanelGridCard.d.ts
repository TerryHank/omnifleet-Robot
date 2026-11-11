/// <reference types="react" />
import { PanelInfo } from "@foxglove/studio-base/context/PanelCatalogContext";
type Props = {
    panel: PanelInfo;
    searchQuery: string;
    onClick: () => void;
};
export declare function PanelGridCard(props: Props): JSX.Element;
export {};
