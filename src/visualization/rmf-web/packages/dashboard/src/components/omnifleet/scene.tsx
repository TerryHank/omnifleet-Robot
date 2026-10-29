import React, { Suspense } from 'react';
import { SettingsContext } from '../app-contexts';
import { ThemeMode } from '../../settings';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { BufferGeometry, Float32BufferAttribute, Matrix4, Quaternion, Vector3, Euler, TextureLoader } from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import { ColladaLoader } from 'three/examples/jsm/loaders/ColladaLoader';
import { FleetState, operatorUrl, request } from './api';
import { useTopics } from './telemetry';

function origin(xyz: string | null, rpy: string | null) {
  const p = (xyz || '0 0 0').split(/\s+/).map(Number), r = (rpy || '0 0 0').split(/\s+/).map(Number);
  return new Matrix4().compose(new Vector3(p[0], p[1], p[2]), new Quaternion().setFromEuler(new Euler(r[0], r[1], r[2], 'ZYX')), new Vector3(1, 1, 1));
}
function frameMatrix(scene: any, frame: string): Matrix4 | null {
  const transforms = new Map<string, any>((scene?.transforms || []).map((t: any) => [t.child_frame_id.replace(/^\//, ''), t]));
  const seen = new Set<string>();
  const read = (key: string): Matrix4 | null => {
    key = key.replace(/^\//, '');
    if (key === 'map') return new Matrix4();
    if (seen.has(key)) return null; seen.add(key);
    const value = transforms.get(key) || Array.from(transforms.values()).find((t: any) => t.child_frame_id.endsWith('/' + key));
    if (!value) return null;
    const parent = read(value.header.frame_id); if (!parent) return null;
    const p = value.transform.translation, q = value.transform.rotation;
    return parent.multiply(new Matrix4().compose(new Vector3(p.x, p.y, p.z), new Quaternion(q.x, q.y, q.z, q.w), new Vector3(1, 1, 1)));
  };
  return read(frame);
}
function AssetMesh({ robot, uri, color }: { robot: string; uri: string; color: string }) {
  const [object, setObject] = React.useState<any>(null);
  React.useEffect(() => {
    let live = true;
    const url = `${operatorUrl}/asset/${encodeURIComponent(robot)}?uri=${encodeURIComponent(uri)}`;
    if (/\.dae$/i.test(uri)) new ColladaLoader().load(url, (result) => { if (live) setObject(result.scene); });
    else new STLLoader().load(url, (geometry) => { if (live) setObject(geometry); }, undefined, () => undefined);
    return () => { live = false; };
  }, [robot, uri]);
  if (!object) return null;
  return object.isBufferGeometry ? <mesh geometry={object}><meshStandardMaterial color={color} /></mesh> : <primitive object={object} />;
}
function Vehicle({ robot, scene }: { robot: string; scene: any }) {
  const visuals = React.useMemo(() => {
    if (!scene?.description) return [];
    const doc = new DOMParser().parseFromString(scene.description, 'text/xml');
    return Array.from(doc.querySelectorAll('link > visual')).map((visual) => {
      const link = visual.parentElement!.getAttribute('name')!, o = visual.querySelector('origin'), geom = visual.querySelector('geometry')?.firstElementChild;
      const rgba = visual.querySelector('material color')?.getAttribute('rgba')?.split(/\s+/).map(Number);
      return { link, origin: origin(o?.getAttribute('xyz') || null, o?.getAttribute('rpy') || null), kind: geom?.tagName, mesh: geom?.getAttribute('filename'), scale: geom?.getAttribute('scale')?.split(/\s+/).map(Number), size: geom?.getAttribute('size')?.split(/\s+/).map(Number), radius: Number(geom?.getAttribute('radius') || .1), length: Number(geom?.getAttribute('length') || .1), color: rgba ? `rgb(${rgba.slice(0, 3).map((n: number) => Math.round(n * 255)).join(',')})` : '#8bb4ca' };
    });
  }, [scene?.description]);
  const a = scene?.alignment || [0, 0, 0];
  return <group position={[a[0], a[1], 0]} rotation={[0, 0, a[2]]}>{visuals.map((v, index) => {
    const matrix = frameMatrix(scene, v.link); if (!matrix) return null; matrix.multiply(v.origin);
    return <group key={index} matrix={matrix} matrixAutoUpdate={false} scale={v.scale as [number, number, number] | undefined}>
      {v.mesh ? <AssetMesh robot={robot} uri={v.mesh} color={v.color} /> : <mesh rotation={v.kind === 'cylinder' ? [Math.PI / 2, 0, 0] : [0, 0, 0]}>
        {v.kind === 'box' ? <boxGeometry args={v.size as [number, number, number]} /> : v.kind === 'sphere' ? <sphereGeometry args={[v.radius]} /> : <cylinderGeometry args={[v.radius, v.radius, v.length]} />}
        <meshStandardMaterial color={v.color} />
      </mesh>}
    </group>;
  })}</group>;
}
function GridImage({ image, elevation = -.03 }: { image: any; elevation?: number }) {
  const [texture, setTexture] = React.useState<any>(null);
  React.useEffect(() => {
    if (!image?.png) return;
    const value = new TextureLoader().load(image.png); setTexture(value);
    return () => value.dispose();
  }, [image?.hash]);
  if (!texture || !image?.transform) return null;
  const a = image.transform, o = image.origin, width = image.width * image.resolution, height = image.height * image.resolution;
  return <group position={[a[0], a[1], elevation]} rotation={[0, 0, a[2]]}><group position={[o[0], o[1], 0]} rotation={[0, 0, o[2]]}><mesh position={[width / 2, height / 2, 0]}><planeGeometry args={[width, height]} /><meshBasicMaterial map={texture} transparent opacity={.85} /></mesh></group></group>;
}
export function Scene({ state, robot, image, overlay, cloud, onCloudChange }: { state: FleetState; robot: string; image: any; overlay?: any; cloud: boolean; onCloudChange: (value: boolean) => void }) {
  const { themeMode } = React.useContext(SettingsContext);
  const light = themeMode === ThemeMode.RmfLight;
  const [scenes, setScenes] = React.useState<Record<string, any>>({});
  const topics = state.robots[robot]?.graph?.topics || {};
  const cloudTopics = Object.keys(topics).filter((topic) => topics[topic].includes('sensor_msgs/msg/PointCloud2')).sort();
  const [selectedTopics, setSelectedTopics] = React.useState<Record<string, string>>({});
  const cloudTopic = cloudTopics.includes(selectedTopics[robot]) ? selectedTopics[robot] : cloudTopics.find((topic) => topic.endsWith('/rslidar_points')) || cloudTopics[0];
  const values = useTopics(state, robot, cloud && cloudTopic ? [cloudTopic] : []);
  React.useEffect(() => {
    let live = true;
    const load = async () => {
      const entries = await Promise.all(Object.keys(state.assignments).map(async (r) => [r, await request(`/scene/${r}`).catch(() => null)]));
      if (live) setScenes(Object.fromEntries(entries));
    };
    void load(); const timer = setInterval(() => void load(), 450);
    return () => { live = false; clearInterval(timer); };
  }, [state.identity_revision]);
  const received = cloudTopic ? values[cloudTopic] : null;
  const epoch = state.robots[robot]?.samples?.navigation?.value?.localization_epoch;
  const oldSession = received?.localization_epoch && received.localization_epoch !== epoch;
  const fresh = !oldSession && typeof received?.age_seconds === 'number' && received.age_seconds <= 2;
  const message = fresh ? received?.value : null;
  const points = React.useMemo(() => (message?.points || []).filter((p: any) => Array.isArray(p) && p.length === 3 && p.every(Number.isFinite)), [message]);
  const geometry = React.useMemo(() => {
    const value = new BufferGeometry();
    value.setAttribute('position', new Float32BufferAttribute(points.flat(), 3)); return value;
  }, [points]);
  React.useEffect(() => () => geometry.dispose(), [geometry]);
  const sharedFrame = message?.frame_id?.replace(/^\//, '') === 'fleet_map';
  const aligned = !!state.maps.transforms?.[robot];
  const cloudTransform = message && aligned ? sharedFrame ? new Matrix4() : frameMatrix(scenes[robot], message.frame_id) : null;
  const a = scenes[robot]?.alignment || [0, 0, 0];
  const cloudAlignment = sharedFrame ? [0, 0, 0] : state.maps.transforms?.[robot] || a;
  const status = !cloudTopic ? '尚未发现点云话题' : !cloud ? '按需订阅，开启后显示' : !state.robots[robot]?.online ? '车辆离线' : received?.error ? received.error : oldSession ? '定位会话已变化，等待新点云' : received?.value && !fresh ? '点云已过期，等待更新' : !message ? '正在订阅，等待点云' : !aligned ? '等待共享地图配准' : !cloudTransform ? `等待坐标变换：${message.frame_id}` : `${points.length} / ${message.original_points ?? points.length} 点 · ${received.age_seconds.toFixed(1)} 秒`;
  const center = state.maps.poses?.[robot] || [0, 0];
  return <div className="of-three"><div className="of-cloud-toggle"><label><input aria-label="启用三维点云" type="checkbox" checked={cloud} disabled={!cloudTopic} onChange={(e) => onCloudChange(e.target.checked)} /> {state.assignments[robot]?.robot_name} 点云</label><select aria-label="点云话题" disabled={!cloudTopics.length} value={cloudTopic || ''} onChange={(e) => setSelectedTopics({ ...selectedTopics, [robot]: e.target.value })}>{!cloudTopics.length && <option value="">暂无点云话题</option>}{cloudTopics.map((topic) => <option key={topic}>{topic}</option>)}</select><small data-testid="pointcloud-status" data-rendered-points={cloud && state.robots[robot]?.online && cloudTransform ? points.length : 0}>{status}</small></div>
    <Canvas camera={{ up: [0, 0, 1], position: [center[0] + 3, center[1] - 4, 6], fov: 48 }}><ambientLight intensity={1.5} /><directionalLight position={[2, -3, 6]} intensity={2} />
      <Suspense fallback={null}><GridImage image={image} /><GridImage image={overlay} elevation={-.02} />{Object.entries(scenes).filter(([, s]) => s).map(([r, s]) => <Vehicle key={r} robot={r} scene={s} />)}
        {cloud && state.robots[robot]?.online && message && cloudTransform && <group position={[cloudAlignment[0], cloudAlignment[1], 0]} rotation={[0, 0, cloudAlignment[2]]}><points geometry={geometry} matrix={cloudTransform} matrixAutoUpdate={false}><pointsMaterial color="#4bdfdf" size={.04} /></points></group>}
      </Suspense><gridHelper args={[30, 60, light ? '#9eb1c1' : '#234963', light ? '#c0ceda' : '#12324b']} rotation={[Math.PI / 2, 0, 0]} /><OrbitControls target={[center[0], center[1], 0]} makeDefault />
    </Canvas>
  </div>;
}
