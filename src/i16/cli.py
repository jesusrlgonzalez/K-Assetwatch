"""CLI for offline synthetic smoke tests and documentary gates."""
import argparse,json
from .demo import run_demo
from .gates import inspect_gate,GATES

def main(argv=None):
    parser=argparse.ArgumentParser(prog='i16')
    sub=parser.add_subparsers(dest='command',required=True)
    d=sub.add_parser('demo');d.add_argument('--out',default='outputs/demo')
    g=sub.add_parser('gate');g.add_argument('--root',default='.');g.add_argument('--gate',choices=GATES,required=True)
    args=parser.parse_args(argv)
    if args.command=='demo':
        r=run_demo(args.out);print(json.dumps(r,indent=2));return 0
    r=inspect_gate(args.root,args.gate);print(json.dumps(r,indent=2));return 0 if r['status']=='DOCUMENTS_VERIFIED_REVIEW_REQUIRED' else 2

if __name__=='__main__':
    raise SystemExit(main())
