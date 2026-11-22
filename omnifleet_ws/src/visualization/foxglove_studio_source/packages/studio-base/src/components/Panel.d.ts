import { ComponentType } from "react";
import { PanelConfig, SaveConfig } from "@foxglove/studio-base/types/panels";
type Props<Config> = {
    childId?: string;
    overrideConfig?: Config;
    tabId?: string;
};
export interface PanelStatics<Config> {
    panelType: string;
    defaultConfig: Config;
}
export default function Panel<Config extends PanelConfig, PanelProps extends {
    config: Config;
    saveConfig: SaveConfig<Config>;
}>(PanelComponent: ComponentType<PanelProps> & PanelStatics<Config>): ComponentType<Props<Config> & Omit<PanelProps, "config" | "saveConfig">> & PanelStatics<Config>;
export {};
