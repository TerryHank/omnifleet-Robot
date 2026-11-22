import type {MessageEvent} from "@foxglove/studio";
import type {BuiltinPanelExtensionContext} from "@foxglove/studio-base/components/PanelExtensionAdapter";
import type {IRenderer} from "./IRenderer";
declare global {
  interface Window {
    OmniFleetWaypointDrag: {
      attach(renderer: IRenderer, context: BuiltinPanelExtensionContext): () => void;
      update(renderer: IRenderer, context: BuiltinPanelExtensionContext, messages: readonly MessageEvent[] | undefined): void;
    };
  }
}
export {};
