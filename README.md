# SEASON Dizest Platform

## Introduction

SEASON DIZESThub Platform (dizest) provides visual convenience for artificial intelligence data analysis based on web technology.

![screenshot](./screenshots/demo.gif)

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

### 3.2.1

- [ui] install bug fixed
- [ui] config path changed (`./config/dizest/`)

### 3.2.0

- [core] process logic changed
- [core] support multi-thread jobs
- [core] job scheduler
- [ui] terminal for admin

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

### 3.0.14

- add `dizest server start --log <file>` method 

### 3.0.13

- update command changed

### 3.0.12

- add crontab

### 3.0.11

- dizest run command bug fixed

### 3.0.10

- add kill command
- wiz config changed (for pwa)

### 3.0.9

- apply natsort in drive api
- kernel api method usage changed: dizest.output(key1=value1, key2=value2)
- upgrade r kernel

### 3.0.8

- remove useless import
- python kernel
    - add `dizest.clear()` function
    - log sync on multi view
    - enhanced plot log
    - dizest.input logic changed: get last proceed result
- add dependencies: pymysql, natsort

### 3.0.7

- kernel logging updated

### 3.0.6

- port bug fixed on command line
- kernel communication changed (http to socket)
- process stabilization

### 3.0.5

- support dizest server command (daemon)

### 3.0.4

- child process bug fixed

### 3.0.3

- bug fixed at sudo spawner

### 3.0.2

- add `executable` option

### 3.0.0

- define dizest process `server`, `kernel`, `spawner`
- update workflow editor ui: `codeflow`, `kernel selector`, etc
- multi kernel support (support multi language like R)
- support 3rd party development (spawner, kernel)
