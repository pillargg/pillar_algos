# create wheel/dist with `python setup.py sdist bdist_wheel`
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pillaralgos", # Replace with your own username
    version= "1.0.0",
    author="Peter Gates",
    author_email="pgate89@gmail.com",
    description='Algorithms for Pillar. Currently includes "mini" algorithms, nothing too sophisticated.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pomkos/twitch_chat_analysis",
    project_urls={
        "Pillar": "https://pillar.gg",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    install_requires=[
        'pandas>=1.2.3',
        'numpy>=1.20.2',
        'matplotlib>=3.4.1',
        'seaborn>=0.11.1'
    ],
    python_requires=">=3.6",
)