/// <reference types="react" />
import type { LayoutActions } from "@foxglove/studio";
type Props = {
    topic: string;
    addPanel: LayoutActions["addPanel"];
    onShowTopicSettings?: (topic: string) => void;
};
export default function TopicLink({ addPanel, onShowTopicSettings, topic }: Props): JSX.Element;
export {};
