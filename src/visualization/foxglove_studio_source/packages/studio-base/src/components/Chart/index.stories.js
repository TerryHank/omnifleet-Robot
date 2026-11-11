import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import * as _ from "lodash-es";
import { useState, useCallback, useEffect } from "react";
import TestUtils from "react-dom/test-utils";
import { useReadySignal } from "@foxglove/studio-base/stories/ReadySignalContext";
import ChartComponent from ".";
const dataPoint = {
    x: 0.000057603000000000004,
    y: 5.544444561004639,
    selectionObj: 1,
    label: "datalabel with selection id 1",
    value: 5.544444561004639,
};
const props = {
    width: 500,
    height: 700,
    isBoundsReset: false,
    data: {
        datasets: [
            {
                borderColor: "#4e98e2",
                label: "/turtle1/pose.x",
                showLine: true,
                borderWidth: 1,
                pointRadius: 1.5,
                pointHoverRadius: 3,
                pointBackgroundColor: "#74beff",
                pointBorderColor: "transparent",
                data: [dataPoint],
                datalabels: { display: false },
            },
        ],
    },
    options: {
        animation: { duration: 0 },
        elements: { line: { tension: 0 } },
        plugins: {
            legend: { display: false },
            annotation: { annotations: [] },
            datalabels: {
                anchor: "start",
                align: 0,
                offset: 5,
                color: "white",
            },
            zoom: {
                zoom: {
                    enabled: true,
                    mode: "xy",
                    sensitivity: 3,
                    speed: 0.1,
                },
                pan: {
                    enabled: true,
                },
            },
        },
        scales: {
            y: {
                ticks: {
                    font: {
                        family: `"IBM Plex Mono"`,
                        size: 10,
                    },
                    color: "#eee",
                    padding: 0,
                    precision: 3,
                },
                grid: {
                    color: "rgba(255, 255, 255, 0.2)",
                },
            },
            x: {
                ticks: {
                    font: {
                        family: `"IBM Plex Mono"`,
                        size: 10,
                    },
                    color: "#eee",
                    maxRotation: 0,
                },
                grid: {
                    color: "rgba(255, 255, 255, 0.2)",
                },
            },
        },
    },
    type: "scatter",
};
const propsWithDatalabels = _.cloneDeep(props);
if (propsWithDatalabels.data.datasets[0]?.datalabels) {
    propsWithDatalabels.data.datasets[0].datalabels.display = true;
}
const divStyle = { width: 600, height: 800, background: "black" };
export default {
    title: "components/Chart",
    component: ChartComponent,
    parameters: {
        chromatic: {
            // additional delay for any final clicks or renders
            delay: 100,
        },
        colorScheme: "dark",
        disableI18n: true,
    },
};
export const Basic = {
    render: function Story() {
        const readySignal = useReadySignal();
        return (_jsx("div", { style: divStyle, children: _jsx(ChartComponent, { ...props, onFinishRender: readySignal }) }));
    },
    play: async (ctx) => {
        await ctx.parameters.storyReady;
    },
    parameters: {
        useReadySignal: true,
    },
};
export const WithDatalabels = {
    render: function Story() {
        const readySignal = useReadySignal();
        return (_jsx("div", { style: divStyle, children: _jsx(ChartComponent, { ...propsWithDatalabels, onFinishRender: readySignal }) }));
    },
    play: async (ctx) => {
        await ctx.parameters.storyReady;
    },
    parameters: {
        useReadySignal: true,
    },
};
export const AllowsClickingOnDatalabels = {
    render: function Story() {
        const [clickedDatalabel, setClickedDatalabel] = useState(undefined);
        const readySignal = useReadySignal();
        const doClick = useCallback(() => {
            if (clickedDatalabel == undefined) {
                const [canvas] = document.getElementsByTagName("canvas");
                TestUtils.Simulate.click(canvas.parentElement, { clientX: 304, clientY: 378 });
            }
        }, [clickedDatalabel]);
        const onClick = useCallback((ev) => {
            setClickedDatalabel(ev.datalabel);
        }, []);
        useEffect(() => {
            if (clickedDatalabel != undefined) {
                readySignal();
            }
        }, [clickedDatalabel, readySignal]);
        const debouncedOnFinish = React.useMemo(() => {
            return _.debounce(() => {
                doClick();
            }, 3000);
        }, [doClick]);
        return (_jsxs("div", { style: divStyle, children: [_jsx("div", { style: { padding: 6, fontSize: 16 }, children: clickedDatalabel != undefined
                        ? `Clicked datalabel with selection id: ${String(clickedDatalabel.selectionObj)}`
                        : "Have not clicked datalabel" }), _jsx(ChartComponent, { ...propsWithDatalabels, onFinishRender: debouncedOnFinish, onClick: onClick })] }));
    },
    play: async (ctx) => {
        await ctx.parameters.storyReady;
    },
    parameters: {
        useReadySignal: true,
    },
};
