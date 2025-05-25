from setuptools import setup, find_packages

setup(
    name="camel-router",
    version="0.1.0",
    description="Apache Camel-style routing engine for multi-language processing",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
        "asyncio-mqtt>=0.13.0",
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "jinja2>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "camel-router=camel_router.cli:main",
        ],
    },
    python_requires=">=3.8",
)