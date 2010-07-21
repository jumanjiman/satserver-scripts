Name:		create-channel-to-update
Version:	0.1
Release:	1%{?dist}
Summary:	create or upgrade channel to specific revision level on RHN Satellite

Group:		Admin
License:	GPLv2
URL:		http://github.com/jumanjiman/satserver-scripts
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
buildarch:	noarch

# 
# note: perl provides Data::Dumper and CGI
BuildRequires:	perl
BuildRequires:	perl-Frontier-RPC-Client.noarch

Requires:		perl
Requires:		perl-Frontier-RPC-Client.noarch

%description
This script can create a channel to a specific update level
(i.e. RHEL4u3) or upgrade an existing channel to a higher update
level on an RHN Satellite.

Note that you must edit variables in create-channel-to-update.pl
before using.



%prep
%setup -q


%build
# this requires perl-Frontier-RPC-Client.noarch
src/create-channel-to-update.pl --help > src/README.help


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/%{name}/{data,bin}
install -m755 src/create-channel-to-update.pl %{buildroot}/opt/%{name}/bin/
install -m644 src/data/* %{buildroot}/opt/%{name}/data/


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc src/README.first
%doc src/README.help
%doc src/COPYING
%doc src/README
%config /opt/%{name}/bin/create-channel-to-update.pl
%config /opt/%{name}/data
%config /opt/%{name}/data/2.1-GOLD-AS-i386
%config /opt/%{name}/data/2.1-GOLD-AS-ia64
%config /opt/%{name}/data/2.1-GOLD-ES-i386
%config /opt/%{name}/data/2.1-GOLD-WS-i386
%config /opt/%{name}/data/2.1-U2-AS-i386
%config /opt/%{name}/data/2.1-U2-AS-ia64
%config /opt/%{name}/data/2.1-U2-ES-i386
%config /opt/%{name}/data/2.1-U2-WS-i386
%config /opt/%{name}/data/2.1-U3-AS-i386
%config /opt/%{name}/data/2.1-U3-AS-ia64
%config /opt/%{name}/data/2.1-U3-ES-i386
%config /opt/%{name}/data/2.1-U3-WS-i386
%config /opt/%{name}/data/2.1-U4-AS-i386
%config /opt/%{name}/data/2.1-U4-AS-ia64
%config /opt/%{name}/data/2.1-U4-ES-i386
%config /opt/%{name}/data/2.1-U4-WS-i386
%config /opt/%{name}/data/2.1-U5-AS-i386
%config /opt/%{name}/data/2.1-U5-AS-ia64
%config /opt/%{name}/data/2.1-U5-ES-i386
%config /opt/%{name}/data/2.1-U5-WS-i386
%config /opt/%{name}/data/2.1-U6-AS-i386
%config /opt/%{name}/data/2.1-U6-AS-ia64
%config /opt/%{name}/data/2.1-U6-ES-i386
%config /opt/%{name}/data/2.1-U6-WS-i386
%config /opt/%{name}/data/3-GOLD-AS-i386
%config /opt/%{name}/data/3-GOLD-AS-ia64
%config /opt/%{name}/data/3-GOLD-AS-ppc
%config /opt/%{name}/data/3-GOLD-AS-s390
%config /opt/%{name}/data/3-GOLD-AS-s390x
%config /opt/%{name}/data/3-GOLD-AS-x86_64
%config /opt/%{name}/data/3-GOLD-ES-i386
%config /opt/%{name}/data/3-GOLD-ES-ia64
%config /opt/%{name}/data/3-GOLD-ES-x86_64
%config /opt/%{name}/data/3-GOLD-WS-i386
%config /opt/%{name}/data/3-GOLD-WS-ia64
%config /opt/%{name}/data/3-GOLD-WS-x86_64
%config /opt/%{name}/data/3-U1-AS-i386
%config /opt/%{name}/data/3-U1-AS-ia64
%config /opt/%{name}/data/3-U1-AS-ppc
%config /opt/%{name}/data/3-U1-AS-s390
%config /opt/%{name}/data/3-U1-AS-s390x
%config /opt/%{name}/data/3-U1-AS-x86_64
%config /opt/%{name}/data/3-U1-ES-i386
%config /opt/%{name}/data/3-U1-ES-ia64
%config /opt/%{name}/data/3-U1-ES-x86_64
%config /opt/%{name}/data/3-U1-WS-i386
%config /opt/%{name}/data/3-U1-WS-ia64
%config /opt/%{name}/data/3-U1-WS-x86_64
%config /opt/%{name}/data/3-U2-AS-i386
%config /opt/%{name}/data/3-U2-AS-ia64
%config /opt/%{name}/data/3-U2-AS-ppc
%config /opt/%{name}/data/3-U2-AS-s390
%config /opt/%{name}/data/3-U2-AS-s390x
%config /opt/%{name}/data/3-U2-AS-x86_64
%config /opt/%{name}/data/3-U2-Desktop-i386
%config /opt/%{name}/data/3-U2-Desktop-x86_64
%config /opt/%{name}/data/3-U2-ES-i386
%config /opt/%{name}/data/3-U2-ES-ia64
%config /opt/%{name}/data/3-U2-ES-x86_64
%config /opt/%{name}/data/3-U2-WS-i386
%config /opt/%{name}/data/3-U2-WS-ia64
%config /opt/%{name}/data/3-U2-WS-x86_64
%config /opt/%{name}/data/3-U3-AS-i386
%config /opt/%{name}/data/3-U3-AS-ia64
%config /opt/%{name}/data/3-U3-AS-ppc
%config /opt/%{name}/data/3-U3-AS-s390
%config /opt/%{name}/data/3-U3-AS-s390x
%config /opt/%{name}/data/3-U3-AS-x86_64
%config /opt/%{name}/data/3-U3-Desktop-i386
%config /opt/%{name}/data/3-U3-Desktop-x86_64
%config /opt/%{name}/data/3-U3-ES-i386
%config /opt/%{name}/data/3-U3-ES-ia64
%config /opt/%{name}/data/3-U3-ES-x86_64
%config /opt/%{name}/data/3-U3-WS-i386
%config /opt/%{name}/data/3-U3-WS-ia64
%config /opt/%{name}/data/3-U3-WS-x86_64
%config /opt/%{name}/data/3-U4-AS-i386
%config /opt/%{name}/data/3-U4-AS-ia64
%config /opt/%{name}/data/3-U4-AS-ppc
%config /opt/%{name}/data/3-U4-AS-s390
%config /opt/%{name}/data/3-U4-AS-s390x
%config /opt/%{name}/data/3-U4-AS-x86_64
%config /opt/%{name}/data/3-U4-Desktop-i386
%config /opt/%{name}/data/3-U4-Desktop-x86_64
%config /opt/%{name}/data/3-U4-ES-i386
%config /opt/%{name}/data/3-U4-ES-ia64
%config /opt/%{name}/data/3-U4-ES-x86_64
%config /opt/%{name}/data/3-U4-WS-i386
%config /opt/%{name}/data/3-U4-WS-ia64
%config /opt/%{name}/data/3-U4-WS-x86_64
%config /opt/%{name}/data/3-U5-AS-i386
%config /opt/%{name}/data/3-U5-AS-ia64
%config /opt/%{name}/data/3-U5-AS-ppc
%config /opt/%{name}/data/3-U5-AS-s390
%config /opt/%{name}/data/3-U5-AS-s390x
%config /opt/%{name}/data/3-U5-AS-x86_64
%config /opt/%{name}/data/3-U5-Desktop-i386
%config /opt/%{name}/data/3-U5-Desktop-x86_64
%config /opt/%{name}/data/3-U5-ES-i386
%config /opt/%{name}/data/3-U5-ES-ia64
%config /opt/%{name}/data/3-U5-ES-x86_64
%config /opt/%{name}/data/3-U5-WS-i386
%config /opt/%{name}/data/3-U5-WS-ia64
%config /opt/%{name}/data/3-U5-WS-x86_64
%config /opt/%{name}/data/3-U6-AS-i386
%config /opt/%{name}/data/3-U6-AS-ia64
%config /opt/%{name}/data/3-U6-AS-ppc
%config /opt/%{name}/data/3-U6-AS-s390
%config /opt/%{name}/data/3-U6-AS-s390x
%config /opt/%{name}/data/3-U6-AS-x86_64
%config /opt/%{name}/data/3-U6-Desktop-i386
%config /opt/%{name}/data/3-U6-Desktop-x86_64
%config /opt/%{name}/data/3-U6-ES-i386
%config /opt/%{name}/data/3-U6-ES-ia64
%config /opt/%{name}/data/3-U6-ES-x86_64
%config /opt/%{name}/data/3-U6-WS-i386
%config /opt/%{name}/data/3-U6-WS-ia64
%config /opt/%{name}/data/3-U6-WS-x86_64
%config /opt/%{name}/data/3-U7-AS-i386
%config /opt/%{name}/data/3-U7-AS-ia64
%config /opt/%{name}/data/3-U7-AS-ppc
%config /opt/%{name}/data/3-U7-AS-s390
%config /opt/%{name}/data/3-U7-AS-s390x
%config /opt/%{name}/data/3-U7-AS-x86_64
%config /opt/%{name}/data/3-U7-Desktop-i386
%config /opt/%{name}/data/3-U7-Desktop-x86_64
%config /opt/%{name}/data/3-U7-ES-i386
%config /opt/%{name}/data/3-U7-ES-ia64
%config /opt/%{name}/data/3-U7-ES-x86_64
%config /opt/%{name}/data/3-U7-WS-i386
%config /opt/%{name}/data/3-U7-WS-ia64
%config /opt/%{name}/data/3-U7-WS-x86_64
%config /opt/%{name}/data/3-U8-AS-i386
%config /opt/%{name}/data/3-U8-AS-ia64
%config /opt/%{name}/data/3-U8-AS-ppc
%config /opt/%{name}/data/3-U8-AS-s390
%config /opt/%{name}/data/3-U8-AS-s390x
%config /opt/%{name}/data/3-U8-AS-x86_64
%config /opt/%{name}/data/3-U8-Desktop-i386
%config /opt/%{name}/data/3-U8-Desktop-x86_64
%config /opt/%{name}/data/3-U8-ES-i386
%config /opt/%{name}/data/3-U8-ES-ia64
%config /opt/%{name}/data/3-U8-ES-x86_64
%config /opt/%{name}/data/3-U8-WS-i386
%config /opt/%{name}/data/3-U8-WS-ia64
%config /opt/%{name}/data/3-U8-WS-x86_64
%config /opt/%{name}/data/3-U9-AS-i386
%config /opt/%{name}/data/3-U9-AS-ia64
%config /opt/%{name}/data/3-U9-AS-ppc
%config /opt/%{name}/data/3-U9-AS-s390
%config /opt/%{name}/data/3-U9-AS-s390x
%config /opt/%{name}/data/3-U9-AS-x86_64
%config /opt/%{name}/data/3-U9-Desktop-i386
%config /opt/%{name}/data/3-U9-Desktop-x86_64
%config /opt/%{name}/data/3-U9-ES-i386
%config /opt/%{name}/data/3-U9-ES-ia64
%config /opt/%{name}/data/3-U9-ES-x86_64
%config /opt/%{name}/data/3-U9-WS-i386
%config /opt/%{name}/data/3-U9-WS-ia64
%config /opt/%{name}/data/3-U9-WS-x86_64
%config /opt/%{name}/data/4-GOLD-AS-i386
%config /opt/%{name}/data/4-GOLD-AS-ia64
%config /opt/%{name}/data/4-GOLD-AS-ppc
%config /opt/%{name}/data/4-GOLD-AS-s390
%config /opt/%{name}/data/4-GOLD-AS-s390x
%config /opt/%{name}/data/4-GOLD-AS-x86_64
%config /opt/%{name}/data/4-GOLD-Desktop-i386
%config /opt/%{name}/data/4-GOLD-Desktop-x86_64
%config /opt/%{name}/data/4-GOLD-ES-i386
%config /opt/%{name}/data/4-GOLD-ES-ia64
%config /opt/%{name}/data/4-GOLD-ES-x86_64
%config /opt/%{name}/data/4-GOLD-WS-i386
%config /opt/%{name}/data/4-GOLD-WS-ia64
%config /opt/%{name}/data/4-GOLD-WS-x86_64
%config /opt/%{name}/data/4-U1-AS-i386
%config /opt/%{name}/data/4-U1-AS-ia64
%config /opt/%{name}/data/4-U1-AS-ppc
%config /opt/%{name}/data/4-U1-AS-s390
%config /opt/%{name}/data/4-U1-AS-s390x
%config /opt/%{name}/data/4-U1-AS-x86_64
%config /opt/%{name}/data/4-U1-Desktop-i386
%config /opt/%{name}/data/4-U1-Desktop-x86_64
%config /opt/%{name}/data/4-U1-ES-i386
%config /opt/%{name}/data/4-U1-ES-ia64
%config /opt/%{name}/data/4-U1-ES-x86_64
%config /opt/%{name}/data/4-U1-WS-i386
%config /opt/%{name}/data/4-U1-WS-ia64
%config /opt/%{name}/data/4-U1-WS-x86_64
%config /opt/%{name}/data/4-U2-AS-i386
%config /opt/%{name}/data/4-U2-AS-ia64
%config /opt/%{name}/data/4-U2-AS-ppc
%config /opt/%{name}/data/4-U2-AS-s390
%config /opt/%{name}/data/4-U2-AS-s390x
%config /opt/%{name}/data/4-U2-AS-x86_64
%config /opt/%{name}/data/4-U2-Desktop-i386
%config /opt/%{name}/data/4-U2-Desktop-x86_64
%config /opt/%{name}/data/4-U2-ES-i386
%config /opt/%{name}/data/4-U2-ES-ia64
%config /opt/%{name}/data/4-U2-ES-x86_64
%config /opt/%{name}/data/4-U2-WS-i386
%config /opt/%{name}/data/4-U2-WS-ia64
%config /opt/%{name}/data/4-U2-WS-x86_64
%config /opt/%{name}/data/4-U3-AS-i386
%config /opt/%{name}/data/4-U3-AS-ia64
%config /opt/%{name}/data/4-U3-AS-ppc
%config /opt/%{name}/data/4-U3-AS-s390
%config /opt/%{name}/data/4-U3-AS-s390x
%config /opt/%{name}/data/4-U3-AS-x86_64
%config /opt/%{name}/data/4-U3-Desktop-i386
%config /opt/%{name}/data/4-U3-Desktop-x86_64
%config /opt/%{name}/data/4-U3-ES-i386
%config /opt/%{name}/data/4-U3-ES-ia64
%config /opt/%{name}/data/4-U3-ES-x86_64
%config /opt/%{name}/data/4-U3-WS-i386
%config /opt/%{name}/data/4-U3-WS-ia64
%config /opt/%{name}/data/4-U3-WS-x86_64
%config /opt/%{name}/data/4-U4-AS-i386
%config /opt/%{name}/data/4-U4-AS-ia64
%config /opt/%{name}/data/4-U4-AS-ppc
%config /opt/%{name}/data/4-U4-AS-s390
%config /opt/%{name}/data/4-U4-AS-s390x
%config /opt/%{name}/data/4-U4-AS-x86_64
%config /opt/%{name}/data/4-U4-Desktop-i386
%config /opt/%{name}/data/4-U4-Desktop-x86_64
%config /opt/%{name}/data/4-U4-ES-i386
%config /opt/%{name}/data/4-U4-ES-ia64
%config /opt/%{name}/data/4-U4-ES-x86_64
%config /opt/%{name}/data/4-U4-WS-i386
%config /opt/%{name}/data/4-U4-WS-ia64
%config /opt/%{name}/data/4-U4-WS-x86_64
%config /opt/%{name}/data/4-U5-AS-i386
%config /opt/%{name}/data/4-U5-AS-ia64
%config /opt/%{name}/data/4-U5-AS-ppc
%config /opt/%{name}/data/4-U5-AS-s390
%config /opt/%{name}/data/4-U5-AS-s390x
%config /opt/%{name}/data/4-U5-AS-x86_64
%config /opt/%{name}/data/4-U5-Desktop-i386
%config /opt/%{name}/data/4-U5-Desktop-x86_64
%config /opt/%{name}/data/4-U5-ES-i386
%config /opt/%{name}/data/4-U5-ES-ia64
%config /opt/%{name}/data/4-U5-ES-x86_64
%config /opt/%{name}/data/4-U5-WS-i386
%config /opt/%{name}/data/4-U5-WS-ia64
%config /opt/%{name}/data/4-U5-WS-x86_64
%config /opt/%{name}/data/4-U6-AS-i386
%config /opt/%{name}/data/4-U6-AS-ia64
%config /opt/%{name}/data/4-U6-AS-ppc
%config /opt/%{name}/data/4-U6-AS-s390
%config /opt/%{name}/data/4-U6-AS-s390x
%config /opt/%{name}/data/4-U6-AS-x86_64
%config /opt/%{name}/data/4-U6-Desktop-i386
%config /opt/%{name}/data/4-U6-Desktop-x86_64
%config /opt/%{name}/data/4-U6-ES-i386
%config /opt/%{name}/data/4-U6-ES-ia64
%config /opt/%{name}/data/4-U6-ES-x86_64
%config /opt/%{name}/data/4-U6-WS-i386
%config /opt/%{name}/data/4-U6-WS-ia64
%config /opt/%{name}/data/4-U6-WS-x86_64
%config /opt/%{name}/data/5-GOLD-Client-i386
%config /opt/%{name}/data/5-GOLD-Client-i386-VT
%config /opt/%{name}/data/5-GOLD-Client-i386-Workstation
%config /opt/%{name}/data/5-GOLD-Client-x86_64
%config /opt/%{name}/data/5-GOLD-Client-x86_64-VT
%config /opt/%{name}/data/5-GOLD-Client-x86_64-Workstation
%config /opt/%{name}/data/5-GOLD-Server-i386
%config /opt/%{name}/data/5-GOLD-Server-i386-Cluster
%config /opt/%{name}/data/5-GOLD-Server-i386-ClusterStorage
%config /opt/%{name}/data/5-GOLD-Server-i386-VT
%config /opt/%{name}/data/5-GOLD-Server-ia64
%config /opt/%{name}/data/5-GOLD-Server-ia64-Cluster
%config /opt/%{name}/data/5-GOLD-Server-ia64-ClusterStorage
%config /opt/%{name}/data/5-GOLD-Server-ia64-VT
%config /opt/%{name}/data/5-GOLD-Server-ppc
%config /opt/%{name}/data/5-GOLD-Server-s390x
%config /opt/%{name}/data/5-GOLD-Server-x86_64
%config /opt/%{name}/data/5-GOLD-Server-x86_64-Cluster
%config /opt/%{name}/data/5-GOLD-Server-x86_64-ClusterStorage
%config /opt/%{name}/data/5-GOLD-Server-x86_64-VT
%config /opt/%{name}/data/5-U1-Client-i386
%config /opt/%{name}/data/5-U1-Client-i386-VT
%config /opt/%{name}/data/5-U1-Client-i386-Workstation
%config /opt/%{name}/data/5-U1-Client-x86_64
%config /opt/%{name}/data/5-U1-Client-x86_64-VT
%config /opt/%{name}/data/5-U1-Client-x86_64-Workstation
%config /opt/%{name}/data/5-U1-Server-i386
%config /opt/%{name}/data/5-U1-Server-i386-Cluster
%config /opt/%{name}/data/5-U1-Server-i386-ClusterStorage
%config /opt/%{name}/data/5-U1-Server-i386-VT
%config /opt/%{name}/data/5-U1-Server-ia64
%config /opt/%{name}/data/5-U1-Server-ia64-Cluster
%config /opt/%{name}/data/5-U1-Server-ia64-ClusterStorage
%config /opt/%{name}/data/5-U1-Server-ia64-VT
%config /opt/%{name}/data/5-U1-Server-ppc
%config /opt/%{name}/data/5-U1-Server-s390x
%config /opt/%{name}/data/5-U1-Server-x86_64
%config /opt/%{name}/data/5-U1-Server-x86_64-Cluster
%config /opt/%{name}/data/5-U1-Server-x86_64-ClusterStorage
%config /opt/%{name}/data/5-U1-Server-x86_64-VT


%changelog
* Wed Jul 21 2010 Paul Morgan <pmorgan@redhat.com> 0.1-1
- new package built with tito


