import setuptools

setuptools.setup(
    name="rofi-blocks",
    version="0.0.1",
    description="Async interface for interacting with rofi blocks modi",
    url="[...]",
    author="L. S. Menicucci",
    licence="unlicensed",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[],
    python_requires='>=3.7',
    zip_safe=False)
