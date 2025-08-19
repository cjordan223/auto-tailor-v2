from setuptools import setup, find_packages

setup(
    name="tex-tailor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "colorama",
        "requests",
        "jsonschema",
    ],
    entry_points={
        "console_scripts": [
            "tex-tailor=tex_tailor.cli:main",
        ],
    },
    python_requires=">=3.8",
)