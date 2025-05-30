<!---
This file should not be manually edited.

This file is auto-generated via `manage-commcare-cloud make-docs > docs/source/reference/1-commcare-cloud/commands.md`

The above command and the command that generates the changelog files are included in the commcare-cloud root Makefile. So if you
run make, this file should automatically get updated.
-->

# Commands

This page explains how to run commcare-cloud commands to perform various
actions on your environment and list of all commcare-cloud commands and their
usage.

## Running Commands with `commcare-cloud`

To run any commcare-cloud command you need to install commcare-cloud first
(Refer to the installation docs) and activate its virtual environment.

All `commcare-cloud` commands take the following form:

```
commcare-cloud [--control] [--control-setup {yes,no}] <env> <command> ...
```

## Positional Arguments

### `<env>`

server environment to run against

## Options

### `--control`

Run command remotely on the control machine.

You can add `--control` _directly after_ `commcare-cloud` to any command
in order to run the command not from the local machine
using the local code,
but from from the control machine for that environment,
using the latest version of `commcare-cloud` available.

It works by issuing a command to ssh into the control machine,
update the code, and run the same command entered locally but with
`--control` removed. For long-running commands,
you will have to remain connected to the the control machine
for the entirety of the run.

### `--control-setup {yes,no}`

Implies --control, and overrides the command's run_setup_on_control_by_default value.

If set to 'yes', the latest version of the branch will be pulled and commcare-cloud will
have all its dependencies updated before the command is run.
If set to 'no', the command will be run on whatever checkout/install of commcare-cloud
is already on the control machine.
This defaults to 'yes' if command.run_setup_on_control_by_default is True, otherwise to 'no'.


### `cchq` alias

Additionally, `commcare-cloud` is aliased to the easier-to-type `cchq`
(short for "CommCare HQ"), so any command you see here can also be run
as

```
cchq <env> <command> <args...>
```

### Underlying tools and common arguments

The `commcare-cloud` command line tool is by and large a relatively
thin wrapper around the other tools it uses: `ansible`, `ansible-playbook`,
`ssh`, etc. For every command you run using `commcare-cloud`,
it will print out the underlying command that it is running,
a faint blue / cyan color.
In each case, if you copy and paste the printed command directly,
it will have essentially the same affect.
(Note too that some commands run
multiple underlying commands in sequence,
and that each command will be printed.)

Where possible, `commcare-cloud` is set up to pass any unknown arguments
to the underlying tool. In addition, there are a number of common
arguments that are recognized by many `commcare-cloud` commands,
and have similar behavior on across them. Rather than include these
on every command they apply to, we will list upfront
these common arguments and when they can be used.

To verify availability on any given command, you can always run the
command with `-h`.

### Ansible-backed commands

For most ansible-backed commands `commcare-cloud`
will run in check mode first, and then ask you to confirm
before applying the changes. Since check mode does not make sense
for all commands, there are some that do not follow this pattern
and apply the changes directly.

### `--skip-check`

When this argument is included,
the "check, ask, apply" behavior described above is circumvented,
and the command is instead applied directly

### `--quiet`

Run the command without every prompting for permission to continue.
At each point, the affirmative response is assumed.

### `--branch <branch>`

In the specific case that `commcare-cloud` has been installed from
git source in egg mode (i.e. using `pip install -e .`), it will always
check that the checked-out git branch matches the `<branch>`
that is thus passed in. If this arg is not specified,
it defaults to `master`. As a consequence, when running from git branch
`master`, there is no need to use the `--branch` arg explicitly.

### `--output [actionable|minimal]`

The callback plugin to use for generating output. See
ansible-doc -t callback -l and ansible-doc -t callback.

## List of Commands

### Internal Housekeeping for your `commcare-cloud` environments

---
#### ``validate-environment-settings`` Command

Validate your environment's configuration files

```
commcare-cloud <env> validate-environment-settings
```

As you make changes to your environment files, you can use this
command to check for validation errors or incompatibilities.

---

#### ``update-local-known-hosts`` Command

Update the local known_hosts file of the environment configuration.

```
commcare-cloud <env> update-local-known-hosts
```

You can run this on a regular basis to avoid having to `yes` through
the ssh prompts. Note that when you run this, you are implicitly
trusting that at the moment you run it, there is no man-in-the-middle
attack going on, the type of security breach that the SSH prompt
is meant to mitigate against in the first place.

---
### Ad-hoc

---
#### ``lookup`` Command

Lookup remote hostname or IP address

```
commcare-cloud <env> lookup [server]
```

##### Positional Arguments

###### `server`

Server name/group: postgresql, proxy, webworkers, ... The server
name/group may be prefixed with 'username@' to login as a
specific user and may be terminated with '[<n>]' to choose one of
multiple servers if there is more than one in the group. For
example: webworkers[0] will pick the first webworker. May also be
omitted for environments with only a single server.

Use '-' for default (django_manage[0])

---

#### ``ssh`` Command

Connect to a remote host with ssh.

```
commcare-cloud <env> ssh [--quiet] [server]
```

This will also automatically add the ssh argument `-A`
when `<server>` is `control`.

All trailing arguments are passed directly to `ssh`.

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Positional Arguments

###### `server`

Server name/group: postgresql, proxy, webworkers, ... The server
name/group may be prefixed with 'username@' to login as a
specific user and may be terminated with '[<n>]' to choose one of
multiple servers if there is more than one in the group. For
example: webworkers[0] will pick the first webworker. May also be
omitted for environments with only a single server.

Use '-' for default (django_manage[0])

##### Options

###### `--quiet`

Don't output the command to be run.

---

#### ``audit-environment`` Command

This command gathers information about your current environment's state.

```
commcare-cloud <env> audit-environment [--use-factory-auth]
```

State information is saved in the '~/.commcare-cloud/audits' directory. It is a good idea to run this before making any major changes to your environment, as it allows you to have a record of your environment's current state.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``scp`` Command

Copy file(s) over SSH.

```
commcare-cloud <env> scp [--quiet] source target
```

If a remote host is not specified in either the `source` or
`target`, the `source` host defaults to `django_manage[0]`.

Examples:

Copy remote `django_manage` file to local current directory
```
cchq <env> scp /tmp/file.txt .
```

Copy remote .txt files to local /texts/ directory
```
cchq <env> scp webworkers[0]:'/tmp/*.txt' /texts/
```

Copy local file to remote path
```
cchq <env> scp file.txt control:/tmp/other.txt
```

Limitations:

- Multiple `source` arguments are not supported.
- File paths do not auto-complete.
- Unlike normal `scp`, options with values are most easily passed
  after the `target` argument.
- `scp://` URIs are not supported.
- Copy from remote to remote is not supported.
- Probably many more.

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Positional Arguments

###### `source`

Local pathname or remote host with optional path in the form [user@]host:[path].

###### `target`

Local pathname or remote host with optional path in the form [user@]host:[path].

##### Options

###### `--quiet`

Don't output the command to be run.

---

#### ``run-module`` Command

Run an arbitrary Ansible module.

```
commcare-cloud <env> run-module [--use-factory-auth] inventory_group module module_args
```

##### Example

To print out the `inventory_hostname` ansible variable for each machine, run
```
commcare-cloud <env> run-module all debug "msg={{ '{{' }} inventory_hostname }}"
```

##### Positional Arguments

###### `inventory_group`

Machines to run on. Is anything that could be used in as a value for
`hosts` in an playbook "play", e.g.
`all` for all machines,
`webworkers` for a single group,
`celery:pillowtop` for multiple groups, etc.
See the description in [this blog](http://goinbigdata.com/understanding-ansible-patterns/)
for more detail in what can go here.

###### `module`

The name of the ansible module to run. Complete list of built-in modules can be found at
[Module Index](http://docs.ansible.com/ansible/latest/modules/modules_by_category.html).

###### `module_args`

Args for the module, formatted as a single string.
(Tip: put quotes around it, as it will likely contain spaces.)
Both `arg1=value1 arg2=value2` syntax
and `{"arg1": "value1", "arg2": "value2"}` syntax are accepted.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

##### The ansible options below are available as well
```
  --list-hosts          outputs a list of matching hosts; does not execute
                        anything else
  --playbook-dir BASEDIR
                        Since this tool does not use playbooks, use this as a
                        substitute playbook directory.This sets the relative
                        path for many features including roles/ group_vars/
                        etc.
  --syntax-check        perform a syntax check on the playbook, but do not
                        execute it
  --task-timeout TASK_TIMEOUT
                        set task timeout limit in seconds, must be positive
                        integer.
  --vault-id VAULT_IDS  the vault identity to use
  --version             show program's version number, config file location,
                        configured module search path, module location,
                        executable location and exit
  -B SECONDS, --background SECONDS
                        run asynchronously, failing after X seconds
                        (default=N/A)
  -M MODULE_PATH, --module-path MODULE_PATH
                        prepend colon-separated path(s) to module library (def
                        ault=~/.ansible/plugins/modules:/usr/share/ansible/plu
                        gins/modules)
  -P POLL_INTERVAL, --poll POLL_INTERVAL
                        set the poll interval if using -B (default=15)
  -e EXTRA_VARS, --extra-vars EXTRA_VARS
                        set additional variables as key=value or YAML/JSON, if
                        filename prepend with @
  -f FORKS, --forks FORKS
                        specify number of parallel processes to use
                        (default=50)
  -l SUBSET, --limit SUBSET
                        further limit selected hosts to an additional pattern
  -o, --one-line        condense output
  -t TREE, --tree TREE  log output to this directory
  -v, --verbose         verbose mode (-vvv for more, -vvvv to enable
                        connection debugging)

```
##### Privilege Escalation Options
```
  control how and which user you become as on target hosts

  --become-method BECOME_METHOD
                        privilege escalation method to use (default=sudo), use
                        `ansible-doc -t become -l` to list valid choices.
  -K, --ask-become-pass
                        ask for privilege escalation password

```
##### Connection Options
```
  control as whom and how to connect to hosts

  --private-key PRIVATE_KEY_FILE, --key-file PRIVATE_KEY_FILE
                        use this file to authenticate the connection
  --scp-extra-args SCP_EXTRA_ARGS
                        specify extra arguments to pass to scp only (e.g. -l)
  --sftp-extra-args SFTP_EXTRA_ARGS
                        specify extra arguments to pass to sftp only (e.g. -f,
                        -l)
  --ssh-common-args SSH_COMMON_ARGS
                        specify common arguments to pass to sftp/scp/ssh (e.g.
                        ProxyCommand)
  --ssh-extra-args SSH_EXTRA_ARGS
                        specify extra arguments to pass to ssh only (e.g. -R)
  -T TIMEOUT, --timeout TIMEOUT
                        override the connection timeout in seconds
                        (default=30)
  -c CONNECTION, --connection CONNECTION
                        connection type to use (default=smart)
  -k, --ask-pass        ask for connection password
  -u REMOTE_USER, --user REMOTE_USER
                        connect as this user (default=None)

Some actions do not make sense in Ad-Hoc (include, meta, etc)
```

---

#### ``run-shell-command`` Command

Run an arbitrary command via the Ansible shell module.

```
commcare-cloud <env> run-shell-command [--silence-warnings] [--use-factory-auth] inventory_group shell_command
```

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Example

```
commcare-cloud <env> run-shell-command all 'df -h | grep /opt/data'
```

to get disk usage stats for `/opt/data` on every machine.

##### Positional Arguments

###### `inventory_group`

Machines to run on. Is anything that could be used in as a value for
`hosts` in an playbook "play", e.g.
`all` for all machines,
`webworkers` for a single group,
`celery:pillowtop` for multiple groups, etc.
See the description in [this blog](http://goinbigdata.com/understanding-ansible-patterns/)
for more detail in what can go here.

###### `shell_command`

Command to run remotely.
(Tip: put quotes around it, as it will likely contain spaces.)
Cannot being with `sudo`; to do that use the ansible `--become` option.

##### Options

###### `--silence-warnings`

Silence shell warnings (such as to use another module instead).

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

##### The ansible options below are available as well
```
  --list-hosts          outputs a list of matching hosts; does not execute
                        anything else
  --playbook-dir BASEDIR
                        Since this tool does not use playbooks, use this as a
                        substitute playbook directory.This sets the relative
                        path for many features including roles/ group_vars/
                        etc.
  --syntax-check        perform a syntax check on the playbook, but do not
                        execute it
  --task-timeout TASK_TIMEOUT
                        set task timeout limit in seconds, must be positive
                        integer.
  --vault-id VAULT_IDS  the vault identity to use
  --version             show program's version number, config file location,
                        configured module search path, module location,
                        executable location and exit
  -B SECONDS, --background SECONDS
                        run asynchronously, failing after X seconds
                        (default=N/A)
  -M MODULE_PATH, --module-path MODULE_PATH
                        prepend colon-separated path(s) to module library (def
                        ault=~/.ansible/plugins/modules:/usr/share/ansible/plu
                        gins/modules)
  -P POLL_INTERVAL, --poll POLL_INTERVAL
                        set the poll interval if using -B (default=15)
  -e EXTRA_VARS, --extra-vars EXTRA_VARS
                        set additional variables as key=value or YAML/JSON, if
                        filename prepend with @
  -f FORKS, --forks FORKS
                        specify number of parallel processes to use
                        (default=50)
  -l SUBSET, --limit SUBSET
                        further limit selected hosts to an additional pattern
  -o, --one-line        condense output
  -t TREE, --tree TREE  log output to this directory
  -v, --verbose         verbose mode (-vvv for more, -vvvv to enable
                        connection debugging)

```
##### Privilege Escalation Options
```
  control how and which user you become as on target hosts

  --become-method BECOME_METHOD
                        privilege escalation method to use (default=sudo), use
                        `ansible-doc -t become -l` to list valid choices.
  -K, --ask-become-pass
                        ask for privilege escalation password

```
##### Connection Options
```
  control as whom and how to connect to hosts

  --private-key PRIVATE_KEY_FILE, --key-file PRIVATE_KEY_FILE
                        use this file to authenticate the connection
  --scp-extra-args SCP_EXTRA_ARGS
                        specify extra arguments to pass to scp only (e.g. -l)
  --sftp-extra-args SFTP_EXTRA_ARGS
                        specify extra arguments to pass to sftp only (e.g. -f,
                        -l)
  --ssh-common-args SSH_COMMON_ARGS
                        specify common arguments to pass to sftp/scp/ssh (e.g.
                        ProxyCommand)
  --ssh-extra-args SSH_EXTRA_ARGS
                        specify extra arguments to pass to ssh only (e.g. -R)
  -T TIMEOUT, --timeout TIMEOUT
                        override the connection timeout in seconds
                        (default=30)
  -c CONNECTION, --connection CONNECTION
                        connection type to use (default=smart)
  -k, --ask-pass        ask for connection password
  -u REMOTE_USER, --user REMOTE_USER
                        connect as this user (default=None)

Some actions do not make sense in Ad-Hoc (include, meta, etc)
```

---

#### ``send-datadog-event`` Command

Track an infrastructure maintainance event in Datadog

```
commcare-cloud <env> send-datadog-event [--tags [TAGS ...]] [--alert_type {error,warning,info,success}]
                                        event_title event_text
```

##### Positional Arguments

###### `event_title`

Title of the datadog event.

###### `event_text`

Text content of the datadog event.

##### Options

###### `--tags [TAGS ...]`

Additional tags e.g. host:web2

###### `--alert_type {error,warning,info,success}`

Alert type.

---

#### ``django-manage`` Command

Run a django management command.

```
commcare-cloud <env> django-manage [--tmux] [--server SERVER] [--release RELEASE] [--tee TEE_FILE] [--quiet]
```

`commcare-cloud <env> django-manage ...`
runs `./manage.py ...` on the first django_manage machine of &lt;env&gt; or
server you specify.
Omit &lt;command&gt; to see a full list of possible commands.

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Example

To open a django shell in a tmux window using the `2018-04-13_18.16` release.

```
commcare-cloud <env> django-manage --tmux --release 2018-04-13_18.16 shell
```

To do this on a specific server

```
commcare-cloud <env> django-manage --tmux shell --server web0
```

##### Options

###### `--tmux`

If this option is included, the management command will be
run in a new tmux window under the `cchq` user. You may then exit using
the customary tmux command `^b` `d`, and resume the session later.
This is especially useful for long-running commands.

The tmux session will be unique to your user. If you want to be able to share
your session with other users, create the tmux session manually on the machine
under a shared user account.

###### `--server SERVER`

Server to run management command on.
Defaults to first server under django_manage inventory group

###### `--release RELEASE`

Name of release to run under.
E.g. '2018-04-13_18.16'.
If none is specified, the `current` release will be used.

###### `--tee TEE_FILE`

Tee output to the screen and to this file on the remote machine

###### `--quiet`

Don't output the command to be run.

---

#### ``tmux`` Command

Connect to a remote host with ssh and open a tmux session.

```
commcare-cloud <env> tmux [--quiet] [server] [remote_command]
```

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Example

Rejoin last open tmux window.

```
commcare-cloud <env> tmux -
```

##### Positional Arguments

###### `server`

Server name/group: postgresql, proxy, webworkers, ... The server
name/group may be prefixed with 'username@' to login as a
specific user and may be terminated with '[<n>]' to choose one of
multiple servers if there is more than one in the group. For
example: webworkers[0] will pick the first webworker. May also be
omitted for environments with only a single server.

Use '-' for default (django_manage[0])

###### `remote_command`

Command to run in the tmux.
If a command is specified, then it will always run in a new window.
If a command is *not* specified, then it will rejoin the most
recently visited tmux window; only if there are no currently open
tmux windows will a new one be opened.

##### Options

###### `--quiet`

Don't output the command to be run.

---

#### ``export-sentry-events`` Command

Export Sentry events. One line per event JSON.

```
commcare-cloud <env> export-sentry-events -k API_KEY -i ISSUE_ID [--full] [--cursor CURSOR]
```

##### Options

###### `-k API_KEY, --api-key API_KEY`

Sentry API Key

###### `-i ISSUE_ID, --issue-id ISSUE_ID`

Sentry project ID

###### `--full`

Export the full event details

###### `--cursor CURSOR`

Starting position for the cursor

---

#### ``pillow-topic-assignments`` Command

Print out the list of Kafka partitions assigned to each pillow process.

```
commcare-cloud <env> pillow-topic-assignments [--csv] pillow_name
```

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

##### Positional Arguments

###### `pillow_name`

Name of the pillow.

##### Options

###### `--csv`

Output as CSV

---
### Operational

---
#### ``secrets`` Command

View and edit secrets through the CLI

```
commcare-cloud <env> secrets {view,edit,list-append,list-remove} secret_name
```

##### Positional Arguments

###### `{view,edit,list-append,list-remove}`

###### `secret_name`

---

#### ``migrate-secrets`` Command

Migrate secrets from one backend to another

```
commcare-cloud <env> migrate-secrets [--to-backend TO_BACKEND] from_backend
```

##### Positional Arguments

###### `from_backend`

##### Options

###### `--to-backend TO_BACKEND`

---

#### ``ping`` Command

Ping specified or all machines to see if they have been provisioned yet.

```
commcare-cloud <env> ping [--use-factory-auth] inventory_group
```

##### Positional Arguments

###### `inventory_group`

Machines to run on. Is anything that could be used in as a value for
`hosts` in an playbook "play", e.g.
`all` for all machines,
`webworkers` for a single group,
`celery:pillowtop` for multiple groups, etc.
See the description in [this blog](http://goinbigdata.com/understanding-ansible-patterns/)
for more detail in what can go here.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``ansible-playbook`` Command
(Alias ``ap``)

Run a playbook as you would with ansible-playbook

```
commcare-cloud <env> ansible-playbook [--use-factory-auth] playbook
```

By default, you will see --check output and then asked whether to apply.

##### Example

```
commcare-cloud <env> ansible-playbook deploy_proxy.yml --limit=proxy
```

##### Positional Arguments

###### `playbook`

The ansible playbook .yml file to run.
Options are the `*.yml` files located under `commcare_cloud/ansible`
which is under `src` for an egg install and under
`<virtualenv>/lib/python<version>/site-packages` for a wheel install.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

##### The ansible-playbook options below are available as well
```
  --flush-cache         clear the fact cache for every host in inventory
  --force-handlers      run handlers even if a task fails
  --list-hosts          outputs a list of matching hosts; does not execute
                        anything else
  --list-tags           list all available tags
  --list-tasks          list all tasks that would be executed
  --skip-tags SKIP_TAGS
                        only run plays and tasks whose tags do not match these
                        values
  --start-at-task START_AT_TASK
                        start the playbook at the task matching this name
  --step                one-step-at-a-time: confirm each task before running
  --syntax-check        perform a syntax check on the playbook, but do not
                        execute it
  --vault-id VAULT_IDS  the vault identity to use
  --version             show program's version number, config file location,
                        configured module search path, module location,
                        executable location and exit
  -M MODULE_PATH, --module-path MODULE_PATH
                        prepend colon-separated path(s) to module library (def
                        ault=~/.ansible/plugins/modules:/usr/share/ansible/plu
                        gins/modules)
  -e EXTRA_VARS, --extra-vars EXTRA_VARS
                        set additional variables as key=value or YAML/JSON, if
                        filename prepend with @
  -f FORKS, --forks FORKS
                        specify number of parallel processes to use
                        (default=50)
  -t TAGS, --tags TAGS  only run plays and tasks tagged with these values
  -v, --verbose         verbose mode (-vvv for more, -vvvv to enable
                        connection debugging)

```
##### Connection Options
```
  control as whom and how to connect to hosts

  --private-key PRIVATE_KEY_FILE, --key-file PRIVATE_KEY_FILE
                        use this file to authenticate the connection
  --scp-extra-args SCP_EXTRA_ARGS
                        specify extra arguments to pass to scp only (e.g. -l)
  --sftp-extra-args SFTP_EXTRA_ARGS
                        specify extra arguments to pass to sftp only (e.g. -f,
                        -l)
  --ssh-common-args SSH_COMMON_ARGS
                        specify common arguments to pass to sftp/scp/ssh (e.g.
                        ProxyCommand)
  --ssh-extra-args SSH_EXTRA_ARGS
                        specify extra arguments to pass to ssh only (e.g. -R)
  -T TIMEOUT, --timeout TIMEOUT
                        override the connection timeout in seconds
                        (default=30)
  -c CONNECTION, --connection CONNECTION
                        connection type to use (default=smart)
  -k, --ask-pass        ask for connection password
  -u REMOTE_USER, --user REMOTE_USER
                        connect as this user (default=None)

```
##### Privilege Escalation Options
```
  control how and which user you become as on target hosts

  --become-method BECOME_METHOD
                        privilege escalation method to use (default=sudo), use
                        `ansible-doc -t become -l` to list valid choices.
  --become-user BECOME_USER
                        run operations as this user (default=root)
  -K, --ask-become-pass
                        ask for privilege escalation password
  -b, --become          run operations with become (does not imply password
                        prompting)
```

---

#### ``deploy-stack`` Command
(Alias ``aps``)

Run the ansible playbook for deploying the entire stack.

```
commcare-cloud <env> deploy-stack [--use-factory-auth] [--first-time]
```

Often used in conjunction with --limit and/or --tag
for a more specific update.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

###### `--first-time`

Use this flag for running against a newly-created machine.

It will first use factory auth to set up users,
and then will do the rest of deploy-stack normally,
but skipping check mode.

Running with this flag is equivalent to

```
commcare-cloud <env> bootstrap-users <...args>
commcare-cloud <env> deploy-stack --skip-check --skip-tags=users <...args>
```

If you run and it fails half way, when you're ready to retry, you're probably
better off running
```
commcare-cloud <env> deploy-stack --skip-check --skip-tags=users <...args>
```
since if it made it through bootstrap-users
you won't be able to run bootstrap-users again.

---

#### ``update-config`` Command

Run the ansible playbook for updating app config.

```
commcare-cloud <env> update-config
```

This includes django `localsettings.py` and formplayer `application.properties`.

---

#### ``after-reboot`` Command

Bring a just-rebooted machine back into operation.

```
commcare-cloud <env> after-reboot [--use-factory-auth] inventory_group
```

Includes mounting the encrypted drive.
This command never runs in check mode.

##### Positional Arguments

###### `inventory_group`

Machines to run on. Is anything that could be used in as a value for
`hosts` in an playbook "play", e.g.
`all` for all machines,
`webworkers` for a single group,
`celery:pillowtop` for multiple groups, etc.
See the description in [this blog](http://goinbigdata.com/understanding-ansible-patterns/)
for more detail in what can go here.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``bootstrap-users`` Command

Add users to a set of new machines as root.

```
commcare-cloud <env> bootstrap-users [--use-factory-auth]
```

This must be done before any other user can log in.

This will set up machines to reject root login and require
password-less logins based on the usernames and public keys
you have specified in your environment. This can only be run once
per machine; if after running it you would like to run it again,
you have to use `update-users` below instead.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``update-users`` Command

Bring users up to date with the current CommCare Cloud settings.

```
commcare-cloud <env> update-users [--use-factory-auth]
```

In steady state this command (and not `bootstrap-users`) should be used
to keep machine user accounts, permissions, and login information
up to date.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``update-user-key`` Command

Update a single user's public key (because update-users takes forever).

```
commcare-cloud <env> update-user-key [--use-factory-auth] username
```

##### Positional Arguments

###### `username`

username who owns the public key

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``update-supervisor-confs`` Command

Updates the supervisor configuration files for services required by CommCare.

```
commcare-cloud <env> update-supervisor-confs [--use-factory-auth]
```

These services are defined in app-processes.yml.

##### Options

###### `--use-factory-auth`

authenticate using the pem file (or prompt for root password if there is no pem file)

---

#### ``fab`` Command

Placeholder for obsolete fab commands

```
commcare-cloud <env> fab [-l] [fab_command]
```

##### Positional Arguments

###### `fab_command`

The name of the obsolete fab command.

##### Options

###### `-l`

Use `-l` instead of a command to see the full list of commands.

##### Obsolete fab commands
```

Obsolete fab command       Replaced by 'commcare-cloud ENV ...'
--------------------       --------------------------------------
check_status               ping all
                           service postgresql status
                           service elasticsearch status
    
clean_releases             clean-releases [--keep=N]
deploy_commcare            deploy commcare
kill_stale_celery_workers  kill-stale-celery-workers
manage                     django-manage
perform_system_checks      perform-system-checks
preindex_views             preindex-views
restart_services           service commcare restart
restart_webworkers         service webworker restart
rollback                   deploy commcare --resume=PREVIOUS_RELEASE

Use the 'list-releases' command to get valid release names.
    
rollback_formplayer        ansible-playbook rollback_formplayer.yml --tags=rollback
setup_limited_release      deploy commcare --private [--keep-days=N] [--commcare-rev=HQ_BRANCH]
setup_release              deploy commcare --private --limit=all [--keep-days=N] [--commcare-rev=HQ_BRANCH]
start_celery               service celery start
start_pillows              service pillowtop start
stop_celery                service celery stop
stop_pillows               service pillowtop stop
supervisorctl              service NAME ACTION
update_current             deploy commcare --resume=RELEASE_NAME
```

---

#### ``deploy`` Command

Deploy CommCare

```
commcare-cloud <env> deploy [--resume RELEASE_NAME] [--private] [-l SUBSET] [--keep-days KEEP_DAYS] [--skip-record]
                            [--commcare-rev COMMCARE_REV] [--ignore-kafka-checkpoint-warning] [--update-config]
                            [{commcare,formplayer} ...]
```

##### Positional Arguments

###### `{commcare,formplayer}`

Component(s) to deploy. Default is 'commcare', or if
always_deploy_formplayer is set in meta.yml, 'commcare formplayer'

##### Options

###### `--resume RELEASE_NAME`

Rather than starting a new deploy, resume a previous release.
This option can be used to "rollback" to a previous release.
Use the 'list-releases' command to get valid release names.

###### `--private`

Set up a private release for running management commands.
This option implies --limit=django_manage. Use --limit=all
to set up a private release on all applicable hosts.

###### `-l SUBSET, --limit SUBSET`

Limit selected hosts.

###### `--keep-days KEEP_DAYS`

The number of days to keep the release before it will be purged.

###### `--skip-record`

Skip the steps involved in recording and announcing the fact of the deploy.

###### `--commcare-rev COMMCARE_REV`

The name of the commcare-hq git branch, tag, or SHA-1 commit hash to deploy.

###### `--ignore-kafka-checkpoint-warning`

Do not block deploy if Kafka checkpoints are unavailable.

###### `--update-config`

Generate new localsettings.py rather than copying from the previous
release.

---

#### ``deploy-diff`` Command

Display pull requests that would be deployed on master now.

```
commcare-cloud <env> deploy-diff [{commcare,formplayer}]
```

##### Positional Arguments

###### `{commcare,formplayer}`

Component to check deploy diff for. Default is 'commcare'.

---

#### ``list-releases`` Command

List names that can be passed to `deploy --resume=RELEASE_NAME`

```
commcare-cloud <env> list-releases [--limit LIMIT]
```

##### Options

###### `--limit LIMIT`

Run command on limited host(s). Default: webworkers[0]

---

#### ``clean-releases`` Command

Cleans old and failed deploys from the ~/www/ENV/releases/ directory.

```
commcare-cloud <env> clean-releases [-k N] [-x [EXCLUDE ...]]
```

##### Options

###### `-k N, --keep N`

The number of releases to retain. Default: 3

###### `-x [EXCLUDE ...], --exclude [EXCLUDE ...]`

Extra release names to exclude from cleanup, in addition to
the automatic exclusions such as the current release.

---

#### ``preindex-views`` Command

```
commcare-cloud <env> preindex-views [--commcare-rev COMMCARE_REV] [--release RELEASE_NAME]
```

Set up a private release on the first pillowtop machine and run
preindex_everything with that release.

##### Options

###### `--commcare-rev COMMCARE_REV`

The name of the commcare-hq git branch, tag, or SHA-1 commit hash to deploy.

###### `--release RELEASE_NAME`

Use/resume an existing release rather than creating a new one.

---

#### ``service`` Command

Manage services.

```
commcare-cloud <env> service [--only PROCESS_PATTERN]
                             {celery,citusdb,commcare,couchdb2,elasticsearch,elasticsearch-classic,formplayer,kafka,nginx,pillowtop,postgresql,rabbitmq,redis,webworker}
                             [{celery,citusdb,commcare,couchdb2,elasticsearch,elasticsearch-classic,formplayer,kafka,nginx,pillowtop,postgresql,rabbitmq,redis,webworker} ...]
                             {start,stop,restart,status,logs,help}
```

##### Example

```
cchq <env> service postgresql status
cchq <env> service celery help
cchq <env> service celery logs
cchq <env> service celery restart --limit <host>
cchq <env> service celery restart --only <queue-name>,<queue-name>:<queue_num>
cchq <env> service pillowtop restart --limit <host> --only <pillow-name>
```

Services are grouped together to form conceptual service groups.
Thus the `postgresql` service group applies to both the `postgresql`
service and the `pgbouncer` service. We'll call the actual services
"subservices" here.

##### Positional Arguments

###### `{celery,citusdb,commcare,couchdb2,elasticsearch,elasticsearch-classic,formplayer,kafka,nginx,pillowtop,postgresql,rabbitmq,redis,webworker}`

The name of the service group(s) to apply the action to.
There is a preset list of service groups that are supported.
More than one service may be supplied as separate arguments in a row.

###### `{start,stop,restart,status,logs,help}`

Action can be `status`, `start`, `stop`, `restart`, or `logs`.
This action is applied to every matching service.

##### Options

###### `--only PROCESS_PATTERN`

Sub-service name to limit action to.
Format as 'name' or 'name:number'.
Use 'help' action to list all options.

---

#### ``migrate-couchdb`` Command
(Alias ``migrate_couchdb``)

Perform a CouchDB migration

```
commcare-cloud <env> migrate-couchdb [--no-stop] migration_plan {describe,plan,migrate,commit,clean}
```

This is a recent and advanced addition to the capabilities,
and is not yet ready for widespread use. At such a time as it is
ready, it will be more thoroughly documented.

##### Positional Arguments

###### `migration_plan`

Path to migration plan file

###### `{describe,plan,migrate,commit,clean}`

Action to perform

- describe: Print out cluster info
- plan: generate plan details from migration plan
- migrate: stop nodes and copy shard data according to plan
- commit: update database docs with new shard allocation
- clean: remove shard files from hosts where they aren't needed

##### Options

###### `--no-stop`

When used with migrate, operate on live couchdb cluster without stopping nodes.

This is potentially dangerous.
If the sets of a shard's old locations and new locations are disjoint---i.e.
if there are no "pivot" locations for a shard---then running migrate and commit
without stopping couchdb will result in data loss.
If your shard reallocation has a pivot location for each shard,
then it's acceptable to do live.

---

#### ``downtime`` Command

Manage downtime for the selected environment.

```
commcare-cloud <env> downtime [-m MESSAGE] [-d DURATION] {start,end}
```

This notifies Datadog of the planned downtime so that is is recorded
in the history, and so that during it service alerts are silenced.

##### Positional Arguments

###### `{start,end}`

##### Options

###### `-m MESSAGE, --message MESSAGE`

Optional message to set on Datadog.

###### `-d DURATION, --duration DURATION`

Max duration in hours for the Datadog downtime after which it will be auto-cancelled.
This is a safeguard against downtime remaining active and preventing future
alerts.
Default: 24 hours

---

#### ``copy-files`` Command

Copy files from multiple sources to targets.

```
commcare-cloud <env> copy-files plan_path {prepare,copy,cleanup}
```

This is a general purpose command that can be used to copy files between
hosts in the cluster.

Files are copied using `rsync` from the target host. This tool assumes that the
specified user on the source host has permissions to read the files being copied.

The plan file must be formatted as follows:

```yml
source_env: env1 (optional if source is different from target;
                  SSH access must be allowed from the target host(s) to source host(s))
copy_files:
  - <target-host>:
      - source_host: <source-host>
        source_user: <user>
        source_dir: <source-dir>
        target_dir: <target-dir>
        rsync_args: []
        files:
          - test/
          - test1/test-file.txt
        exclude:
          - logs/*
          - test/temp.txt
```
- **copy_files**: Multiple target hosts can be listed.
- **target-host**: Hostname or IP of the target host. Multiple source
  definitions can be listed for each target host.
- **source-host**: Hostname or IP of the source host.
- **source-user**: (optional) User to ssh as from target to source. Defaults
  to 'ansible'. This user must have permissions to read the files being
  copied.
- **source-dir**: The base directory from which all source files referenced.
- **target-dir**: Directory on the target host to copy the files to.
- **rsync_args**: Additional arguments to pass to rsync.
- **files**: List of files to copy. File paths are relative to `source-dir`.
  Directories can be included and must end with a `/`.
- **exclude**: (optional) List of relative paths to exclude from the
  *source-dir*. Supports wildcards e.g. "logs/*".

##### Positional Arguments

###### `plan_path`

Path to plan file

###### `{prepare,copy,cleanup}`

Action to perform

- prepare: generate the scripts and push them to the target servers
- copy: execute the scripts
- cleanup: remove temporary files and remote auth

---

#### ``list-postgresql-dbs`` Command

Example:

```
commcare-cloud <env> list-postgresql-dbs [--compare]
```

To list all database on a particular environment.

```
commcare-cloud <env> list-postgresql-dbs
```

##### Options

###### `--compare`

Gives additional databases on the server.

---

#### ``celery-resource-report`` Command

Report of celery resources by queue.

```
commcare-cloud <env> celery-resource-report [--show-workers] [--csv]
```

##### Options

###### `--show-workers`

Includes the list of worker nodes for each queue

###### `--csv`

Output table as CSV

---

#### ``pillow-resource-report`` Command

Report of pillow resources.

```
commcare-cloud <env> pillow-resource-report [--csv]
```

##### Options

###### `--csv`

Output table as CSV

---

#### ``kill-stale-celery-workers`` Command

Kill celery workers that failed to properly go into warm shutdown.

```
commcare-cloud <env> kill-stale-celery-workers
```

When used with --control, this command skips the slow setup.
To force setup, use --control-setup=yes instead.

---

#### ``perform-system-checks`` Command

```
commcare-cloud <env> perform-system-checks
```

Check the Django project for potential problems in two phases, first
check all apps, then run database checks only.

See https://docs.djangoproject.com/en/dev/ref/django-admin/#check

---

#### ``couchdb-cluster-info`` Command

Output information about the CouchDB cluster.

```
commcare-cloud <env> couchdb-cluster-info [--raw] [--shard-counts] [--database DATABASE] [--couch-port COUCH_PORT]
                                          [--couch-local-port COUCH_LOCAL_PORT] [--couchdb-version COUCHDB_VERSION]
```

##### Shard counts are displayed as follows
```
* a single number if all nodes have the same count
* the count on the first node followed by the difference in each following node
  e.g. 2000,+1,-2 indicates that the counts are 2000,2001,1998
```

##### Options

###### `--raw`

Output raw shard allocations as YAML instead of printing tables

###### `--shard-counts`

Include document counts for each shard

###### `--database DATABASE`

Only show output for this database

###### `--couch-port COUCH_PORT`

CouchDB port. Defaults to 15984

###### `--couch-local-port COUCH_LOCAL_PORT`

CouchDB local port (only applicable to CouchDB version < '3.0.0'). Defaults to 15986

###### `--couchdb-version COUCHDB_VERSION`

CouchDB version. Assumes '2.3.1' or couchdb_version if set in public.yml

---

#### ``terraform`` Command

Run terraform for this env with the given arguments

```
commcare-cloud <env> terraform [--skip-secrets] [--apply-immediately] [--username USERNAME]
```

##### Options

###### `--skip-secrets`

Skip regenerating the secrets file.

Good for not having to enter vault password again.

###### `--apply-immediately`

Apply immediately regardless fo the default.

In RDS where the default is to apply in the next maintenance window,
use this to apply immediately instead. This may result in a service interruption.

###### `--username USERNAME`

The username of the user whose public key will be put on new servers.

Normally this would be _your_ username.
Defaults to the value of the COMMCARE_CLOUD_DEFAULT_USERNAME environment variable
or else the username of the user running the command.

---

#### ``terraform-migrate-state`` Command

Apply unapplied state migrations in commcare_cloud/commands/terraform/migrations

```
commcare-cloud <env> terraform-migrate-state [--replay-from REPLAY_FROM]
```

This migration tool should exist as a generic tool for terraform,
but terraform is still not that mature, and it doesn't seem to exist yet.

Terraform assigns each resource an address so that it can map it back to the code.
However, often when you change the code, the addresses no longer map to the same place.
For this, terraform offers the terraform state mv &lt;address&gt; &lt;new_address&gt; command,
so you can tell it how existing resources map to your new code.

This is a tedious task, and often follows a very predictable renaming pattern.
This command helps fill this gap.

##### Options

###### `--replay-from REPLAY_FROM`

Set the last applied migration value to this number before running. Will begin running migrations after this number, not including it.

---

#### ``aws-sign-in`` Command

Use your MFA device to "sign in" to AWS for &lt;duration&gt; minutes (default 30)

```
commcare-cloud <env> aws-sign-in [--duration-minutes DURATION_MINUTES]
```

This will store the temporary session credentials in ~/.aws/credentials
under a profile named with the pattern "&lt;aws_profile&gt;:profile".
After this you can use other AWS-related commands for up to &lt;duration&gt; minutes
before having to sign in again.

##### Options

###### `--duration-minutes DURATION_MINUTES`

Stay signed in for this many minutes

---

#### ``aws-list`` Command

List endpoints (ec2, rds, etc.) on AWS

```
commcare-cloud <env> aws-list
```

---

#### ``aws-fill-inventory`` Command

Fill inventory.ini.j2 using AWS resource values cached in aws-resources.yml

```
commcare-cloud <env> aws-fill-inventory [--cached]
```

If --cached is not specified, also refresh aws-resources.yml
to match what is actually in AWS.

##### Options

###### `--cached`

Use the values set in aws-resources.yml rather than fetching from AWS.

This runs much more quickly and gives the same result, provided no changes
have been made to our actual resources in AWS.

---

#### ``forward-port`` Command

Port forward to access a remote admin console

```
commcare-cloud <env> forward-port {flower,couch,elasticsearch}
```

##### Positional Arguments

###### `{flower,couch,elasticsearch}`

The remote service to port forward. Must be one of couch,elasticsearch,flower.

---