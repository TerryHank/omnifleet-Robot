// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

import assert from "assert";
import { useEffect } from "react";
import { useDebounce } from "use-debounce";

import Log from "@foxglove/log";
import { LOCAL_STORAGE_STUDIO_LAYOUT_KEY } from "@foxglove/studio-base/constants/localStorageKeys";
import {
  LayoutState,
  useCurrentLayoutActions,
  useCurrentLayoutSelector,
} from "@foxglove/studio-base/context/CurrentLayoutContext";
import { LayoutData } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
import { usePlayerSelection } from "@foxglove/studio-base/context/PlayerSelectionContext";
import { defaultLayout } from "@foxglove/studio-base/providers/CurrentLayoutProvider/defaultLayout";
import { migratePanelsState } from "@foxglove/studio-base/services/migrateLayout";

function selectLayoutData(state: LayoutState) {
  return state.selectedLayout?.data;
}

const log = Log.getLogger(__filename);
const RRC_CHASSIS_LAYOUT_VERSION_KEY = "studio.rrcChassisLayoutVersion";
const RRC_CHASSIS_LAYOUT_VERSION = "2";

export function CurrentLayoutLocalStorageSyncAdapter(): JSX.Element {
  const { selectedSource } = usePlayerSelection();

  const { setCurrentLayout } = useCurrentLayoutActions();
  const currentLayoutData = useCurrentLayoutSelector(selectLayoutData);

  useEffect(() => {
    if (selectedSource?.sampleLayout) {
      setCurrentLayout({ data: selectedSource.sampleLayout });
    }
  }, [selectedSource, setCurrentLayout]);

  const [debouncedLayoutData] = useDebounce(currentLayoutData, 250, { maxWait: 500 });

  useEffect(() => {
    if (!debouncedLayoutData) {
      return;
    }

    const serializedLayoutData = JSON.stringify(debouncedLayoutData);
    assert(serializedLayoutData);
    localStorage.setItem(LOCAL_STORAGE_STUDIO_LAYOUT_KEY, serializedLayoutData);
  }, [debouncedLayoutData]);

  useEffect(() => {
    log.debug(`Reading layout from local storage: ${LOCAL_STORAGE_STUDIO_LAYOUT_KEY}`);

    let serializedLayoutData = localStorage.getItem(LOCAL_STORAGE_STUDIO_LAYOUT_KEY);
    const installedChassisLayoutVersion = localStorage.getItem(RRC_CHASSIS_LAYOUT_VERSION_KEY);

    // Apply the robot-specific dashboard once when this desktop build is first
    // installed. Store the layout immediately so React StrictMode cannot restore
    // the previous layout during its second development mount. Subsequent user
    // edits remain untouched until this version is intentionally bumped.
    if (installedChassisLayoutVersion !== RRC_CHASSIS_LAYOUT_VERSION) {
      const serializedDefaultLayout = JSON.stringify(defaultLayout);
      assert(serializedDefaultLayout);
      serializedLayoutData = serializedDefaultLayout;
      localStorage.setItem(LOCAL_STORAGE_STUDIO_LAYOUT_KEY, serializedDefaultLayout);
      localStorage.setItem(RRC_CHASSIS_LAYOUT_VERSION_KEY, RRC_CHASSIS_LAYOUT_VERSION);
      log.info(`Installed RRC chassis dashboard version ${RRC_CHASSIS_LAYOUT_VERSION}`);
    }

    if (serializedLayoutData) {
      log.debug("Restoring layout from local storage");
    } else {
      log.debug("No layout found in local storage. Using default layout.");
    }

    const layoutData = migratePanelsState(
      serializedLayoutData ? (JSON.parse(serializedLayoutData) as LayoutData) : defaultLayout,
    );
    setCurrentLayout({ data: layoutData });
  }, [setCurrentLayout]);

  return <></>;
}
