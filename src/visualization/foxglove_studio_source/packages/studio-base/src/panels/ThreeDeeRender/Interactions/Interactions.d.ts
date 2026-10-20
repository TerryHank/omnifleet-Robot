/// <reference types="react" />
import type { LayoutActions } from "@foxglove/studio";
import { InteractionData } from "./types";
import { Pose } from "../transforms";
export declare const OBJECT_TAB_TYPE = "Selected object";
export type TabType = typeof OBJECT_TAB_TYPE;
export type SelectionObject = {
    object: {
        pose: Pose;
        interactionData?: InteractionData;
    };
    instanceIndex: number | undefined;
};
type Props = {
    addPanel: LayoutActions["addPanel"];
    interactionsTabType?: TabType;
    onShowTopicSettings?: (topic: string) => void;
    selectedObject?: SelectionObject;
    setInteractionsTabType: (arg0?: TabType) => void;
    timezone: string | undefined;
};
export default function Interactions(props: Props): JSX.Element;
export {};
