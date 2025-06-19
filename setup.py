"""
Setup do KTR Migrator
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ktr-migrator",
    version="1.0.0",
    author="Leonardo A. Mota",
    author_email="dev.lamota@gmail.com",
    description="Ferramenta para migração de pipelines Pentaho KTR para Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmottta/ktr_migrator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ktr-migrator=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "ktr_migrator": [
            "src/templates/*.j2",
            "examples/*.ktr",
            "docs/*.md",
        ],
    },
    keywords="pentaho etl migration python data-engineering",
    project_urls={
        "Bug Reports": "https://github.com/example/ktr-migrator/issues",
        "Source": "https://github.com/example/ktr-migrator",
        "Documentation": "https://ktr-migrator.readthedocs.io/",
    },
) 