import { DetailsType } from "@foxglove/studio-base/util/sendNotification";
export declare class AppError extends Error {
    details: DetailsType;
    extraInfo: unknown;
    message: string;
    constructor(details: DetailsType, extraInfo?: unknown);
}
