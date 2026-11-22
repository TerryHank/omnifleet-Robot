import { TextFieldProps } from "@mui/material";
import { StoryObj } from "@storybook/react";
type Story = StoryObj<TextFieldProps>;
declare const _default: import("@storybook/types").ComponentAnnotations<import("@storybook/react/dist/types-0fc72a6d").R, {
    variant?: import("@mui/material").TextFieldVariants | undefined;
} & Omit<import("@mui/material").FilledTextFieldProps | import("@mui/material").OutlinedTextFieldProps | import("@mui/material").StandardTextFieldProps, "variant">>;
export default _default;
export declare const DefaultLight: Story;
export declare const DefaultDark: Story;
export declare const ErrorLight: Story;
export declare const ErrorDark: Story;
