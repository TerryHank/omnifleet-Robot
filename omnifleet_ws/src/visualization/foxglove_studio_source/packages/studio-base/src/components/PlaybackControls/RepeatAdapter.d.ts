/// <reference types="react" />
import { Time } from "@foxglove/rostime";
type RepeatAdapterProps = {
    repeatEnabled: boolean;
    play: () => void;
    seek: (to: Time) => void;
};
/**
 * RepeatAdapter handled looping from the start of playback when playback reaches the end
 *
 * NOTE: Because repeat adapter receives every message pipeline frame, we isolate its logic inside
 * a separate component so it does not cause virtual DOM diffing on any children.
 */
export declare function RepeatAdapter(props: RepeatAdapterProps): JSX.Element;
export {};
