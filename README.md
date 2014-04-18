sles-sudo
=======

This builds a sudo-1.8.10p2-1.rpm suitable for SLES 11.

Why ?

1. sssd support introduced somewhere around 1.7.7
2. group support for ldap sudo queries (integration with RedHats FreeIPA)

Usage
=======

    git clone https://github.com/jonuwz/sles-sudo.git
    cd sles-sudo
    ./build_sudo.sh


