// MPL-2.0. School runtime 5ddcccf: tracking renderer retained without desktop catalogue.
(function (root) {
  'use strict';
  const CONTROL = '/vision/demo/control', STATUS = '/vision/demo/status';
  const RGB = '/camera/color/image_raw/compressed';
  const RENDER_MODE='latest-canvas';

  const frameNow=()=>performance.timeOrigin+performance.now();
  let timingRows=[];
  function frameTiming(trace,decoded) {
    requestAnimationFrame(()=>{
      timingRows.push([trace.source,trace.received,trace.started,decoded,frameNow()].map(n=>Number(n.toFixed(3))));
      if(timingRows.length>=20){console.info('RGB_TIMING '+JSON.stringify({mode:RENDER_MODE,link:window.__followLink,rows:timingRows}));timingRows=[];}
    });
  }
  const sharedRgb=document.createElement('canvas');
  sharedRgb.dataset.ui='kcfPreview';
  sharedRgb.hidden=true;
  sharedRgb.draggable=false;
  Object.defineProperties(sharedRgb,{
    naturalWidth:{get:()=>sharedRgb.width},naturalHeight:{get:()=>sharedRgb.height}
  });
  const bitmapContext=sharedRgb.getContext('bitmaprenderer');
  const imageContext=bitmapContext?null:sharedRgb.getContext('2d');
  let pendingRgb,decodingRgb=false;
  async function drawLatestRgb() {
    if(decodingRgb||!pendingRgb)return;
    decodingRgb=true;
    const frame=pendingRgb;pendingRgb=undefined;frame.started=frameNow();
    try {
      const bitmap=await createImageBitmap(new Blob([frame.message.data],{type:'image/jpeg'}));
      const resized=sharedRgb.width!==bitmap.width||sharedRgb.height!==bitmap.height;
      if(resized){sharedRgb.width=bitmap.width;sharedRgb.height=bitmap.height;}
      if(bitmapContext)bitmapContext.transferFromImageBitmap(bitmap);
      else {imageContext.drawImage(bitmap,0,0);bitmap.close();}
      sharedRgb.frameStamp=frame.source/1000;
      sharedRgb.hidden=false;
      sharedRgb.dispatchEvent(new Event('rgb-frame'));
      if(resized)sharedRgb.dispatchEvent(new Event('load'));
      frameTiming(frame,frameNow());
    } catch(error) {console.warn('RGB decode failed: '+String(error));}
    finally {decodingRgb=false;if(pendingRgb)drawLatestRgb();}
  }
  function updateRgb(message) {
    const stamp=message.header?.stamp;
    pendingRgb={message,source:stamp?Number(stamp.sec)*1000+Number(stamp.nanosec??stamp.nsec??0)*1e-6:0,received:frameNow()};
    drawLatestRgb();
  }
  const COLOR_PICK='/vision/color/pick', KCF_ROI='/omnifleet_vision/kcf/roi', PANEL='local.omnifleet-vision.demo!functional-control';
  function initKcfPanel(context) {
    const color=context.initialState?.followKind==='color';
    const marker=context.initialState?.markerKind;
    const caseId=context.initialState?.caseId||(color?(context.initialState?.caseId||'04_01_color_follow'):marker==='qr'?'02_05_qr':marker==='apriltag'?'02_06_apriltag':'02_07_kcf');
    const body=caseId==='04_09_body_tracking';
    const follower=color?(caseId==='02_04_color'?'/course_color_box_follow':'/course_target_follow'):marker?'/'+marker+'_follower':'/kcf_follower';
    const KCF_STATUS=body?'/vision/body_tracking/status':color?'/vision/target_follow/status':marker?'/vision/'+marker+'/follow/status':'/omnifleet_vision/kcf/status';
    const el=document.createElement('div');el.className='vision-demo vision-kcf-window'+(body?' vision-body-preview':'');
    el.innerHTML=`<style>
      .vision-demo{height:100%;box-sizing:border-box;overflow:auto;padding:14px;color:#e5edf7;background:#151b25;font:14px/1.5 "Microsoft YaHei",sans-serif}
      .vision-demo h2{font-size:21px;margin:0 0 4px}.vision-demo p{margin:6px 0}.vision-demo small{color:#a9bbcf}
      .vision-demo input,.vision-demo select,.vision-demo textarea{box-sizing:border-box;width:100%;font:inherit;color:#e8edf6;background:#202a39;border:1px solid #43536b;border-radius:5px;padding:7px;margin:4px 0}
      .vision-demo select[data-ui=list]{padding:3px;min-height:160px}.vision-demo option{padding:6px}.vision-demo option:checked{background:#245583}
      .vision-demo button{font:inherit;border:1px solid #4c6585;border-radius:5px;padding:8px;color:white;background:#293f59;cursor:pointer}
      .vision-demo button:disabled{opacity:.55;cursor:default}.vision-demo .vd-row{display:flex;gap:7px}.vision-demo .vd-row>*{flex:1;min-width:0}
      .vision-demo .vd-card{padding:10px;border:1px solid #34455b;border-radius:7px;margin:10px 0}.vision-demo [data-ui=start]{background:#1467ad}.vision-demo [data-ui=stop]{background:#9a343f}
      .vision-demo [data-ui=message]{white-space:pre-wrap;color:#9fd3ff}.vision-demo pre{white-space:pre-wrap;overflow:auto;max-height:240px;font:12px/1.45 Consolas,monospace;color:#c5d6e9}
      .vision-demo [data-ui=logs]{height:180px;max-height:300px;background:#101620;padding:8px}.vision-demo label{display:block;margin:5px 0}.vision-demo details{margin:8px 0}
    </style><style>
      .vision-kcf-window{overflow:auto;padding:12px}
      .vision-kcf-window [data-ui=kcfControls]{margin:0;padding:0;border:0;display:flex;flex-direction:column;min-height:0}
      .vision-kcf-window [data-ui=kcfPicker]{flex:none;width:min(100%,1120px);aspect-ratio:16/9;min-height:0;align-self:center;background:#0d121a;overflow:hidden}
      .vision-kcf-window [data-ui=kcfPreview],.vision-kcf-window [data-ui=kcfCanvas]{width:100%;height:100%;object-fit:contain}
      .vision-kcf-window [data-ui=kcfLoading]{position:absolute;inset:0;margin:auto;width:32px;height:32px;box-sizing:border-box;border:3px solid #34455b;border-top-color:#74b9ff;border-radius:50%;animation:vision-rgb-spin .8s linear infinite;pointer-events:none}
      .vision-body-preview [data-ui=kcfControls] > :not([data-ui=kcfPicker]):not([data-ui=kcfReply]){display:none}
      .vision-body-preview [data-ui=kcfCanvas]{pointer-events:none}
      @keyframes vision-rgb-spin{to{transform:rotate(360deg)}}
      .vision-kcf-window [data-ui=kcfPreview]:not([hidden]){display:block}
      .vision-kcf-window [data-ui=start]{background:#1467ad}.vision-kcf-window [data-ui=stop]{background:#9a343f}
    </style>    <div class="vd-card" data-ui=kcfControls><strong>${color?'颜色目标跟随':marker?'二维码 / AprilTag 自动识别并跟随':'框选物体并跟随'}</strong><div class="vd-row" style="margin:6px 0"><button data-ui=start>开始 / 重新跟踪</button><button data-ui=stop>停止跟随</button></div>
      <p>${color?'点击颜色检测框后，只检测并跟踪选中的色块。点击“清除跟踪”停车并恢复全部颜色检测，再选择新目标。底盘运动由下方开关控制。':marker?'无需拖框。识别后保留二维码内容或标签ID，解码间隙使用KCF连续跟踪；底盘运动由下方按钮控制。重新开始可重新选择目标。':'点击“开始 / 重新跟踪”，然后在下面实时画面拖框，松手锁定目标。底盘是否运动由下方按钮控制；再次拖框可切换物体，“停止跟随”结束案例。'}</p>
      ${color?`<details ><summary>预设颜色（可选）</summary><label>跟随颜色<select data-ui=selectedColor disabled><option value=red>红色</option><option value=yellow>黄色</option><option value=green>绿色</option><option value=blue>蓝色</option><option value=picked disabled>点击选中的颜色目标</option></select></label><button data-ui=applyColor disabled>应用预设颜色</button></details><button data-ui=clearColor>清除跟踪 · 恢复全部颜色检测</button><p data-ui=colorActual>等待读取检测与跟随颜色</p><p data-ui=colorReply>点击检测框选择目标；选中后需先清除跟踪才能重新选择。</p>`:''}
      ${marker==='apriltag'?'<label>跟随测距来源<select data-ui=rangeSource><option value=depth>配准深度图 · 真实深度采样</option><option value=rgb>纯RGB · 210mm标签位姿估距</option></select></label><p data-ui=rangeSourceReply>RGB识别同一标签，两种距离来源可热切换。</p>':''}
      <div data-ui=kcfPicker style="position:relative;touch-action:none"><span data-ui=kcfLoading role="status" aria-label="正在加载实时图像"></span><canvas data-ui=kcfCanvas style="position:absolute;inset:0;width:100%;height:100%;cursor:crosshair"></canvas></div>
      <p data-ui=kcfReply>${marker||color?'等待自动识别目标':'等待框选；尚未指定目标。'}</p>
      <button data-ui=kcfMotion disabled>等待底盘跟随状态</button><p data-ui=kcfMotionReply>关闭运动仍保留目标框和ID。</p>
      <label>与物体保持距离：<strong data-ui=kcfActualDistance>等待读回</strong>
        <span class="vd-row"><input data-ui=kcfDistance type=range min=0.2 max=3.5 step=0.05 value=2 aria-label="物体跟随距离滑块"><input data-ui=kcfDistanceNumber type=number min=0.2 max=3.5 step=0.05 value=2 aria-label="物体跟随距离米"></span></label>
      <button data-ui=kcfApplyDistance>应用跟随距离</button><p data-ui=kcfDistanceReply></p>
      <small>单位米，范围大于0.2且小于3.5。输入后按回车、点击应用或松开滑块生效，无需重选目标。成功设置后永久保存在机器人端，重启读取本案例上一次的值，各案例独立保存。</small></div>
`;
    context.panelElement.append(el);
    const ui={};el.querySelectorAll('[data-ui]').forEach(item=>{ui[item.dataset.ui]=item;item.dataset.testid='vision-'+item.dataset.ui;});
    let kcfDrag,kcfSourceWidth,kcfDistanceEdited=false,kcfPendingDistance,kcfMotion,kcfPendingMotion,kcfMotionBusy=false,kcfStopReason='';
    let detectorColor,controllerColor,detectorSample,colorBusy=false,pendingColor,pickPendingId,pickTimer,kcfImageStamp=0,overlay,caseReady=false;
    const colorNames={red:'红色',yellow:'黄色',green:'绿色',blue:'蓝色'};
    const colorLabel=value=>colorNames[value]||(typeof value==='string'&&value.startsWith('picked_')?(detectorSample?.name===value&&colorNames[detectorSample.source_color]?colorNames[detectorSample.source_color]+'（已点击）':'画面取色'):value===''?'全部颜色':value==='__click_target__'?'等待点击检测框':'等待读回');
    async function callFollowService(name,request){
      for(let attempt=0;;attempt++)try{return await context.callService(name,request);}
      catch(error){if(attempt>=3||!/not been advertised|not advertised/i.test(error.message))throw error;await new Promise(resolve=>setTimeout(resolve,500));}
    }
    function renderColor(){
      if(!color)return;
      ui.selectedColor.disabled=ui.applyColor.disabled=Boolean(detectorColor)||colorBusy||pendingColor!==undefined||detectorColor===undefined||controllerColor===undefined;
      ui.clearColor.disabled=detectorColor===undefined||controllerColor===undefined;
      ui.colorActual.textContent=detectorColor?'仅检测并跟踪：'+colorLabel(detectorColor):'检测：全部颜色；跟随：'+colorLabel(controllerColor);
      if(detectorSample&&detectorSample.name===detectorColor){
        ui.colorActual.textContent+=' · HSV '+detectorSample.hsv.join('/');
        const bgr=detectorSample.bgr;ui.colorActual.style.borderLeft='8px solid rgb('+[bgr[2],bgr[1],bgr[0]].join(',')+')';ui.colorActual.style.paddingLeft='8px';
      }else ui.colorActual.style.borderLeft='';
      if(pendingColor!==undefined&&detectorColor===pendingColor&&controllerColor===(pendingColor||'__click_target__')){
        ui.colorReply.textContent=pendingColor?'已应用'+colorLabel(pendingColor)+'（检测器与控制器读回）':'已清除跟踪并停车，全部颜色检测已恢复';pendingColor=undefined;
        ui.selectedColor.disabled=ui.applyColor.disabled=colorBusy||Boolean(detectorColor);
      }
      if(!colorBusy&&pendingColor===undefined&&detectorColor===controllerColor)ui.selectedColor.value=String(controllerColor).startsWith('picked_')?'picked':controllerColor;
    }
    if(color){
      ui.applyColor.onclick=async()=>{
        if(detectorColor){ui.colorReply.textContent='已锁定目标，请先清除跟踪';return;}
        const value=ui.selectedColor.value;if(value==='picked'){ui.colorReply.textContent='请直接点击实时画面中的色块取色';return;}
        colorBusy=true;renderColor();ui.colorReply.textContent='正在切换颜色…';
        try{
          for(const [node,name]of [[follower,'class_filter'],['/course_color','selected_color']]){
            const reply=await callFollowService(node+'/set_parameters',{parameters:[{name,value:{type:4,bool_value:false,integer_value:0,double_value:0,string_value:value,byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
            if(!reply.results?.length||reply.results.some(r=>!r.successful))throw Error(reply.results?.map(r=>r.reason).join('; ')||'颜色参数未接受');
          }
          pendingColor=value;ui.colorReply.textContent='已提交，等待两端颜色读回…';
        }catch(error){ui.colorReply.textContent='切换失败：'+error.message;}
        finally{colorBusy=false;renderColor();}
      };
      ui.selectedColor.onchange=()=>ui.applyColor.onclick();
      ui.clearColor.onclick=()=>{
        pickPendingId=root.crypto?.randomUUID?.()||String(Date.now());colorBusy=true;pendingColor=undefined;renderColor();
        try{context.publish(COLOR_PICK,{data:JSON.stringify({id:pickPendingId,op:'clear'})});ui.colorReply.textContent='正在清除跟踪并停车…';}
        catch(error){colorBusy=false;pickPendingId=undefined;renderColor();ui.colorReply.textContent='清除失败：'+error.message;return;}
        clearTimeout(pickTimer);const id=pickPendingId;pickTimer=setTimeout(()=>{if(pickPendingId===id){pickPendingId=undefined;colorBusy=false;renderColor();ui.colorReply.textContent='清除请求未收到机器人确认，请检查连接';}},5000);
      };
    }
    const stringType={datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string',isArray:false,isComplex:false}]}]])};
    context.advertise?.(CONTROL,'std_msgs/msg/String',stringType);
    if(color)context.advertise?.(COLOR_PICK,'std_msgs/msg/String',stringType);
    function send(op){
      const config=root.foxgloveDemoControl?.layout?.()?.data?.configById?.[PANEL];
      const parameters=config?.parametersByCase?.[caseId]||{enable_motion:marker||color?'false':'true'};
      try{context.publish(CONTROL,{data:JSON.stringify({id:root.crypto?.randomUUID?.()||String(Date.now()),op,case_id:caseId,parameters})});ui.kcfReply.textContent=op==='start'?'已提交开始跟踪，等待机器人状态…':'已提交停止跟随…';}
      catch(error){ui.kcfReply.textContent='请求发送失败：'+error.message;}
    }
    ui.start.onclick=()=>send('start');ui.stop.onclick=()=>send('stop');
    function renderMotion(){
      ui.kcfMotion.disabled=typeof kcfMotion!=='boolean'||kcfMotionBusy||kcfPendingMotion!==undefined;
      ui.kcfMotion.textContent=kcfMotion?'关闭底盘跟随':'开启底盘跟随';
    }
    ui.kcfMotion.onclick=async()=>{
      if(typeof kcfMotion!=='boolean'||kcfMotionBusy||kcfPendingMotion!==undefined)return;
      const value=!kcfMotion;kcfMotionBusy=true;renderMotion();ui.kcfMotionReply.textContent='正在修改底盘跟随…';
      try{
        const reply=await callFollowService(follower+'/set_parameters',{parameters:[{name:'enable_motion',value:{type:1,bool_value:value,integer_value:0,double_value:0,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受运动参数');
        const api=root.foxgloveDemoControl,current=api?.layout?.();
        if(current?.data&&api?.setLayout){
          const data=JSON.parse(JSON.stringify(current.data));
          const config=data.configById[PANEL];config.parametersByCase??={};config.parametersByCase[caseId]??={};
          config.parametersByCase[caseId].enable_motion=String(value);
          api.setLayout(current.name||'视觉功能演示',data);
        }
        kcfPendingMotion=value;
        ui.kcfMotionReply.textContent='参数已接受，等待控制器状态确认…';
      }catch(error){ui.kcfMotionReply.textContent='修改失败：'+error.message;}
      finally{kcfMotionBusy=false;renderMotion();}
    };
    context.advertise?.(KCF_ROI,'sensor_msgs/msg/RegionOfInterest',{datatypes:new Map([
      ['sensor_msgs/msg/RegionOfInterest',{definitions:[
        ...['x_offset','y_offset','height','width'].map(name=>({name,type:'uint32',isArray:false,isComplex:false})),
        {name:'do_rectify',type:'bool',isArray:false,isComplex:false}
      ]}]
    ])});
    function kcfPoint(event){
      const rect=ui.kcfCanvas.getBoundingClientRect();
      const scale=Math.min(rect.width/ui.kcfCanvas.width,rect.height/ui.kcfCanvas.height);
      const left=rect.left+(rect.width-ui.kcfCanvas.width*scale)/2;
      const top=rect.top+(rect.height-ui.kcfCanvas.height*scale)/2;
      return [Math.max(0,Math.min(ui.kcfCanvas.width,(event.clientX-left)/scale)),
              Math.max(0,Math.min(ui.kcfCanvas.height,(event.clientY-top)/scale))];
    }
    function drawKcfBox(end){
      const canvas=ui.kcfCanvas, pen=canvas.getContext('2d');
      pen.clearRect(0,0,canvas.width,canvas.height);pen.strokeStyle='#ffdc00';pen.lineWidth=2;
      pen.strokeRect(kcfDrag[0],kcfDrag[1],end[0]-kcfDrag[0],end[1]-kcfDrag[1]);
    }
    function drawOverlay() {
      if(kcfDrag)return;
      const canvas=ui.kcfCanvas,pen=canvas.getContext('2d');
      pen.clearRect(0,0,canvas.width,canvas.height);
      if(!overlay||!kcfImageStamp||Math.abs(overlay.stamp-kcfImageStamp)>.5)return;
      const sx=canvas.width/(overlay.width||canvas.width),sy=canvas.height/(overlay.height||canvas.height);
      pen.strokeStyle='#74e9a8';pen.fillStyle=pen.strokeStyle;pen.lineWidth=2;pen.font='14px sans-serif';
      for(const track of overlay.tracks){
        if(!Array.isArray(track.bbox)||track.bbox.length!==4||!track.bbox.every(Number.isFinite))continue;
        const [x,y,a,b]=track.bbox;
        pen.strokeRect(x*sx,y*sy,(body?a-x:a)*sx,(body?b-y:b)*sy);
        const id=track.track_id??track.id,depth=track.foreground?.depth_m??overlay.depth;
        const label=[track.color??track.class??(id==null?'':'ID '+id),Number.isFinite(depth)?depth.toFixed(2)+' m':''].filter(Boolean).join(' ');
        if(label)pen.fillText(label,x*sx,Math.max(14,y*sy-4));
      }
    }
    function setOverlay(value,tracks){
      const stamp=value.source_stamp??value.stamp;
      const seconds=Array.isArray(stamp)?Number(stamp[0])+Number(stamp[1])*1e-9:
        typeof stamp==='object'&&stamp?Number(stamp.sec)+Number(stamp.nanosec??stamp.nsec??0)*1e-9:Number(stamp);
      overlay={tracks:tracks||[],stamp:Number.isFinite(seconds)?seconds:kcfImageStamp,
        width:value.rgb_resolution?.[0]??value.image_width,height:value.rgb_resolution?.[1]??value.image_height,depth:value.depth_m};
      drawOverlay();
    }
    function syncRgb() {
      if(sharedRgb.parentNode!==ui.kcfPicker)return;
      if(!sharedRgb.frameStamp||!sharedRgb.naturalWidth)return;
      ui.kcfLoading.hidden=caseReady;
      if(ui.kcfCanvas.width!==sharedRgb.naturalWidth||ui.kcfCanvas.height!==sharedRgb.naturalHeight){
        ui.kcfCanvas.width=sharedRgb.naturalWidth;ui.kcfCanvas.height=sharedRgb.naturalHeight;
      }
      kcfImageStamp=sharedRgb.frameStamp;drawOverlay();
    }
    ui.kcfCanvas.onpointerdown=event=>{
      if(marker||body||!kcfImageStamp)return;
      if(color){
        if(detectorColor){ui.colorReply.textContent='已锁定此色块，请先点击清除跟踪再选择其他目标';return;}
        event.preventDefault();const [x,y]=kcfPoint(event);
        pickPendingId=root.crypto?.randomUUID?.()||String(Date.now());colorBusy=true;pendingColor=undefined;renderColor();
        const request={id:pickPendingId,x,y,width:ui.kcfCanvas.width,height:ui.kcfCanvas.height,stamp:kcfImageStamp,...(caseId==='02_04_color'?{mode:'box'}:{})};
        try{context.publish(COLOR_PICK,{data:JSON.stringify(request)});ui.colorReply.textContent='已提交点击位置，等待机器人锁定颜色目标…';}
        catch(error){colorBusy=false;pickPendingId=undefined;renderColor();ui.colorReply.textContent='取色发送失败：'+error.message;return;}
        clearTimeout(pickTimer);const id=pickPendingId;pickTimer=setTimeout(()=>{if(pickPendingId===id){pickPendingId=undefined;colorBusy=false;renderColor();ui.colorReply.textContent='取色请求未收到确认，请检查案例与连接';}},5000);
        return;
      }
      event.preventDefault();kcfDrag=kcfPoint(event);ui.kcfCanvas.setPointerCapture?.(event.pointerId);
    };
    ui.kcfCanvas.onpointermove=event=>{if(kcfDrag)drawKcfBox(kcfPoint(event));};
    ui.kcfCanvas.onpointerup=event=>{
      if(!kcfDrag)return;
      const end=kcfPoint(event);drawKcfBox(end);
      const x=Math.round(Math.min(kcfDrag[0],end[0])),y=Math.round(Math.min(kcfDrag[1],end[1]));
      const width=Math.min(ui.kcfCanvas.width-x,Math.round(Math.abs(end[0]-kcfDrag[0])));
      const height=Math.min(ui.kcfCanvas.height-y,Math.round(Math.abs(end[1]-kcfDrag[1])));
      kcfDrag=undefined;ui.kcfCanvas.releasePointerCapture?.(event.pointerId);
      if(width<=1||height<=1){ui.kcfReply.textContent='选框太小，请框住物体。';return;}
      const scale=(kcfSourceWidth||ui.kcfCanvas.width)/ui.kcfCanvas.width;
      const roi={x_offset:Math.round(x*scale),y_offset:Math.round(y*scale),width:Math.round(width*scale),height:Math.round(height*scale),do_rectify:false};
      try{context.publish(KCF_ROI,roi);ui.kcfReply.textContent=`已提交选框 (${x},${y}) ${width}×${height}，等待机器人锁定。`;}
      catch(error){ui.kcfReply.textContent='选框发送失败：'+error.message;}
    };
    ui.kcfCanvas.onpointercancel=()=>{kcfDrag=undefined;};
    ui.kcfDistance.oninput=()=>{kcfDistanceEdited=true;ui.kcfDistanceNumber.value=ui.kcfDistance.value;};
    ui.kcfDistanceNumber.oninput=()=>{kcfDistanceEdited=true;if(ui.kcfDistanceNumber.validity.valid)ui.kcfDistance.value=ui.kcfDistanceNumber.value;};
    ui.kcfApplyDistance.onclick=async()=>{
      const value=Number(ui.kcfDistanceNumber.value);
      if(!ui.kcfDistanceNumber.value||!ui.kcfDistanceNumber.validity.valid||!Number.isFinite(value)){ui.kcfDistanceReply.textContent='请输入有效的跟随距离（米）';return;}
      kcfPendingDistance=value;ui.kcfDistanceReply.textContent='已提交，等待跟随控制器读回…';
      try{
        const reply=await callFollowService(follower+'/set_parameters',{parameters:[{name:'target_distance',value:{type:3,bool_value:false,integer_value:0,double_value:value,string_value:'',byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(result=>!result.successful))throw Error(reply.results?.map(result=>result.reason).filter(Boolean).join('; ')||'控制器未接受距离参数');
      }catch(error){kcfPendingDistance=undefined;ui.kcfDistanceReply.textContent='修改失败：'+error.message;}
    };
    ui.kcfDistance.onchange=()=>ui.kcfApplyDistance.click();
    ui.kcfDistanceNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();ui.kcfApplyDistance.click();}};
    if(ui.rangeSource)ui.rangeSource.onchange=async()=>{
      const value=ui.rangeSource.value;ui.rangeSourceReply.textContent='正在切换测距来源…';
      try{
        const reply=await callFollowService('/course_apriltag/set_parameters',{parameters:[{name:'distance_source',value:{type:4,bool_value:false,integer_value:0,double_value:0,string_value:value,byte_array_value:[],bool_array_value:[],integer_array_value:[],double_array_value:[],string_array_value:[]}}]});
        if(!reply.results?.length||reply.results.some(r=>!r.successful))throw Error(reply.results?.map(r=>r.reason).join('; ')||'参数未接受');
        ui.rangeSourceReply.textContent='已提交，等待识别节点读回…';
      }catch(error){ui.rangeSourceReply.textContent='切换失败：'+error.message;}
    };
    context.watch('currentFrame');
    const colorTopic=caseId==='02_04_color'?'/vision/color/result':'/vision/detections';
    const markerTracks=marker?'/vision/'+marker+'/tracks':null;
    context.subscribe([KCF_STATUS,...(body?[]:color?[colorTopic]:marker?['/vision/'+marker+'/result',markerTracks]:['/vision/nanotrack/selected']),STATUS].map(topic=>({topic})));
    ui.kcfPicker.insertBefore(sharedRgb,ui.kcfCanvas);
    sharedRgb.addEventListener('rgb-frame',syncRgb);
    syncRgb();
    context.onRender=(state,done)=>{
      try{for(const event of state.currentFrame||[]){
          if(event.topic===STATUS){
            const manager=JSON.parse(event.message.data);
            if(manager.case_id===caseId&&['ERROR','COMPLETED'].includes(manager.phase)||!manager.case_id&&manager.phase==='STOPPED'){
              caseReady=true;
              syncRgb();
            }
            if(manager.case_id===caseId&&['STARTING','STOPPING','ERROR','COMPLETED'].includes(manager.phase))ui.kcfReply.textContent=({STARTING:'正在启动跟踪…',STOPPING:'正在停止跟随…',ERROR:'跟踪启动错误',COMPLETED:'跟踪进程已结束'})[manager.phase];
            else if(!manager.case_id&&['STOPPED','IDLE'].includes(manager.phase))ui.kcfReply.textContent='目标追踪案例已停止';
            else if(manager.case_id&&manager.case_id!==caseId)ui.kcfReply.textContent='目标物跟随未运行；当前案例 '+manager.case_id;
          }
          if(event.topic==='/vision/nanotrack/selected')kcfStopReason=JSON.parse(event.message.data).tracking_stop_reason||'';
          if(color&&event.topic===colorTopic){
            const value=JSON.parse(event.message.data);if(typeof value.selected_color==='string')detectorColor=value.selected_color;detectorSample=value.picked_color;setOverlay(value,value.detections);
            const reply=value.pick_result;
            if(reply&&reply.id===pickPendingId){
              clearTimeout(pickTimer);pickPendingId=undefined;colorBusy=false;
              if(reply.success){pendingColor=reply.selected_color;ui.colorReply.textContent=reply.op==='clear'?'已提交清除，等待读回停车与全部颜色检测状态…':reply.source_color?'已选中'+colorLabel(reply.source_color)+'目标，等待跟随确认…':'已从RGB取色，等待跟随颜色确认…';}
              else ui.colorReply.textContent='取色失败：'+reply.message;
            }
            renderColor();
          }
          if(markerTracks&&event.topic===markerTracks){const value=JSON.parse(event.message.data);setOverlay(value,value.tracks);}
          if(marker&&event.topic==='/vision/'+marker+'/result'){
            const value=JSON.parse(event.message.data);
            if(ui.rangeSource&&value.distance_source){ui.rangeSource.value=value.distance_source;ui.rangeSourceReply.textContent='当前来源：'+(value.distance_source==='rgb'?'RGB位姿估距':'配准深度采样')+'（节点读回）';}
          }
          if(event.topic===KCF_STATUS){
            const kcf=JSON.parse(event.message.data);
            caseReady=true;
            syncRgb();
            if(body){
              setOverlay(kcf,kcf.tracks);
              const distance=kcf.person_range_m;
              ui.kcfReply.textContent='人体手势跟随 · '+(kcf.body_tracking?.motion_state??kcf.follow_control_state??kcf.state??'等待目标')+
                (Number.isFinite(distance)?' · '+distance.toFixed(2)+' m':'');
              continue;
            }
            if(!color&&!marker)setOverlay(kcf,kcf.tracks);
            if(color&&typeof kcf.class_filter==='string'){controllerColor=kcf.class_filter;renderColor();}
            if(typeof kcf.enable_motion==='boolean'){
              kcfMotion=kcf.enable_motion;
              if(kcfPendingMotion===kcfMotion){kcfPendingMotion=undefined;ui.kcfMotionReply.textContent=kcfMotion?'已开启底盘跟随（控制器读回）':'已关闭底盘跟随，目标框和ID保留（控制器读回）';}
              renderMotion();
            }
            if(Number.isFinite(kcf.target_distance_m)){
              const value=kcf.target_distance_m;ui.kcfActualDistance.textContent=value.toFixed(2)+' m（控制器读回'+(kcf.distance_persistent?' · 已永久保存':'')+'）';
              if(kcfPendingDistance!==undefined&&Math.abs(value-kcfPendingDistance)<1e-6){
                if(kcf.distance_persistent){kcfPendingDistance=undefined;kcfDistanceEdited=false;ui.kcfDistanceReply.textContent='已生效并永久保存：'+value.toFixed(2)+' m';}
                else ui.kcfDistanceReply.textContent='距离已生效，等待机器人确认保存…';
              }
              if(!kcfDistanceEdited){ui.kcfDistance.value=ui.kcfDistanceNumber.value=value;}
            }
            kcfSourceWidth=kcf.image_width||kcfSourceWidth;const labels={FOLLOW:'前进跟随',BACKOFF:'后退保持距离',HOLD:'距离合适，保持',ALIGN:'转向对准物体',WAIT_DEPTH:'等待有效深度',LOST:kcfStopReason==='template_mismatch'?'原目标模板不匹配，已停止并保留原目标':'等待框选目标'};
            ui.kcfReply.textContent=(color?'颜色跟随':marker?marker.toUpperCase()+' / KCF':kcf.tracker_backend==='nanotrack'?'NanoTrack':'KCF')+(kcf.tracking_runtime&&kcf.tracking_runtime!=='unknown'?' · '+kcf.tracking_runtime:'')+' · '+(color&&kcf.class_filter==='__click_target__'?'等待点击颜色检测框':(marker||color)&&kcf.motion_state==='LOST'?'等待识别目标':labels[kcf.motion_state]||kcf.motion_state)+' · ID '+(kcf.locked_id??'无')+(kcf.depth_m!=null?' · '+Number(kcf.depth_m).toFixed(2)+' m':'')+(kcf.enable_motion?' · 实机跟随':' · 识别演示，运动关闭');
          }
      }}catch(error){ui.kcfReply.textContent='追踪窗口错误：'+error.message;}finally{done();}
    };
    return ()=>{context.subscribe([]);context.unadvertise?.(CONTROL);context.unadvertise?.(KCF_ROI);if(color)context.unadvertise?.(COLOR_PICK);clearTimeout(pickTimer);sharedRgb?.removeEventListener('rgb-frame',syncRgb);context.onRender=undefined;el.remove();};
  }

  root.FoxgloveVision={initKcfPanel,updateRgb};
})(window);
