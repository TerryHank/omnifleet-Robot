/// <reference types="jest" />
import type { DetailsType, NotificationHandler, NotificationSeverity, NotificationType } from "@foxglove/studio-base/util/sendNotification";
declare const mockSendNotification: jest.Mock<void, [string, DetailsType, NotificationType, NotificationSeverity], any>;
declare const mockSetNotificationHandler: (handler?: NotificationHandler) => void;
declare function setupMockSendNotification(): void;
export { mockSendNotification, mockSetNotificationHandler, setupMockSendNotification };
