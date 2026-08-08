@echo off
echo ============================================
echo    AutoClicker - EXE Olusturucu
echo ============================================
echo.

echo [1/3] Gerekli kutuphaneler yukleniyor...
pip install pynput pyinstaller --quiet

echo.
echo [2/3] EXE dosyasi olusturuluyor...
pyinstaller --onefile --noconsole --name AutoClicker auto_clicker.py

echo.
echo [3/3] Temizlik yapiliyor...
if exist build rmdir /s /q build
if exist auto_clicker.spec del auto_clicker.spec

echo.
echo ============================================
echo  TAMAMLANDI! EXE dosyasi:
echo  dist\AutoClicker.exe
echo ============================================
echo.
pause
