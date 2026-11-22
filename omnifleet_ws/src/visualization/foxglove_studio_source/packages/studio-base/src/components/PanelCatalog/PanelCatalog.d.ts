/// <reference types="react" />
import { PanelSelection } from "./types";
type Props = {
    onPanelSelect: (arg0: PanelSelection) => void;
    onDragStart?: () => void;
    selectedPanelType?: string;
    mode?: "grid" | "list";
    isMenu?: boolean;
};
export declare const PanelCatalog: import("react").ForwardRefExoticComponent<Props & import("react").RefAttributes<HTMLDivElement>>;
export {};
