export interface NetworkInterface {
    name: string;
    family: "IPv4" | "IPv6";
    internal: boolean;
    address: string;
    cidr?: string;
    mac: string;
    netmask: string;
}
/** OsContext is exposed over the electron Context Bridge */
export interface OsContext {
    platform: string;
    pid: number;
    getEnvVar: (envVar: string) => string | undefined;
    getHostname: () => string;
    getNetworkInterfaces: () => NetworkInterface[];
    getAppVersion: () => string;
}
