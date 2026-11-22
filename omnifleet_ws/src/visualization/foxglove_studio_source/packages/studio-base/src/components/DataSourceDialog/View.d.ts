import { PropsWithChildren } from "react";
type ViewProps = {
    onOpen?: () => void;
};
export default function View(props: PropsWithChildren<ViewProps>): JSX.Element;
export {};
