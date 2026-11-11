import { IDataSourceFactory, DataSourceFactoryInitializeArgs } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { Player } from "@foxglove/studio-base/players/types";
declare class RosbridgeDataSourceFactory implements IDataSourceFactory {
    id: string;
    type: IDataSourceFactory["type"];
    displayName: string;
    iconName: IDataSourceFactory["iconName"];
    docsLinks: {
        url: string;
    }[];
    description: string;
    formConfig: {
        fields: {
            id: string;
            label: string;
            defaultValue: string;
            validate: (newValue: string) => Error | undefined;
        }[];
    };
    initialize(args: DataSourceFactoryInitializeArgs): Player | undefined;
}
export default RosbridgeDataSourceFactory;
