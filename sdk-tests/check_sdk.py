"""Pinned official SDK/storage; mocked LLM, not network consensus."""
import json
from pathlib import Path
from gltest.direct import VMContext,deploy_contract
root=Path(__file__).resolve().parents[1];plan=json.loads((root/'examples/plan.json').read_text())
answer={'bounds':[{'id':i,'status':'KNOWN','lower':lo,'upper':hi,'reason':'The supplied rule explicitly sets these relative minute bounds.'} for i,(lo,hi) in enumerate([(30,60),(120,120),(None,200)])]}
vm=VMContext();vm.sender='0x'+'1'*40;vm.mock_llm('^Compile relative',json.dumps(answer))
with vm.activate():
 c=deploy_contract(root/'contracts/chrono_bound.py',vm,sdk_version='v0.3.0-rc7');c.seal('sdk',json.dumps(plan));r=json.loads(c.compile(str(vm.sender),'sdk'))
 assert r['status']=='FEASIBLE' and r['proof']['ranges']==[[0,0],[30,60],[150,180]]
 assert vm.run_validator() is True
 vm.clear_mocks();answer['bounds'][0]['lower']=31;vm.mock_llm('^Compile relative',json.dumps(answer));assert vm.run_validator() is False
 r=json.loads(c.certify(str(vm.sender),'sdk',r['digest']));assert r['status']=='CERTIFIED'
print('PASS: official SDK storage/calldata, temporal proof, validator acceptance/rejection and certification (mocked LLM).')
