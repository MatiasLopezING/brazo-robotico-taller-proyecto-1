from glob import glob

from setuptools import find_packages, setup

paquete = 'brazo_control'

setup(
    name=paquete,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + paquete]),
        ('share/' + paquete, ['package.xml']),
        ('share/' + paquete + '/launch', glob('launch/*.launch.py')),
        ('share/' + paquete + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Matias Lopez',
    maintainer_email='ml3280199@gmail.com',
    description='Control del brazo robotico del Grupo 3 (Taller de Proyecto I, UNLP)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controlador = brazo_control.controlador:main',
            'planificador = brazo_control.planificador:main',
            'demo = brazo_control.demo:main',
        ],
    },
)
