# SEASON Datahub Platform

## Introduction

SEASON Datahub Platform (seasondh) provides visual convenience for artificial intelligence data analysis based on web technology.

![screenshot](./screenshots/editor.png)

## Installation

```bash
pip install seasondh
```

## Run Datahub

run web daemon

```bash
cd ~
mkdir workspace
cd workspace
seasondh web --port 3000 --host 127.0.0.1 --password 1234
```

connect http://127.0.0.1:3000 on your web browser

![screenshot](./screenshots/protected.png)


## Basic Concepts

seasondh provides pipeline-based data processing flow. like below.

![screenshot](./screenshots/pipeline.png)

Each component is designed with the concept of an app and performs tasks independently according to the sequence of data processing.

