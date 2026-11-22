import { TypographyOptions } from "@mui/material/styles/createTypography";
declare module "@mui/material/styles/createTypography" {
    interface Typography {
        fontMonospace: string;
        fontSansSerif: string;
        fontFeatureSettings: string;
    }
    interface TypographyOptions {
        fontMonospace: string;
        fontSansSerif: string;
        fontFeatureSettings: string;
    }
}
export declare const fontSansSerif = "'Inter'";
export declare const fontMonospace = "'IBM Plex Mono'";
export declare const fontFeatureSettings: string;
export declare const typography: TypographyOptions;
