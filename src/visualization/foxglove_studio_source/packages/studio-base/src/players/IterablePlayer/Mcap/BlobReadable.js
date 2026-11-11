// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export class BlobReadable {
    file;
    constructor(file) {
        this.file = file;
    }
    async size() {
        return BigInt(this.file.size);
    }
    async read(offset, size) {
        if (offset + size > this.file.size) {
            throw new Error(`Read of ${size} bytes at offset ${offset} exceeds file size ${this.file.size}`);
        }
        return new Uint8Array(await this.file.slice(Number(offset), Number(offset + size)).arrayBuffer());
    }
}
