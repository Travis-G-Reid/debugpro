import sys
import functools
import inspect
import pandas as pd
from debugpro.excepthook import install_custom_excepthook
install_custom_excepthook()
__all__ = ["trace_var"]


def trace_var(variable_name):
    """Decorator that tracks changes to a specific variable within a function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Store the original value to detect changes
            traced_var_value = None
            traced_var_initialized = False
            last_line_executed = None
            source_lines = inspect.getsourcelines(func)[0]
            first_line_no = func.__code__.co_firstlineno
            
            def trace_function(frame, event, arg):
                nonlocal traced_var_value, traced_var_initialized, last_line_executed
                
                # Track when the variable is accessed or modified
                if event == 'line':
                    # Record the current line before it executes
                    last_line_executed = frame.f_lineno
                    return after_line_execution
                elif event == 'return':
                    # Check if our variable is being returned
                    local_vars = frame.f_locals
                    if variable_name in local_vars and local_vars[variable_name] == arg:
                        line_no = last_line_executed
                        source_line = source_lines[line_no - first_line_no].strip()
                        print(f"Line {line_no}: {variable_name} returned with value {arg} ({source_line})")
                
                return trace_function
            
            def after_line_execution(frame, event, arg):
                nonlocal traced_var_value, traced_var_initialized, last_line_executed
                
                # Check if our variable exists in local scope
                local_vars = frame.f_locals
                if variable_name in local_vars:
                    current_value = local_vars[variable_name]
                    
                    # Track initialization and modifications
                    if not traced_var_initialized:
                        line_no = last_line_executed
                        source_line = source_lines[line_no - first_line_no].strip()
                        print(f"Line {line_no}: {variable_name} initialized to {current_value} ({source_line})")
                        traced_var_value = current_value
                        traced_var_initialized = True
                    elif traced_var_value != current_value:
                        # Value has changed
                        line_no = last_line_executed
                        print(line_no - first_line_no)
                        source_line = source_lines[line_no - first_line_no].strip()
                        print(f"Line {line_no}: {variable_name} changed from {traced_var_value} to {current_value} ({source_line})")
                        traced_var_value = current_value
                
                # Also track when variable is accessed but not modified
                code_object = frame.f_code
                if event == 'opcode' and variable_name in frame.f_locals:
                    # This additional check would require Python 3.11+ with the opcode event
                    pass
                
                return trace_function
            
            # Set the trace function and execute
            sys.settrace(trace_function)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                sys.settrace(None)  # Always restore trace function
                
        return wrapper
    return decorator


@trace_var("counter")
def test_function():
    counter = 0
    for i in range(5):
        counter += i

    counter += 9 # Why isn't this getting logged? Is it optimized out?
    counter = {'a': 'b', 'c': 'd'}
    if counter.get('a', None) != None:
        counter = 0
    counter = pd.DataFrame(data={'3': 3, 2: 1})
    return counter


if __name__ == "__main__":
    test_function()
