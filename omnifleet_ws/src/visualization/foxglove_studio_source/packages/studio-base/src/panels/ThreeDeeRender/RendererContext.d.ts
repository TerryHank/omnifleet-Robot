/// <reference types="react" />
import EventEmitter from "eventemitter3";
import type { IRenderer, RendererEvents } from "./IRenderer";
export declare const RendererContext: import("react").Context<IRenderer | undefined>;
/**
 * React hook to retrieve the Renderer instance registered with the
 * RendererContext. This will always return undefined from the ThreeDeeRender()
 * component since the context exists below ThreeDeeRender().
 */
export declare function useRenderer(): IRenderer | undefined;
/**
 * React hook that subscribes to Renderer events. The optional
 * `rendererInstance` argument must be passed when calling from the
 * ThreeDeeRender() component which is above the RendererContext.
 * @param eventName Event name to subscribe to
 * @param listener Event callback
 * @param rendererInstance Optional Renderer instance to subscribe to instead of
 *   the reference returned by useRenderer()
 */
export declare function useRendererEvent<K extends keyof RendererEvents>(eventName: K, listener: (...args: EventEmitter.ArgumentMap<RendererEvents>[Extract<K, keyof RendererEvents>]) => void, rendererInstance?: IRenderer | ReactNull): void;
/**
 * Returns a property from the Renderer instance. Updates when the event is called
 *
 * @param key - Property key to subscribe to
 * @param event - Event name that should trigger a re-render to read the property again
 * @param fallback - Fallback value to use if the property is not available or undefined
 * @param rendererInstance - Optional Renderer instance to subscribe to instead of the reference returned by useRenderer()
 * @returns - value of renderer property or fallback if undefined
 */
export declare function useRendererProperty<K extends keyof IRenderer>(key: K, event: keyof RendererEvents, fallback: () => IRenderer[K], rendererInstance?: IRenderer | undefined): IRenderer[K];
