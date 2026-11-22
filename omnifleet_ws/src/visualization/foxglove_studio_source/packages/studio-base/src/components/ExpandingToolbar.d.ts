import { ReactNode } from "react";
export declare function ToolGroup<T>({ children }: {
    name: T;
    children: React.ReactElement;
}): JSX.Element;
export declare function ToolGroupFixedSizePane({ children }: {
    children: ReactNode;
}): JSX.Element;
type Props<T extends string> = {
    checked?: boolean;
    children: React.ReactElement<typeof ToolGroup>[] | React.ReactElement<typeof ToolGroup>;
    icon: ReactNode;
    onSelectTab: (name: T | undefined) => void;
    selectedTab?: T;
    tooltip: string;
    dataTest?: string;
};
export default function ExpandingToolbar<T extends string>({ children, checked, icon, onSelectTab, selectedTab, tooltip, dataTest, }: Props<T>): JSX.Element;
export {};
