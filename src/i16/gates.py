"""Hash-and-separation gate admission check, not an auditor substitute."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re

GATES=['G0','G1','G2','G3','G4','G5_TECH','G5_BUSINESS']

def inspect_gate(root, gate):
    if gate not in GATES:
        raise ValueError('Invalid gate')
    root=Path(root).resolve()
    path=root/'EVIDENCIAS'/gate/'approval.json'
    if not path.is_file():
        return {'gate':gate,'status':'BLOCKED','reason':'missing_independent_approval'}
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        needed=['gate','decision','implementer_id','reviewer_id','evidence_path','sha256','signed_at_utc']
        if any(not data.get(k) for k in needed):
            raise ValueError('missing required approval fields')
        if data['gate']!=gate or data['decision']!='PASS':
            raise ValueError('not an approved gate')
        if data['reviewer_id']==data['implementer_id']:
            raise ValueError('self review forbidden')
        rel=Path(data['evidence_path'])
        target=(root/rel).resolve()
        if not target.is_relative_to((root/'EVIDENCIAS').resolve()) or not target.is_file() or target==path:
            raise ValueError('evidence must exist inside EVIDENCIAS and differ from approval')
        if not re.fullmatch(r'[a-fA-F0-9]{64}',data['sha256']):
            raise ValueError('invalid sha256 format')
        if hashlib.sha256(target.read_bytes()).hexdigest()!=data['sha256'].lower():
            raise ValueError('evidence digest mismatch')
        signed=datetime.fromisoformat(data['signed_at_utc'].replace('Z','+00:00'))
        if signed.tzinfo is None:
            raise ValueError('UTC signature timestamp required')
        if signed.astimezone(timezone.utc)>datetime.now(timezone.utc):
            raise ValueError('signature from future')
        # A positive check is solely DOCUMENTARY and still requires audit judgment.
        return {'gate':gate,'status':'DOCUMENTS_VERIFIED_REVIEW_REQUIRED','reason':'approval_document_and_digest_valid_but_external_audit_not_confirmed'}
    except (ValueError,OSError,TypeError,KeyError,json.JSONDecodeError) as ex:
        return {'gate':gate,'status':'BLOCKED','reason':f'invalid_approval:{ex}'}
