/// <reference types="react" />
import { Time } from "@foxglove/rostime";
type Props = {
    onSeek: (seekTo: Time) => void;
};
export default function Scrubber(props: Props): JSX.Element;
export {};
