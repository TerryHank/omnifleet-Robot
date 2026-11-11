function OmniFleetNavigationStrategy() {
  const service = (0,Je.A1)(state => state.callService);
  const [strategy, setStrategy] = (0,p.useState)('sequential');
  const [loaded, setLoaded] = (0,p.useState)(false);
  const [busy, setBusy] = (0,p.useState)(false);
  const [message, setMessage] = (0,p.useState)('正在读取执行策略……');
  async function request(name, value) {
    let timer;
    try {
      const response = await Promise.race([
        service('/omnifleet_t2/nav2/save_parameters', {parameters:[{name, value:{type:4, string_value:value}}]}),
        new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('策略服务超时')), 12000); })
      ]);
      const result = response.results?.[0];
      if (!result?.successful) throw new Error(result?.reason || '策略服务未确认');
      return JSON.parse(result.reason).strategy;
    } finally { clearTimeout(timer); }
  }
  (0,p.useEffect)(() => {
    let live = true, timer;
    const read = async () => {
      try {
        const value = await request('__navigation_strategy_status', '');
        if (live) { setStrategy(value); setLoaded(true); setMessage('策略已保存，下一次开始生效'); }
      } catch (error) { if (live) setMessage('策略读取失败：'+String(error)); }
      finally { if (live) timer = setTimeout(read, 5000); }
    };
    read();
    return () => { live = false; clearTimeout(timer); };
  }, [service]);
  const choose = async value => {
    if (busy) return;
    setBusy(true);
    try { setStrategy(await request('__navigation_strategy', value)); setMessage('已保存；当前任务保持原策略，下一次开始生效'); }
    catch (error) { setMessage('策略保存失败：'+String(error)); }
    finally { setBusy(false); }
  };
  return (0,n.jsxs)('div', {style:{margin:'8px 0'}, 'data-testid':'local-navigation-strategy', children:[
    (0,n.jsx)('b', {children:'多点执行策略'}),
    (0,n.jsx)('div', {style:{display:'flex',gap:8,margin:'6px 0'}, children:[['sequential','逐点到达（默认）'],['through_poses','连续途经']].map(([value,label]) => (0,n.jsx)('button', {
      type:'button', 'data-navigation-strategy':value, 'aria-pressed':strategy===value,
      disabled:busy||!loaded, onClick:()=>choose(value),
      style:{padding:'7px 10px',borderRadius:6,border:strategy===value?'2px solid #478ae5':'1px solid #8793a3',background:strategy===value?'#d8eaff':'transparent',color:strategy===value?'#14273e':'inherit'}, children:label
    },value))}),
    (0,n.jsx)('small', {children:'逐点：到达并停稳后执行下一点。连续：整路规划，中间途经点不要求停车。途经／停靠类型用于连续模式，逐点模式每点均停稳。'}),
    (0,n.jsx)('div', {'data-testid':'local-navigation-strategy-status', style:{fontSize:12,marginTop:4}, children:message})
  ]});
}
