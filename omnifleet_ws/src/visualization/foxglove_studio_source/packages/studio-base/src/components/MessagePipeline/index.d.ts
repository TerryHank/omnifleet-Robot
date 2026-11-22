/// <reference types="react" />
import { StoreApi } from "zustand";
import { Player } from "@foxglove/studio-base/players/types";
import { MessagePipelineInternalState } from "./store";
import { MessagePipelineContext } from "./types";
export type { MessagePipelineContext };
export declare const ContextInternal: import("react").Context<StoreApi<MessagePipelineInternalState> | undefined>;
/**
 * useMessagePipelineGetter returns a function to access the current message pipeline context.
 * Commonly used in places where you want to access a value from the latest pipeline in a useCallback hook
 * but don't want the callback dependencies invalidated on ever change.
 *
 * @returns a function to return the current MessagePipelineContext
 */
export declare function useMessagePipelineGetter(): () => MessagePipelineContext;
export declare function useMessagePipeline<T>(selector: (arg0: MessagePipelineContext) => T): T;
export declare function useMessagePipelineSubscribe(): (fn: (state: MessagePipelineContext) => void) => () => void;
type ProviderProps = {
    children: React.ReactNode;
    player?: Player;
};
export declare function MessagePipelineProvider({ children, player }: ProviderProps): React.ReactElement;
