# The Essential Guide to pyproject.toml

What is pyproject.toml?
The pyproject.toml file is the cornerstone of modern Python packaging, standardized in PEP 518 and PEP 621. It replaces the legacy setup.py approach with a declarative configuration that makes package distribution more reliable and consistent.
Example pyproject.toml:
```python
toml[build-system]
requires = ["setuptools>=42", "wheel"] # This is generally always default and required
build-backend = "setuptools.build_meta" # This is generally always default and required

[project]
name = "example-package"
version = "0.1.0"
description = "An example package to demonstrate pyproject.toml"
readme = "README.md"
authors = [
    {name = "Example Author", email = "author@example.com"},
]
license = {text = "MIT"} # Don't include this if you aren't making open source software
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
requires-python = ">=3.7"
dependencies = [
    "requests>=2.25.0",
    "pandas>=1.0.0",
]

[project.urls]
"Homepage" = "https://github.com/yourusername/example-package"
"Bug Tracker" = "https://github.com/yourusername/example-package/issues"

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black>=21.5b2",
]

# THIS IS ESSENTIAL FOR PACKAGE DISCOVERABILITY
[tool.setuptools]
package-dir = {"" = "src"} # Only if your packages directory is inside of source. "" = "src" sets the root directory for packages to "src"
packages = ["example_package"] # This specifies which package to export and make available during installation.
```

Critical Fields for Package Availability

1. [build-system]
This mandatory section defines how your package is built:

requires: Lists build-time dependencies (not runtime)
build-backend: Specifies which system builds your package

Without this section, modern packaging tools won't know how to build your package.

2. [project]
This core section contains essential metadata:

name: The install name (pip install example-package)
version: Package version, ideally following semantic versioning
description: Short summary of your package
dependencies: Runtime requirements for your package

The name and version fields are particularly critical - they identify your package uniquely in repositories like PyPI.
3. requires-python
This field prevents installation on incompatible Python versions. If omitted, your package might be installed on Python versions where it fails to run.

4. [project.optional-dependencies]
Defines feature sets users can optionally install:
bashpip install example-package[dev]
This keeps your base package lean while offering enhanced functionality for those who need it.

5. [tool.setuptools] Package Structure
These fields tell the build system where to find your code:

package-dir: Maps namespace roots to directories
packages: Lists all packages to include

If these are incorrect, your package might build but could be missing critical modules or files.
Common Packaging Pitfalls

Missing py.typed: If your package uses type hints, include an empty py.typed file to enable type checking.
Namespace packages: For namespace packages, ensure packages correctly lists all subpackages.
Package discovery: For complex projects, consider setuptools.find_packages() via dynamic configuration.
Version management: Consider using tools like setuptools_scm to automatically derive versions from git tags.

Best Practices

Use strict version constraints only when necessary
Include proper classifiers to help users find your package
Add comprehensive metadata like README, license, and URLs
Test your package build with pip install -e . before publishing

Next Steps
After configuring your pyproject.toml:

Build your package: python -m build
Test locally: pip install dist/your_package-0.1.0-py3-none-any.whl
Publish to PyPI: python -m twine upload dist/*

For more information, consult the Python Packaging User Guide.
