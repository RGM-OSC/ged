Summary: Generic Event Dispatcher
Name: ged
Version: 1.6
Release: 10.rgm
Source: %{name}.tar.gz
BuildRoot: /tmp/%{name}-%{version}
Group: Applications/Base
Packager: http://generic-ed.sourceforge.net
License: GPL

BuildRequires: gcc >= 4.0.0
BuildRequires: pkgconfig
BuildRequires: libgenerics-devel >= 1.2-1
BuildRequires: libgcrypt-devel
BuildRequires: mysql-devel >= 5.0.3
BuildRequires: glib2-devel
BuildRequires: zlib-devel
#BuildRequires: db4-devel
BuildRequires: rpm-macros-rgm

Requires: libgenerics >= 1.2-1
Requires: openssl
Requires: libgcrypt
Requires: glib2
Requires: zlib
Requires: rgm-base

%description
GED is a wire designed to handle templated data transmission over HTTP in distributed networks. 

%package mysql
Summary: Generic Event Dispatcher MySQL backend
License: GPL
Group: Applications/Base

Requires: %{name} = %{version}
Requires: mariadb-libs

%description mysql
GED is a wire designed to handle templated data transmission over HTTP in distributed networks. 
This is the mysql GED backend.

#%package bdb
#Summary: Generic Event Dispatcher Berkeley backend
#License: GPL
#Group: Applications/Base
#
#Requires: %{name} = %{version}
#Requires: db4

#%description bdb
#GED is a wire designed to handle templated data transmission over HTTP in distributed networks.
#This is the berkeley GED backend.

%package devel

Summary: Generic Event Dispatcher
License: GPL
Group: Applications/Base

Requires: %{name} = %{version}
Requires: libgenerics-devel >= 1.2
Requires: libgcrypt-devel
Requires: mysql-devel >= 5.0.0
Requires: glib2-devel
Requires: zlib-devel
#Requires: db4-devel
Requires: openssl-devel

%description devel
GED is a wire designed to handle templated data transmission over HTTP in distributed networks. 
This is the devel part as you may want to write your own backend.

%prep
%setup -q -n %{name}

%build
    make 

%install
    rm -rf ${RPM_BUILD_ROOT}
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/bin
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/ssl/easy-rsa
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/bkd
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.d
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d
    mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/lib64
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/man/man8
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/scripts
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/www/
    mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}

    install -m 640 etc.in/ged2rss ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.d/
    install -m 640 etc.in/purge_ged ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.d/
    install -m 666 etc.in/*.cfg ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc
    install -m 666 etc.in/bkd/gedmysql.cfg ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/bkd
    install -m 666 etc.in/bkd/geddummy.cfg ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/bkd
    install -m 755 ged ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/bin
    install -m 755 gedq ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/bin
    install -m 755 gedbackup ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/bin
    install -m 755 gedrestore ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/bin
    install -m 655 %{name}dummy-%{version}.so %{name}mysql-%{version}.so ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/lib64
    install -m 655 lib%{name}-%{version}.* lib%{name}q-%{version}.* ${RPM_BUILD_ROOT}%{_libdir}
    install -m 644 etc.in/bkd/*.sql ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/bkd
    install -m 640 -t ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/ etc.in/httpd-ged_rss.example.conf
    install -m 644 gedq.8.gz ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/man/man8
    install -m 744 ssl/mk* ssl/check* ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/ssl
    install -m 744 ssl/easy-rsa/* ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/ssl/easy-rsa
    install -m 755 scripts/* ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/scripts

    mkdir -p ${RPM_BUILD_ROOT}/usr/include/ged
    install -m 644 inc/* ${RPM_BUILD_ROOT}/usr/include/ged
    install -m 644 %{name}-%{version}.pc ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig
    install -m 644 var/www/index.html ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/www/

    install -m 644 etc.in/gedd.service $RPM_BUILD_ROOT/%{_unitdir}/gedd.service

%post
    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/cache
    chmod 777 ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/cache

    mkdir -p ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/lib
    chmod 777 ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/var/lib

    ln -sf %{rgm_path}/%{name}-%{version} %{rgm_path}/%{name}

    if [ ! -f %{rgm_path}/%{name}-%{version}/etc/ssl/ca.crt ]; then
        cd %{rgm_path}/%{name}-%{version}/etc/ssl
        ./mkgedsrvcerts.sh geds
        ./mkgedclicerts.sh gedc
        cd -
    fi
    # Force gedt deactivation
    sed -i 's/^include \/srv\/rgm\/ged\/etc\/gedt\.cfg/# include \/srv\/rgm\/ged\/etc\/gedt\.cfg/g' ${RPM_BUILD_ROOT}%{rgm_path}/%{name}-%{version}/etc/ged.cfg
    %systemd_post gedd.service

%post mysql
    # execute SQL postinstall script
    /usr/share/rgm/manage_sql.sh -d %{rgm_db_ged} -s %{rgm_path}/%{name}-%{version}/etc/bkd/ged-init.sql -u %{rgm_sql_internal_user} -p %{rgm_sql_internal_pwd}
    if [ -e %{rgm_path}/%{name}-%{version}/lib64/gedmysql.so.1 ] && [ -L %{rgm_path}/%{name}-%{version}/lib64/gedmysql.so.1 ] ; then
        rm -f %{rgm_path}/%{name}-%{version}/lib64/gedmysql.so.1
    fi
    ln -s %{rgm_path}/%{name}-%{version}/lib64/gedmysql-%{version}.so %{rgm_path}/%{name}-%{version}/lib64/gedmysql.so.1

%preun
    %systemd_preun gedd.service
    if [ "$1" = 0 ]; then
        if [ -e %{rgm_path}/%{name} ]; then
            rm -f %{rgm_path}/%{name}
        fi
    fi

%preun mysql
    if [ "$1" = 0 ]; then
        if [ -e %{rgm_path}/%{name} ]; then
            rm -f %{rgm_path}/%{name}-%{version}/lib64/gedmysql.so.1
        fi
    fi

%postun
    %systemd_postun_with_restart gedd.service

%clean
    rm -rf ${RPM_BUILD_ROOT}
    rm -rf /tmp/%{name}-%{version}


%files
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/ged.cfg
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/gedq.cfg
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/gedp.cfg
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/gedt.cfg
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/event_rgm.cfg
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/bkd/geddummy.cfg
%{_unitdir}/gedd.service
%{rgm_path}/%{name}-%{version}/etc/ssl
%{_sysconfdir}/cron.d/ged2rss
%{_sysconfdir}/cron.d/purge_ged
%{rgm_path}/%{name}-%{version}/etc/httpd-ged_rss.example.conf
%{rgm_path}/%{name}-%{version}/lib64/geddummy-%{version}.so
%{rgm_path}/%{name}-%{version}/bin/ged
%{rgm_path}/%{name}-%{version}/bin/gedq
%{rgm_path}/%{name}-%{version}/bin/gedbackup
%{rgm_path}/%{name}-%{version}/bin/gedrestore
%{rgm_path}/%{name}-%{version}/man/man8/gedq.8.gz
%{rgm_path}/%{name}-%{version}/scripts/
%{rgm_path}/%{name}-%{version}/var/www/index.html
%{_libdir}/libged-%{version}.so
%{_libdir}/libged-%{version}.a
%{_libdir}/libgedq-%{version}.so
%{_libdir}/libgedq-%{version}.a

#%files bdb
#%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/bkd/gedhdb.cfg
#%{rgm_path}/%{name}-%{version}/lib64/gedhdb-%{version}.so

%files mysql
%config(noreplace) %{rgm_path}/%{name}-%{version}/etc/bkd/gedmysql.cfg
%{rgm_path}/%{name}-%{version}/lib64/gedmysql-%{version}.so
%{rgm_path}/%{name}-%{version}/etc/bkd/ged-init.sql

%files devel
%{_usr}/include/ged
%{_libdir}/pkgconfig/%{name}-%{version}.pc

%changelog
* Thu Oct 20 2022 Christophe Cassan <ccassan@fr.scc.com> - 1.6-10.rgm
- Add two types of event secu_display and secu_nodisplay
- New large string type log columns added for these types

* Thu Oct 20 2022 Alex Rocher <arocher@fr.scc.com> - 1.6-9.rgm
- Add some columns for SOC

* Fri Sep 10 2021 Alex Rocher <arocher@fr.scc.com> - 1.6-8.rgm
- Deactivate gedt include

* Wed Mar 17 2021 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-7.rgm
- remove httpd config file

* Wed Oct 28 2020 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-6.rgm
- fix bad symlink handling in SPEC file

* Fri Oct 23 2020 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-5.rgm
- fix buggy cronjob for ged purge

* Thu May 09 2019 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-4.rgm
- call SQL schema init script to fix SQL privileges for 'gedadmin' user
- fix SPEC for mysql package creation

* Fri Mar 29 2019 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-3.rgm
- fix mariadb dependency to mariadb-libs
- fix apache config file

* Fri Mar 15 2019 Eric Belhomme <ebelhomme@fr.scc.com> - 1.6-2.rgm
- add rgm-macros-rpm as build dependency
- add rgm-base as dependency
- create DB on post section
- replaced hardcoded dirs by macros

* Tue Mar 12 2019 Michael Aubertin <maubertin@fr.scc.com> - 1.6-1.rgm
- Change path

* Wed Feb 20 2019 Michael Aubertin <maubertin@fr.scc.com> - 1.6.0
- Prepare RGM customization

* Wed Feb 20 2019 Samuel Ronciaux <Samuel.ronciaux@gmail.com> - 1.5.9
- Initial fork

* Wed May 04 2016 Jean-Philippe Levy <jeanphilippe.levy@gmail.com> - 1.5.9  
- Add systemd service
- Fix do not copy gedhdb.cfg 
- Fix ged_rss.conf

* Wed May 04 2016 Michael Aubertin <michael.aubertin@gmail.com> - 1.5-8
- Patch Nagios relation file script
- Add daily purge with Problem MGT

* Tue Apr 19 2016 Michael Aubertin <michael.aubertin@gmail.com> - 1.5-7
- With Eric Belhomme :)
- Replace TYPE by ENGINE and build against EON5 (centos7)
- Remove Berkeley DB Backend
- Replace Nagios Scripts

* Mon Jan 13 2014 Jeremie Bernard <gremi@users.sourceforge.net> - 1.5.6
- Fix casting variables for 64 Bits arch.

* Sat Jun 29 2013 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.5
- Remove glib forgetted dependencies. 
- Fix ged2rss group bug.

* Wed Jun 26 2013 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.4
- Add GED Rss feature per user and per filter but the service group.

* Sat Jun 08 2013 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.3
- Add Ged 2 RSS XML feature :)

* Fri Jun 07 2013 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.2
- Compile against 64Bit with fPIC translation.
- Port to glib2 compliance GString

* Sat Jul 07 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.1
- Backport 1.4.11 patch
- 1.4.11 Correcting minor state bug when unspecified massive drop.

* Mon Jun 25 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.5.0
- Adding Time To Own Flags handling feature

* Wed May 30 2012 Jeremie Bernard <gremi@users.sourceforge.net> - 1.4.10
- Handling my database issue regarding mysql backend.

* Fri May 11 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.9
- Hacking script for migration facilities 
- Fixing 0 addition in case of uncomplete gedq -push packet.
- Change ack default time in conf file
- Remove sync as default in gedt.cfg

* Mon Apr 23 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.8
- Fixing end of heap segfault in CChunk object in case of null argument packet dropping.

* Wed Apr 18 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.7
- Allow compatibility of sync queue between 1.2.12 and 1.4 series.

* Mon Apr 16 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.6
- Fixing gedq version number

* Wed Apr 04 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.5
- Fixing duplicate id in case of multiple cross migration queue packet

* Mon Apr 02 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.4
- Fixing duplicate id using multiple SYNC queue. 
- Set AUTO_INCREMENT to all data packet tables.

* Fri Mar 30 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.3
- Fixing last id record major bug... Yeeeha !!!!

* Mon Mar 19 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.2
- Fixing SLA usec bug.

* Fri Mar 9 2012 Michael Aubertin <michael.aubertin@gmail.com> - 1.4.1
- Multiple optimisation. MySQL 5.5 compliant. Multi-table handling

* Tue Oct 4 2011 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.12
- Daemonization patch (tty detach : pgrp)

* Sun Oct 2 2011 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.11
- Backend config cache is no more written when finalizing (but when initializing)
- CREATE TABLE has been added the IF NOT EXISTS option which is permissive 
- DROP TABLE has been added the IF EXIXTS option which is permissive

* Wed Sep 14 2011 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.10
- MySQL backend query execution error handling modification

* Wed May 19 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.9
- TTL backend nrecords queue inc patch

* Wed May 12 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.8
- potential TTL backend dead threads while forking patch 

* Fri Apr 9 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.7
- mysql filters (< > ' ") options addon

* Tue Feb 9 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.6
- connect option replaces bind to specify gedq and gedt targets
- bind option remains but now forces source interface to be used

* Thu Feb 4 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.5
- gcrypt init statement and pthread protection (to avoid recurent warning logs)

* Mon Jan 18 2010 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.4
- static mysql varchar 255 => varchar N option (mysql > 5.0.3 required)
- mysql ' " < > filtering

* Wed Nov 25 2009 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.3
- mysql mode no backslash escapes option addon

* Sat May 30 2009 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.2 
- nosync flag implementation
- performance inc, light xml format option
- local file socket bindings
- ged/gedq communication improvement
- history queue gedq drop id list arg
- mysql backend proposal

* Fri Feb 20 2009 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.1 
- non root low port binding enabling
- ged/gedq security enhencement (peer data and request access notion)
- gedq sem patch (exception catch in ctx constructor)
- xml output update (root version attr, content key spec, content meta spec)
- xml recover patch (empty fields specifics)
- backend config cache flush once loaded
- async mode patch
- user meta data implementation (push/update requests specifics)
- update request reverse sync
- gedq utf8 filtering
- history queue record id addon and drop specific request modification
- ged daemon mode
- mysql backend temporary removed

* Tue Dec 30 2008 Jeremie Bernard <gremi@users.sourceforge.net> - 1.2.0 
- lzo removal, zlib use instead
- http/s tunnel implementation
- proxy basic and ntlm auth handling

* Sun Sep 14 2008 Jeremie Bernard <gremi@users.sourceforge.net> - 1.1
- xml output tree update
- packages split (backends)

* Thu Nov 29 2007 Jeremie Bernard <gremi@users.sourceforge.net> - 1.1
- simple http proxy passthru

* Mon Sep 03 2007 Jeremie Bernard <gremi@users.sourceforge.net> - 1.0b
- first beta package including mysql and hash berkeley backends
