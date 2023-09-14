import importlib.util
import os
from setuptools import setup, find_packages

SRC_DIR = 'src'
SEASON_PKG_DIR = os.path.join(SRC_DIR, 'dizest')
spec = importlib.util.spec_from_file_location('version', os.path.join(SEASON_PKG_DIR, 'version.py'))
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename)[11:])
    return paths

extra_files = package_files(os.path.join(SEASON_PKG_DIR, 'command'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'daemon'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'res'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'util'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'kernel'))
extra_files = extra_files + package_files(os.path.join(SEASON_PKG_DIR, 'bundle'))

setup(
    name='dizest',
    version=version.VERSION_STRING,
    description='season dizest: data management platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    url='https://github.com/season-framework/dizest',
    author='proin',
    author_email='proin@season.co.kr',
    license='MIT',
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    package_data = {
        'dizest': extra_files
    },
    zip_safe=False,
    entry_points={'console_scripts': [
        'dizest = dizest.cmd:main [dizest]',
    ]},
    install_requires=[
        'argh',
        'python-crontab',
        'matplotlib',
        'psutil',
        'requests',
        'Pillow',
        'numpy',
        'pandas',
        'pymysql',
        'natsort',
        'season==2.3.17',
        'peewee',
        'libsass',
        'bcrypt',
        'python-socketio==5.7.2',
        'python-socketio[client]'
    ],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ] 
)