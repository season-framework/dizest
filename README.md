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

### 3.1.9

- select previous file on workflow

### 3.1.8

- kernel api update

### 3.1.7

- drive api update (filename to download_name)

### 3.1.6

- kernel display name bug fixed

### 3.1.5

- mobile nav bug fixed

### 3.1.4

- cron bug fixed

### 3.1.3

- pwa bug fixed
- safari bug fixed (URLPattern)

### 3.1.2

- bug fixed on kernel

### 3.1.1

- bug fixed on run command

### 3.1.0

- ui full changed
- upgrade command
- use built-in web server bundle
- upgrade to wiz 2.0
- upgrade to angular

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
