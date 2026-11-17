@echo off
python -m pip install -r requirements.txt
pyinstaller --onefile --windowed --name "UniversalAuditorDataCleaner" universal_data_clean.py
echo Build complete. EXE is in dist\UniversalAuditorDataCleaner.exe
pause