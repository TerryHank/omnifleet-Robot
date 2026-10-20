"use strict";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
Object.defineProperty(exports, "__esModule", { value: true });
const tslib_1 = require("tslib");
const rule_tester_1 = require("@typescript-eslint/rule-tester");
const path_1 = tslib_1.__importDefault(require("path"));
// eslint-disable-next-line @typescript-eslint/no-var-requires
const rule = require("./lodash-ramda-imports");
const ruleTester = new rule_tester_1.RuleTester({
    parser: "@typescript-eslint/parser",
    parserOptions: {
        ecmaVersion: 2020,
        tsconfigRootDir: path_1.default.join(__dirname, "fixture"),
        project: "tsconfig.json",
    },
});
ruleTester.run("lodash-ramda-imports", rule, {
    valid: [
        /* ts */ `
    import * as _ from "lodash-es";
    _.isEqual(1, 1);
    import * as R from "ramda";
    R.equals(1, 1);
    `,
    ],
    invalid: [
        {
            code: /* ts */ `
        import * as _ from "lodash";
        _.isEqual(1, 1);
      `,
            errors: [
                { messageId: "useDifferentPackage", data: { package: "lodash-es", convertFrom: "lodash" } },
            ],
            output: /* ts */ `
        import * as _ from "lodash-es";
        _.isEqual(1, 1);
      `,
        },
        {
            code: /* ts */ `
        import _ from "lodash-es";
        _.isEqual(1, 1);
      `,
            errors: [{ messageId: "useNamespaceImport", data: { name: "_", package: "lodash-es" } }],
            output: /* ts */ `
        import * as _ from "lodash-es";
        _.isEqual(1, 1);
      `,
        },
        {
            code: /* ts */ `
        import _, { isEmpty } from "lodash-es";
        _.isEqual(1, 1);
        isEmpty({});
      `,
            errors: [{ messageId: "useNamespaceImport", data: { name: "_", package: "lodash-es" } }],
            output: /* ts */ `
        import * as _ from "lodash-es";
        _.isEqual(1, 1);
        _.isEmpty({});
      `,
        },
        {
            code: /* ts */ `
        import lodash, { isEmpty as lodashIsEmpty } from "lodash-es";
        lodash.isEqual(1, 1);
        lodashIsEmpty({});
      `,
            errors: [{ messageId: "useNamespaceImport", data: { name: "_", package: "lodash-es" } }],
            output: /* ts */ `
        import * as _ from "lodash-es";
        _.isEqual(1, 1);
        _.isEmpty({});
      `,
        },
        {
            code: /* ts */ `
        import lodash, { isEmpty as lodashIsEmpty } from "lodash-es";
        lodash.isEqual(1, 1);
        lodashIsEmpty({});
      `,
            errors: [{ messageId: "useNamespaceImport", data: { name: "_", package: "lodash-es" } }],
            output: /* ts */ `
        import * as _ from "lodash-es";
        _.isEqual(1, 1);
        _.isEmpty({});
      `,
        },
        {
            code: /* ts */ `
        import ramda, { isEmpty as ramdaIsEmpty } from "ramda";
        ramda.equals(1, 1);
        ramdaIsEmpty({});
      `,
            errors: [{ messageId: "useNamespaceImport", data: { name: "R", package: "ramda" } }],
            output: /* ts */ `
        import * as R from "ramda";
        R.equals(1, 1);
        R.isEmpty({});
      `,
        },
    ],
});
//# sourceMappingURL=lodash-ramda-imports.test.js.map