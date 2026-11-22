import { IDataSourceFactory, DataSourceFactoryInitializeArgs } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { Player } from "@foxglove/studio-base/players/types";
declare class Ros1LocalBagDataSourceFactory implements IDataSourceFactory {
    id: string;
    type: IDataSourceFactory["type"];
    displayName: string;
    iconName: IDataSourceFactory["iconName"];
    supportedFileTypes: string[];
    initialize(args: DataSourceFactoryInitializeArgs): Player | undefined;
}
export default Ros1LocalBagDataSourceFactory;
