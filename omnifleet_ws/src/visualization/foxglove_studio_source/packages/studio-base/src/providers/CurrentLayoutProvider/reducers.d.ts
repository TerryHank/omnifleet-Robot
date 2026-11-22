import { PanelsActions, LayoutData } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
import { PlaybackConfig } from "@foxglove/studio-base/types/panels";
export declare const defaultPlaybackConfig: PlaybackConfig;
export default function (panelsState: Readonly<LayoutData>, action: PanelsActions): LayoutData;
