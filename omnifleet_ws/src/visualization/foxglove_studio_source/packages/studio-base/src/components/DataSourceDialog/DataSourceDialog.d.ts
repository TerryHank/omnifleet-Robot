/// <reference types="react" />
declare const DataSourceDialogItems: readonly ["start", "file", "demo", "remote", "connection"];
export type DataSourceDialogItem = (typeof DataSourceDialogItems)[number];
type DataSourceDialogProps = {
    backdropAnimation?: boolean;
};
export declare function DataSourceDialog(props: DataSourceDialogProps): JSX.Element;
export {};
