import { Time } from "@foxglove/rostime";
import { ParameterValue } from "@foxglove/studio";
import { AdvertiseOptions, Player, PlayerMetricsCollectorInterface, PlayerState, PublishPayload, SubscribePayload } from "@foxglove/studio-base/players/types";
import { IIterableSource } from "./IIterableSource";
type IterablePlayerOptions = {
    metricsCollector?: PlayerMetricsCollectorInterface;
    source: IIterableSource;
    name?: string;
    urlParams?: Record<string, string>;
    sourceId: string;
    isSampleDataSource?: boolean;
    enablePreload?: boolean;
};
/**
 * IterablePlayer implements the Player interface for IIterableSource instances.
 *
 * The iterable player reads messages from an IIterableSource. The player is implemented as a state
 * machine. Each state runs until it finishes. A request to change state is handled by each state
 * detecting that there is another state waiting and cooperatively ending itself.
 */
export declare class IterablePlayer implements Player {
    #private;
    /** Promise that resolves when the player is closed. Only used for testing currently */
    readonly isClosed: Promise<void>;
    constructor(options: IterablePlayerOptions);
    setListener(listener: (playerState: PlayerState) => Promise<void>): void;
    startPlayback(): void;
    playUntil(time: Time): void;
    pausePlayback(): void;
    setPlaybackSpeed(speed: number): void;
    seekPlayback(time: Time): void;
    setSubscriptions(newSubscriptions: SubscribePayload[]): void;
    setPublishers(_publishers: AdvertiseOptions[]): void;
    setParameter(_key: string, _value: ParameterValue): void;
    publish(_payload: PublishPayload): void;
    callService(): Promise<unknown>;
    close(): void;
    setGlobalVariables(): void;
}
export {};
