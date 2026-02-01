# Workflow Class API Reference

## Overview

The `Workflow` class is the core class of DIZEST that provides functionality for loading, managing, and executing workflow packages.

## Class Definition

```python
from dizest import Workflow

workflow = Workflow(package, **kwargs)
```

## Constructor

### `__init__(package, **kwargs)`

Creates a workflow object.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `package` | `str` or `dict` | ✓ | - | Workflow file path (.dwp) or workflow dictionary |
| `cwd` | `str` | ✗ | `os.getcwd()` | Workflow working directory |
| `max_log_size` | `int` | ✗ | `50` | Maximum number of log entries per Flow |
| `event` | `dict` | ✗ | `{}` | Event handler dictionary |

#### Example

```python
# Load from file path
workflow = Workflow("myworkflow.dwp")

# Specify working directory
workflow = Workflow("myworkflow.dwp", cwd="/path/to/workdir")

# Limit log size
workflow = Workflow("myworkflow.dwp", max_log_size=100)

# Load directly from dictionary
package = {
    "apps": {...},
    "flow": {...}
}
workflow = Workflow(package)
```

---

## Properties

### `config`

Workflow configuration object.

**Type**: `Config`

**Properties**:
- `cwd`: Working directory
- `max_log_size`: Maximum log size
- `event`: Event handler dictionary

### `run`

Workflow execution engine.

**Type**: `Runnable`

### `render`

Workflow renderer.

**Type**: `Renderer`

---

## Methods

### Workflow Management

#### `load(package)`

Loads a workflow package.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `package` | `str` or `dict` | Workflow file path or dictionary |

##### Return Value

`Workflow` - self object

##### Exceptions

- `Exception`: If `apps` or `flow` key is missing

##### Example

```python
workflow = Workflow({"apps": {}, "flow": {}})
workflow.load("updated_workflow.dwp")
```

---

#### `to_dict()`

Returns the workflow as a dictionary.

##### Return Value

`dict` - Workflow package dictionary

##### Example

```python
package = workflow.to_dict()
print(package.keys())  # dict_keys(['apps', 'flow', ...])
```

---

### App Management

#### `apps()`

Returns a list of all App IDs in the workflow.

##### Return Value

`list` - List of App ID strings

##### Example

```python
app_ids = workflow.apps()
# ['app_id_1', 'app_id_2', ...]
```

---

#### `app(app_id)`

Returns a specific App object.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `app_id` | `str` | Unique ID of the App |

##### Return Value

`App` - App object (or `None` if not found)

##### Example

```python
app = workflow.app("my_app_id")
if app:
    print(app.title())
```

---

### Flow Management

#### `flows()`

Returns a list of all Flow objects in the workflow.

##### Return Value

`list` - List of Flow objects

##### Example

```python
flows = workflow.flows()
for flow in flows:
    print(flow.id(), flow.title())
```

---

#### `flow(flow_id)`

Returns a specific Flow object.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `flow_id` | `str` | Unique ID of the Flow |

##### Return Value

`Flow` - Flow object (or `None` if not found)

##### Example

```python
flow = workflow.flow("app_id-1234567890")
if flow:
    print(f"Active: {flow.active()}")
```

---

### Event Handling

#### `on(name, fn)`

Registers an event listener.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Event name (`'*'` for all events) |
| `fn` | `callable` | Event handler function |

##### Event Types

| Event Name | Description | Callback Signature |
|------------|-------------|-------------------|
| `workflow.status` | Overall workflow status change | `fn(flow_id, event_name, value)` |
| `flow.status` | Flow status change | `fn(flow_id, event_name, value)` |
| `flow.index` | Flow execution order index | `fn(flow_id, event_name, value)` |
| `log.append` | Log appended | `fn(flow_id, event_name, value)` |
| `log.clear` | Log cleared | `fn(flow_id, event_name, value)` |
| `result` | Result output | `fn(flow_id, event_name, value)` |
| `*` | All events | `fn(flow_id, event_name, value)` |

##### Flow Status Values

- `idle`: Waiting
- `pending`: Preparing
- `running`: Running
- `ready`: Completed
- `error`: Error occurred

##### Example

```python
# Log event listener
def on_log(flow_id, event_name, log_message):
    print(f"[{flow_id}] {log_message}")

workflow.on('log.append', on_log)

# Status change listener
def on_status(flow_id, event_name, status):
    print(f"Flow {flow_id}: {status}")

workflow.on('flow.status', on_status)

# All events listener
def on_all(flow_id, event_name, value):
    print(f"Event: {event_name} from {flow_id}")

workflow.on('*', on_all)
```

---

### Workflow Analysis

#### `spec()`

Analyzes the workflow's input/output specification.

##### Return Value

`tuple` - `(requested, outputs)`
- `requested`: Required inputs dictionary `{flow_id: {input_name: None}}`
- `outputs`: Provided outputs dictionary `{flow_id: [output_name1, output_name2, ...]}`

##### Example

```python
requested, outputs = workflow.spec()

# Check required external inputs
print("Required inputs:", requested)
# {'flow_1': {'param1': None, 'param2': None}}

# Check final outputs
print("Available outputs:", outputs)
# {'flow_3': ['result', 'summary']}
```

---

## Execution (Runnable Methods)

Workflow execution is performed through the `workflow.run` object.

### `workflow.run(flow=None, threaded=False, **kwargs)`

Executes the workflow.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `flow` | `Flow` | ✗ | `None` | Flow to execute (None for entire workflow) |
| `threaded` | `bool` | ✗ | `False` | Background execution flag |
| `**kwargs` | `dict` | ✗ | `{}` | Input parameters to pass to Flow |

#### Return Value

- `threaded=False`: Blocking execution, returns after completion
- `threaded=True`: Returns `multiprocessing.Process` object

#### Example

```python
# Synchronous execution of entire workflow
workflow.run()

# Execute specific Flow only
flow = workflow.flow("flow_id")
workflow.run(flow)

# Pass parameters
workflow.run(flow, message="Hello", count=10)

# Asynchronous execution
process = workflow.run(flow, threaded=True)
process.join()  # Wait for completion
```

---

### `workflow.run.status()`

Returns the overall workflow execution status.

#### Return Value

`str` - Workflow status
- `idle`: All Flows waiting
- `pending`: Some Flows preparing
- `running`: Some Flows running
- `ready`: All Flows completed
- `error`: Error occurred in some Flows

#### Example

```python
status = workflow.run.status()
print(f"Workflow status: {status}")
```

---

### `workflow.run.instance(flow)`

Returns the execution instance of a specific Flow.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `flow` | `Flow` | Flow object |

#### Return Value

`FlowInstance` - Flow execution instance object

#### Example

```python
flow = workflow.flow("flow_id")
instance = workflow.run.instance(flow)

# Check execution status
print(instance.status())

# Check logs
for log in instance.log():
    print(log)

# Check output data
output_data = instance.output_data
print(output_data)
```

---

### `workflow.run.stop()`

Stops a running workflow.

#### Example

```python
# Start workflow
workflow.run(threaded=True)

# Stop
workflow.run.stop()
```

---

### `workflow.run.sync()`

Synchronizes and returns the status of all Flow instances.

#### Return Value

`dict` - Flow status dictionary `{flow_id: {'status': ..., 'index': ..., 'log': [...]}}`

#### Example

```python
sync_data = workflow.run.sync()
for flow_id, data in sync_data.items():
    print(f"{flow_id}: {data['status']}")
```

---

## Rendering

### `workflow.render(value, **kwargs)`

Converts a value to a renderable format.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `any` | Value to render |
| `**kwargs` | `dict` | Additional options |

#### Supported Types

- `str`: String (HTML possible)
- `dict`, `list`: JSON
- `pandas.DataFrame`: HTML table
- `matplotlib.figure.Figure`: Base64 image
- `plotly.graph_objs.Figure`: Plotly JSON
- `PIL.Image`: Base64 image

#### Return Value

Rendered result (string or dictionary)

#### Example

```python
import pandas as pd

df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
html = workflow.render(df)
print(html)  # HTML table
```

---

## Usage Examples

### Basic Usage

```python
import dizest

# Load workflow
workflow = dizest.Workflow("myworkflow.dwp")

# Register event listeners
workflow.on('log.append', lambda fid, e, log: print(log))

# Execute
workflow.run()

# Check results
requested, outputs = workflow.spec()
for flow_id in outputs:
    flow = workflow.flow(flow_id)
    instance = workflow.run.instance(flow)
    print(f"Output: {instance.output_data}")
```

### Passing Parameters

```python
# Check required inputs
requested, outputs = workflow.spec()

# Provide inputs
params = {
    'param1': 'value1',
    'param2': 100
}

# Execute
for flow_id in requested:
    flow = workflow.flow(flow_id)
    workflow.run(flow, **params)
```

### Conditional Execution

```python
# Activate specific Flows only
for flow in workflow.flows():
    if "test" in flow.title():
        flow.update(active=True)
    else:
        flow.update(active=False)

# Execute active Flows only
workflow.run()
```

---

## Related Documentation

- [Flow Class API](flow.md)
- [App Class API](app.md)
- [FlowInstance Class API](flowinstance.md)
- [Usage Guide](../usage-guide.md)
