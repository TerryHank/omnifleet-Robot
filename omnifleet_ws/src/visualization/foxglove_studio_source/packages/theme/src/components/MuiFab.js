// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export const MuiFab = {
    defaultProps: {
        color: "inherit",
    },
    styleOverrides: {
        root: ({ theme }) => ({
            boxShadow: theme.shadows[2],
        }),
        colorInherit: ({ theme }) => ({
            backgroundColor: theme.palette.background.paper,
        }),
        extended: ({ theme }) => ({
            gap: theme.spacing(1),
        }),
    },
};
