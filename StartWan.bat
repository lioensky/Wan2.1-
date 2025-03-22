@echo off
chcp 65001 > nul

:menu
cls
echo ====================================
echo         视频生成工具菜单
echo ====================================
echo 1. 提交新的视频生成请求
echo 2. 查询视频生成状态
echo 3. 退出程序
echo ====================================

choice /C 123 /N /M "请选择操作 (1-3): "

if errorlevel 3 goto :exit
if errorlevel 2 goto :get
if errorlevel 1 goto :post

:post
echo.
echo 正在启动视频生成请求...
python wan2.1post.py
echo.
echo 按任意键返回主菜单...
pause > nul
goto :menu

:get
echo.
echo 正在启动视频状态查询...
python wan2.1get.py
echo.
echo 按任意键返回主菜单...
pause > nul
goto :menu

:exit
echo.
echo 感谢使用，再见！
timeout /t 2 > nul