export type FoxgloveMessages = {
    "foxglove.GeoJSON": {
        geojson: string;
    };
    "foxglove.Pose": {
        position: {
            x: number;
            y: number;
            z: number;
        };
        orientation: {
            x: number;
            y: number;
            z: number;
            w: number;
        };
    };
};
