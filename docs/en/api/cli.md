# CLI API Reference

## Overview

The DIZEST CLI is a command-line tool for project management, server execution, and service management.

## Basic Usage

```bash
dizest <command> [options]
```

Check version:
```bash
dizest --version
```

---

## Project Management Commands

### install

Creates a new DIZEST project.

#### Usage

```bash
dizest install [PROJECT_NAME] [OPTIONS]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `PROJECT_NAME` | string | ✓ | - | Project directory name to create (minimum 3 characters) |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--password` | string | Auto-generated | Root account password |

#### Example

```bash
# Basic installation (auto-generated password)
dizest install myproject

# Custom password
dizest install myproject --password mysecret123

# Output example:
# dizest installed at `myproject`
# password: aB3dE5fG7hI9jK1l
```

#### Created Structure

```
myproject/
├── config.py           # Project configuration
├── password            # bcrypt encrypted password
├── project/            # Project source
│   └── main/
├── plugin/             # Plugin directory
└── public/             # Public directory
    └── app.py
```

---

### upgrade

Upgrades an existing DIZEST project to the latest version.

#### Usage

```bash
dizest upgrade
```

#### Requirements

- `project/` folder must exist in the current directory
- User data is preserved, only system files are updated

#### Example

```bash
cd myproject
dizest upgrade
```

#### Notes

- Backup your project before upgrading (recommended)
- The `project/` directory is completely replaced
- Custom modifications should be stored in the `plugin/` directory

---

### password

Changes the root user password in Single mode.

#### Usage

```bash
dizest password <NEW_PASSWORD>
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `NEW_PASSWORD` | string | ✓ | New password |

#### Example

```bash
dizest password mynewpassword123
```

#### Security Considerations

- Passwords are encrypted with bcrypt before storage
- Be careful as passwords may remain in command history

---

## Server Execution Commands

### run

Runs the DIZEST server in the foreground.

#### Usage

```bash
dizest run [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | string | `0.0.0.0` | Web server host address |
| `--port` | integer | `3000` | Web server port number |
| `--log` | string | `None` | Log file path (stdout if not specified) |

#### Example

```bash
# Basic run
dizest run

# Specify port
dizest run --port=4000

# Specify host and port
dizest run --host=127.0.0.1 --port=8080

# Specify log file
dizest run --port=4000 --log=/var/log/dizest.log

# Allow external connections
dizest run --host=0.0.0.0 --port=80
```

#### Access

Access via browser at `http://localhost:PORT`

#### Stop

Press `Ctrl+C` to stop the server

---

### server

Runs/stops the DIZEST server as a daemon.

#### Usage

```bash
dizest server <ACTION> [OPTIONS]
```

#### Actions

| Action | Description |
|--------|-------------|
| `start` | Start server in background |
| `stop` | Stop running server |

#### Options (start only)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | string | `0.0.0.0` | Web server host |
| `--port` | integer | `3000` | Web server port |
| `--log` | string | `None` | Log file path |

#### Example

```bash
# Start daemon
dizest server start

# Start with port specification
dizest server start --port=4000

# Stop daemon
dizest server stop
```

#### Check Process

```bash
# Check running dizest processes
ps aux | grep dizest
```

---

### kill

Forcefully terminates all running DIZEST server processes.

#### Usage

```bash
dizest kill
```

#### Example

```bash
dizest kill
```

#### Notes

- All dizest processes are terminated
- Running workflow executions are also interrupted
- Data loss is possible, use with caution

---

## Service Management Commands

### service

Manages DIZEST as a system service (Linux systemd).

#### Usage

```bash
dizest service <ACTION>
```

#### Actions

| Action | Description |
|--------|-------------|
| `install` | Register as systemd service |
| `uninstall` | Unregister systemd service |
| `start` | Start service |
| `stop` | Stop service |
| `restart` | Restart service |
| `status` | Check service status |

#### Example

```bash
# Register service
sudo dizest service install

# Start service
sudo dizest service start

# Check service status
sudo dizest service status

# Restart service
sudo dizest service restart

# Stop service
sudo dizest service stop

# Unregister service
sudo dizest service uninstall
```

#### Auto-start Configuration

```bash
# After registering service
sudo systemctl enable dizest

# Disable auto-start on boot
sudo systemctl disable dizest
```

#### Check Logs

```bash
# Check systemd logs
sudo journalctl -u dizest -f
```

---

## Environment Variables

DIZEST supports the following environment variables:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DIZEST_HOST` | Default server host | `0.0.0.0` |
| `DIZEST_PORT` | Default server port | `3000` |
| `DIZEST_LOG` | Default log file path | `None` |

#### Usage Example

```bash
# Run server with environment variable
export DIZEST_PORT=4000
dizest run

# One-time configuration
DIZEST_PORT=5000 dizest run
```

---

## Complete Workflow Examples

### 1. Starting a New Project

```bash
# Create project
dizest install myai

# Move to project
cd myai

# Run server
dizest run --port=4000
```

### 2. Production Deployment

```bash
# Create project (on server)
dizest install production --password securepassword123

cd production

# Register systemd service
sudo dizest service install

# Start service
sudo dizest service start

# Enable auto-start
sudo systemctl enable dizest

# Check status
sudo dizest service status
```

### 3. Upgrade

```bash
# Upgrade DIZEST package
pip install dizest --upgrade

# Upgrade project
cd myproject
dizest upgrade

# Restart server (if in daemon mode)
dizest server stop
dizest server start
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check process using port
lsof -i :3000

# Kill process
kill <PID>

# Or use different port
dizest run --port=4000
```

### Permission Error

```bash
# Ports below 1024 require root privileges
sudo dizest run --port=80

# Or use port above 1024
dizest run --port=8080
```

### Server Won't Start

```bash
# Check logs
dizest run --log=debug.log

# Or
cat debug.log
```

### Lost Password

```bash
# Reset password
dizest password newpassword123
```

---

## Related Documentation

- [Usage Guide](../usage-guide.md)
- [Workflow API](workflow.md)
- [Serve API](serve.md)
