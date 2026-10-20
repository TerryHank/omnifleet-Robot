import { ParameterValue } from "@foxglove/studio";
import { PlayerCapabilities, PlayerStateActiveData, PlayerState, Player, SubscribePayload, AdvertiseOptions, PlayerPresence } from "@foxglove/studio-base/players/types";
export default class FakePlayer implements Player {
    #private;
    playerId: string;
    subscriptions: SubscribePayload[];
    publishers: AdvertiseOptions[] | undefined;
    setListener(listener: (arg0: PlayerState) => Promise<void>): void;
    emit({ activeData, presence, progress, playerId, }?: {
        activeData?: PlayerStateActiveData;
        presence?: PlayerPresence;
        progress?: PlayerState["progress"];
        playerId?: string;
    }): Promise<void>;
    close: () => void;
    setPlaybackSpeed: () => void;
    pausePlayback: () => void;
    publish: () => void;
    callService: () => Promise<void>;
    setPublishers: (pubs: AdvertiseOptions[]) => void;
    setParameter(_key: string, _value: ParameterValue): void;
    setSubscriptions: (subs: SubscribePayload[]) => void;
    setCapabilities: (capabilities: (typeof PlayerCapabilities)[keyof typeof PlayerCapabilities][]) => void;
    setProfile: (profile: string | undefined) => void;
    startPlayback: () => void;
    seekPlayback: () => void;
    setGlobalVariables: () => void;
}
