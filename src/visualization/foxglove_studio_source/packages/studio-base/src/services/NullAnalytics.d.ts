import IAnalytics from "@foxglove/studio-base/services/IAnalytics";
export default class NullAnalytics implements IAnalytics {
    logEvent(): void | Promise<void>;
}
