"""Deployable source under a mocked host and model. Not network consensus."""
import importlib.util,itertools,json,sys,types,unittest
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1];A='0x'+'1'*40;B='0x'+'2'*40;C='0x'+'3'*40;D='0x'+'4'*40
class Return:
 def __init__(self,x):self.calldata=x
class Public:
 write=staticmethod(lambda f:f);view=staticmethod(lambda f:f)
gl=types.SimpleNamespace(Contract=object,public=Public(),message=types.SimpleNamespace(sender_address=A),vm=types.SimpleNamespace(Return=Return,UserError=ValueError),nondet=types.SimpleNamespace())
sys.modules['genlayer']=types.SimpleNamespace(gl=gl,TreeMap=dict)
spec=importlib.util.spec_from_file_location('p',ROOT/'contracts/chrono_bound.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
EX=json.loads((ROOT/'examples/plan.json').read_text())
def answer():return {'bounds':[{'id':i,'status':'KNOWN','lower':lo,'upper':hi,'reason':'The supplied rule explicitly sets these relative minute bounds.'} for i,(lo,hi) in enumerate([(30,60),(120,120),(None,200)])]}
class Tests(unittest.TestCase):
 def setUp(self):
  gl.message.sender_address=A;self.c=p.ChronoBound();self.answer=answer();self.second=None;self.calls=0
  def llm(*a,**kw):self.calls+=1;return self.second if self.calls>1 and self.second is not None else self.answer
  gl.nondet.exec_prompt=llm
  def run(l,v):
   x=l()
   if not v(Return(x)):raise ValueError('DISAGREE')
   return x
  gl.vm.run_nondet_unsafe=run;self.c.seal('s',json.dumps(EX))
 def test_lifecycle_certificate(self):
  r=json.loads(self.c.compile(A,'s'));self.assertEqual(r['status'],'FEASIBLE');self.assertEqual(r['proof']['ranges'],[[0,0],[30,60],[150,180]])
  r=json.loads(self.c.certify(A,'s',r['digest']));self.assertEqual(r['status'],'CERTIFIED')
 def test_negative_cycle_witness(self):
  self.answer['bounds'][2]['upper']=100;r=json.loads(self.c.compile(A,'s'));pr=r['proof'];self.assertEqual(r['status'],'INCONSISTENT');self.assertLess(pr['cycle_weight'],0)
  self.assertEqual(sum(pr['edges'][i]['weight'] for i in pr['cycle']),pr['cycle_weight'])
  with self.assertRaisesRegex(ValueError,'NOT_FEASIBLE'):self.c.certify(A,'s',r['digest'])
 def test_unclear_blocks_certificate(self):
  self.answer['bounds'][0].update(status='UNCLEAR',lower=None,upper=None);r=json.loads(self.c.compile(A,'s'));self.assertEqual(r['status'],'REVIEW');self.assertEqual(r['proof']['times'],[])
 def test_disagreement_preserves_sealed(self):
  self.second=answer();self.second['bounds'][0]['lower']=31
  with self.assertRaisesRegex(ValueError,'DISAGREE'):self.c.compile(A,'s')
  self.assertEqual(json.loads(self.c.get_schedule(A,'s'))['status'],'SEALED')
 def test_permissionless_compile_owner_certify(self):
  gl.message.sender_address=B;r=json.loads(self.c.compile(A,'s'))
  with self.assertRaisesRegex(ValueError,'NOT_OWNER'):self.c.certify(A,'s',r['digest'])
 def test_bad_digest(self):
  self.c.compile(A,'s')
  with self.assertRaisesRegex(ValueError,'CERTIFICATE_MISMATCH'):self.c.certify(A,'s','forged')
 def test_no_overwrite_or_recompile(self):
  with self.assertRaisesRegex(ValueError,'ID_USED'):self.c.seal('s',json.dumps(EX))
  self.c.compile(A,'s')
  with self.assertRaisesRegex(ValueError,'ALREADY_COMPILED'):self.c.compile(A,'s')
 def test_no_recertify(self):
  r=json.loads(self.c.compile(A,'s'));self.c.certify(A,'s',r['digest'])
  with self.assertRaisesRegex(ValueError,'NOT_FEASIBLE'):self.c.certify(A,'s',r['digest'])
 def test_malformed_semantics(self):
  plan=p.parse_plan(json.dumps(EX))
  for x in [{'bounds':answer()['bounds'][:-1]},{'bounds':list(reversed(answer()['bounds']))}]:
   with self.assertRaises(ValueError):p.canonical(x,plan)
  x=answer();x['bounds'][0]['lower']=True
  with self.assertRaises(ValueError):p.canonical(x,plan)
 def test_bad_plan(self):
  for change in [{'horizon':True},{'events':['Start','Start']},{'rules':[{'from':0,'to':0,'text':'An impossible self reference rule.'}]}]:
   with self.assertRaises(ValueError):p.parse_plan(json.dumps({**EX,**change}))
 def test_temporal_solver_against_bruteforce(self):
  # 729 networks, independently enumerate every integral assignment in a 4-minute horizon.
  plan={'events':['Origin','Alpha','Beta'],'horizon':4,'rules':[{'id':i,'from':a,'to':b,'text':'Explicit test constraint.'} for i,(a,b) in enumerate([(0,1),(1,2),(0,2)])]}
  possibilities=[(None,0),(None,2),(0,None),(2,None),(1,1),(3,1),(None,-1),(1,3),(None,4)]
  for settings in itertools.product(possibilities,repeat=3):
   bounds=[{'status':'KNOWN','lower':lo,'upper':hi} for lo,hi in settings]
   feasible=[]
   for a,b in itertools.product(range(5),repeat=2):
    times=[0,a,b]
    if all((v['lower'] is None or times[r['to']]-times[r['from']]>=v['lower']) and (v['upper'] is None or times[r['to']]-times[r['from']]<=v['upper']) for r,v in zip(plan['rules'],bounds)):feasible.append(times)
   result=p.solve(plan,bounds);self.assertEqual(result['status']=='FEASIBLE',bool(feasible))
   if feasible:
    self.assertIn(result['times'],feasible);self.assertEqual(result['ranges'],[[min(t[i] for t in feasible),max(t[i] for t in feasible)] for i in range(3)])
   else:self.assertLess(result['cycle_weight'],0)
if __name__=='__main__':unittest.main()
