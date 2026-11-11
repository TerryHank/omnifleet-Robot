/// <reference types="react" />
import { StoreApi } from "zustand";
import { ExtensionPanelRegistration, Immutable, RegisterMessageConverterArgs } from "@foxglove/studio";
import { TopicAliasFunctions } from "@foxglove/studio-base/players/TopicAliasingPlayer/TopicAliasingPlayer";
import { ExtensionInfo, ExtensionNamespace } from "@foxglove/studio-base/types/Extensions";
export type RegisteredPanel = {
    extensionName: string;
    extensionNamespace?: ExtensionNamespace;
    registration: ExtensionPanelRegistration;
};
export type ExtensionCatalog = Immutable<{
    installExtension: (namespace: ExtensionNamespace, foxeFileData: Uint8Array) => Promise<ExtensionInfo>;
    installedExtensions: undefined | ExtensionInfo[];
    installedPanels: undefined | Record<string, RegisteredPanel>;
    installedMessageConverters: undefined | RegisterMessageConverterArgs<unknown>[];
    installedTopicAliasFunctions: undefined | TopicAliasFunctions;
}>;
export declare const ExtensionCatalogContext: import("react").Context<StoreApi<{
    readonly installExtension: (namespace: ExtensionNamespace, foxeFileData: Uint8Array) => Promise<ExtensionInfo>;
    readonly installedExtensions: readonly {
        readonly id: string;
        readonly description: string;
        readonly displayName: string;
        readonly homepage: string;
        readonly keywords: readonly string[];
        readonly license: string;
        readonly name: string;
        readonly namespace?: ExtensionNamespace | undefined;
        readonly publisher: string;
        readonly qualifiedName: string;
        readonly version: string;
    }[] | undefined;
    readonly installedPanels: {
        readonly [x: string]: {
            readonly extensionName: string;
            readonly extensionNamespace?: ExtensionNamespace | undefined;
            readonly registration: {
                readonly name: string;
                readonly initPanel: (context: import("@foxglove/studio").PanelExtensionContext) => void | (() => void);
            };
        };
    } | undefined;
    readonly installedMessageConverters: readonly {
        readonly fromSchemaName: string;
        readonly toSchemaName: string;
        readonly converter: (msg: unknown, event: {
            readonly topic: string;
            readonly schemaName: string;
            readonly receiveTime: {
                readonly sec: number;
                readonly nsec: number;
            };
            readonly publishTime?: {
                readonly sec: number;
                readonly nsec: number;
            } | undefined;
            readonly message: unknown;
            readonly sizeInBytes: number;
            readonly originalMessageEvent?: any | undefined;
        }) => unknown;
    }[] | undefined;
    readonly installedTopicAliasFunctions: readonly {
        readonly extensionId: string;
        readonly aliasFunction: import("@foxglove/studio").TopicAliasFunction;
    }[] | undefined;
}>>;
export declare function useExtensionCatalog<T>(selector: (registry: ExtensionCatalog) => T): T;
