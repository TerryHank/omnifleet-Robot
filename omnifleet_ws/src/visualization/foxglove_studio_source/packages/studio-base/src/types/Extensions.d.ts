export type ExtensionNamespace = "local" | "org";
/**
 * Metadata describing an extension.
 */
export type ExtensionInfo = {
    id: string;
    description: string;
    displayName: string;
    homepage: string;
    keywords: string[];
    license: string;
    name: string;
    namespace?: ExtensionNamespace;
    publisher: string;
    qualifiedName: string;
    version: string;
};
