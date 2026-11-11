/// <reference types="react" />
import { ValidationResult } from "@foxglove/studio-base/util/validators";
type Value = unknown;
type OnChange = (obj: unknown) => void;
type BaseProps = {
    dataTestId?: string;
    dataValidator?: (data: unknown) => ValidationResult | undefined;
    onChange?: OnChange;
    onError?: (err: string) => void;
    readOnly?: boolean;
    maxHeight?: number | "auto" | "none";
    value: Value;
};
export default function JsonInput(props: BaseProps): JSX.Element;
export {};
