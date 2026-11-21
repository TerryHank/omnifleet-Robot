"""TensorRT executor matching the three Net methods used by OpenCV Zoo."""
from pathlib import Path
import numpy as np


class TensorRTNet:
    def __init__(self,path,output_names):
        import torch
        import tensorrt as trt
        self.torch=torch
        self.logger=trt.Logger(trt.Logger.WARNING)
        self.runtime=trt.Runtime(self.logger)
        self.engine=self.runtime.deserialize_cuda_engine(Path(path).read_bytes())
        self.context=self.engine.create_execution_context()
        self.stream=torch.cuda.Stream()
        self.outputs={}
        for index in range(self.engine.num_io_tensors):
            name=self.engine.get_tensor_name(index)
            shape=tuple(self.engine.get_tensor_shape(name))
            dtype=torch.from_numpy(np.empty((),trt.nptype(self.engine.get_tensor_dtype(name)))).dtype
            if self.engine.get_tensor_mode(name)==trt.TensorIOMode.INPUT:
                self.input_name,self.input_shape,self.input_dtype=name,shape,dtype
            else:
                value=torch.empty(shape,dtype=dtype,device='cuda')
                self.outputs[name]=value
                self.context.set_tensor_address(name,value.data_ptr())
        self.output_names=tuple(output_names)
        if set(self.outputs)!=set(self.output_names):
            raise ValueError('TensorRT and OpenCV Zoo output names differ')

    def getUnconnectedOutLayersNames(self):
        return self.output_names

    def setInput(self,value):
        self.blob=np.ascontiguousarray(value)

    def forward(self,names):
        if self.blob.shape!=self.input_shape:
            raise ValueError(f'TensorRT input {self.blob.shape} != {self.input_shape}')
        with self.torch.inference_mode(),self.torch.cuda.stream(self.stream):
            value=self.torch.from_numpy(self.blob).to(device='cuda',dtype=self.input_dtype)
            self.context.set_tensor_address(self.input_name,value.data_ptr())
            if not self.context.execute_async_v3(self.stream.cuda_stream):
                raise RuntimeError('TensorRT hand inference failed')
            values=[self.outputs[name] for name in names]
            merged=self.torch.cat([value.reshape(-1) for value in values]).cpu().numpy()
            result=[]
            offset=0
            for value in values:
                size=value.numel()
                result.append(merged[offset:offset+size].reshape(value.shape).astype(np.float32,copy=True))
                offset+=size
            return result

    def close(self):
        self.context=None
        self.engine=None
        self.runtime=None
