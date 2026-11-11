/// <reference types="react" />
export type ShareJsonModalProps = {
    onRequestClose: () => void;
    onChange: (value: unknown) => void;
    initialValue: unknown;
    title: string;
};
export declare function ShareJsonModal({ initialValue, onChange, onRequestClose, title, }: ShareJsonModalProps): JSX.Element;
