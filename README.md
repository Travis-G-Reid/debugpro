# debugpro
debug like a pro

Import the project `from debugpro import install_custom_excepthook` and run `install_custom_excepthook()` to enable the custom exception messages.

Note: The console print includes colored and bolded text whose rich formatting may be partially lost when running inside a container or other abstraction.

Example input/output:

Input:
```
from debugpro import install_custom_excepthook
install_custom_excepthook()

my_list = [1, 3, 9]
my_list[999]
```

Output:
```
============================================================
ERROR: IndexError: list index out of range
============================================================

------ Modules ------
sys

------ Functions ------
install_custom_excepthook

------ System Info ------
Python version: 3.13.3
Platform: Windows-11-10.0.26100-SP0
Current working directory: C:\Users\Travi\repos\import-test

------ Python Path ------
  1. c:\Users\Travi\repos\import-test
  2. C:\Users\Travi\AppData\Local\Programs\Python\Python313\python313.zip
  3. C:\Users\Travi\AppData\Local\Programs\Python\Python313\DLLs
  4. C:\Users\Travi\AppData\Local\Programs\Python\Python313\Lib
  5. C:\Users\Travi\AppData\Local\Programs\Python\Python313
  6. C:\Users\Travi\AppData\Local\Programs\Python\Python313\Lib\site-packages
  7. C:\Users\Travi\repos\debugpro\src

------ Variables ------
my_list = [1, 3, 9]

Location: ...\import-test\import-test.py, line 8
------ Stack Trace ------
1. __main__ in ...\import-test\import-test.py:8

------ Code Context ------
  5: install_custom_excepthook()
  6:
  7: my_list = [1, 3, 9]
→ 8: my_list[999]
  --- End of file ---

------ IndexError Details ------
Collection: my_list = [1, 3, 9]
Length: 3
Valid indices: 0 to 2
Invalid index: 999
```

Example Input/Output

Input:
```
from debugpro import install_custom_excepthook
install_custom_excepthook()

my_list = {'example_key_1': 'some_value', 'example_key_2': 'other_value'}
my_list['example_key_999']
```

Output (omitting the same as above):
```
------ Variables ------
my_list = {'example_key_1': 'some_value', 'example_key_2': 'other_value'}

Location: ...\import-test\import-test.py, line 5
------ Stack Trace ------
1. __main__ in ...\import-test\import-test.py:5

------ Code Context ------
  2: install_custom_excepthook()
  3:
  4: my_list = {'example_key_1': 'some_value', 'example_key_2': 'other_value'}
→ 5: my_list['example_key_999']
  --- End of file ---

------ KeyError Details ------
Dictionary: my_list = {'example_key_1': 'some_value', 'example_key_2': 'other_value'}
Missing key: 'example_key_999'
Available keys: ['example_key_1', 'example_key_2']
```
