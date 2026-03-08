from setuptools import setup, find_packages

setup(
    name="xauusd_quant_lab",
    version="1.0.0",
    packages=find_packages(),
    # sitecustomize.py runs automatically on Python startup — adds repo root to sys.path
    py_modules=["sitecustomize", "config", "_pathfix"],
)
