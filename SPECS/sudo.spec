#
# spec file for package sudo
#
# Copyright (c) 2012 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild


Name:           sudo
BuildRequires:  openldap2-devel pam-devel postfix
BuildRequires:  libselinux-devel
PreReq:         coreutils
Version:        1.8.10p2
Release:        1
AutoReqProv:    on
Group:          System/Base
License:        BSD 3-Clause
Url:            http://www.sudo.ws/
Summary:        Execute some commands as root
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}-1.8.10p2.pamd
Source2:        README.SUSE
Patch2:         %{name}-1.8.10p2-sudoers.diff
Patch5:         %{name}-1.8.10p2-secure_path.diff
Patch7:         %{name}-1.8.10p2-env.diff
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Obsoletes:      sudo < 1.8.10p2-1
Vendor:         SUSE LINUX Products GmbH, Nuernberg, Germany

%description
Sudo is a command that allows users to execute some commands as root.
The /etc/sudoers file (edited with 'visudo') specifies which users have
access to sudo and which commands they can run. Sudo logs all its
activities to syslogd, so the system administrator can keep an eye on
things. Sudo asks for the password for initializing a check period of a
given time N (where N is defined at installation and is set to 5
minutes by default).



Authors:
--------
    Jeff Nieusma <nieusma@rootgroup.com>
    David Hieb <davehieb@rootgroup.com>
    Ian McCloghrie <ian@ucsd.edu>

%prep
%setup -q
%patch2
%patch5
%patch7
cp %{S:1} %{S:2} .

%build
%ifarch s390 s390x
F_PIE=-fPIE
%else
F_PIE=-fpie
%endif
export CFLAGS="$RPM_OPT_FLAGS -Wall $F_PIE -DLDAP_DEPRECATED"
export LDFLAGS="-pie"
%configure \
    --libexecdir=%{_libexecdir}/sudo \
    --docdir=%{_docdir}/%{name} \
    --with-noexec=%{_libexecdir}/sudo/sudo_noexec.so \
    --with-selinux \
    --with-logfac=auth \
    --with-ignore-dot \
    --with-tty-tickets \
    --enable-shell-sets-home \
    --with-sudoers-mode=0440 \
    --with-pam \
    --with-sssd \
    --with-sssd-lib=%{_libexecdir} \
    --with-ldap \
    --with-env-editor \
    --without-secure-path \
    --with-passprompt='%%p\x27s password:'
make %{?jobs:-j%jobs}

%install
make DESTDIR=$RPM_BUILD_ROOT install
install -d -m 700 $RPM_BUILD_ROOT/var/lib/sudo
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -m 644 sudo-1.8.10p2.pamd $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sudo
install -m 755 plugins/sudoers/sudoers2ldif $RPM_BUILD_ROOT%{_sbindir}/sudoers2ldif
rm -f $RPM_BUILD_ROOT%{_bindir}/sudoedit
ln -sf %{_bindir}/sudo $RPM_BUILD_ROOT%{_bindir}/sudoedit
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema
install -m 644 doc/schema.OpenLDAP $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema/sudo.schema
rm -f %{buildroot}%{_docdir}/%{name}/sample.pam
rm -f %{buildroot}%{_docdir}/%{name}/sample.syslog.conf
rm -f %{buildroot}%{_docdir}/%{name}/schema.OpenLDAP
rm -f %{buildroot}%{_libexecdir}/%{name}/sudoers.la
rm -rf %{buildroot}%{_includedir}
%find_lang %{name}
%find_lang sudoers
cat sudoers.lang >> %{name}.lang

%post
chmod 0440 %{_sysconfdir}/sudoers
#bnc#712434
rm -rf /var/run/sudo

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%doc ChangeLog README README.LDAP README.SUSE
%doc %{_mandir}/man?/*
%config(noreplace) %attr(0440,root,root) %{_sysconfdir}/sudoers
%dir %{_sysconfdir}/sudoers.d
%config %{_sysconfdir}/pam.d/sudo
%attr(4755,root,root) %{_bindir}/sudo
%dir %{_sysconfdir}/openldap/schema
%attr(0444,root,root) %config %{_sysconfdir}/openldap/schema/sudo.schema
%{_bindir}/sudoedit
%{_bindir}/sudoreplay
%{_sbindir}/visudo
%attr(0755,root,root) %{_sbindir}/sudoers2ldif
%{_libexecdir}/sudo
%attr(0700,root,root) %dir %ghost %{_localstatedir}/lib/sudo

%changelog
* Mon Jan  2 2012 vcizek@suse.cz
- escape values passed to ldap_search (bnc#724490)
* Tue Dec 13 2011 vcizek@suse.com
- manpage claimed keeping DISPLAY environment variable (bnc#720181)
* Mon Aug 29 2011 puzel@suse.com
- update to sudo-1.7.6p2 (bnc#681296)
  - Two-character CIDR-style IPv4 netmasks are now matched correctly
  in the sudoers file.
  - A non-existent includedir is now treated the same as an empty
  directory and not reported as an error.
  - Removed extraneous parens in LDAP filter when
  sudoers_search_filter is enabled that can cause an LDAP search
  error.
  - A new LDAP setting, sudoers_search_filter, has been added to
  ldap.conf.  This setting can be used to restrict the set of
  records returned by the LDAP query.  Based on changes from
  Matthew Thomas.
  - White space is now permitted within a User_List when used in
  conjunction with a per-user Defaults definition.
  - A group ID (%%#gid) may now be specified in a User_List or
  Runas_List.  Likewise, for non-Unix groups the syntax is %%:#gid.
  - Support for double-quoted words in the sudoers file has been
  fixed.  The change in 1.7.5 for escaping the double quote
  character caused the double quoting to only be available at the
  beginning of an entry.
  - The fix for resuming a suspended shell in 1.7.5 caused problems
  with resuming non-shells on Linux.  Sudo will now save the
  process group ID of the program it is running on suspend and
  restore it when resuming, which fixes both problems.
  - A bug that could result in corrupted output in "sudo -l" has
  been fixed.
  - LDAP Sudoers entries may now specify a time period for which
  the entry is valid.  This requires an updated sudoers schema
  that includes the sudoNotBefore and sudoNotAfter attributes.
  Support for timed entries must be explicitly enabled in the
  ldap.conf file.  Based on changes from Andreas Mueller.
  - Time stamp files have moved from /var/run/sudo to either
  /var/db/sudo, /var/lib/sudo or /var/adm/sudo.  The directories
  are checked for existence in that order.  This prevents users
  from receiving the sudo lecture every time the system reboots.
  Time stamp files older than the boot time are ignored on systems
  where it is possible to determine this.
  - Defaults settings that are tied to a user, host or command may
  now include the negation operator.  For example:
  Defaults:!millert lecture
  will match any user but millert.
  - Support for logging I/O for the command being run.
  For more information, see the documentation for the "log_input"
  and "log_output" Defaults options in the sudoers manual.  Also
  see the sudoreplay manual for how to replay I/O log sessions.
  - A new #includedir directive is available in sudoers.  This can be
  used to implement an /etc/sudo.d directory.  Files in an includedir
  are not edited by visudo unless they contain a syntax error.
  - Sudoers now supports a #include facility to allow the inclusion
  of other sudoers-format files.
  - The "secure_path" run-time Defaults option has been restored.
  - Password and group data is now cached for fast lookups.
  - A new Defaults option, "mailfrom" that sets the value of the
  "From:" field in the warning/error mail.  If unspecified, the
  login name of the invoking user is used.
  - A new Defaults option, "env_file" that refers to a file
  containing environment variables to be set in the command being
  run.
- dropped patches (in upstream):
  - sudo-1.6.9p17-strip.diff
  - sudo-1.6.9p17-pam_rhost.diff
  - sudo-1.6.9p17-fast_glob.diff
  - sudo-1.6.9p17-CVE-2010-0426.diff
  - sudo-1.6.9p17-root-leak.diff
  - sudo-1.6.9p17-CVE-2010-0427.diff
  - sudo-1.6.9p17-selinux.diff
- sudo now uses /var/lib/sudo instead of /var/run/sudo
- package LDAP schema (bnc#667558)
- delete /var/run/sudo in %%post (bnc#712434)
* Fri Feb 26 2010 prusnak@suse.cz
- fixed CVE-2010-0426 and CVE-2010-0427 [bnc#582556] [bnc#582555]
* Mon Feb 23 2009 prusnak@suse.cz
- backport fast_glob sudoers flag (fast_glob.diff) [bnc#474068]
* Mon Jan 26 2009 prusnak@suse.cz
- fixed root leak in sudoers (root-leak.diff) [bnc#468923]
- fixed 'sudo -l' segfault (selinux.diff) [bnc#464471]
* Wed Aug 20 2008 prusnak@suse.cz
- enabled SELinux support [Fate#303662]
- added comment about !env_reset into sudoers file
* Wed Aug  6 2008 prusnak@suse.cz
- updated to 1.6.9p17
  * The -i flag should imply resetting the environment, as it did in
    sudo version prior to 1.6.9.  Also, the -i and -E flags are
    mutually exclusive.
  * Fixed the configure test for dirfd() under Linux.
  * Fixed test for whether -lintl is required to link.
  * Changed how sudo handles the child process when sending mail.
    This fixes a problem on Linux with the mail_always option.
  * Fixed a problem with line continuation characters inside of
    quoted strings.
- updated to 1.6.9p16
  * There was a missing space before the ldap libraries in the Makefile
    for some configurations.
  * LDAPS_PORT may not be defined on older Solaris LDAP SDKs.
  * If the LDAP server could not be contacted and the user was not present
    in sudoers, a syntax error in sudoers was incorrectly reported.
* Wed Jul 30 2008 prusnak@suse.cz
- fix note in manpage (added to sudoers.diff) [bnc#404710]
- added commented 'session optional pam_xauth.so' to pam [bnc#402818]
* Tue May  6 2008 prusnak@suse.cz
- do not set PAM_RHOST (pam_rhost.diff) [bnc#386587]
* Thu Apr 24 2008 prusnak@suse.cz
- updated to 1.6.9p15
  * updated libtool to version 1.5.26
  * fixed printing of default SELinux role and type in -V mode
  * the HOME environment variable is once again preserved by default,
    as per the documentation
* Wed Mar 19 2008 prusnak@suse.cz
- updated to 1.6.9p14
  * Moved LDAP options into a table for simplified parsing/setting.
  * Fixed a problem with how some LDAP options were being applied.
  * Added support for connecting directly to LDAP servers via SSL
    in addition to the existing start_tls support.
  * Fixed a compilation problem on SCO related to how they
    store the high resolution timestamps in struct stat.
  * Avoid checking the passwd file group multiple times
    in the LDAP query when the user's passwd group is also
    listed in the supplemental group vector.
  * The URI specifier can now be used in ldap.conf even when
    the LDAP SDK doesn't support ldap_initialize().
  * New %%p prompt escape that expands to the user whose password
    is being prompted, as specified by the rootpw, targetpw and
    runaspw sudoers flags.  Based on a diff from Patrick Schoenfeld.
  * Added a configure check for the ber_set_option() function.
  * Fixed a compilation problem with the HP-UX K&R C compiler.
  * Revamped the Kerberos 5 ticket verification code.
  * Added support for the checkpeer ldap.conf variable for
    netscape-based LDAP SDKs.
  * Fixed a problem where an incomplete password could be echoed
    to the screen if there was a read timeout.
  * Sudo will now set the nproc resource limit to unlimited on Linux
    systems to work around Linux's setuid() resource limit semantics.
    On PAM systems the resource limits will be reset by pam_limits.so
    before the command is executed.
  * SELinux support that can be used to implement role based access
    control (RBAC).  A role and (optional) type may be specified
    in sudoers or on the command line.  These are then used in the
    security context that the command is run as.
  * Fixed a Kerberos 5 compilation problem with MIT Kerberos.
  * Fixed an invalid assumption in the PAM conversation function
    introduced in version 1.6.9p9.  The conversation function may
    be called for non-password reading purposes as well.
  * Fixed freeing an uninitialized pointer in -l mode, introduced in
    version 1.6.9p13.
  * Check /etc/sudoers after LDAP even if the user was found in LDAP.
    This allows Defaults options in /etc/sudoers to take effect.
  * Add missing checks for enforcing mode in SELinux RBAC mode.
- dropped obsoleted patch:
  * prompt.patch (included in update)
* Tue Dec  4 2007 prusnak@suse.cz
- updated to 1.6.9p9
  * the ALL command in sudoers now implies SETENV permissions
  * the command search is now performed using the target user's
    auxiliary group vector too
  * when determining if the PAM prompt is the default "Password: ",
    compare the localized version if possible
  * added passprompt_override flag to sudoers to cause sudo's prompt
    to be used in all cases, also set when the -p flag is used
* Tue Nov  6 2007 prusnak@suse.cz
- updated to 1.6.9p8
  * fixed a bug where a sudoers entry with no runas user specified
    was treated differently from a line with the default runas user
    explicitly specified
* Tue Oct 30 2007 prusnak@suse.cz
- updated to 1.6.9p7
  * go back to using TCSAFLUSH instead of TCSADRAIN when turning off
    echo during password reading
  * fixed a configure bug that was preventing the addition of -lutil
    for login.conf support on FreeBSD and NetBSD
  * add configure check for struct in6_addr since some systems define
    AF_INET6 but have no real IPv6 support
* Wed Oct 10 2007 prusnak@suse.cz
- update to 1.6.9p6
  * worked around bugs in the session support of some PAM
    implementations
  * the full tty path is now passed to PAM as well
  * sudo now only prints the password prompt if the process is in
    the foreground
  * inttypes.h is now included when appropriate if it is present
  * simplified alias allocation in the parser
* Tue Sep 25 2007 prusnak@suse.cz
- update to 1.6.9p5
  * fixed a bug related to supplemental group matching
  * added IPv6 support from YOSHIFUJI Hideaki
  * fixed the sudo_noexec installation path
  * fixed a compilation error on old K&R-style compilers
  * fixed a bug in the IP address matching introduced by the IPV6 merge
  * for "visudo -f file" we now use the permissions of the original file
    and not the hard-coded sudoers owner/group/mode
    (this makes it possible to use visudo with a revision control system)
  * fixed sudoedit when used on a non-existent file
  * regenerated configure using autoconf 2.6.1 and libtool 1.5.24
  * groups and netgroups are now valid in an LDAP sudoRunas statement
- dropped obsolete patches:
  * groupmatch.patch (included in update)
* Tue Aug 28 2007 prusnak@suse.cz
- build --without-secure-path
- hardcoded secure path changed to /usr/sbin:/bin:/usr/bin:/sbin
  (secure_path.diff)
- user can now add PATH variable to env_keep in /etc/sudoers
* Tue Aug 14 2007 prusnak@suse.cz
- added XDG_SESSION_COOKIE to env_keep variables [#298943]
- fixed supplemental group matching (groupmatch.patch)
* Sat Aug 11 2007 schwab@suse.de
- Avoid command line parsing bug in autoconf < 2.59c.
* Tue Jul 31 2007 prusnak@suse.cz
- updated to 1.6.9p2
  * fixed a crash in the error logging function
  * worked around a crash when no tty was present in some PAM
    implementations
  * fixed updating of the saved environment when the environ pointer
    gets changed out from underneath us
* Tue Jul 24 2007 prusnak@suse.cz
- updated to 1.6.9
  * added to the list of variables to remove from the environment
  * fixed a Kerberos V security issue that could allow a user to
    authenticate using a fake KDC
  * PAM is now the default on systems where it is supported
  * removed POSIX saved uid use; the stay_setuid option now requires
    the setreuid() or setresuid() functions to work
  * fixed fd leak when lecture file option is enabled
  * PAM fixes
  * security fix for Kerberos5
  * fixed securid5 authentication
  * added fcntl F_CLOSEM support to closefrom()
  * sudo now uses the supplemental group vector for matching
  * added more environment variables to remove by default
  * mail from sudo now includes an Auto-Submitted: auto-generated header
  * reworked the environment handling code
  * remove the --with-execv option, it was not useful
  * use TCSADRAIN instead of TCSAFLUSH in tgetpass() since some OSes
    have issues with TCSAFLUSH
  * use glob(3) instead of fnmatch(3) for matching pathnames
  * reworked the syslog long line splitting code based on changes
    from Eygene Ryabinkin
  * visudo will now honor command line arguments in the EDITOR or VISUAL
    environment variables if env_editor is enabled
  * LDAP now honors rootbinddn, timelimit and bind_timelimit in /etc/ldap.conf
  * For LDAP, do a sub tree search instead of a base search (one level in
    the tree only) for sudo right objects
  * env_reset option is now enabled by default
  * moved LDAP schema data into separate files
  * sudo no longer assumes that gr_mem in struct group is non-NULL
  * added support for setting environment variables on the command line
    if the command has the SETENV attribute set in sudoers
  * added a -E flag to preserve the environment if the SETENV attribute
    has been set
  * sudoers2ldif script now parses Runas users
  * -- flag now behaves as documented
  * sudo -k/-K no longer cares if the timestamp is in the future
  * when searching for the command, sudo now uses the effective gid of
    the runas user
  * sudo no longer updates the timestamp if not validated by sudoers
  * now rebuild environment regardless of how sudo was invoked
  * more accurate usage() when called as sudoedit
  * command line environment variables are now treated like normal
    environment variables unless the SETENV tag is set
  * better explanation of environment handling in the sudo man page
- changed '/usr/bin/env perl' to '/usr/bin/env' in sudoers2ldif
  script (env.diff)
- dropped obsoleted patches:
  * sudo-1.6.8p12-conf.diff
  * sudo-1.6.8p12-configure.diff
* Tue Jul 17 2007 prusnak@suse.cz
- added note about special input method variables into /etc/sudoers
  (sudoers.diff) [#222728]
* Fri Jan 26 2007 prusnak@suse.cz
- packaged script sudoers2ldif
  * can be used for importing /etc/sudoers to LDAP
  * more info at http://www.sudo.ws/sudo/readme_ldap.html
* Wed Jan 24 2007 prusnak@suse.cz
- added sudoers permission change to %%post section of spec file
* Thu Nov 30 2006 prusnak@suse.cz
- package /etc/sudoers as 0440 [Fate#300934]
* Wed Nov 29 2006 prusnak@suse.cz
- protect locale-related environment variables from resetting (sudoers.diff) [#222728]
* Wed Oct  4 2006 mjancar@suse.cz
- enable LDAP support (#159774)
* Wed Jun 14 2006 schwab@suse.de
- Fix quoting in configure script.
* Wed Mar  8 2006 mjancar@suse.cz
- don't limit access to local group users (#151938)
* Fri Jan 27 2006 mjancar@suse.cz
- set environment and sudo search PATH to SECURE_PATH
  only when env_reset (#145687)
* Thu Jan 26 2006 schwab@suse.de
- Fix syntax error in /etc/sudoers.
* Thu Jan 26 2006 mjancar@suse.cz
- fix PATH always reset (#145687)
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Sun Jan 15 2006 schwab@suse.de
- Don't strip binaries.
* Tue Jan 10 2006 mjancar@suse.cz
- fix CVE-2005-4158 (#140300)
  * compile with --with-secure-path
  * use always_set_home and env_reset by default
- document purpose of the default asking for root password
* Wed Dec 21 2005 mjancar@suse.cz
- update to 1.6.8p12
* Fri Dec  9 2005 ro@suse.de
- disabled selinux
* Tue Aug  2 2005 mjancar@suse.cz
- update to 1.6.8p9
* Mon Jun 20 2005 anicka@suse.cz
- build position independent binaries
* Mon Feb 28 2005 ro@suse.de
- update to 1.6.8p7
* Mon Nov 15 2004 kukuk@suse.de
- Use common PAM config files
* Mon Sep 13 2004 ro@suse.de
- undef __P first
* Tue Apr  6 2004 kukuk@suse.de
- fix default permissions of sudo
* Fri Mar 26 2004 ro@suse.de
- added postfix to neededforbuild
* Wed Feb 25 2004 lnussel@suse.de
- Add comment and warning for 'Defaults targetpw' to config file
* Thu Jan 29 2004 kukuk@suse.de
- Fix sudo configuration broken by last patch
* Wed Jan 28 2004 kukuk@suse.de
- Add SELinux patch
* Thu Jan 22 2004 ro@suse.de
- package /etc/sudoers as 0640
* Fri Jan 16 2004 kukuk@suse.de
- Add pam-devel to neededforbuild
* Sun Jan 11 2004 adrian@suse.de
- build as user
* Fri Nov  7 2003 schwab@suse.de
- Fix quoting in configure script.
* Wed Sep 10 2003 mjancar@suse.cz
- move the defaults to better place in /etc/sudoers (#30282)
* Mon Aug 25 2003 mjancar@suse.cz
- update to 1.6.7p5
  * Fixed a problem with large numbers
    of environment variables.
- more useful defaults (#28056)
* Wed May 14 2003 mjancar@suse.cz
- update to version 1.6.7p4
* Fri Feb  7 2003 kukuk@suse.de
- Use pam_unix2.so instead of pam_unix.so
* Wed Jun  5 2002 pmladek@suse.cz
- updated to version 1.6.6
- removed obsolete heap-overflow fix in prompt patch
* Mon Apr 22 2002 pmladek@suse.cz
- fixed a heap-overflow (prompt patch)
- fixed prompt behaviour, %%%% is always translated to %% (prompt patch)
* Tue Feb 12 2002 pmladek@suse.cz
- insults are really off by default now [#13134]
- sudo.pamd moved from patch to sources
- used %%defattr(-,root,root)
* Thu Jan 24 2002 postadal@suse.cz
- updated to version 1.6.5p2
* Thu Jan 17 2002 pmladek@suse.cz
- updated to version 1.6.5p1
- removed obsolete security patch (to do not run mailer as root),
  sudo runs mailer again as root but with hard-coded environment
* Wed Jan  2 2002 pmladek@suse.cz
- aplied security patch from Sebastian Krahmer <krahmer@suse.de>
  to do not run mailer as root
- NOTIFY_BY_EMAIL enabled
* Tue Oct 30 2001 bjacke@suse.de
- make /etc/sudoers (noreplace)
* Wed Aug 15 2001 pmladek@suse.cz
- updated to version 1.6.3p7
* Tue Aug 14 2001 ro@suse.de
- Don't use absolute paths to PAM modules in PAM config files
* Tue Feb 27 2001 pblaha@suse.cz
- update on 1.6.3p6 for fix potential security problems
* Mon Jun 26 2000 schwab@suse.de
- Add %%suse_update_config.
* Thu May  4 2000 smid@suse.cz
- upgrade to 1.6.3
- buildroot added
* Tue Apr  4 2000 uli@suse.de
- added "--with-env-editor" to configure call
* Wed Mar  1 2000 schwab@suse.de
- Specfile cleanup, remove Makefile.Linux
- /usr/man -> /usr/share/man
* Mon Sep 13 1999 bs@suse.de
- ran old prepare_spec on spec file to switch to new prepare_spec.
* Wed Jun  9 1999 kukuk@suse.de
- update to version 1.5.9p1
- enable PAM
* Thu Jan  2 1997 florian@suse.de
- update to version 1.5.2
- sudo has changed a lot, please check the sudo documentation
