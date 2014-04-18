wget -O /usr/src/packages/SOURCES/sudo-1.8.10p2.tar.gz 'http://www.sudo.ws/sudo/dist/sudo-1.8.10p2.tar.gz'
find . -type f -exec mv {} /usr/src/packages/{}
echo "Now run :"
echo "    rpmbuild -ba /usr/src/packages/SPECS/sudo.spec"
echo
