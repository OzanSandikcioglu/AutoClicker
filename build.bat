@echo off
echo ============================================
echo    AutoClicker - EXE Olusturucu
echo ============================================
echo.

echo [1/5] Gerekli kutuphaneler yukleniyor...
python -m pip install pynput pyinstaller --quiet

echo.
echo [2/5] Eski build dosyalari temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AutoClicker.spec del AutoClicker.spec
if exist auto_clicker.spec del auto_clicker.spec

echo.
echo [3/5] EXE dosyasi olusturuluyor (onedir modu)...
python -m PyInstaller -y --onedir --noconsole --uac-admin --name AutoClicker --version-file version_info.txt auto_clicker.py

echo.
echo [4/5] Kullanim talimatlari kopyalaniyor...
copy /y OKU-BENI.txt dist\AutoClicker\OKU-BENI.txt >nul
copy /y README.txt dist\AutoClicker\README.txt >nul

echo.
echo [5/5] Temizlik yapiliyor...
if exist build rmdir /s /q build
if exist AutoClicker.spec del AutoClicker.spec

echo.
echo ============================================
echo  TAMAMLANDI! EXE dosyasi:
echo  dist\AutoClicker\AutoClicker.exe
echo.
echo  Dagitmak icin dist\AutoClicker klasorunu
echo  zip olarak paylasiniz.
echo ============================================
echo.
pause
