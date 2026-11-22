import { PaletteOptions } from "@mui/material/styles";
import { CSSProperties } from "react";
declare module "@mui/material/styles" {
    interface Palette {
        name: string;
        appBar: {
            main: CSSProperties["color"];
            primary: CSSProperties["color"];
            text: CSSProperties["color"];
        };
    }
    interface PaletteOptions {
        name: string;
        appBar: {
            main: CSSProperties["color"];
            primary: CSSProperties["color"];
            text: CSSProperties["color"];
        };
    }
    interface TypeBackground {
        menu: CSSProperties["color"];
    }
}
export declare const dark: PaletteOptions;
export declare const light: PaletteOptions;
