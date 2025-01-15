from setuptools import setup, find_packages

setup(
    name="interest-rate-swap-analyzer",
    version="1.0.0",
    description="A tool to analyze interest rate swaps",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Christopher Lawson",
    author_email="117199342+chrislawson-au@users.noreply.github.com",
    url="https://github.com/chrislawson-au/interest-rate-swap-analyzer",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
        "plotly>=5.0.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=22.0.0',
            'flake8>=3.9.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'swap-analyzer=interest_rate_swap_analyzer.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires='>=3.6',
)
