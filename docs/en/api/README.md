# API Reference

Detailed API documentation for DIZEST's core classes and interfaces.

## Core Classes

### [Workflow Class](workflow.md)

The core class for loading, managing, and executing workflows.

**Key Methods:**
- `__init__(package, **kwargs)` - Create workflow
- `load(package)` - Load workflow
- `apps()` - Get App list
- `app(app_id)` - Get specific App
- `flows()` - Get Flow list
- `flow(flow_id)` - Get specific Flow
- `on(name, fn)` - Register event listener
- `spec()` - Analyze workflow inputs/outputs
- `run(flow, **kwargs)` - Execute workflow

**Usage Example:**
```python
import dizest

workflow = dizest.Workflow("myworkflow.dwp")
workflow.on('log.append', lambda f, e, log: print(log))
workflow.run()
```

---

### [Flow, App, FlowInstance Classes](flow-app-instance.md)

Core components that make up a workflow.

#### Flow Class

An instance of an App placed on the canvas.

**Key Methods:**
- `id()` - Get Flow ID
- `title()` - Get Flow title
- `active()` - Check active status
- `app()` - Get referenced App
- `inputs()` - Get input information
- `previous()` - Get previous Flow list
- `update(**kwargs)` - Update Flow properties

#### App Class

Reusable code blocks.

**Key Methods:**
- `id()` - Get App ID
- `title()` - Get App title
- `code()` - Get Python code
- `inputs()` - Get input definitions
- `outputs()` - Get output definitions
- `update(**kwargs)` - Update App properties

#### FlowInstance Class

Manages the state of a running Flow.

**Key Methods:**
- `status(value)` - Get/set status
- `log(value)` - Get/append log
- `input(name, default)` - Get input
- `inputs(name)` - Get multiple inputs
- `output(*args, **kwargs)` - Set/get output
- `result(name, value)` - Render result
- `drive(*path)` - File storage
- `clear()` - Clear logs

**Usage Example (Inside App Code):**
```python
# Get input
data = dizest.input("data", default=[])
message = dizest.input("message", default="Hello")

# Process
result = [x * 2 for x in data]

# Output
dizest.output("result", result)
print(f"Processed {len(result)} items")

# Save file
fs = dizest.drive()
fs.write("output.json", {"result": result})
```

---

### [Serve Class](serve.md)

Runs DIZEST as a Flask web server and provides REST API.

**Key Methods:**
- `__init__(**config)` - Create server
- `run()` - Start server
- `on(name, fn)` - Register event listener
- `query(key, default)` - Get query parameter

**Default API Endpoints:**
- `GET /health` - Health check
- `POST /workflow/update` - Update workflow
- `GET /workflow/status` - Get workflow status
- `POST /workflow/run` - Run workflow
- `POST /workflow/stop` - Stop workflow
- `GET /flow/status/<flow_id>` - Get Flow status
- `POST /flow/run/<flow_id>` - Run Flow

**Usage Example:**
```python
from dizest import Serve

serve = Serve(host='0.0.0.0', port=8000)

@serve.app.route('/custom')
def custom_api():
    param = serve.query('param', default='default')
    return {'status': 'ok', 'param': param}

serve.run()
```

---

### [CLI Commands](cli.md)

DIZEST command-line interface.

**Project Management:**
- `dizest install [PROJECT_NAME]` - Create project
- `dizest upgrade` - Upgrade project
- `dizest password <PASSWORD>` - Change password

**Server Execution:**
- `dizest run` - Run server (foreground)
- `dizest server start` - Start server (daemon)
- `dizest server stop` - Stop server
- `dizest kill` - Kill all server processes

**Service Management:**
- `dizest service install` - Register systemd service
- `dizest service start` - Start service
- `dizest service stop` - Stop service
- `dizest service status` - Check service status

---

## Data Types and Structures

### Workflow Package Structure

```python
{
    "apps": {
        "app_id": {
            "id": str,
            "title": str,
            "version": str,
            "inputs": list,
            "outputs": list,
            "code": str,
            ...
        }
    },
    "flow": {
        "flow_id": {
            "id": str,
            "app_id": str,
            "active": bool,
            "inputs": dict,
            "outputs": dict,
            "data": dict,
            "pos_x": int,
            "pos_y": int,
            ...
        }
    },
    ...
}
```

### Event Types

| Event | Parameters | Description |
|-------|------------|-------------|
| `workflow.status` | `(flow_id, event_name, status)` | Workflow status change |
| `flow.status` | `(flow_id, event_name, status)` | Flow status change |
| `flow.index` | `(flow_id, event_name, index)` | Flow execution order |
| `log.append` | `(flow_id, event_name, log)` | Log appended |
| `log.clear` | `(flow_id, event_name, value)` | Log cleared |
| `result` | `(flow_id, event_name, result)` | Result output |

### Flow Status Values

- `idle` - Waiting
- `pending` - Preparing
- `running` - Running
- `ready` - Completed
- `error` - Error occurred

---

## Quick Reference

### Workflow Execution

```python
import dizest

# Load
workflow = dizest.Workflow("workflow.dwp")

# Events
workflow.on('log.append', handler)

# Execute
workflow.run()

# Results
requested, outputs = workflow.spec()
for flow_id in outputs:
    flow = workflow.flow(flow_id)
    instance = workflow.run.instance(flow)
    print(instance.output_data)
```

### App Code Writing

```python
# Input
data = dizest.input("data", default=[])
param = dizest.input("param", default=1)

# Process
result = process(data, param)

# Output
dizest.output("result", result)

# Log
print(f"Processed {len(data)} items")

# Result visualization
import pandas as pd
df = pd.DataFrame(result)
dizest.result("table", df)

# Save file
fs = dizest.drive()
fs.write("output.json", result)
```

### REST API Calls

```bash
# Run workflow
curl "http://localhost:4000/dizest/api/run/workflow.dwp?param1=value1"

# Streaming execution
curl "http://localhost:4000/dizest/api/stream/workflow.dwp?param1=value1"
```

---

## Related Documentation

- [Usage Guide](../usage-guide.md) - Complete usage instructions
- [Architecture](../architecture.md) - System structure
- [DWP File Specification](../dwp-specification.md) - File format
- [Examples](../examples.md) - Use cases
