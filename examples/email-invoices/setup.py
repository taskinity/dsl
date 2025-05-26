from setuptools import setup, find_packages

setup(
    name="email-invoice-processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'taskinity-dsl',
        'python-dotenv',
        'pytesseract',
        'pdf2image',
        'Pillow',
        'opencv-python-headless',
        'numpy',
        'imap-tools',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'flake8',
            'black',
            'isort',
        ],
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'email-processor=email_processor.cli:main',
        ],
    },
)
