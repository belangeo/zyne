rm -rf build dist
py2applet --make-setup Zyne.py Resources/*
python setup.py py2app --plist=scripts/Info.plist
rm -f setup.py
rm -rf build
mv dist zyne_0.1.0
if cd zyne_0.1.0;
then
    find . -name .svn -depth -exec rm -rf {} \;
    find . -name *.pyc -depth -exec rm -f {} \;
    find . -name .* -depth -exec rm -f {} \;
else
    echo "Something wrong. zyne_0.1.0 not created"
    exit;
fi

echo "Remove Windows .ico files"
rm Zyne.app/Contents/Resources/zyneicon.ico
rm Zyne.app/Contents/Resources/zyneiconDoc.ico

cd ..
cp -R zyne_0.1.0/Zyne.app .
tar -cjvf Zyne_0.1.0.tar.bz2 Zyne.app
rm -rf zyne_0.1.0
rm -rf Zyne.app
