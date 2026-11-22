type HtmlTemplate = unknown;
type DevtoolFormatterConfig = {
    key: unknown;
};
interface DevtoolFormatter {
    header: (object: Record<string, unknown>, config: DevtoolFormatterConfig) => HtmlTemplate;
    hasBody: (object: unknown) => boolean;
    body?: (object: Record<string, unknown>) => HtmlTemplate;
}
declare global {
    interface Window {
        devtoolsFormatters: DevtoolFormatter[];
    }
}
export default function installDevtoolsFormatters(): void;
export {};
