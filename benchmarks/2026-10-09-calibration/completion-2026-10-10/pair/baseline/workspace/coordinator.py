import local_driver
import remote_driver
from cli import parse
from planner import make_plan

def execute(args, env):
    try:
        plan = make_plan(parse(args), env)
        driver = remote_driver if plan['driver'] == 'remote' else local_driver
        actual = driver.dispatch(plan)
        return {'retries': actual['retries'], 'timeout_ms': plan['timeout_ms'],
                'client_timeout_ms': actual['client_timeout_ms'], 'error': None}
    except ValueError as exc:
        message = str(exc)
        error = message if message in ('retries_range', 'timeout_range') else 'integer_parse'
        return {'retries': None, 'timeout_ms': None, 'client_timeout_ms': None, 'error': error}
