import { Immutable } from "@foxglove/studio";
import { Topic } from "@foxglove/studio-base/players/types";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
import { SaveConfig } from "@foxglove/studio-base/types/panels";
import { PublishConfig } from "./types";
export declare const defaultConfig: PublishConfig;
export declare function usePublishPanelSettings(config: PublishConfig, saveConfig: SaveConfig<PublishConfig>, topics: readonly Topic[], datatypes: Immutable<RosDatatypes>): void;
