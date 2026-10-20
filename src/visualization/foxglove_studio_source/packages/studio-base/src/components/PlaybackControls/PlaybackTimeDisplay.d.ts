/// <reference types="react" />
import { Time } from "@foxglove/rostime";
type Props = {
    onSeek: (seekTo: Time) => void;
    onPause: () => void;
};
export default function PlaybackTimeDisplay(props: Props): JSX.Element;
export {};
