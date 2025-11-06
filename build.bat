@echo off
setlocal

:: 设置虚拟环境路径
set VENV_PATH=.\.venv

:: 清理旧构建
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: 激活虚拟环境（注意要加 .bat）
call %VENV_PATH%\Scripts\activate.bat

:: 确认 pyinstaller 存在（调试用）
where pyinstaller

:: 运行 pyinstaller 打包
pyinstaller --noconfirm --onefile --windowed ^
  --icon "Gesture&Guess.ico" ^
  --name "GestureGuessGame" ^
  --add-data "bg.jpg;." ^
  --add-data "button.wav;." ^
  --add-data "gameover.wav;." ^
  --add-data "gamestart.wav;." ^
  --add-data "getpoint.wav;." ^
  --add-data "losepoint.wav;." ^
  --add-data "HYPixel11pxU-2.ttf;." ^
  --add-data "topics.json;." ^
  --add-data "pictures/*;pictures" ^
  "Gesture&Guess.py"

:: 不用 deactivate，激活窗口关闭即退出虚拟环境

:: 创建发布目录
mkdir "dist\GestureGuessGame" 2>nul

:: 移动 exe 到发布目录
move /Y "dist\GestureGuessGame.exe" "dist\GestureGuessGame\"

:: 复制资源文件
xcopy /Y /E "pictures" "dist\GestureGuessGame\pictures\" >nul
copy /Y "topics.json" "dist\GestureGuessGame\" >nul

:: 创建 ZIP 发布包
powershell -Command "Compress-Archive -Path 'dist\GestureGuessGame' -DestinationPath 'GestureGuessGame_v1.0.zip' -Force"

echo.
echo 打包成功完成!
echo 发布包: GestureGuessGame_v1.0.zip
echo 游戏目录: dist\GestureGuessGame
echo.

endlocal
