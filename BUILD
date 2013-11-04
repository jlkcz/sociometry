How to build this app to binary form:

Linux:
* Make sure you have installed virtualenv in your distribution. 
* Run ./install.sh, it's very simple script, it basically creates virtualenv and install all necessary dependencies
* Build it with: pyinstaller.py --onedir --hidden-import=flask cli.py 
* Copy sociometry/db.sql, sociometry/static and sociometry/templates to dist/cli/sociometry

Windows:
* Make sure you have (somehow) installed all dependencies
* Run pyinstaller.py --onedir --hidden-import=flask --hidden-import=cairo --hidden-import=xlsxwriter
(it's weird, but building on windows doesn't work without all those hidden imports)

Mac:
* I have no idea, never used Mac. Basically it should be similarly easy as on Windows and Linux

