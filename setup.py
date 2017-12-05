from setuptools import setup


setup(
    name='fakeout',
    version='0.1.0',
    description='CLI-based Checkout Implementation',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    url='http://github.com/svsticky/fakeout',
    author='Maarten van den Berg',
    author_email='maartenberg1@gmail.com',
    license='MIT',
    packages=['fakeout'],
    entry_points={
        'console_scripts': [
            'fakeout=fakeout.script:main'
            ]
        },
    install_requires=[
        'requests',
        'prettytable'
    ],
    include_package_data=True,
    zip_safe=False
)
