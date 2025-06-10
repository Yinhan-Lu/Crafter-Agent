from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crafter-agent",
    version="0.1.0",
    author="Yinhan Lu",
    description="AI agents for the Crafter environment using ReAct framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yinhan-Lu/Crafter-Agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crafter-agent=crafter_agents.run_agents:main",
        ],
    },
    include_package_data=True,
    package_data={
        "crafter": ["data.yaml"],
    },
) 