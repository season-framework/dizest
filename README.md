# SEASON Dizest Platform

## Introduction

SEASON Dizest Platform (dizest) provides visual convenience for artificial intelligence data analysis based on web technology.

![screenshot](./screenshots/dizest.gif)

## Installation

```bash
pip install dizest
cd <your-workspace>
dizest run
dizest run --port 4000 --host 0.0.0.0
```

## Upgrade

```bash
pip install dizest --upgrade
cd <your-workspace>
dizest update
```

## Roadmap

- Core
    - run entire workflow
    - kernel for k8s
    - cache controller
    - command line tools (run workflow on terminal)
- General
    - User's mypage (for password change)
    - SAML Authentication
- Apps
    - copy apps from hub to myapps
    - export/import app
- Workflow
    - display error status
    - auto process (auto ordering flows)
    - export/import app
- Explore
    - explore workflow on hub
    - comment or review functions
    - copy workflow to my workflow
- Drive
    - connect with Google Drive, Dropbox, etc.
- Dizest Cloud
    - manage apps & workflow on cloud
    - connect with hub by API

## Release Note

### 2.0.5
- app ui api bug fixed
- display workflow error message
- workflow running status logic changed

### 2.0.4
- dizest runner update (--host, --port option)
- change dizest app process cwd (to local drive)
- run shortcut on app development page (shift+enter)

### 2.0.3
- bug fixed

### 2.0.2
- bug fixed

### 2.0.1
- bug fixed

### 2.0.0
- Upgrade Workflow Engine
- Upgrade App development API
- Change UI/UX
- adding Drive Concept