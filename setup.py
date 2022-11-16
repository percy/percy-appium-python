from os import path
from setuptools import find_packages, setup
import percy

# read the README for long_description
cwd = path.abspath(path.dirname(__file__))
with open(path.join(cwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='percy-appium-app',
    description='Python client for visual testing with Percy for mobile apps',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=percy.__version__,
    license='MIT',
    author='Perceptual Inc.',
    author_email='team@percy.io',
    url='https://github.com/percy/percy-appium-python',
    keywords='appium percy visual testing',
    packages=find_packages(include=['percy*']),
    package_data={'percy': ['configs/*.json']},
    include_package_data=True,
    install_requires=[
        'Appium-Python-Client',
        'requests'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    tests_require=['Appium-Python-Client', 'httpretty', 'requests'],
    zip_safe=False
)
