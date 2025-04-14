import sys
import os
import traceback
import linecache
import pathlib
import platform
import inspect
from types import FrameType, TracebackType
from typing import Dict, Any, Type, Optional, Tuple


__all__ = ["install_custom_excepthook"]


def _get_frame_info(frame: FrameType) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Extract and categorize local variables from a frame."""
    modules = {}
    functions = {}
    variables = {}

    for name, val in frame.f_locals.items():
        if name.startswith('__'):
            continue
            
        try:
            repr_val = repr(val)
            if repr_val.startswith('<module'):
                modules[name] = repr_val
            elif repr_val.startswith('<function') or repr_val.startswith('<bound method'):
                functions[name] = repr_val
            else:
                variables[name] = repr_val
        except Exception as e:
            variables[name] = f"<unprintable: {e}>"
            
    return modules, functions, variables


def _print_frame_info(frame: FrameType, filename: str, lineno: int, line: str, **kwargs):
    """Print detailed information about the frame where the exception occurred."""
    modules, functions, variables = _get_frame_info(frame)
    
    # Print modules
    print("\n------ Modules ------")
    if modules:
        for name, val in modules.items():
            print(name)
    else:
        print("  None")
        
    # Print functions
    print("\n------ Functions ------")
    if functions:
        for name, val in functions.items():
            print(name)
    else:
        print("  None")

    # Print system info
    print("\n------ System Info ------")
    print(f"Python version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Current working directory: {pathlib.Path.cwd()}")
    
    # Print accessible import paths
    print("\n------ Python Path ------")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")

    # Print all accessible variables 
    print("\n------ Variables ------")
    if variables:
        for name, val in sorted(variables.items()):
            if len(val) > 500:
                val = val[:500]
            print(f"{name} = {val}")
    else:
        print("  None")


def _print_code_context(filename: str, lineno: int, **kwargs):
    """Print code context around the error line.
    
    Example:
    
    ------ Code Context ------
    2:
    3: def test_AttributeError():
    4:     my_dict = {'a': 1, 'b': 2, 'c': 3}
    → 5:     my_dict[5]
    6:
    7: if __name__ == "__main__":
    8:     install_custom_excepthook()
    ... (1 more lines below)
    
    """
    RED = "\033[31m"
    RESET = "\033[0m"

    # Count total lines in file
    line_count = 0
    while linecache.getline(filename, line_count + 1):
        line_count += 1
    
    # Define context window (lines before and after error)
    context_lines = 3
    start_line = max(1, lineno - context_lines)
    end_line = min(line_count, lineno + context_lines)
    
    print("\n------ Code Context ------")
    if start_line <= 1:
        print("   -- start of file --")
        
    for i in range(start_line, end_line + 1):
        context_line = linecache.getline(filename, i)
        if context_line:  # Only print if the line exists
            prefix = "→ " if i == lineno else "  "
            # Apply color to the error line
            if i == lineno:
                print(f"{prefix}{i}: {RED}{context_line.rstrip()}{RESET}")
            else:
                print(f"{prefix}{i}: {context_line.rstrip()}")
    
    # Check if there are more lines after our context window
    if end_line < line_count:
        lines_below = line_count - end_line
        print(f"   ... ({lines_below} more lines below)")
    else:
        print("  --- End of file ---")


def _print_stack_frames(exc_traceback, **kwargs):
    """ Prints the stack trace. Example:

    ------ Stack Trace ------
    1. test_AttributeError in ...\tests\attributeerror.py:5
    2. __main__ in ...\tests\attributeerror.py:9

    """
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"{BOLD}------ Stack Trace ------{RESET}")
    tb = exc_traceback
    stack = []
    while tb:
        stack.append((tb.tb_frame, tb.tb_lineno))
        tb = tb.tb_next
        
    for i, (frame, lineno) in enumerate(reversed(stack), 1):
        filename = frame.f_code.co_filename
        name = frame.f_code.co_name
        if name == '<module>':
            name = '__main__'
            
        # Shorten path for display
        file_path_parts = filename.split(os.sep)
        if len(file_path_parts) > 2:
            shortened_path = os.path.join('...', *file_path_parts[-2:])
        else:
            shortened_path = filename
        print(f"{i}. {CYAN}{name}{RESET} in {shortened_path}:{lineno}")


def _print_file_location(filename, lineno, **kwargs):
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    file_path_parts = filename.split(os.sep)
    if len(file_path_parts) > 2:
        shortened_path = os.path.join('...', *file_path_parts[-2:])
    else:
        shortened_path = filename
    print(f"\n{YELLOW}Location: {CYAN}{shortened_path}{RESET}, line {BOLD}{lineno}{RESET}")


def _print_exception_header(exc_type, exc_value, **kwargs):
    RED = "\033[31m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"\n{BOLD}{RED}{'=' * 60}{RESET}")
    print(f"{BOLD}{RED}ERROR: {exc_type.__name__}: {exc_value}{RESET}")
    print(f"{BOLD}{RED}{'=' * 60}{RESET}")


def _print_exception_details(exception_details, exc_type, exc_value, line, **kwargs):
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"\n{BOLD}{RED}------ {exception_details.get('type', exc_type.__name__)} Details ------{RESET}")
    if "dictionary" in exception_details:
        print(f"{YELLOW}Dictionary:{RESET} {exception_details['dictionary']} = {exception_details['dict_value']}")
        print(f"{YELLOW}Missing key:{RESET} {exception_details['missing_key']}")
        print(f"{YELLOW}Available keys:{RESET} {exception_details['available_keys']}")
        if "similar_keys" in exception_details:
            print(f"{YELLOW}Possible similar keys:{RESET} {exception_details['similar_keys']}")
    
    elif "collection" in exception_details:
        print(f"{YELLOW}Collection:{RESET} {exception_details['collection']} = {exception_details['collection_value']}")
        if "length" in exception_details:
            print(f"{YELLOW}Length:{RESET} {exception_details['length']}")
        if "valid_indices" in exception_details:
            print(f"{YELLOW}Valid indices:{RESET} {exception_details['valid_indices']}")
        try:
            bad_idx = line.split('[')[1].split(']')[0]
            print(f"{YELLOW}Invalid index:{RESET} {bad_idx}")
        except:
            print(f"{YELLOW}Invalid index: Unparseable{RESET}")
            pass
    
    elif "object" in exception_details:
        print(f"{YELLOW}Object:{RESET} {exception_details['object']} = {exception_details['object_value']}")
        print(f"{YELLOW}Type:{RESET} {exception_details['object_type']}")
        if "available_attributes" in exception_details:
            attrs_display = ", ".join(exception_details['available_attributes'])
            print(f"{YELLOW}Available attributes:{RESET} {attrs_display}")
            if exception_details.get('attributes_count', 0) > 100:
                print(f"  ... and {exception_details['attributes_count'] - 100} more")
        if "similar_attributes" in exception_details:
            print(f"{YELLOW}Possible similar attributes:{RESET} {exception_details['similar_attributes']}")
        
        print(f"{YELLOW}Missing Attribute:{RESET}{exc_value}")
    
    elif "undefined_variable" in exception_details:
        print(f"{YELLOW}Undefined variable:{RESET} '{exception_details['undefined_variable']}'")
        if "similar_variables" in exception_details:
            print(f"{YELLOW}Similar variable names:{RESET} {exception_details['similar_variables']}")


def _get_exception_details_KeyError(exc_value, frame, line, **kwargs):
    culprit_var = None
    exception_details = {}
    for name, val in frame.f_locals.items():
        if isinstance(val, dict) and line and name in line:
            try:
                key_str = str(exc_value).strip("'\"")
                culprit_var = name
                exception_details["type"] = "KeyError"
                exception_details["dictionary"] = name
                exception_details["dict_value"] = repr(val)
                exception_details["missing_key"] = repr(key_str)
                exception_details["available_keys"] = list(val.keys())
                
                # Suggest similar keys if any
                similar_keys = [k for k in val.keys() if str(k) and key_str and 
                                (str(k) in str(key_str) or str(key_str) in str(k))]
                if similar_keys:
                    exception_details["similar_keys"] = similar_keys
                break
            except Exception as e:
                print(f"Error analyzing dictionary: {e}")
    return exception_details


def _get_exception_details_IndexError_TypeError(frame, line, exc_type, **kwargs):
    exception_details = {}
    var_name = None
    for name, val in frame.f_locals.items():
        if hasattr(val, '__len__') and name in line:
            try:
                exception_details["type"] = "IndexError" if issubclass(exc_type, IndexError) else "TypeError"
                exception_details["collection"] = name
                exception_details["collection_value"] = repr(val)
                if hasattr(val, '__len__'):
                    exception_details["length"] = len(val)
                if isinstance(val, (list, tuple)):
                    exception_details["valid_indices"] = f"0 to {len(val)-1 if len(val) > 0 else 'N/A (empty)'}"
                break
            except Exception as e:
                print(f"Error analyzing collection: {e}")

    return exception_details


def _get_exception_details_AttributeError(exc_value, frame, line, **kwargs):
    exception_details = {}
    attr_name = str(exc_value).split("'")[1] if "'" in str(exc_value) else None
    if attr_name:
        for name, val in frame.f_locals.items():
            if name in line:
                try:
                    exception_details["type"] = "AttributeError"
                    exception_details["object"] = name
                    exception_details["object_value"] = repr(val)
                    exception_details["object_type"] = type(val).__name__
                    exception_details["missing_attribute"] = attr_name
                    
                    # List available attributes
                    attrs = [attr for attr in dir(val) if not attr.startswith('__')]
                    if attrs:
                        exception_details["available_attributes"] = attrs[:100]
                        if len(attrs) > 20:
                            exception_details["attributes_count"] = len(attrs)
                        
                        # Suggest similar attributes
                        similar_attrs = [a for a in attrs if attr_name in a or a in attr_name]
                        if similar_attrs:
                            exception_details["similar_attributes"] = similar_attrs

                    break
                except Exception as e:
                    print(f"Error analyzing object: {e}")

    return exception_details


def _get_exception_details_NameError(exc_value, frame, **kwargs):
    exception_details = {}
    var_name = str(exc_value).split("'")[1] if "'" in str(exc_value) else None
    if var_name:
        exception_details["type"] = "NameError"
        exception_details["undefined_variable"] = var_name
        
        # Suggest similar variables
        similar_vars = [name for name in frame.f_locals.keys() 
                        if var_name in name or name in var_name]
        if similar_vars:
            exception_details["similar_variables"] = similar_vars

    return exception_details


def _get_exception_details(exc_type, exc_value, frame, **kwargs):
    if issubclass(exc_type, KeyError):
        return _get_exception_details_KeyError(**locals(), **kwargs)
    elif issubclass(exc_type, (IndexError, TypeError)):
        return _get_exception_details_IndexError_TypeError(**locals(), **kwargs)
    elif issubclass(exc_type, AttributeError):
        return _get_exception_details_AttributeError(**locals(), **kwargs)
    elif issubclass(exc_type, NameError):
        return _get_exception_details_NameError(**locals(), **kwargs)


def _custom_excepthook(exc_type: Type[BaseException], 
                     exc_value: BaseException, 
                     exc_traceback: Optional[TracebackType]):
    """Enhanced exception hook that provides detailed debugging information."""
    # Note: As per python convention, `tb` indicates "traceback" and
    #  `co` indicates "code object", a Python interpreter-related code object

    # Get the last frame where the exception occurred
    tb: TracebackType | None = exc_traceback
    while tb and tb.tb_next:
        tb = tb.tb_next
    
    if tb:
        frame: FrameType = tb.tb_frame
        filename: str = frame.f_code.co_filename
        lineno = tb.tb_lineno
        line = linecache.getline(filename, lineno).strip()

        kwargs = {
            'frame': frame,
            'filename': filename,
            'lineno': lineno,
            'line': line,
            'exc_type': exc_type,
            'exc_value': exc_value,
            'exc_traceback': exc_traceback
        }
        
        _print_exception_header(**kwargs)
        _print_frame_info(**kwargs)
        _print_file_location(**kwargs)
        _print_stack_frames(**kwargs)
        _print_code_context(**kwargs)
        exception_details = _get_exception_details(**kwargs)

        if exception_details:
            _print_exception_details(exception_details, **kwargs)
        else:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)


def install_custom_excepthook():
    print("[debug-pro] Custom except hook enabled")
    sys.excepthook = _custom_excepthook
