import { jsx as _jsx } from "react/jsx-runtime";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import ErrorBoundary from "./ErrorBoundary";
function Broken({ depth = 1 }) {
    if (depth > 20) {
        throw Object.assign(new Error("Hello!"), {
            stack: `
        an error occurred
        it's caught by this component
        now the user sees
            `,
        });
    }
    else {
        return _jsx(Broken, { depth: depth + 1 });
    }
}
export default {
    title: "components/ErrorBoundary",
};
export const Default = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(ErrorBoundary, { children: _jsx(Broken, {}) }) }));
    },
};
export const ShowingDetails = {
    render: () => {
        return (_jsx(DndProvider, { backend: HTML5Backend, children: _jsx(ErrorBoundary, { showErrorDetails: true, hideErrorSourceLocations: true, children: _jsx(Broken, {}) }) }));
    },
};
