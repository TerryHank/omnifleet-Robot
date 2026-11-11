/// <reference types="react" />
import { LayoutActions } from "@foxglove/studio";
import { PublishClickType } from "./renderables/PublishClickTool";
import { InterfaceMode } from "./types";
type Props = {
    addPanel: LayoutActions["addPanel"];
    canPublish: boolean;
    canvas: HTMLCanvasElement | ReactNull;
    enableStats: boolean;
    interfaceMode: InterfaceMode;
    measureActive: boolean;
    onChangePublishClickType: (_: PublishClickType) => void;
    onClickMeasure: () => void;
    onClickPublish: () => void;
    onShowTopicSettings: (topic: string) => void;
    onTogglePerspective: () => void;
    perspective: boolean;
    publishActive: boolean;
    publishClickType: PublishClickType;
    timezone: string | undefined;
};
/**
 * Provides DOM overlay elements on top of the 3D scene (e.g. stats, debug GUI).
 */
export declare function RendererOverlay(props: Props): JSX.Element;
export {};
