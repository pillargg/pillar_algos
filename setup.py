# create wheel/dist with `python setup.py sdist bdist_wheel`
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pillaralgos", # Replace with your own username
    version= "1.0.0.2",
    author="Peter Gates",
    author_email="pgate89@gmail.com",
    description='Algorithms for Pillar. Curently includes "mini" algorithms, nothing too sophisticated.',
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
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)