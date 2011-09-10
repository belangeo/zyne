import os

build = True

os.system("python ..\pyinstaller\Configure.py")
os.system('python ..\pyinstaller\Makespec.py -F -c --icon=Resources\zyneicon.ico "Zyne.py"')
if build:
    os.system('python ..\pyinstaller\Build.py "Zyne.spec"')
    os.system("svn export . Zyne_Win")
    os.system("copy dist\Zyne.exe Zyne_Win /Y")
    os.system("rmdir /Q /S Zyne_Win\scripts")
    os.remove("Zyne_Win/Zyne.py")
    os.remove("Zyne_Win/Resources/zyneicon.icns")
    os.remove("Zyne_Win/Resources/zyneiconDoc.icns")
    os.remove("Zyne.spec")
    os.system("rmdir /Q /S build")
    os.system("rmdir /Q /S dist")

