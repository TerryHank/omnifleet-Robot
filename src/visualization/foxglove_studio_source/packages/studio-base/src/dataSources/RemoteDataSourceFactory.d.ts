import { IDataSourceFactory, DataSourceFactoryInitializeArgs } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { Player } from "@foxglove/studio-base/players/types";
declare class RemoteDataSourceFactory implements IDataSourceFactory {
    #private;
    id: string;
    legacyIds: string[];
    type: IDataSourceFactory["type"];
    displayName: string;
    iconName: IDataSourceFactory["iconName"];
    supportedFileTypes: string[];
    description: string;
    docsLinks: {
        label: string;
        url: string;
    }[];
    formConfig: {
        fields: {
            id: string;
            label: string;
            placeholder: string;
            validate: (newValue: string) => Error | undefined;
        }[];
    };
    warning: import("react/jsx-runtime").JSX.Element;
    initialize(args: DataSourceFactoryInitializeArgs): Player | undefined;
}
export default RemoteDataSourceFactory;
