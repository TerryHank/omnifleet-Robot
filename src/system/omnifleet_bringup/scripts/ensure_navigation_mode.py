"""Confirm STM32 NAV ownership at chassis startup; never send nonzero motor commands."""
import json,struct,time
from pathlib import Path
import serial
STATE_FORMAT='<BBBBBHI16H'
STATE_SIZE=struct.calcsize(STATE_FORMAT)
def decode_state(payload):
    if len(payload) != STATE_SIZE:
        return None
    version, mode, result, failsafe, armed, age, frames, *channels = struct.unpack(STATE_FORMAT, payload)
    if version != 1 or mode not in (0, 1) or failsafe not in (0, 1, 3) or armed not in (0, 1) or any(ch > 2047 for ch in channels):
        return None
    return {'version': version, 'mode': mode, 'result': result, 'failsafe': failsafe,
            'armed': bool(armed), 'age_ms': age, 'frames': frames, 'channels': channels,
            'mapping': {'forward': 'CH3', 'turn': 'CH1', 'center': 1000, 'deadband': 60,
                        'max_linear_mps': 0.3, 'max_angular_rps': 1.0}}


out=Path('/home/iecme/.local/share/omnifleet_t2');out.mkdir(parents=True,exist_ok=True)
result={'before':None,'after':None,'observed_velocity':[],'switch_sent':False,'car_type':None};buffer=b''
def send(port,func,payload):
    packet=bytes([255,252,len(payload)+3,func])+payload
    port.write(packet+bytes([sum(packet[2:])&255]));time.sleep(.005)
def collect(port,seconds):
    global buffer
    deadline=time.monotonic()+seconds;query=0;state=None
    while time.monotonic()<deadline:
        if time.monotonic()>=query:
            send(port,0x50,bytes([0x17,0]));send(port,0x50,bytes([0x15,0]));query=time.monotonic()+.15
        buffer+=port.read(port.in_waiting or 1)
        while len(buffer)>=5:
            i=buffer.find(b'\xff')
            if i<0:buffer=b'';break
            buffer=buffer[i:]
            if len(buffer)<5:break
            size=buffer[2]+2
            if not 5<=size<=64:buffer=buffer[1:];continue
            if len(buffer)<size:break
            f,buffer=buffer[:size],buffer[size:]
            if sum(f[2:-1])&255!=f[-1]:continue
            if f[3]==0x17:state=decode_state(f[4:-1])
            elif f[3]==0x15:result['car_type']=f[4]
            elif f[3]==0x0a and len(f)>=12:result['observed_velocity'].append(list(struct.unpack('<hhh',f[4:10])))
    return state
with serial.Serial('/dev/omnifleet_t2_stm32',115200,timeout=.03,exclusive=True) as port:
    result['before']=collect(port,1.)
    assert result['before'] is not None,'Missing STM32 mode readback'
    assert result['car_type']==7,'STM32 is not a tracked chassis'
    assert len(result['observed_velocity'])>=10 and all(abs(v[0])<10 and abs(v[2])<50 for v in result['observed_velocity']),'Chassis is not stopped'
    if result['before']['mode']!=0:
        assert result['before']['frames']==0 or result['before']['failsafe']!=0,'Receiver is active; inspect before changing owner'
        send(port,0x17,bytes([0,0x5f]));result['switch_sent']=True
    result['after']=collect(port,2.)
(out/'navigation-ownership.json').write_text(json.dumps(result,indent=2))
print(json.dumps({**result,'observed_velocity':result['observed_velocity'][-5:]},ensure_ascii=False))
assert result['after'] and result['after']['mode']==0 and result['after']['result']==0,'STM32 did not confirm NAV mode'
