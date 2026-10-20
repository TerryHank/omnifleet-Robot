import { ReactNode } from "react";
import { PanelContextType } from "@foxglove/studio-base/components/PanelContext";
import { PanelConfig } from "@foxglove/studio-base/types/panels";
type MockProps = Partial<PanelContextType<PanelConfig>>;
declare function MockPanelContextProvider({ children, ...rest }: MockProps & {
    children: ReactNode;
}): JSX.Element;
export default MockPanelContextProvider;
