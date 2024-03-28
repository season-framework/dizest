# SEASON Dizest Platform

## Introduction

SEASON DIZESThub Platform (dizest) provides visual convenience for artificial intelligence data analysis based on web technology.

![screenshot](./screenshots/3.4.0.gif)

## Installation

```bash
pip install dizest
dizest install <INSTALL_DIRECTORY>
```

## Start dizest server

- run server

```bash
cd <INSTALL_DIRECTORY>
dizest run --port 4000 --host 0.0.0.0
```

- run server as daemon

```bash
dizest server start # start dizest server daemon
dizest server stop  # stop dizest server daemon
```

## Upgrade

```bash
pip install dizest --upgrade
cd <INSTALL_DIRECTORY>
dizest upgrade
```

## Install with source code

```
cd <workspace>
wiz create dizest --uri https://github.com/season-framework/dizest-ui-angular

```

## DIZEST CLI

### Project API
- `dizest install [Project Name] --mode single --password 1234`
    - Flag
        | Flag | Syntax | Description |
        |---|---|---|
        | --mode | dizest install [Project Name] --mode=single | single or system, default single |
        | --password | dizest install [Project Name] --password=1234 | root account password, default 1234 |
    - Example
        ```bash
        dizest install myapp
        ```

- `dizest upgrade`
    - Example
        ```bash
        cd myapp
        dizest upgrade
        ```
    
- `dizest password <password>`
    - change root user password on single mode
    - Example
        ```bash
        dizest password mypassword
        ```

### Daemon API
- `dizest run --host=<host> --port=<port> --log=<log file path>`
    - Flag
        | Flag | Syntax | Description |
        |---|---|---|
        | --port | dizest run [action] --port=PORT | Web server port, Default 3000 |
        | --host | dizest run [action] --host=HOST | Web server host, Default 0.0.0.0 |
        | --log | dizest run [action] --log=PATH | Log file path, Default None |
    - Example
        ```bash
        dizest run --port=3000
        dizest run --port=3000 --host=0.0.0.0
        dizest run --port 3000 --log dizest.log
        ```

- `dizest server [action] --log=<log file path> --force`
    - Action
        | Action | Syntax | Description |
        |---|---|---|
        | start | dizest server start [flags] | Start dizest server as daemon |
        | stop | dizest server stop [flags] | Stop dizest server daemon |
        | restart | dizest server restart [flags] | Restart dizest server daemon |
    - Flag
        | Flag | Syntax | Description |
        |---|---|---|
        | --log | dizest server [action] --log=PATH | Log file path, Default None |
        | --force | dizest server start --force | Force start daemon |
    - Example
        ```bash
        dizest server start --force
        dizest server stop
        dizest server restart
        ```

### Service API
- `dizest service list`
    - Example
        ```bash
        dizest service list
        ```

- `dizest service regist [name]`
    - Same AS
        - `install`
    - Example
        ```bash
        dizest service regist myapp
        # or
        dizest service install myapp
        ```

- `dizest service unregist [name]`
    - Same AS
        - `uninstall`, `remove`, `delete`, `rm`
    - Example
        ```bash
        dizest service unregist myapp
        # or
        dizest service remove myapp
        ```

- `dizest service status [name]`
    - Example
        ```bash
        dizest service status myapp
        ```

- `dizest service start [name]`
    - Example
        ```bash
        dizest service start myapp
        ```

- `dizest service stop [name]`
    - Example
        ```bash
        dizest service stop myapp
        ```

- `dizest service restart [name]`
    - Example
        ```bash
        dizest service restart myapp
        ```

## Roadmap

- Spawner
    - spawner for k8s
- General
    - SAML Authentication
- Workflow
    - export/import app
    - upgrade display function (full function of jupyter)
- Drive
    - connect with Google Drive, Dropbox, etc.
- Dizest Cloud
    - manage apps & workflow on cloud
    - connect with hub by API

## Release Note

### 3.4.11

- [core] update wiz 2.4 & bug fixed

### 3.4.10

- [ui] argh version bug fixed

### 3.4.9

- [ui] terminal width/height bug fixed
- [ui] terminal starting path changed
- [ui] input list bug fixed at node
- [ui] display text max length changed (100 to 2000)
- [ui] user login changed (multi to single and support auth mode)
- [core] install command changed (default as single user mode)

### 3.4.8

- [ui] sidebar lifecycle changed
- [core] wiz version

### 3.4.7

- [ui] loading ui design changed
- [ui] image/video viewer at drive
- [ui] disk path config added for system status
- [core] service command updated

### 3.4.6

- [ui] scroll bug fixed at system info
- [ui] kill workflow button at drive
- [ui] move workflow bug fixed when workflow is running
- [ui] display file upload status at drive
- [ui] restart server (admin)
- [ui] conda env upgrade at admin setting page
- [core] kernel socket error fixed

### 3.4.5

- kernel socket error fixed

### 3.4.4

- kernel socket error fixed
- dizest service display bug fixed

### 3.4.3

- support customize Workflow Node
- `/api/drive` ownership bug fixed

### 3.4.2

- [ui] terminal bug fixed
- [ui] authenticate api & config
- [ui] file selector in workflow node bug fixed 

### 3.4.1

- [ui] draw workflow bug fixed
- [ui] flow stop bug fixed

### 3.4.0

- [ui] UI full changed (Single page hub)
- [ui] Remove installation page
- [ui] change user login using linux account
- [ui] using kernel for each workflow

### 3.3.x

- [3.3.0]
    - [core] dizest input/output automation
    - [core] dizest cli updated (service)
    - [ui] code refactoring
    - [ui] display filename on file delete popup
    - [ui] codeflow resize bug fixed
    - [ui] support multiple app upload
    - [ui] open workflow as href
    - [ui] workflow favorite and category added
    - [ui] support activated workflow list

- 3.3.1 ~ 2
    - [ui] uimode bug fixed 
    - [ui] uimode bug fixed 

### 3.2.x

- [3.2.0]
    - [core] process logic changed
    - [core] support multi-thread jobs
    - [core] job scheduler
    - [ui] terminal for admin

- 3.2.1 ~ 6
    - [ui] install bug fixed
    - [ui] config path changed (`./config/dizest/`)
    - [ui] add config (cron_host, dsocket_host)
    - [ui] set browser title on workflow
    - [ui] code block drag bug fixed on codeflow
    - [ui] opacity changed on focused app
    - [ui] pip install btn bug fixed
    - [ui] dconfig.py home path bug fixed
    - [ui] node start bug fixed
    - [core] ui api bug fixed (flask send_file api)
    - [ui] user home path bug fixed
    - [core] python-socketio version fixed (5.7.2)

### 3.1.x

- [3.1.0]
    - ui full changed
    - upgrade command
    - use built-in web server bundle
    - upgrade to wiz 2.0
    - upgrade to angular

- 3.1.1 ~ 13
    - [ui] bug fixed on run command
    - [core] bug fixed on kernel
    - [ui] pwa bug fixed
    - [ui] safari bug fixed (URLPattern)
    - [ui] cron bug fixed
    - [ui] mobile nav bug fixed
    - [ui] kernel display name bug fixed
    - [core] drive api update (filename to download_name)
    - [core] kernel api update
    - [ui] select previous file on workflow
    - [ui] bug fixed
    - [ui] drop workflow & apps
    - [ui] support app category
    - [ui] monaco bug fixed
    - [ui] login bug fixed

### 3.0.x

- [3.0.0]
    - define dizest process `server`, `kernel`, `spawner`
    - update workflow editor ui: `codeflow`, `kernel selector`, etc
    - multi kernel support (support multi language like R)
    - support 3rd party development (spawner, kernel)

- 3.0.1 ~ 14
    - add `executable` option
    - bug fixed at sudo spawner
    - child process bug fixed
    - support dizest server command (daemon)
    - port bug fixed on command line
    - kernel communication changed (http to socket)
    - process stabilization
    - kernel logging updated
    - remove useless import
    - python kernel
        - add `dizest.clear()` function
        - log sync on multi view
        - enhanced plot log
        - dizest.input logic changed: get last proceed result
    - add dependencies: pymysql, natsort
    - apply natsort in drive api
    - kernel api method usage changed: dizest.output(key1=value1, key2=value2)
    - upgrade r kernel
    - add kill command
    - wiz config changed (for pwa)
    - dizest run command bug fixed
    - add crontab
    - update command changed
    - add `dizest server start --log <file>` method 
