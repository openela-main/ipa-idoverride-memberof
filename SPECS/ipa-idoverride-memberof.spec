%global debug_package %{nil}
%define plugin_name idoverride-memberof
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
%define ipa_python_sitelib %{python3_sitelib}
%else
%define ipa_python_sitelib %{python2_sitelib}
%endif

Name:           ipa-%{plugin_name}
Version:        0.0.4
Release:        6%{?dist}
Summary:        RHEL IdM plugin to allow AD users to be members of IdM groups for management purposes

License:        GPLv3+
Source0:        ipa-%{plugin_name}-%{version}.tar.gz

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
BuildRequires: python3-devel
%else
BuildRequires:  python2-devel
%endif

Requires:       ipa-server-common >= 4.5
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
BuildRequires: python3-ipaserver >= 4.6.0
%else
BuildRequires:  python2-ipaserver >= 4.5
%endif

%description
This plugin adds an experimental support to RHEL IdM to allow
Active Directory users to be members of IdM groups. As result,
AD users can manage IdM resources if they are allowed to do so
by roles their groups are part of.

%package plugin
Summary:        RHEL IdM plugin to allow AD users to be members of IdM groups for management purposes
License:        GPLv3+

%description plugin
This plugin adds an experimental support to RHEL IdM to allow
Active Directory users to be members of IdM groups. As result,
AD users can manage IdM resources if they are allowed to do so
by roles their groups are part of.

%prep
%autosetup -n ipa-%{plugin_name}-%{version}

%build
touch debugfiles.list

%install
rm -rf $RPM_BUILD_ROOT
#%%__mkdir_p %buildroot/%%{ipa_python_sitelib}/ipaclient/plugins
%__mkdir_p %buildroot/%{ipa_python_sitelib}/ipaserver/plugins
%__mkdir_p %buildroot/%_datadir/ipa/schema.d
%__mkdir_p %buildroot/%_datadir/ipa/updates
%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}

for i in ipaserver ; do
	for j in $(find plugin/$i/plugins -name '*.py') ; do
		%__cp $j %buildroot/%{ipa_python_sitelib}/$i/plugins/
	done
done

for j in $(find plugin/schema.d -name '*.ldif') ; do
	%__cp $j %buildroot/%_datadir/ipa/schema.d/
done

for j in $(find plugin/updates -name '*.update') ; do
	%__cp $j %buildroot/%_datadir/ipa/updates/
done

for j in $(find plugin/ui -name '*.js') ; do
	%__cp $j %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}/
done

if test "%{plugin_name}" != "idoverride-admemberof" ; then
	pushd %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}/
	%__ln_s idoverride-admemberof.js %{plugin_name}.js
	popd
fi


%posttrans plugin
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
ipa_interp=python3
%else
ipa_interp=python2
%endif
$ipa_interp -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files plugin
%license COPYING
%doc plugin/Feature.mediawiki README.md
# There is no client-side component yet
#%%python2_sitelib/ipaclient/plugins/*
%{ipa_python_sitelib}/ipaserver/plugins/*
%_datadir/ipa/schema.d/*
%_datadir/ipa/updates/*
%_datadir/ipa/ui/js/plugins/%{plugin_name}/*

%changelog
* Mon Oct 22 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-6
- Fixes: WebUI (Default Page) for ipa-server installed on ppc64le is not loading.
- Fixes: rhbz#1639738

* Wed Oct 10 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-5
- Fix license field: use GPLv3+ instead of ambiguous GPL

* Wed Oct 03 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-4
- Fix the plugin primary JS file according to IdM Web UI requirements
- Fixes: RHELPLAN-9230

* Mon Jul 30 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-3
- Refactor spec file

* Fri Jul 27 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-2
- Build for idm module stream 4

* Fri Jan 12 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-1
- New release
- For non-admins reading memberOf from the user ID Overrride was not possible, fix it

* Wed Jan 10 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.3-1
- New release
- Show self-service to AD users only if they have no roles/privileges/permissions assigned

* Wed Dec 13 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.2-1
- New release

* Wed Dec 13 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.1-2
- Remove packaging for components that aren't needed in this plugin
- Package README.md too

* Fri Nov 10 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.1-1
- Initial release

