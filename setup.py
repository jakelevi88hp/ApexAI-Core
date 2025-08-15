from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="apexai-core",
    version="0.1.0",
    author="ApexAI Team",
    author_email="info@apexadvantage.co",
    description="ApexAI Core - AI automation stack for business operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakelevi88hp/ApexAI-Core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)

