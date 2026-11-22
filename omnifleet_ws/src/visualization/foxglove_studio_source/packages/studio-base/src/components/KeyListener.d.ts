import { ReactElement } from "react";
type KeyHandlers = Record<string, (event: KeyboardEvent) => void | boolean | undefined>;
type Props = {
    global?: boolean;
    keyDownHandlers?: KeyHandlers;
    keyPressHandlers?: KeyHandlers;
    keyUpHandlers?: KeyHandlers;
};
export default function KeyListener(props: Props): ReactElement;
export {};
