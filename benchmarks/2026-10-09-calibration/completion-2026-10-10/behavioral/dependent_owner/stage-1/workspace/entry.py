import json, sys
from source import resolve
from driver import dispatch
from summary import mean
c = json.load(sys.stdin)
try:
    result = {"dispatch": dispatch(resolve(c["opts"], c["env"])), "mean": mean(c["readings"])}
except ValueError:
    result = {"error": "empty_readings"}
print(json.dumps(result))
