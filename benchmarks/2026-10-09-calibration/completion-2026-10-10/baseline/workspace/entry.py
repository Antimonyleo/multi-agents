import json
import sys
from coordinator import execute

if __name__ == '__main__':
    case = json.load(sys.stdin)
    print(json.dumps(execute(case['args'], case['env'])))
