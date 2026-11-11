import { Component, ErrorInfo, PropsWithChildren, ReactNode } from "react";
type Props = {
    actions?: JSX.Element;
    showErrorDetails?: boolean;
    hideErrorSourceLocations?: boolean;
};
type State = {
    currentError: {
        error: Error;
        errorInfo: ErrorInfo;
    } | undefined;
};
export default class ErrorBoundary extends Component<PropsWithChildren<Props>, State> {
    state: State;
    componentDidCatch(error: Error, errorInfo: ErrorInfo): void;
    render(): ReactNode;
}
export {};
