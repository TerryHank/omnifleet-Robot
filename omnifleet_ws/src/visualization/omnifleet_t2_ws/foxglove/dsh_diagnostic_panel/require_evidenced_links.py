from pathlib import Path
import shutil
p=Path(__file__).with_name('DshDiagnosticPanel.js')
b=Path('/home/iecme/robot_backups/dsh_parameter_guidance_20260907');b.mkdir(exist_ok=True)
shutil.copy2(p,b/p.name)
s=p.read_text()
old="              const button = document.createElement('button'); button.textContent = '定位：'+(result.parameter_labels?.[id] || id);"
new="""              const action = (result.parameter_actions || []).find(a => a.id === id && ['inspect','adjust'].includes(a.intent));
              if (!action) continue;
              const button = document.createElement('button'); button.textContent = (action.intent === 'adjust' ? '建议检查：' : '查看：')+(result.parameter_labels?.[id] || id);
              button.title = action.reason || '';"""
assert old in s
p.write_text(s.replace(old,new,1))
print('UI now requires a validated action, and distinguishes viewing from a configuration suggestion')
