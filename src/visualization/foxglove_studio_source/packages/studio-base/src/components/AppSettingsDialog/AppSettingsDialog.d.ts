/// <reference types="react" />
import { DialogProps } from "@mui/material";
export type AppSettingsTab = "general" | "extensions" | "experimental-features" | "about";
export declare function AppSettingsDialog(props: DialogProps & {
    activeTab?: AppSettingsTab;
}): JSX.Element;
