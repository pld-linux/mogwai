#
# Conditional build:
%bcond_without	static_libs	# static libraries
%bcond_with	libsoup2	# libsoup 2 instead of libsoup3
#
Summary:	Mogwai - monitor network usage and schedule downloads do minimize their cost
Summary(pl.UTF-8):	Mogwai - monitorowanie wykorzystania sieci i planowanie pobrań tak, aby zminimalizować ich koszt
Name:		mogwai
Version:	0.3.0
Release:	2
License:	LGPL v2.1+
Group:		Libraries
#Source0Download: https://gitlab.freedesktop.org/pwithnall/mogwai/-/tags
Source0:	https://gitlab.freedesktop.org/pwithnall/mogwai/-/archive/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	147fe0243383a14aab5a0fd837de5825
Patch0:		%{name}-systemd.patch
URL:		https://gitlab.freedesktop.org/pwithnall/mogwai
BuildRequires:	NetworkManager-devel >= 2:1.8.0
BuildRequires:	glib2-devel >= 1:2.57.1
BuildRequires:	libgsystemservice-devel >= 0.1.0
%{?with_libsoup2:BuildRequires:	libsoup-devel >= 2.42}
%{!?with_libsoup2:BuildRequires:	libsoup3-devel >= 3.0}
BuildRequires:	meson >= 0.50.0
BuildRequires:	ninja >= 1.5
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	systemd-devel
Requires:	%{name}-libs = %{version}-%{release}
%{?with_libsoup2:Requires:	libsoup >= 2.42}
%{!?with_libsoup2:Requires:	libsoup3 >= 3.0}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Mogwai allows systems to take advantage of reduced cost bandwidth at
off-peak times of day. It provides a monitoring daemon which checks
bandwidth usage, a scheduling daemon which prioritises downloads to
minimise cost, and a tariff library which describes different data
plans.

This package contains client tools.

%description -l pl.UTF-8
Mogwai pozwala systemom wykorzystywać mniejszy koszt pobierania danych
poza godzinami szczytu. Zawiera demona monitorującego, sprawdzającego
wykorzystanie sieci, demona planującego, który określa priorytet
pobrań w celu zminimalizowania kosztu oraz bibliotekę taryfikującą,
opisującą różne plany danych.

Ten pakiet zawiera narzędzia klienckie.

%package libs
Summary:	Mogwai shared libraries
Summary(pl.UTF-8):	Biblioteki współdzielone Mogwai
Group:		Libraries
Requires:	glib2 >= 1:2.57.1

%description libs
Mogwai shared libraries.

%description libs -l pl.UTF-8
Biblioteki współdzielone Mogwai.

%package devel
Summary:	Header files for Mogwai library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki Mogwai
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	glib2-devel >= 1:2.57.1

%description devel
Header files for Mogwai library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki Mogwai.

%package static
Summary:	Static Mogwai library
Summary(pl.UTF-8):	Statyczna biblioteka Mogwai
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Mogwai library.

%description static -l pl.UTF-8
Statyczna biblioteka Mogwai.

%package scheduled
Summary:	Mogwai scheduling daemon
Summary(pl.UTF-8):	Demon planujący Mogwai
Group:		Daemons
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun,postun):	systemd-units >= 38
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires:	%{name}-libs = %{version}-%{release}
Requires:	NetworkManager >= 2:1.8.0
Requires:	libgsystemservice >= 0.1.0
Requires:	systemd
Provides:	group(mogwai-scheduled)
Provides:	user(mogwai-scheduled)

%description scheduled
Mogwai allows systems to take advantage of reduced cost bandwidth at
off-peak times of day. It provides a monitoring daemon which checks
bandwidth usage, a scheduling daemon which prioritises downloads to
minimise cost, and a tariff library which describes different data
plans.

This package contains scheduling daemon.

%description scheduled -l pl.UTF-8
Mogwai pozwala systemom wykorzystywać mniejszy koszt pobierania danych
poza godzinami szczytu. Zawiera demona monitorującego, sprawdzającego
wykorzystanie sieci, demona planującego, który określa priorytet
pobrań w celu zminimalizowania kosztu oraz bibliotekę taryfikującą,
opisującą różne plany danych.

Ten pakiet zawiera demona planującego.

%prep
%setup -q
%patch -P0 -p1

%build
%meson \
	%{!?with_static_libs:--default-library=shared} \
	%{!?with_libsoup3:-Dsoup2=true}

%meson_build

%install
rm -rf $RPM_BUILD_ROOT

%meson_install

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%pre	scheduled
%groupadd -g 337 mogwai-scheduled
%useradd -u 337 -d /usr/share/empty -g mogwai-scheduled -c 'Mogwai Scheduling Daemon' mogwai-scheduled

%post	scheduled
%systemd_post mogwai-scheduled.service

%preun	scheduled
%systemd_preun mogwai-scheduled.service

%postun	scheduled
%systemd_reload
if [ "$1" = "0" ]; then
	%userremove mogwai-scheduled
	%groupremove mogwai-scheduled
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/mogwai-schedule-client-1
%attr(755,root,root) %{_bindir}/mogwai-tariff-0
%{_mandir}/man8/mogwai-schedule-client.8*
%{_mandir}/man8/mogwai-tariff.8*

%files libs
%defattr(644,root,root,755)
%doc AUTHORS README.md
%attr(755,root,root) %{_libdir}/libmogwai-schedule-client-0.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmogwai-schedule-client-0.so.0
%attr(755,root,root) %{_libdir}/libmogwai-tariff-0.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmogwai-tariff-0.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmogwai-schedule-client-0.so
%attr(755,root,root) %{_libdir}/libmogwai-tariff-0.so
%{_includedir}/mogwai-schedule-client-0
%{_includedir}/mogwai-tariff-0
%{_pkgconfigdir}/mogwai-schedule-client-0.pc
%{_pkgconfigdir}/mogwai-tariff-0.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libmogwai-schedule-client-0.a
%{_libdir}/libmogwai-tariff-0.a
%endif

%files scheduled
%defattr(644,root,root,755)
%attr(755,root,root) %{_libexecdir}/mogwai-scheduled1
%{systemdunitdir}/mogwai-scheduled.service
%{_prefix}/lib/sysusers.d/mogwai-scheduled.conf
%{_datadir}/dbus-1/system-services/com.endlessm.MogwaiSchedule1.service
%{_datadir}/dbus-1/system.d/com.endlessm.MogwaiSchedule1.conf
%{_datadir}/polkit-1/rules.d/com.endlessm.MogwaiSchedule1.rules
%{_mandir}/man8/mogwai-scheduled.8*
