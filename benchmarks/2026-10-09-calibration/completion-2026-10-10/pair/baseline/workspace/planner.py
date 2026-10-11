from sources import load
from validation import validate

def make_plan(opts, env):
    return validate(load(opts, env))
