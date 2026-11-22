import { ReactNode } from "react";
export type NotificationType = "app" | "user";
export type DetailsType = string | Error | ReactNode;
export type NotificationSeverity = "error" | "warn" | "info";
export type NotificationHandler = (message: string, details: DetailsType, type: NotificationType, severity: NotificationSeverity) => void;
export type NotificationMessage = {
    readonly id?: string;
    readonly message: string;
    readonly details: DetailsType;
    readonly subText?: string;
    readonly created?: Date;
    readonly severity: NotificationSeverity;
};
export declare function setNotificationHandler(handler: NotificationHandler): void;
export declare function unsetNotificationHandler(): void;
declare function sendNotification(message: string, details: DetailsType, type: NotificationType, severity: NotificationSeverity): void;
declare namespace sendNotification {
    var expectCalledDuringTest: () => void;
}
export default sendNotification;
