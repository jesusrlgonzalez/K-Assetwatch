import tempfile,json,unittest,hashlib
from pathlib import Path
from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from i16.demo import run_demo
from i16.gates import inspect_gate

class TestDemoAndGates(unittest.TestCase):
    def test_demo_rebuild_byteidentical(self):
        with tempfile.TemporaryDirectory() as p:
            a=run_demo(Path(p)/'a')
            b=run_demo(Path(p)/'b')
            self.assertEqual(a,b)
            self.assertEqual((Path(p)/'a/report.json').read_bytes(),(Path(p)/'b/report.json').read_bytes())
    def test_gate_missing_stays_blocked(self):
        with tempfile.TemporaryDirectory() as p:
            self.assertEqual(inspect_gate(p,'G1')['status'],'BLOCKED')
    def test_gate_rejects_self_review(self):
        with tempfile.TemporaryDirectory() as p:
            r=Path(p);d=r/'EVIDENCIAS'/'G1';d.mkdir(parents=True)
            proof=d/'run.json';proof.write_text('{"proof":true}')
            (d/'approval.json').write_text(json.dumps({'gate':'G1','decision':'PASS','implementer_id':'same','reviewer_id':'same','evidence_path':'EVIDENCIAS/G1/run.json','sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'signed_at_utc':'2025-01-01T00:00:00Z'}))
            self.assertEqual(inspect_gate(r,'G1')['status'],'BLOCKED')
    def test_gate_rejects_bad_hash(self):
        with tempfile.TemporaryDirectory() as p:
            r=Path(p);d=r/'EVIDENCIAS'/'G2';d.mkdir(parents=True)
            proof=d/'run.json';proof.write_text('{"proof":true}')
            (d/'approval.json').write_text(json.dumps({'gate':'G2','decision':'PASS','implementer_id':'dev','reviewer_id':'aud','evidence_path':'EVIDENCIAS/G2/run.json','sha256':'0'*64,'signed_at_utc':'2025-01-01T00:00:00Z'}))
            self.assertEqual(inspect_gate(r,'G2')['status'],'BLOCKED')
    def test_gate_valid_doc_never_auto_certifies(self):
        with tempfile.TemporaryDirectory() as p:
            r=Path(p);d=r/'EVIDENCIAS'/'G3';d.mkdir(parents=True)
            proof=d/'run.json';proof.write_text('{"proof":true}')
            (d/'approval.json').write_text(json.dumps({'gate':'G3','decision':'PASS','implementer_id':'dev','reviewer_id':'aud','evidence_path':'EVIDENCIAS/G3/run.json','sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'signed_at_utc':'2025-01-01T00:00:00Z'}))
            self.assertEqual(inspect_gate(r,'G3')['status'],'DOCUMENTS_VERIFIED_REVIEW_REQUIRED')

if __name__=='__main__':unittest.main()
