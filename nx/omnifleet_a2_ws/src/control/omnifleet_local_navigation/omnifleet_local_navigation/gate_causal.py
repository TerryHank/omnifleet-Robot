"""Opt-in bounded asynchronous diagnostics, no new ROS subscriptions."""
import atexit,json,os,queue,threading,time
from pathlib import Path

class Recorder:
    def __init__(self,path):
        self.queue=queue.Queue(maxsize=8192);self.lost=0;self.seq=0
        self.stop=threading.Event();self.path=Path(path);self.error=None
        self.thread=threading.Thread(target=self.writer,daemon=True);self.thread.start()
        atexit.register(self.close)
    def emit(self,event,**values):
        self.seq+=1
        row=dict(seq=self.seq,event=event,record_wall=time.time(),record_mono=time.monotonic(),
                 lost=self.lost,**values)
        try:self.queue.put_nowait(row)
        except queue.Full:self.lost+=1
    def writer(self):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open('w') as f:
                while not self.stop.is_set() or not self.queue.empty():
                    batch=[]
                    try:batch.append(self.queue.get(timeout=.1))
                    except queue.Empty:pass
                    while len(batch)<256:
                        try:batch.append(self.queue.get_nowait())
                        except queue.Empty:break
                    if batch:
                        f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in batch));f.flush()
        except Exception as exc:self.error=str(exc)
    def close(self):
        self.stop.set();self.thread.join(timeout=2)

def create():
    path=os.environ.get('OMNIFLEET_GATE_CAUSAL_FILE')
    return Recorder(path) if path else None
