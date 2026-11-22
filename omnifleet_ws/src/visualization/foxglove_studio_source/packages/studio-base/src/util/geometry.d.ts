export type Point = {
    x: number;
    y: number;
    z: number;
};
export type Quaternion = {
    x: number;
    y: number;
    z: number;
    w: number;
};
export type Vector3 = {
    x: number;
    y: number;
    z: number;
};
export declare function eulerToQuaternion(rpy: Vector3): Quaternion;
export declare function makeCovarianceArray(xDev: number, yDev: number, thetaDev: number): number[];
