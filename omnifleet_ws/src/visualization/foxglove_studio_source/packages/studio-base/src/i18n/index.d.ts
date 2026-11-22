import * as en from "./en";
import * as ja from "./ja";
import * as zh from "./zh";
export declare const translations: {
    en: typeof en;
    zh: typeof zh;
    ja: typeof ja;
};
export type Language = keyof typeof translations;
export declare const defaultNS = "general";
export declare function initI18n(options?: {
    context?: "browser" | "electron-main";
}): Promise<void>;
