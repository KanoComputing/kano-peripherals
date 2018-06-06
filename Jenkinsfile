#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg


def repo_name = 'kano-peripherals'


stage ('Test') {
    def dep_repos = [
        "kano-i18n",
        "kano-profile",
        "kano-settings",
        "kano-toolset",
        "kano-widgets"
    ]
	python_test_env(dep_repos) { python_path_var ->
        // Add dependencies for pip module `dbus-python`
        sh 'ln -s /repos/kano-widgets/lxpanel-plugin-notifications/notifications.py /repos/kano-toolset/kano/'
        sh 'apt-get install -y libdbus-1-dev'
    }
}


stage ('Build') {
    autobuild_repo_pkg "$repo_name"
}

stage ('Docs') {
    build_docs "$repo_name"
}
