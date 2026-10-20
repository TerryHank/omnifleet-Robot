type SliderProps = {
    min: number;
    max: number;
    step: number;
};
export type VariableSliderConfig = {
    sliderProps: Partial<SliderProps>;
    globalVariableName: string;
};
export {};
