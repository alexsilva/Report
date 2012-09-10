"""
Tools for debugging python applications
"""
from StringIO import StringIO
import inspect

__all__ = ('stack_trace', 'middleware')

def stack_trace(depth=None):
    """
    returns a print friendly stack trace at the current frame,
    without aborting the application.
    
    :param depth: The depth of the stack trace. if omitted, the entire
        stack will be printed.
    
    usage::
    
        print stack_trace(10)
    """
    frames = inspect.stack()[2:]
    if depth:
        frames = frames[:depth]
        
    result = StringIO()
    result.write("----------------------------------------------------\n")
    for (frame, file, line, context, code, status) in frames:
        result.write("In %s from %s\n%s %s" % (context, file, line, "\n".join(code)))
        result.write("----------------------------------------------------\n")        
    return result.getvalue()
