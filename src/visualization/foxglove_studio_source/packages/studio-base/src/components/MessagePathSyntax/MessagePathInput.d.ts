import { TextFieldProps } from "@mui/material";
import { CSSProperties } from "react";
import { MessagePath } from "@foxglove/message-path";
import { GlobalVariables } from "@foxglove/studio-base/hooks/useGlobalVariables";
export declare function tryToSetDefaultGlobalVar(variableName: string, setGlobalVariables: (arg0: GlobalVariables) => void): boolean;
export declare function getFirstInvalidVariableFromRosPath(rosPath: MessagePath, globalVariables: GlobalVariables, setGlobalVariables: (arg0: GlobalVariables) => void): {
    variableName: string;
    loc: number;
} | undefined;
type MessagePathInputBaseProps = {
    supportsMathModifiers?: boolean;
    path: string;
    index?: number;
    onChange: (value: string, index?: number) => void;
    validTypes?: readonly string[];
    noMultiSlices?: boolean;
    placeholder?: string;
    inputStyle?: CSSProperties;
    disabled?: boolean;
    disableAutocomplete?: boolean;
    readOnly?: boolean;
    prioritizedDatatype?: string;
    variant?: TextFieldProps["variant"];
};
/**
 * To show an input field with an autocomplete so the user can enter message paths, use:
 *
 *  <MessagePathInput path={this.state.path} onChange={path => this.setState({ path })} />
 *
 * To limit the autocomplete items to only certain types of values, you can use
 *
 *  <MessagePathInput types={["message", "array", "primitives"]} />
 *
 * Or use actual ROS primitive types:
 *
 *  <MessagePathInput types={["uint16", "float64"]} />
 *
 * If you are rendering many input fields, you might want to use `<MessagePathInput index={5}>`,
 * which gets passed down to `<MessagePathInput onChange>` as the second parameter, so you can
 * avoid creating anonymous functions on every render (which will prevent the component from
 * rendering unnecessarily).
 */
declare const _default: import("react").NamedExoticComponent<MessagePathInputBaseProps>;
export default _default;
