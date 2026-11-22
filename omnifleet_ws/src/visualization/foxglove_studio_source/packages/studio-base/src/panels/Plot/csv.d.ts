import { Immutable } from "@foxglove/studio";
import { CsvDataset } from "./builders/IDatasetsBuilder";
import { PlotXAxisVal } from "./config";
declare function generateCSV(datasets: Immutable<CsvDataset[]>, xAxisVal: PlotXAxisVal): string;
declare function downloadCSV(filename: string, datasets: Immutable<CsvDataset[]>, xAxisVal: PlotXAxisVal): void;
export { downloadCSV, generateCSV };
