import React from 'react';
import { FleetState } from './api';

export function SharedCostmapSettings({ state, busy, act }: { state: FleetState; busy: boolean; act: (op: string, fields?: Record<string, unknown>) => Promise<any>; }) {
  const config = state.maps.shared_costmap;
  const [values, setValues] = React.useState<Record<string, string>>({});
  const [revision, setRevision] = React.useState<number | undefined>();
  React.useEffect(() => {
    if (config && (revision === undefined || config.revision > revision)) {
      setValues(Object.fromEntries(Object.entries(config.parameters).map(([key, value]) => [key, String(value)])));
      setRevision(config.revision);
    }
  }, [config, revision]);
  const save = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (Array.from(event.currentTarget.closest('details')!.querySelectorAll('input')).some((input) => !input.reportValidity())) return;
    void act('shared_costmap_configure', { shared_costmap_revision: revision, parameters: Object.fromEntries(Object.entries(values).map(([key, value]) => [key, Number(value)])) }).then((result) => {
      if (result?.phase === 'saved') setRevision(result.shared_costmap_revision);
    });
  };
  return <details className="of-section-body" aria-label="WSL共享代价参数"><summary>WSL 共享代价地图参数</summary>
    <p>首次复制 car1，之后由 WSL 独立保存。共享图包含所有车辆；修改这里不修改车端导航参数。实际行驶规划仍由各车 Nav2 执行。</p>
    <div className="of-traffic-fields">{(config?.fields || []).map((field: any) => <label key={field.id}>{field.label}<input aria-label={`共享${field.label}`} type="number" required disabled={busy} min={field.min} max={field.max} step={field.step} value={values[field.id] ?? ''} onChange={(e) => setValues({ ...values, [field.id]: e.target.value })} /></label>)}
      <button disabled={busy || !config} onClick={save}>保存共享代价参数到 WSL</button>
    </div><p className="of-muted">独立共享层：{config?.ready ? '已生成' : '等待地图'} · 车辆占用区与车体膨胀半径是不同参数。</p>
  </details>;
}
