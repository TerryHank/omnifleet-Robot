/// <reference types="react" />
import { AppBarProps } from "@foxglove/studio-base/components/AppBar";
import { CustomWindowControlsProps } from "@foxglove/studio-base/components/AppBar/CustomWindowControls";
type WorkspaceProps = CustomWindowControlsProps & {
    deepLinks?: readonly string[];
    appBarLeftInset?: number;
    onAppBarDoubleClick?: () => void;
    disablePersistenceForStorybook?: boolean;
    AppBarComponent?: (props: AppBarProps) => JSX.Element;
};
export default function Workspace(props: WorkspaceProps): JSX.Element;
export {};
