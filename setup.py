"""
Setup script pro instalaci balíčku rpg_notion.
"""
from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rpg_notion",
    version="0.1.0",
    author="RPG Notion Team",
    author_email="info@rpgnotion.example.com",
    description="Systém pro automatické zaznamenávání obsahu solo RPG her s AI do Notion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rpg_notion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)
