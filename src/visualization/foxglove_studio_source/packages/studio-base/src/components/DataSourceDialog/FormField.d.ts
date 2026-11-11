/// <reference types="react" />
import { Field } from "@foxglove/studio-base/context/PlayerSelectionContext";
type Props = {
    disabled: boolean;
    field: Field;
    onChange: (newValue: string | undefined) => void;
    onError: (message: string) => void;
};
export declare function FormField(props: Props): JSX.Element;
export {};
