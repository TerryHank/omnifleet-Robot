type Draw = (context: CanvasRenderingContext2D, width: number, height: number) => void;
type AutoSizingCanvasProps = {
    draw: Draw;
    overrideDevicePixelRatioForTest?: number;
};
declare const AutoSizingCanvas: ({ draw, overrideDevicePixelRatioForTest, }: AutoSizingCanvasProps) => JSX.Element;
export default AutoSizingCanvas;
