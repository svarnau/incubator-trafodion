Summary:	Ambari management pack for Trafodion
Name:		traf_ambari
Version:	%{version}
Release:	%{release}
AutoReqProv:	no
License:	TBD
Group:		Applications/Databases
Source0:        ambari_rpm.tar.gz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}
URL:            http://trafodion.incubator.apache.org

Requires: ambari-server

Prefix: /opt/trafodion

%description
This extension enables management of Trafodion via Ambari.


%prep
%setup -b 0 -n %{name} -c

%build

%install
cd %{_builddir}
mkdir -p %{buildroot}/opt/trafodion
cp -rf %{name}/* %{buildroot}/opt/trafodion

%post
$RPM_INSTALL_PREFIX/mpack-install/am_install.sh "$RPM_INSTALL_PREFIX"

%clean
/bin/rm -rf %{buildroot}

%files
/opt/trafodion/traf-mpack/
/opt/trafodion/mpack-install/

%changelog
* Fri Oct 21 2016 Steve Varnau
- ver 1.0
