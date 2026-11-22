import { ReactNode } from "react";
import { DiffObject } from "@foxglove/studio-base/panels/RawMessages/getDiff";
export default function DiffStats({ data, itemType, }: {
    data: DiffObject;
    itemType: ReactNode;
}): JSX.Element;
