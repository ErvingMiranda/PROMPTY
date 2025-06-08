from setuptools import setup, find_packages

setup(
    name='prompty',
    version='2.5.0',
    packages=find_packages(include=['prompty', 'prompty.*']),
    install_requires=[
        'SpeechRecognition',
        'pyttsx3',
        'colorama'
    ],
    entry_points={
        'console_scripts': [
            'prompty=prompty.main:main'
        ]
    },
    description='Asistente virtual de escritorio con voz',
    author='PROMPTY Team',
)
