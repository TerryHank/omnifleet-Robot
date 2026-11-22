import { jsx as _jsx } from "react/jsx-runtime";
import { screen, userEvent } from "@storybook/testing-library";
import WorkspaceContextProvider from "@foxglove/studio-base/providers/WorkspaceContextProvider";
import { AppSettingsDialog } from "./AppSettingsDialog";
function Wrapper(StoryComponent) {
    return (_jsx(WorkspaceContextProvider, { children: _jsx(StoryComponent, {}) }));
}
export default {
    title: "components/AppSettingsDialog",
    component: AppSettingsDialog,
    parameters: { colorScheme: "light" },
    decorators: [Wrapper],
};
export const Default = {
    render: () => {
        return _jsx(AppSettingsDialog, { open: true });
    },
};
export const DefaultChinese = {
    ...Default,
    parameters: { forceLanguage: "zh" },
};
export const DefaultJapanese = {
    ...Default,
    parameters: { forceLanguage: "ja" },
};
export const ChangingLanguage = {
    render: function Story() {
        return _jsx(AppSettingsDialog, { open: true });
    },
    play: async () => {
        const { click, keyboard } = userEvent.setup();
        const input = await screen.findByText("English", { exact: false });
        await click(input);
        await keyboard("中文");
        const item = await screen.findByText("中文", { exact: false });
        await click(item);
    },
};
export const General = {
    render: () => {
        return _jsx(AppSettingsDialog, { open: true, activeTab: "general" });
    },
};
export const GeneralChinese = {
    ...General,
    parameters: { forceLanguage: "zh" },
};
export const GeneralJapanese = {
    ...General,
    parameters: { forceLanguage: "ja" },
};
export const Experimental = {
    render: () => {
        return _jsx(AppSettingsDialog, { open: true, activeTab: "experimental-features" });
    },
};
export const ExperimentalChinese = {
    ...Experimental,
    parameters: { forceLanguage: "zh" },
};
export const ExperimentalJapanese = {
    ...Experimental,
    parameters: { forceLanguage: "ja" },
};
export const About = {
    render: () => {
        return _jsx(AppSettingsDialog, { open: true, activeTab: "about" });
    },
};
export const AboutChinese = {
    ...About,
    parameters: { forceLanguage: "zh" },
};
export const AboutJapanese = {
    ...About,
    parameters: { forceLanguage: "ja" },
};
