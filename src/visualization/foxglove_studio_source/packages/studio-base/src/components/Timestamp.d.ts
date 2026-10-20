/// <reference types="react" />
import { Time } from "@foxglove/rostime";
type Props = {
    disableDate?: boolean;
    horizontal?: boolean;
    time: Time;
    title?: string;
};
export default function Timestamp(props: Props): JSX.Element;
export {};
