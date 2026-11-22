import type { MosaicPath } from "react-mosaic-component";
export type MosaicDropTargetPosition = "top" | "bottom" | "left" | "right";
export type MosaicDropResult = {
    path?: MosaicPath;
    position?: MosaicDropTargetPosition;
    tabId?: string;
};
export type PanelConfig = {
    [key: string]: unknown;
};
export type TimeDisplayMethod = "SEC" | "TOD";
export type PlaybackConfig = {
    speed: number;
};
export type UserScript = {
    name: string;
    sourceCode: string;
};
export type UserScripts = {
    [scriptId: string]: UserScript;
};
export type SaveConfig<Config> = (newConfig: Partial<Config> | ((oldConfig: Config) => Partial<Config>)) => void;
export type SavedProps = {
    [panelId: string]: PanelConfig;
};
export type OpenSiblingPanel = (params: {
    panelType: string;
    siblingConfigCreator: (config: PanelConfig) => PanelConfig;
    updateIfExists: boolean;
}) => void;
