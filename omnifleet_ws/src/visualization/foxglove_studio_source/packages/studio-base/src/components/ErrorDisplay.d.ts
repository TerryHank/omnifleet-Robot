import { ErrorInfo } from "react";
type ErrorDisplayProps = {
    title?: string;
    error?: Error;
    errorInfo?: ErrorInfo;
    content?: JSX.Element;
    actions?: JSX.Element;
    showErrorDetails?: boolean;
    hideErrorSourceLocations?: boolean;
};
declare function ErrorDisplay(props: ErrorDisplayProps): JSX.Element;
export default ErrorDisplay;
