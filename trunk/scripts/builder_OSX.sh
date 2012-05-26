rm -rf build dist
py2applet --make-setup Zyne.py Resources/*
python setup.py py2app --plist=scripts/Info.plist
rm -f setup.py
rm -rf build
mv dist zyne_0.1.2
if cd zyne_0.1.2;
then
    find . -name .svn -depth -exec rm -rf {} \;
    find . -name *.pyc -depth -exec rm -f {} \;
    find . -name .* -depth -exec rm -f {} \;
else
    echo "Something wrong. zyne_0.1.2 not created"
    exit;
fi

echo "Remove Windows .ico files"
rm Zyne.app/Contents/Resources/zyneicon.ico
rm Zyne.app/Contents/Resources/zyneiconDoc.ico

ditto --rsrc --arch i386 Zyne.app Zyne-i386.app
rm -rf Zyne.app
mv Zyne-i386.app Zyne.app

cd ..
cp -R zyne_0.1.2/Zyne.app .

# Fixed wrong path in Info.plist
cd Zyne.app/Contents
awk '{gsub("Library/Frameworks/Python.framework/Versions/2.6/Resources/Python.app/Contents/MacOS/Python", "@executable_path/../Frameworks/Python.framework/Versions/2.6/Python")}1' Info.plist > Info.plist_tmp && mv Info.plist_tmp Info.plist

cd ../..
tar -cjvf Zyne_0.1.2.tar.bz2 Zyne.app
rm -rf zyne_0.1.2
rm -rf Zyne.app

svn export . Zyne_0.1.2-src
tar -cjvf Zyne_0.1.2-src.tar.bz2 Zyne_0.1.2-src
rm -R Zyne_0.1.2-src
