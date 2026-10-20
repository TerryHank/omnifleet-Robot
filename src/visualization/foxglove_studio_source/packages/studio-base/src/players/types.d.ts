import { MessageDefinition } from "@foxglove/message-definition";
import { Time } from "@foxglove/rostime";
import type { MessageEvent, ParameterValue } from "@foxglove/studio";
import { Immutable } from "@foxglove/studio";
import { Asset } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
import { RosDatatypes } from "@foxglove/studio-base/types/RosDatatypes";
import { Range } from "@foxglove/studio-base/util/ranges";
import { NotificationSeverity } from "@foxglove/studio-base/util/sendNotification";
export type { MessageEvent };
export type MessageDefinitionsByTopic = {
    [topic: string]: string;
};
export type ParsedMessageDefinitionsByTopic = {
    [topic: string]: MessageDefinition[];
};
export type TopicSelection = Map<string, SubscribePayload>;
export interface Player {
    setListener(listener: (playerState: PlayerState) => Promise<void>): void;
    close(): void;
    setSubscriptions(subscriptions: Immutable<SubscribePayload[]>): void;
    setPublishers(publishers: AdvertiseOptions[]): void;
    setParameter(key: string, value: ParameterValue): void;
    publish(request: PublishPayload): void;
    callService(service: string, request: unknown): Promise<unknown>;
    fetchAsset?(uri: string): Promise<Asset>;
    startPlayback?(): void;
    pausePlayback?(): void;
    seekPlayback?(time: Time): void;
    playUntil?(time: Time): void;
    setPlaybackSpeed?(speedFraction: number): void;
    setGlobalVariables(globalVariables: GlobalVariables): void;
}
export declare enum PlayerPresence {
    NOT_PRESENT = "NOT_PRESENT",
    INITIALIZING = "INITIALIZING",
    RECONNECTING = "RECONNECTING",
    BUFFERING = "BUFFERING",
    PRESENT = "PRESENT",
    ERROR = "ERROR"
}
export type PlayerProblem = {
    severity: NotificationSeverity;
    message: string;
    error?: Error;
    tip?: string;
};
export type PlayerURLState = Immutable<{
    sourceId: string;
    parameters?: Record<string, string>;
}>;
export type PlayerState = {
    presence: PlayerPresence;
    progress: Progress;
    capabilities: (typeof PlayerCapabilities)[keyof typeof PlayerCapabilities][];
    /**
     * Identifies the semantics of the data being played back, such as which topics or parameters are
     * semantically meaningful or normalization conventions to use. This typically maps to a shorthand
     * identifier for a robotics framework such as "ros1", "ros2", or "ulog". See the MCAP profiles
     * concept at <https://github.com/foxglove/mcap/blob/main/docs/specification/appendix.md#well-known-profiles>.
     */
    profile: string | undefined;
    playerId: string;
    name?: string;
    problems?: PlayerProblem[];
    activeData?: PlayerStateActiveData;
    /** State to serialize into the active URL. */
    urlState?: PlayerURLState;
};
export type PlayerStateActiveData = {
    messages: readonly MessageEvent[];
    totalBytesReceived: number;
    currentTime: Time;
    startTime: Time;
    endTime: Time;
    isPlaying: boolean;
    speed: number;
    lastSeekTime: number;
    topics: Topic[];
    topicStats: Map<string, TopicStats>;
    datatypes: RosDatatypes;
    publishedTopics?: Map<string, Set<string>>;
    subscribedTopics?: Map<string, Set<string>>;
    services?: Map<string, Set<string>>;
    parameters?: Map<string, ParameterValue>;
};
export type Topic = {
    name: string;
    schemaName: string | undefined;
    aliasedFromName?: string;
};
export type TopicWithSchemaName = Topic & {
    schemaName: string;
};
export type TopicStats = {
    numMessages: number;
    firstMessageTime?: Time;
    lastMessageTime?: Time;
};
type RosTypedArray = Int8Array | Uint8Array | Int16Array | Uint16Array | Int32Array | Uint32Array | Float32Array | Float64Array;
type RosSingularField = number | string | boolean | RosObject | undefined;
export type RosValue = RosSingularField | readonly RosSingularField[] | RosTypedArray | null;
export type RosObject = Readonly<{
    [property: string]: RosValue;
}>;
export type MessageBlock = {
    readonly messagesByTopic: {
        readonly [topic: string]: MessageEvent[];
    };
    /**
     * Indicates which topics are yet to be fully loaded for this block. Can be used to track the
     * progress of block loading. For a fully loaded block this will be empty or undefined.
     */
    needTopics?: TopicSelection;
    readonly sizeInBytes: number;
};
export type BlockCache = {
    blocks: readonly (MessageBlock | undefined)[];
    startTime: Time;
};
export type Progress = Readonly<{
    fullyLoadedFractionRanges?: Range[];
    readonly messageCache?: BlockCache;
    /** Memory usage information, e.g. the memory size occupied by preloaded or buffered messages. */
    readonly memoryInfo?: Record<string, number>;
}>;
export type SubscriptionPreloadType = "full" | "partial";
/**
 * Represents a subscription to a single topic, for use in `setSubscriptions`.
 */
export type SubscribePayload = {
    /**
     * The name of the topic to subscribe to.
     */
    topic: string;
    /**
     * If defined the source will return only these fields from messages.
     * Otherwise entire messages will be returned.
     */
    fields?: string[];
    /**
     * Defines the range of messages to subscribe to.
     */
    preloadType?: SubscriptionPreloadType;
};
export type AdvertiseOptions = {
    /** The topic name */
    topic: string;
    /** The schema name */
    schemaName: string;
    /** Additional player-specific advertise options */
    options?: Record<string, unknown>;
};
export type PublishPayload = {
    topic: string;
    msg: Record<string, unknown>;
};
export declare const PlayerCapabilities: {
    advertise: string;
    assets: string;
    callServices: string;
    setSpeed: string;
    playbackControl: string;
    getParameters: string;
    setParameters: string;
};
export interface PlayerMetricsCollectorInterface {
    setProperty(key: string, value: string | number | boolean): void;
    playerConstructed(): void;
}
