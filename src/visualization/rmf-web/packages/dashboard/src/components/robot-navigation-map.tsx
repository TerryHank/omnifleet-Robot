import React from 'react';
import { Alert, Button, Stack, Typography } from '@mui/material';
import appConfig from '../app-config';

interface MapInfo { width: number; height: number; bounds: number[] | null; resolution: number; frame_id: string; origin: { x: number; y: number; yaw: number }; hash: string; message_count: number; age_seconds: number; error?: string; }
interface Pose { x: number; y: number; yaw: number; frame_id: string; }
interface RobotMapState { online: boolean; map: MapInfo | null; samples: { pose: { value: Pose; fresh: boolean } | null }; }

export function RobotNavigationMap() {
  const [robot, setRobot] = React.useState<RobotMapState | null>(null);
  const [connected, setConnected] = React.useState(false);
  const [zoom, setZoom] = React.useState(1);
  const [imageError, setImageError] = React.useState(false);
  React.useEffect(() => {
    const stream = new EventSource(`${appConfig.rmfServerUrl}/omnifleet/status/stream`);
    stream.onopen = () => setConnected(true);
    stream.onmessage = (event) => setRobot(JSON.parse(event.data).robots.find((r: { robot_id: string }) => r.robot_id === 'robot_104') ?? null);
    stream.onerror = () => setConnected(false);
    return () => stream.close();
  }, []);
  const map = robot?.map;
  const pose = robot?.samples.pose;
  React.useEffect(() => setImageError(false), [map?.hash]);
  if (!map || !map.width) return <Alert severity="info" sx={{ m: 2 }}>{map?.error || '正在等待 104 的真实导航栅格地图 /map。中央目前未提供 RMF 建筑地图。'}</Alert>;
  const matchingFrame = pose?.value.frame_id === map.frame_id;
  const dx = (pose?.value.x ?? 0) - map.origin.x;
  const dy = (pose?.value.y ?? 0) - map.origin.y;
  const c = Math.cos(map.origin.yaw), s = Math.sin(map.origin.yaw);
  const px = (c * dx + s * dy) / map.resolution;
  const py = map.height - (-s * dx + c * dy) / map.resolution;
  const bounds = map.bounds || [0, 0, map.width, map.height];
  const centerX = (bounds[0] + bounds[2]) / 2, centerY = (bounds[1] + bounds[3]) / 2;
  const width = Math.max(20, bounds[2] - bounds[0] + 20) / zoom;
  const height = Math.max(20, bounds[3] - bounds[1] + 20) / zoom;
  const view = `${centerX - width / 2} ${centerY - height / 2} ${width} ${height}`;
  const fresh = connected && robot?.online && pose?.fresh;
  const angle = -((pose?.value.yaw ?? 0) - map.origin.yaw) * 180 / Math.PI;
  return <div style={{ height: '90%', display: 'flex', flexDirection: 'column', padding: 8 }}>
    <Alert severity="info" sx={{ mb: 1 }}>104 实时导航地图 · 车辆坐标系 {map.frame_id}。这是原始导航栅格，非 RMF 建筑地图；仅供查看。</Alert>
    <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', mb: 1 }}>
      <Button size="small" onClick={() => setZoom((value) => Math.min(value * 1.5, 12))}>放大</Button>
      <Button size="small" onClick={() => setZoom((value) => Math.max(value / 1.5, 1))}>缩小</Button>
      <Button size="small" onClick={() => setZoom(1)}>适合地图</Button>
      <Typography variant="caption">{map.width} × {map.height} · {map.resolution.toFixed(2)} 米/格 · 地图消息 {map.message_count} · 最近 {map.age_seconds.toFixed(1)} 秒</Typography>
    </Stack>
    {imageError && <Alert severity="warning">地图图像读取失败，等待下一次更新。</Alert>}
    {!connected && <Alert severity="warning">实时通道已中断，当前显示上次收到的地图。</Alert>}
    {pose && !matchingFrame && <Alert severity="warning">位姿与地图坐标系不同，不叠加机器人位置。</Alert>}
    <svg role="img" aria-label="104 真实导航地图与当前位置" viewBox={view} style={{ flex: 1, width: '100%', minHeight: 240, background: '#cdd1d4' }}>
      <image href={`${appConfig.rmfServerUrl}/omnifleet/robots/robot_104/map.png?v=${map.hash}`} width={map.width} height={map.height} onError={() => setImageError(true)} style={{ imageRendering: 'pixelated' }} />
      {pose && matchingFrame && <g transform={`translate(${px} ${py}) rotate(${angle})`}>
        <circle r="4" fill={fresh ? '#d32f2f' : '#777'} stroke="white" strokeWidth="1" />
        <path d="M 4 -3 L 13 0 L 4 3 Z" fill={fresh ? '#d32f2f' : '#777'} stroke="white" strokeWidth="0.5" />
        <title>robot_104：{pose.value.x.toFixed(3)}, {pose.value.y.toFixed(3)} 米；{fresh ? '实时位姿' : '上次位姿，已过期'}</title>
      </g>}
    </svg>
    <Typography variant="caption">白色：空闲 · 黑色：占据 · 灰色：未知 · 红色箭头：104 位置与朝向。{pose && matchingFrame ? `坐标 (${pose.value.x.toFixed(3)}, ${pose.value.y.toFixed(3)}) 米；${fresh ? '实时' : '位姿过期'}` : ''}</Typography>
  </div>;
}
