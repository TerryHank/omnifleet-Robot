/// <reference types="react" />
import { StoreApi } from "zustand";
import IAnalytics from "@foxglove/studio-base/services/IAnalytics";
export type ForwardedAnalytics = StoreApi<{
    value: IAnalytics;
}>;
/**
 * Returns a store for forwarding the given context's value, which can be passed to
 * `ForwardAnalyticsContextProvider`.
 */
export declare function useForwardAnalytics(): ForwardedAnalytics;
/**
 * Forwards React context values for analytics between separate React trees. This is used for
 * exposing the Studio internal analytics context to internal extension panels, which are in their
 * own React trees and otherwise can't access context values from the rest of Studio.
 *
 * This component should be rendered in the destination tree, with the `forwardedAnalytics` prop
 * constructed from the `useForwardAnalytics()` hook rendered in the source tree.
 */
export declare function ForwardAnalyticsContextProvider({ 
/** Context to forward. Should be the return value from useForwardAnalytics in the outer tree. */
forwardedAnalytics, children, }: React.PropsWithChildren<{
    forwardedAnalytics: ForwardedAnalytics;
}>): JSX.Element;
