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



%prep
%setup -q


%build
# this requires perl-Frontier-RPC-Client.noarch
src/create-channel-to-update.pl --help > src/README.help


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/local/bin
install -m755 src/create-channel-to-update.pl %{buildroot}/usr/local/bin


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc src/README.help
%doc src/COPYING
%doc src/README
/usr/local/bin/create-channel-to-update.pl



%changelog

