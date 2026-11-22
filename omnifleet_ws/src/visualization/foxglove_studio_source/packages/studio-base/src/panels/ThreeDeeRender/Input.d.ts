import EventEmitter from "eventemitter3";
import * as THREE from "three";
import { Key } from "ts-key-enum";
export type InputEvents = {
    resize: (windowSize: THREE.Vector2) => void;
    click: (cursorCoords: THREE.Vector2, worldSpaceCursorCoords: THREE.Vector3 | undefined, event: MouseEvent) => void;
    mousedown: (cursorCoords: THREE.Vector2, worldSpaceCursorCoords: THREE.Vector3 | undefined, event: MouseEvent) => void;
    mousemove: (cursorCoords: THREE.Vector2, worldSpaceCursorCoords: THREE.Vector3 | undefined, event: MouseEvent) => void;
    mouseup: (cursorCoords: THREE.Vector2, worldSpaceCursorCoords: THREE.Vector3 | undefined, event: MouseEvent) => void;
    wheel: (cursorCoords: THREE.Vector2, worldSpaceCursorCoords: THREE.Vector3 | undefined, event: WheelEvent) => void;
    keydown: (key: Key, event: KeyboardEvent) => void;
};
export declare class Input extends EventEmitter<InputEvents> {
    #private;
    private getCamera;
    /** Size in CSS pixels */
    canvasSize: THREE.Vector2;
    constructor(canvas: HTMLCanvasElement, getCamera: () => THREE.Camera);
    dispose(): void;
    /**
     * Call this from mousedown to activate event tracking for a drag. mousemove events will be
     * handled on the window and `onUpdate()` will be called until mouseup occurs.
     */
    trackDrag(onUpdate: (cursorCoords: THREE.Vector2) => void): void;
}
