/// <reference types="react" />
import { Immutable, SettingsTree } from "@foxglove/studio";
export default function SettingsTreeEditor({ variant, settings, }: {
    variant: "panel" | "log";
    settings: Immutable<SettingsTree>;
}): JSX.Element;
