import { PlayerMetricsCollectorInterface } from "@foxglove/studio-base/players/types";
import IAnalytics, { AppEvent } from "@foxglove/studio-base/services/IAnalytics";
type EventData = {
    [key: string]: string | number | boolean;
};
export default class AnalyticsMetricsCollector implements PlayerMetricsCollectorInterface {
    #private;
    constructor(analytics: IAnalytics);
    setProperty(key: string, value: string | number | boolean): void;
    logEvent(event: AppEvent, data?: EventData): void;
    playerConstructed(): void;
}
export {};
