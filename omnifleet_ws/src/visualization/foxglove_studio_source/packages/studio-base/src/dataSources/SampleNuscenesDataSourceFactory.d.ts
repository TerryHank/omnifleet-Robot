import { IDataSourceFactory, DataSourceFactoryInitializeArgs } from "@foxglove/studio-base/context/PlayerSelectionContext";
declare class SampleNuscenesDataSourceFactory implements IDataSourceFactory {
    id: string;
    type: IDataSourceFactory["type"];
    displayName: string;
    iconName: IDataSourceFactory["iconName"];
    hidden: boolean;
    sampleLayout: import("../context/CurrentLayoutContext").LayoutData | undefined;
    initialize(args: DataSourceFactoryInitializeArgs): ReturnType<IDataSourceFactory["initialize"]>;
}
export default SampleNuscenesDataSourceFactory;
