# Clint McGraw Scripting Portfolio

## Table of Contents

-   [Summary](#summary)
-   [Directories and Files](#directories-and-files)
    -   [Directories](#directories)
    -   [Files](#files)

## Summary

This repository contains scripts and support files written for Clint McGraw's
personal home environment. They are meant to be examples of the type of work
that Clint McGraw can produce.

**None of these scripts are from any business related work I have performed
and does not contain any proprietary information.**

I have strict rule against sharing scripts developed for any entity. That is
considered their data, is confidential, and I do not retain those scripts.

A few items to note:

1.  I know some scripts are missing proper documentation and commented. Since
    they are personal scripts, they tend to be scripts that I can read and
    quickly figure out how they work and are only in this repository as coding
    examples. However, most scripts are properly documented.

2.  I only run Ubuntu hosts in my home environment. So, these scripts are not
    designed for or tested on Windows hosts.

3.  I have an extensive Perl background, I have converted my personal home
    environment to Python and Ansible, and have no current examples of my Perl
    scripts.

4.  There are references to a `clintosaurous.ddi` module. This was from a DDI
    project I was working on for my personal environment. I have currently
    abandoned that project, but many of the examples I have are from that
    project.

5.  Although I am well versed in Microsoft Visio, I do not have a personal
    copy and cannot generate examples.

## Directories and Files

Below are a lists of the directories and files within this repository.

### Directories

| Path | Description |
| ---- | ----------- |
| ansible | Ansible inventory, variables, and playbooks located in `/etc/ansible`. |
| ansible/host_vars | Ansible host specific variable files locally located in `/etc/ansible`. |
| ansible/j2 | Ansible Jinja2 templates. |
| ansible/tasks | Ansible helper task scripts. |
| ansible/vars | General Ansible variable files imported by playbooks locally located in `/etc/ansible`. |
| lib | Module/backend library files used by other scripts. |
| lib/python | Python modules/libraries used by the included scripts. |
| lib/sh | Shell script include scripts. |
| python | Python scripts. |
| sh | Shell scripts. |
| www | Web services scripts. |

### Files

| Path | Description |
| ---- | ----------- |
| ansible/ansible.cfg | Ansible general configuration file locally located in `/etc/ansible`. |
| ansible/data-backup.yaml | Ansible playbook to backup files specified in the `ansible/vars/data-backup.yaml` locally located in `/etc/ansible`. |
| ansible/group_vars/all.yaml | Ansible variable file for all Ansible hosts locally located in `/etc/ansible/group_vars`. |
| ansible/group_vars/vmhosthost.yaml | Ansible variable file for the `vmhosthost` group locally located in `/etc/ansible/group_vars`. |
| ansible/hosts | Ansible inventory file in YAML format locally located in `/etc/ansible`. |
| ansible/host_vars/mylaptop.yaml | Ansible variable file for the `mylaptop` host locally located in `/etc/ansible/host_vars`. |
| ansible/host_vars/vmhost.yaml | Ansible variable file for the `vmhost` host locally located in `/etc/ansible/host_vars`. |
| ansible/j2/snmpd.conf.j2 | Jinja2 template for generating an SNMPD configuration file. |
| ansible/provision-apt-common.yaml | Ansible playbook for provisioning `apt` packages to Ubuntu host. |
| ansible/provision-end.yaml | Last Ansible playbook to be executed during a new Ubuntu host build. |
| ansible/provision-files-common.yaml | Ansible playbook to copy and generate common files on Ubuntu hosts. |
| ansible/provision-srv.yaml | Master Ansible playbook for provisioning a new Ubuntu host. |
| ansible/provision-system-common.yaml | Ansible playbook to provision common system level actions on Ubuntu hosts. |
| ansible/provision-ufw.yaml | Ansible playbook to provision UFW firewall rules on Ubuntu hosts. |
| ansible/provision-users-common.yaml | Ansible playbook to provision users and groups on Ubuntu hosts. |
| ansible/provision-vbox-extensions.yaml | Ansible playbook to provision VirtualBox extensions on Ubuntu hosts. |
| ansible/remote-inventory.yaml | Ansible playbook to copy Ansible inventory and variable files to a remote host. |
| ansible/system-update.yaml | Ansible playbook to perform `apt` package updates. |
| ansible/tasks/data-backup-home.yaml | Ansible playbook task include script for building files to backup in home directories for the `ansible/data-backup.yaml` playbook. |
| ansible/tasks/remote-inventory-hosts.yaml | Ansible playbook task include script for stripping out and updating hosts in an Ansible inventory file for the `ansible/remote-inventory.yaml` playbook. |
| ansible/vars/data-backup.yaml | Variable file of directories and files to be backed up by the `ansible/data-backup.yaml` playbook. |
