/// <reference types="react" />
export declare enum DirectionalPadAction {
    UP = 0,
    DOWN = 1,
    LEFT = 2,
    RIGHT = 3
}
type DirectionalPadProps = {
    disabled?: boolean;
    emergencyStopped?: boolean;
    onAction?: (action?: DirectionalPadAction) => void;
    onEmergencyStop?: () => void;
};
declare function DirectionalPad(props: DirectionalPadProps): JSX.Element;
export default DirectionalPad;
