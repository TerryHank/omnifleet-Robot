/// <reference types="react" />
import { AppBarProps } from "@foxglove/studio-base/components/AppBar";
import { CustomWindowControlsProps } from "@foxglove/studio-base/components/AppBar/CustomWindowControls";
import { IAppConfiguration } from "@foxglove/studio-base/context/AppConfigurationContext";
import { IDataSourceFactory } from "@foxglove/studio-base/context/PlayerSelectionContext";
interface ISharedRootContext {
    deepLinks: readonly string[];
    appConfiguration?: IAppConfiguration;
    dataSources: readonly IDataSourceFactory[];
    enableLaunchPreferenceScreen?: boolean;
    enableGlobalCss?: boolean;
    appBarLeftInset?: number;
    extraProviders?: readonly JSX.Element[];
    customWindowControlProps?: CustomWindowControlsProps;
    onAppBarDoubleClick?: () => void;
    AppBarComponent?: (props: AppBarProps) => JSX.Element;
}
declare const SharedRootContext: import("react").Context<ISharedRootContext>;
export declare function useSharedRootContext(): ISharedRootContext;
export { SharedRootContext };
export type { ISharedRootContext };
