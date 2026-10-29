export interface ManualRequest { robot: string; velocity: [number, number]; }

// Serialize POST admission, not vehicle acknowledgements. A release replaces
// unsent renewals and is admitted after the already in-flight command.
export class ManualQueue {
  private next: ManualRequest | null = null;
  private stops: ManualRequest[] = [];
  private sending = false;
  constructor(private send: (request: ManualRequest) => Promise<void>, private error: (error: Error, request: ManualRequest) => void) {}
  submit(robot: string, velocity: [number, number]) {
    if (velocity.every((v) => v === 0)) {
      if (this.next?.robot === robot) this.next = null;
      if (!this.stops.some((request) => request.robot === robot)) this.stops.push({ robot, velocity });
    } else this.next = { robot, velocity };
    void this.flush();
  }
  private async flush() {
    if (this.sending) return;
    this.sending = true;
    try {
      while (this.stops.length || this.next) {
        const stop = this.stops.shift();
        const request = stop || this.next!; if (!stop) this.next = null;
        try { await this.send(request); }
        catch (error) { this.error(error as Error, request); }
      }
    } finally { this.sending = false; }
  }
}
