from types import SimpleNamespace as NS
import pytest
from omnifleet_hikrobot_rgbd.camera_node import HikrobotCamera


def camera(fail_rate=False):
    device=HikrobotCamera.__new__(HikrobotCamera)
    values={'ExposureTime':1000.,'AcquisitionFrameRate':15.}
    def write(name,value):
        if fail_rate and name=='AcquisitionFrameRate' and value==30.:
            return 1
        values[name]=value
        return 0
    def read(name,value):
        value.fMax=30.001 if values['ExposureTime']<=500 else 15.001
        return 0
    device.camera=NS(MV_CC_SetFloatValue=write,MV_CC_GetFloatValue=read)
    device.mvs=NS(MVCC_FLOATVALUE=NS)
    device.depth_settings=lambda:dict(depth_exposure_time_us=values['ExposureTime'],
                                      acquisition_frame_rate=values['AcquisitionFrameRate'])
    return device,values


def test_hot_exposure_updates_frame_rate_with_exposure():
    device,_=camera()
    assert device.set_depth_exposure(500.)==dict(depth_exposure_time_us=500.,acquisition_frame_rate=30.)
    assert device.set_depth_exposure(1000.)==dict(depth_exposure_time_us=1000.,acquisition_frame_rate=15.)


def test_hot_update_rolls_back_if_new_frame_rate_fails():
    device,values=camera(True)
    with pytest.raises(RuntimeError):device.set_depth_exposure(500.)
    assert values=={'ExposureTime':1000.,'AcquisitionFrameRate':15.}


def test_changing_limit_inside_auto_mode_pauses_and_resumes_grabbing():
    device,values=camera()
    device.running=True
    values['upper']=500
    events=[]
    device.depth_settings=lambda:dict(depth_exposure_mode='DynamicMode',depth_exposure_time_us=None,
        depth_auto_exposure_max_us=values['upper'],acquisition_frame_rate=values['AcquisitionFrameRate'])
    def limit(name,value):
        assert not device.running
        assert name=='StereoAutoExposureTimeUpperLimit'
        values['upper']=value
        return 0
    device.camera.MV_CC_SetIntValueEx=limit
    device.camera.MV_CC_StopGrabbing=lambda:events.append('stop') or 0
    device.camera.MV_CC_StartGrabbing=lambda:events.append('start') or 0
    result=device.set_depth_exposure(300.,'DynamicMode')
    assert result['depth_auto_exposure_max_us']==300
    assert device.running and events==['stop','start']
