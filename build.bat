cd client-build
pyinstaller --windowed --name=mjc-broker --version-file=file_version_info.txt ..\client-src\main.py
cd ..
