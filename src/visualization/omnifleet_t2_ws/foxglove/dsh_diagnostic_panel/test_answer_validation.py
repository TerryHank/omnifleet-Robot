import io,json
import pytest
import dsh_runner as runner
from test_timing import sample

def fake_process(text):
 class Process:
  pid=1;returncode=0
  stdout=io.BytesIO(text.encode());stderr=io.BytesIO(b'')
  def wait(self,timeout):return 0
 return Process()

def test_preparatory_message_is_not_a_completed_diagnosis(monkeypatch):
 monkeypatch.setattr(runner.subprocess,'Popen',lambda *a,**k:fake_process(json.dumps({'answer':'我先检查一下。','parameter_actions':[]})))
 with pytest.raises(RuntimeError,match='完整'):
  runner.ask_dsh('当前状态',sample(),_format_retry=False)

def test_structured_answer_is_preserved(monkeypatch):
 answer='发现的问题\n- 数据不足\n\n判断依据\n- 没有运行样本\n\n处理步骤\n1. 保持停车。'
 monkeypatch.setattr(runner.subprocess,'Popen',lambda *a,**k:fake_process(json.dumps({'answer':answer,'parameter_actions':[]})))
 assert runner.ask_dsh('当前状态',sample(),_format_retry=False)['answer']==answer
