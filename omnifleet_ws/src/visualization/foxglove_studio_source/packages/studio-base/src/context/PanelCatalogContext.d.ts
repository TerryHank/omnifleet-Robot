import { ComponentType } from "react";
import { PanelStatics } from "@foxglove/studio-base/components/Panel";
import { ExtensionNamespace } from "@foxglove/studio-base/types/Extensions";
import { PanelConfig } from "@foxglove/studio-base/types/panels";
export type PanelComponent = ComponentType<{
    childId?: string;
    tabId?: string;
}> & PanelStatics<PanelConfig>;
export type PanelInfo = {
    title: string;
    type: string;
    description?: string;
    thumbnail?: string;
    help?: React.ReactNode;
    /** Set this to true if a panel has custom toolbar items and so cannot be renamed. */
    hasCustomToolbar?: boolean;
    /**
     * The panel module is a function to load the panel.
     * This is to support our lazy built-in panels
     */
    module: () => Promise<{
        default: PanelComponent;
    }>;
    config?: PanelConfig;
    extensionNamespace?: ExtensionNamespace;
};
/** PanelCatalog describes the interface for getting available panels */
export interface PanelCatalog {
    /** get a list of the available panels */
    getPanels(): readonly PanelInfo[];
    /** Get panel information for a specific panel type (i.e. 3d, map, image, etc) */
    getPanelByType(type: string): PanelInfo | undefined;
}
declare const PanelCatalogContext: import("react").Context<PanelCatalog | undefined>;
export declare function usePanelCatalog(): PanelCatalog;
export default PanelCatalogContext;
