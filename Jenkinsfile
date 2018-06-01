#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg


def repo_name = 'kano-peripherals'


stage ('Test') {
    def dep_repos = [
        "kano-i18n",
        "kano-settings",
        "kano-toolset"
    ]
	python_test_env(dep_repos) { python_path_var ->
    }
}


stage ('Build') {
    autobuild_repo_pkg "$repo_name"
}

stage ('Docs') {
    build_docs "$repo_name"
}
