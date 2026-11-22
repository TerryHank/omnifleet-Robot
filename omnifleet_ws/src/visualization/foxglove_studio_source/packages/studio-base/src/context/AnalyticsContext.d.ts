/// <reference types="react" />
import IAnalytics from "@foxglove/studio-base/services/IAnalytics";
declare const AnalyticsContext: import("react").Context<IAnalytics>;
export declare function useAnalytics(): IAnalytics;
export default AnalyticsContext;
