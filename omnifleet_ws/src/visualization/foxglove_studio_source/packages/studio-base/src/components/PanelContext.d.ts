/// <reference types="react" />
import { MessagePathDropConfig } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { SaveConfig, PanelConfig, OpenSiblingPanel } from "@foxglove/studio-base/types/panels";
export type PanelContextType<T> = {
    type: string;
    id: string;
    title: string;
    tabId?: string;
    config: PanelConfig;
    saveConfig: SaveConfig<T>;
    updatePanelConfigs: (panelType: string, updateConfig: (config: T) => T) => void;
    openSiblingPanel: OpenSiblingPanel;
    replacePanel: (panelType: string, config: Record<string, unknown>) => void;
    enterFullscreen: () => void;
    exitFullscreen: () => void;
    isFullscreen: boolean;
    /** Used to adjust z-index settings on parent panels when children are fullscreen */
    setHasFullscreenDescendant: (hasFullscreenDescendant: boolean) => void;
    connectToolbarDragHandle?: (el: Element | ReactNull) => void;
    setMessagePathDropConfig: (config: MessagePathDropConfig | undefined) => void;
};
declare const PanelContext: import("react").Context<PanelContextType<PanelConfig> | undefined>;
export declare function usePanelContext(): PanelContextType<PanelConfig>;
export default PanelContext;
