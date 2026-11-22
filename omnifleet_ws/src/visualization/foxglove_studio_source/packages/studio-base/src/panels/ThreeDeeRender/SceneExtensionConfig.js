// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Cameras } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Cameras";
import { FoxgloveGrid } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/FoxgloveGrid";
import { FrameAxes } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/FrameAxes";
import { Grids } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Grids";
import { ImageMode } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/ImageMode/ImageMode";
import { Images } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Images";
import { LaserScans } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/LaserScans";
import { Markers } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Markers";
import { OccupancyGrids } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/OccupancyGrids";
import { PointClouds } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/PointClouds";
import { Polygons } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Polygons";
import { PoseArrays } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/PoseArrays";
import { Poses } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Poses";
import { PublishSettings } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/PublishSettings";
import { FoxgloveSceneEntities } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/SceneEntities";
import { SceneSettings } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/SceneSettings";
import { Urdfs } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/Urdfs";
import { VelodyneScans } from "@foxglove/studio-base/panels/ThreeDeeRender/renderables/VelodyneScans";
import { MeasurementTool } from "./renderables/MeasurementTool";
import { PublishClickTool } from "./renderables/PublishClickTool";
export const DEFAULT_SCENE_EXTENSION_CONFIG = {
    reserved: {
        imageMode: {
            init: (renderer) => new ImageMode(renderer),
        },
        measurementTool: {
            init: (renderer) => new MeasurementTool(renderer),
        },
        publishClickTool: {
            init: (renderer) => new PublishClickTool(renderer),
        },
    },
    extensionsById: {
        [PublishSettings.extensionId]: {
            init: (renderer) => new PublishSettings(renderer),
            supportedInterfaceModes: ["3d"],
        },
        [Images.extensionId]: {
            init: (renderer) => new Images(renderer),
            supportedInterfaceModes: ["3d"],
        },
        [Cameras.extensionId]: {
            init: (renderer) => new Cameras(renderer),
            supportedInterfaceModes: ["3d"],
        },
        [SceneSettings.extensionId]: {
            init: (renderer) => new SceneSettings(renderer),
        },
        [FrameAxes.extensionId]: {
            init: (renderer) => 
            // only show frame axes and labels by default when in 3d mode
            new FrameAxes(renderer, { visible: renderer.interfaceMode === "3d" }),
        },
        [Grids.extensionId]: {
            init: (renderer) => new Grids(renderer),
        },
        [Markers.extensionId]: {
            init: (renderer) => new Markers(renderer),
        },
        [FoxgloveSceneEntities.extensionId]: {
            init: (renderer) => new FoxgloveSceneEntities(renderer),
        },
        [FoxgloveGrid.extensionId]: {
            init: (renderer) => new FoxgloveGrid(renderer),
        },
        [LaserScans.extensionId]: {
            init: (renderer) => new LaserScans(renderer),
        },
        [OccupancyGrids.extensionId]: {
            init: (renderer) => new OccupancyGrids(renderer),
        },
        [PointClouds.extensionId]: {
            init: (renderer) => new PointClouds(renderer),
        },
        [Polygons.extensionId]: {
            init: (renderer) => new Polygons(renderer),
        },
        [Poses.extensionId]: {
            init: (renderer) => new Poses(renderer),
        },
        [PoseArrays.extensionId]: {
            init: (renderer) => new PoseArrays(renderer),
        },
        [Urdfs.extensionId]: {
            init: (renderer) => new Urdfs(renderer),
        },
        [VelodyneScans.extensionId]: {
            init: (renderer) => new VelodyneScans(renderer),
        },
    },
};
