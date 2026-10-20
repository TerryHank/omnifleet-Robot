"use strict";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
Object.defineProperty(exports, "__esModule", { value: true });
const tslib_1 = require("tslib");
const rule_tester_1 = require("@typescript-eslint/rule-tester");
const path_1 = tslib_1.__importDefault(require("path"));
// eslint-disable-next-line @typescript-eslint/no-var-requires
const rule = require("./no-map-type-argument");
const ruleTester = new rule_tester_1.RuleTester({
    parser: "@typescript-eslint/parser",
    parserOptions: {
        ecmaVersion: 2020,
        tsconfigRootDir: path_1.default.join(__dirname, "fixture"),
        project: "tsconfig.json",
    },
});
ruleTester.run("no-map-type-argument", rule, {
    valid: [
        /* ts */ `
    [1, 2].map((x) => x + 1);
    [1, 2].map((x): number => x + 1);
    [1, 2].map<number>((x): number => x + 1);
    [1, 2].map<number, string>((x) => x + 1);
    ({ x: 1 }).map<number>((x) => x + 1);
    `,
    ],
    invalid: [
        {
            code: /* ts */ `
        [1, 2].map<number>(x => x + 1);
        [1, 2].map<number>((x) => x + 1);
      `,
            errors: [
                { messageId: "preferReturnTypeAnnotation", line: 2 },
                { messageId: "preferReturnTypeAnnotation", line: 3 },
            ],
            output: /* ts */ `
        [1, 2].map((x): number => x + 1);
        [1, 2].map((x): number => x + 1);
      `,
        },
    ],
});
//# sourceMappingURL=no-map-type-argument.test.js.map