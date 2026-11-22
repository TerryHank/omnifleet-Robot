type ReportErrorHandler = (error: Error) => void;
/**
 * Report an error that has escaped past normal error-handling flows in the app and should be
 * triaged and diagnosed.
 */
export declare function reportError(error: Error): void;
/**
 * Set the handler function which will be called when an error is passed to `reportError()`. The default is
 * a no-op.
 */
export declare function setReportErrorHandler(fn: ReportErrorHandler): void;
export {};
