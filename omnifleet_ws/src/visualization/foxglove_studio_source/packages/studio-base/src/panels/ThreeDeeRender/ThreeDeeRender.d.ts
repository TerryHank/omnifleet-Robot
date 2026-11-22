/// <reference types="react" />
import { DeepPartial } from "ts-essentials";
import { BuiltinPanelExtensionContext } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { SceneExtensionConfig } from "@foxglove/studio-base/panels/ThreeDeeRender/SceneExtensionConfig";
import type { TestOptions } from "./IRenderer";
import { InterfaceMode } from "./types";
/**
 * A panel that renders a 3D scene. This is a thin wrapper around a `Renderer` instance.
 */
export declare function ThreeDeeRender(props: {
    context: BuiltinPanelExtensionContext;
    interfaceMode: InterfaceMode;
    testOptions: TestOptions;
    /** Allow for injection or overriding of default extensions by custom extensions */
    customSceneExtensions?: DeepPartial<SceneExtensionConfig>;
}): JSX.Element;
