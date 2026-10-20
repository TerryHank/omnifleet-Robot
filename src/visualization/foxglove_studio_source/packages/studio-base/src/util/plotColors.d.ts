export declare const lineColors: string[];
export declare const expandedLineColors: string[];
export declare const lightColor: (_: string) => string;
export declare const darkColor: (_: string) => string;
export declare function getLineColor(color: string | undefined, index: number): string;
export declare function getContrastColor(colorScheme: "light" | "dark", color: string): string;
