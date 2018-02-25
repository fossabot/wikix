from distutils.core import setup

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

from wikix import __version__

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile["packages"], r=False)

setup(
    name="wikix",
    packages=["wikix"],
    version=__version__,
    description="Simple, yet highly customizable wiki-engine for personal use.",
    author="Maximilian Remming",
    author_email="maxremming@gmail.com",
    url="https://github.com/PolarPayne/wikix",
    download_url="https://github.com/PolarPayne/wikix/archive/{}.tar.gz".format(__version__),
    license="MIT",
    install_requires=requirements,
    entry_points={
          'console_scripts': [
              'wikix = wikix.__main__:main'
          ]
      },
    keywords=["wiki"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
