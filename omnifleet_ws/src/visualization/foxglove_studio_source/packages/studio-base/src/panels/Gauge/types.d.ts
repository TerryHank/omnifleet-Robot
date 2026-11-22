export type Config = {
    path: string;
    minValue: number;
    maxValue: number;
    colorMode: "colormap" | "gradient";
    colorMap: "red-yellow-green" | "rainbow" | "turbo";
    gradient: [string, string];
    reverse: boolean;
};
