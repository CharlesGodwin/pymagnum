call make.bat clean
call make.bat html
@REM generated documentation is in ../build/html
rd /s /q dist
rd /s /q pymagnum.egg-info
py -m build
