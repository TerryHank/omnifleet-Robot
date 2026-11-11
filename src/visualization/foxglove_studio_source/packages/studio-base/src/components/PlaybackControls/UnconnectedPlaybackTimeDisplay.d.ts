/// <reference types="react" />
import { Time } from "@foxglove/rostime";
import { IAppTimeFormat } from "@foxglove/studio-base/hooks/useAppTimeFormat";
type PlaybackTimeDisplayMethodProps = {
    appTimeFormat: IAppTimeFormat;
    currentTime?: Time;
    startTime?: Time;
    endTime?: Time;
    timezone?: string;
    onSeek: (arg0: Time) => void;
    onPause: () => void;
    isPlaying: boolean;
};
export declare function UnconnectedPlaybackTimeDisplay({ appTimeFormat, currentTime, startTime, endTime, timezone, onSeek, onPause, isPlaying, }: PlaybackTimeDisplayMethodProps): JSX.Element;
export {};
