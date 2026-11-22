/// <reference types="react" />
import { MessageEvent } from "@foxglove/studio-base/players/types";
type Props = {
    data: unknown;
    diffData: unknown;
    diff: unknown;
    datatype?: string;
    message: MessageEvent;
    diffMessage?: MessageEvent;
};
export default function Metadata({ data, diffData, diff, datatype, message, diffMessage, }: Props): JSX.Element;
export {};
