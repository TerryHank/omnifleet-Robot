import { PropsWithChildren } from "react";
import { IDataSourceFactory } from "@foxglove/studio-base/context/PlayerSelectionContext";
type PlayerManagerProps = {
    playerSources: readonly IDataSourceFactory[];
};
export default function PlayerManager(props: PropsWithChildren<PlayerManagerProps>): JSX.Element;
export {};
