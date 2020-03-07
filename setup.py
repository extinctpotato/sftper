import setuptools

setuptools.setup(
        name="sftper",
        version="0.1",
        author="Adam Olech",
        author_email="nddr89@gmail.com",
        description="Helper utility for mounting sshfs mounts in PyQt",
        #url="",
        packages=["sftper"],
        python_requires='>=3.6',
        entry_points={
            "console_scripts": ["sftper = sftper:main"]
            },
        install_requires=["PyQt5"],
        )
