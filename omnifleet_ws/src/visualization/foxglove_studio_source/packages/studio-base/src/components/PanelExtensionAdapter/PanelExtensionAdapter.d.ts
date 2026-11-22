/// <reference types="react" />
import { ExtensionPanelRegistration } from "@foxglove/studio";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { BuiltinPanelExtensionContext } from "./types";
export declare const VERSION_CONFIG_KEY = "foxgloveConfigVersion";
type PanelExtensionAdapterProps = {
    /** function that initializes the panel extension */
    initPanel: ExtensionPanelRegistration["initPanel"] | ((context: BuiltinPanelExtensionContext) => void);
    /**
     * If defined, the highest supported version of config the panel supports.
     * Used to prevent older implementations of a panel from trying to access
     * newer, incompatible versions of the panel's config. Panels should include a
     * numbered foxgloveConfigVersion property in their config to control this.
     */
    highestSupportedConfigVersion?: number;
    config: unknown;
    saveConfig: SaveConfig<unknown>;
};
/**
 * PanelExtensionAdapter renders a panel extension via initPanel
 *
 * The adapter creates a PanelExtensionContext and invokes initPanel using the context.
 */
declare function PanelExtensionAdapter(props: React.PropsWithChildren<PanelExtensionAdapterProps>): JSX.Element;
export default PanelExtensionAdapter;
