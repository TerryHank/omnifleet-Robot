import { Row } from "@tanstack/react-table";
import { PropsWithChildren } from "react";
import { CellValue } from "@foxglove/studio-base/panels/Table/types";
type TableCellProps = {
    row: Row<CellValue>;
    accessorPath: string;
};
export default function TableCell({ row, accessorPath, children, }: PropsWithChildren<TableCellProps>): JSX.Element;
export {};
