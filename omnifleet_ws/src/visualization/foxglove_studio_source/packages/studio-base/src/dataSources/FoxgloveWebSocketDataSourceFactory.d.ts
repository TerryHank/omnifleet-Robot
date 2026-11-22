import { IDataSourceFactory, DataSourceFactoryInitializeArgs } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { Player } from "@foxglove/studio-base/players/types";
export default class FoxgloveWebSocketDataSourceFactory implements IDataSourceFactory {
    id: string;
    type: IDataSourceFactory["type"];
    displayName: string;
    iconName: IDataSourceFactory["iconName"];
    description: string;
    docsLinks: {
        label: string;
        url: string;
    }[];
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
