import { Component, ErrorInfo, PropsWithChildren, ReactNode } from "react";
type Props = {
    showErrorDetails?: boolean;
    hideErrorSourceLocations?: boolean;
    onResetPanel: () => void;
    onRemovePanel: () => void;
};
type State = {
    currentError: {
        error: Error;
        errorInfo: ErrorInfo;
    } | undefined;
};
export default class PanelErrorBoundary extends Component<PropsWithChildren<Props>, State> {
    state: State;
    componentDidCatch(error: Error, errorInfo: ErrorInfo): void;
    render(): ReactNode;
}
export {};
