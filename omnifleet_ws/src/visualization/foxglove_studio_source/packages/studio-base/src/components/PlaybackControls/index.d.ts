/// <reference types="react" />
import { Time } from "@foxglove/rostime";
import { Player } from "@foxglove/studio-base/players/types";
export default function PlaybackControls(props: {
    play: NonNullable<Player["startPlayback"]>;
    pause: NonNullable<Player["pausePlayback"]>;
    seek: NonNullable<Player["seekPlayback"]>;
    playUntil?: Player["playUntil"];
    isPlaying: boolean;
    getTimeInfo: () => {
        startTime?: Time;
        endTime?: Time;
        currentTime?: Time;
    };
}): JSX.Element;
