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

## External API

- `http://127.0.0.1:4000/dizest/api/run/<workflow path>?key=value...`
    
```bash
curl http://127.0.0.1:4000/dizest/api/run/sample.dwp?message=Hello
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

## Release Note

### 4.0.15

- add flow status in response at External API

### 4.0.14

- remove renderer at External API

### 4.0.13

- display log bug fixed (whitespace pre-wrap)

### 4.0.12

- UI Mode ACL Bug Fixed

### 4.0.11

- App category sort bug fixed
- Flow instance bug fixed (External API)

### 4.0.10

- External API UI path bug fixed

### 4.0.9

- External API UI bug fixed
- Finish event added at External API Stream mode

### 4.0.8

- Workflow kernel bug fixed (id generation)

### 4.0.7

- Add External API UI
- Add Baerer Token for External API
- Workflow status bug fixed at core

### 4.0.6

- Default Config Bug fixed

### 4.0.5

- Added variable type checking to workflow nodes
- Added `dizest run <workflow_file>` command
- Added External Workflow Running API

### 4.0.4

- update to LLM Stream mode
- id & password option support at login

### 4.0.3

- file browser bug fixed on workflow node file selector

### 4.0.2

- Allowed relative library paths when running workflows (sys.path.append)
- Enabled copying of workflow result values
- Fixed interval disabling issue in Health feature
- Resolved execution order error in workflows (cache issue with previously executed workflows)
- Added functionality to view and upgrade DIZEST versions per Python environment in settings

### 4.0.1

- UI Mode path bug fixed

### 4.0.0
> Oct 6, 2024

- Improved workflow UI for better usability (node size adjustment)
- Enhanced usability of UI mode (updated positioning for better node integration)
- Improved Codeflow usability (including scrolling enhancements)
- Updated screen layout and structure
- Added support for LLM integration
- Core updates for better MSA compatibility

### Version 3
> Aug 7, 2022

- UI Enhancements & Bug Fixes: There were multiple bug fixes related to the user interface (UI) across all versions. This includes resolving issues with UI mode in both versions 3.4.13 and 3.4.14, and fixing a version mismatch bug in 3.4.15.
- Angular Upgrade: In version 3.4.13, the UI was upgraded to Angular 18, representing a significant update in the underlying framework used for the frontend, potentially enhancing performance and development flexibility.
- UI Restructuring: Version 3.4.13 also introduced changes to the layout by moving the App List to the sidebar in workflows, improving the workflow navigation and overall user experience.

### Version 2
> May 8, 2022

- Workflow and App Development Enhancements: Version 2.0.0 introduced major upgrades to the workflow engine and app development API, along with a complete UI/UX overhaul, including the introduction of the Drive concept. Subsequent updates (2.0.5 to 2.0.8) focused on improving workflow management, with features like workflow import/export, error status display, and process killing on the admin dashboard.
- UI and Functional Improvements: Version 2.2.0 introduced significant changes to the app editor, including drag-and-drop input/output ordering and CDN configuration, while 2.2.1 updated to Wiz 1.0. These changes enhanced both the app development interface and the backend configuration management.
- Backend and Configuration Updates: Several versions included updates to the kernel configuration (2.1.5), workflow app variable types (2.1.4), and bug fixes across the board to improve stability, including socket communication improvements and class-related workflow issues.

### Version 1
> Jan 18, 2022