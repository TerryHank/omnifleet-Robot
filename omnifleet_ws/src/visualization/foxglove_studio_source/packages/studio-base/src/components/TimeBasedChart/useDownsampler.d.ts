import type { ObjectData, RpcScales } from "@foxglove/studio-base/components/Chart/types";
import { PlotDataProvider, ChartDataset } from "./types";
/**
 * useDownsampler downsamples the given datasets before providing them to the
 * TimeBasedChart. This is used primarily for downsampling data passed into the
 * TimeBasedChart component without using a PlotDataProvider.
 */
export default function useDownsampler(datasets: ChartDataset[]): {
    downsampler: PlotDataProvider<ObjectData>;
    setScales: (scales: RpcScales) => void;
};
