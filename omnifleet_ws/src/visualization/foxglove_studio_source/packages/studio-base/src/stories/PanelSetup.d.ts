import { ComponentProps } from "react";
import { MosaicNode } from "react-mosaic-component";
import { MessageEvent, ParameterValue, RegisterMessageConverterArgs } from "@foxglove/studio";
import MockMessagePipelineProvider from "@foxglove/studio-base/components/MessagePipeline/MockMessagePipelineProvider";
import { PanelsActions } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
import { PanelCatalog } from "@foxglove/studio-base/context/PanelCatalogContext";
import { PanelStateStore } from "@foxglove/studio-base/context/PanelStateContext";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
import { AdvertiseOptions, PlayerStateActiveData, Progress, PublishPayload, Topic } from "@foxglove/studio-base/players/types";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
import { SavedProps, UserScripts } from "@foxglove/studio-base/types/panels";
import "react-mosaic-component/react-mosaic-component.css";
type Frame = {
    [topic: string]: MessageEvent[];
};
export type Fixture = {
    frame?: Frame;
    topics?: Topic[];
    capabilities?: string[];
    profile?: string;
    /** Do not include `messages` in player `activeData`.
     * Use `frame` instead, as it will populate player `activeData` automatically as necessary.
     */
    activeData?: Omit<Partial<PlayerStateActiveData>, "messages">;
    progress?: Progress;
    datatypes?: RosDatatypes;
    globalVariables?: GlobalVariables;
    layout?: MosaicNode<string>;
    userScripts?: UserScripts;
    savedProps?: SavedProps;
    publish?: (request: PublishPayload) => void;
    setPublishers?: (publisherId: string, advertisements: AdvertiseOptions[]) => void;
    setSubscriptions?: ComponentProps<typeof MockMessagePipelineProvider>["setSubscriptions"];
    setParameter?: (key: string, value: ParameterValue) => void;
    fetchAsset?: ComponentProps<typeof MockMessagePipelineProvider>["fetchAsset"];
    callService?: (service: string, request: unknown) => Promise<unknown>;
    messageConverters?: readonly RegisterMessageConverterArgs<unknown>[];
    panelState?: Partial<PanelStateStore>;
};
type UnconnectedProps = {
    children: React.ReactNode;
    fixture?: Fixture;
    includeSettings?: boolean;
    settingsWidth?: number;
    panelCatalog?: PanelCatalog;
    omitDragAndDrop?: boolean;
    pauseFrame?: ComponentProps<typeof MockMessagePipelineProvider>["pauseFrame"];
    style?: React.CSSProperties;
    className?: string;
};
export declare function triggerWheel(target: HTMLElement, deltaX: number): void;
type Props = UnconnectedProps & {
    includeSettings?: boolean;
    settingsWidth?: number;
    onLayoutAction?: (action: PanelsActions) => void;
};
export default function PanelSetup(props: Props): JSX.Element;
export {};
