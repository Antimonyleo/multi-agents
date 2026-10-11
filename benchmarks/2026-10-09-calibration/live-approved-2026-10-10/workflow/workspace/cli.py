import argparse

def parse(args):
    p = argparse.ArgumentParser()
    p.add_argument('--retries', type=int)
    p.add_argument('--timeout-ms', type=int)
    p.add_argument('--driver', choices=['local', 'remote'], default='local')
    return p.parse_args(args)
