"""Navigation output passthrough; collision handling remains in Nav2."""


class TrackingGuard:
    def __init__(self,length,width,padding):
        self.length=length;self.width=width;self.padding=padding
        self.reset()

    def reset(self):
        self.progress=None;self.progress_mode=None
        self.progress_has_translation=False

    def evaluate(self,now,pose,stamp,command,path,obstacles,resolution,pose_age,obstacle_age,complete,require_path=True,check_body_clearance=True):
        return '',False
