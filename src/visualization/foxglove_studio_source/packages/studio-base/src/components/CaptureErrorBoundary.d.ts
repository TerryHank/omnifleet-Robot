import { Component, PropsWithChildren, ReactNode } from "react";
type Props = {
    onError: (err: Error) => void;
};
type State = {
    hadError: boolean;
};
/** An error boundary that calls an onError function when it captures an error */
export declare class CaptureErrorBoundary extends Component<PropsWithChildren<Props>, State> {
    state: State;
    componentDidCatch(error: Error): void;
    render(): ReactNode;
}
export {};
