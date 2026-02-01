# Flow, App, FlowInstance Class API Reference

## Table of Contents

1. [Flow Class](#flow-class)
2. [App Class](#app-class)
3. [FlowInstance Class](#flowinstance-class)

---

## Flow Class

A Flow is an instance of an App placed on the workflow canvas.

### Overview

```python
flow = workflow.flow(flow_id)
```

### Methods

#### `id()`

Returns the unique identifier of the Flow.

##### Return Value

`str` - Flow ID (e.g., `app_id-1234567890`)

##### Example

```python
flow_id = flow.id()
print(flow_id)  # "my_app-1706123456789"
```

---

#### `title()`

Returns the display name of the Flow.

##### Return Value

`str` - Flow title (or App's title if not set)

##### Example

```python
title = flow.title()
print(title)  # "My Custom Flow"
```

---

#### `active()`

Checks the activation status of the Flow.

##### Return Value

`bool` - `True` if active, `False` if inactive

##### Example

```python
if flow.active():
    print("This flow will be executed")
else:
    print("This flow is disabled")
```

---

#### `app()`

Returns the App object that this Flow references.

##### Return Value

`App` - App object

##### Example

```python
app = flow.app()
print(f"App title: {app.title()}")
print(f"App code:\n{app.code()}")
```

---

#### `inputs()`

Returns the Flow's input information.

##### Return Value

`dict` - Input dictionary
```python
{
    "input_name": {
        "type": "output" or "variable",
        "data": [...] or value,
        "inputtype": "text" | "number" | ...  # for variable type
    }
}
```

**Input Types:**
- `output`: Connected to another Flow's output
  - `data`: `[[source_flow_id, output_name], ...]`
- `variable`: User input value
  - `data`: Input value
  - `inputtype`: Input field type

##### Example

```python
inputs = flow.inputs()

for name, info in inputs.items():
    if info['type'] == 'output':
        print(f"{name}: connected to {info['data']}")
    else:
        print(f"{name}: value = {info['data']}")

# Output example:
# data: connected to [['flow_1', 'result']]
# message: value = Hello World
```

---

#### `previous()`

Returns a list of previous Flow IDs that this Flow depends on.

##### Return Value

`list` - List of previous Flow ID strings

##### Example

```python
prev_flows = flow.previous()
print(f"This flow depends on: {prev_flows}")
# ['flow_1', 'flow_2']
```

---

#### `package()`

Returns the raw package dictionary of the Flow.

##### Return Value

`dict` - Flow package data

##### Example

```python
pkg = flow.package()
print(pkg.keys())
# dict_keys(['id', 'app_id', 'active', 'inputs', 'outputs', 'data', 'pos_x', 'pos_y', ...])
```

---

#### `update(**kwargs)`

Updates Flow properties.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `**kwargs` | dict | Dictionary of properties to update |

##### Example

```python
# Deactivate Flow
flow.update(active=False)

# Change Flow title
flow.update(title="Updated Title")

# Change multiple properties at once
flow.update(
    active=True,
    title="New Title",
    description="Updated description"
)
```

---

## App Class

An App is a reusable code block that can be used in multiple Flows.

### Overview

```python
app = workflow.app(app_id)
# or
app = flow.app()
```

### Methods

#### `id()`

Returns the unique identifier of the App.

##### Return Value

`str` - App ID

##### Example

```python
app_id = app.id()
print(app_id)  # "my_custom_app"
```

---

#### `title()`

Returns the title of the App.

##### Return Value

`str` - App title (or `"Unknown"` if not set)

##### Example

```python
title = app.title()
print(title)  # "Data Processor"
```

---

#### `code()`

Returns the Python code of the App.

##### Return Value

`str` - Python code

##### Example

```python
code = app.code()
print(code)
# output:
# data = dizest.input("data", [])
# result = [x * 2 for x in data]
# dizest.output("result", result)
```

---

#### `api()`

Returns the REST API code of the App.

##### Return Value

`str` - API code

##### Example

```python
api_code = app.api()
if api_code:
    print("This app has API endpoint")
```

---

#### `inputs()`

Returns the App's input definitions.

##### Return Value

`list` - List of input definitions
```python
[
    {
        "type": "output" or "variable",
        "name": "input_name",
        "inputtype": "text" | "number" | ...  # for variable type
    }
]
```

##### Example

```python
inputs = app.inputs()
for inp in inputs:
    print(f"{inp['name']} ({inp['type']})")

# Output:
# data (output)
# message (variable)
# count (variable)
```

---

#### `outputs()`

Returns the list of App output names.

##### Return Value

`list` - List of output name strings

##### Example

```python
outputs = app.outputs()
print(f"This app outputs: {outputs}")
# ['result', 'summary', 'status']
```

---

#### `update(**kwargs)`

Updates App properties.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `**kwargs` | dict | Dictionary of properties to update |

##### Example

```python
# Update code
app.update(code="""
data = dizest.input("data")
processed = process(data)
dizest.output("result", processed)
""")

# Update title and description
app.update(
    title="Updated App",
    description="New description"
)
```

---

## FlowInstance Class

FlowInstance manages the state of a running Flow.

### Overview

```python
instance = workflow.run.instance(flow)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `flow` | `Flow` | Associated Flow object |
| `data` | `dict` | Input data |
| `output_data` | `dict` | Output data |
| `timestamp` | `float` | Creation time (Unix timestamp) |
| `process` | `Process` | Execution process object |

### Methods

#### `status(value=None)`

Gets or sets the Flow execution status.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `str` or `None` | Status to set (or None to query) |

##### Status Values

- `idle`: Waiting
- `pending`: Preparing
- `running`: Running
- `ready`: Completed
- `error`: Error occurred

##### Return Value

`str` - Current status

##### Example

```python
# Query status
current_status = instance.status()
print(current_status)  # "running"

# Change status
instance.status("ready")
```

---

#### `index(value=None)`

Gets or sets the Flow execution order index.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `int` or `None` | Index to set (or None to query) |

##### Return Value

`int` - Execution order index

##### Example

```python
idx = instance.index()
print(f"Execution order: {idx}")
```

---

#### `log(value=None)`

Gets or appends log messages.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `str` or `None` | Log message to append (or None to query) |

##### Return Value

`list` - List of log messages

##### Example

```python
# Append logs
instance.log("Processing started")
instance.log("Data loaded successfully")

# Query logs
logs = instance.log()
for log in logs:
    print(log)
```

---

#### `clear()`

Clears logs.

##### Example

```python
instance.clear()
```

---

#### `input(name, default=None)`

Gets an input value.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Input name |
| `default` | `any` | Default value (if input is not available) |

##### Return Value

Input value (connected output or variable value)

##### Example

```python
# Basic usage
data = instance.input("data", default=[])

# Numeric input (automatic type conversion)
count = instance.input("count", default=0)

# String input
message = instance.input("message", default="Hello")
```

---

#### `inputs(name)`

Returns a list of all output values connected to a specific input.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Input name |

##### Return Value

`list` - List of all connected output values

##### Example

```python
# When multiple Flow outputs are connected to a single input
all_data = instance.inputs("data")
# [data1, data2, data3]

# Calculate sum
total = sum(all_data)
```

---

#### `output(*args, **kwargs)`

Sets or gets output values.

##### Usage 1: Query single value

```python
value = instance.output("result")
```

##### Usage 2: Set single value

```python
instance.output("result", value)
```

##### Usage 3: Set multiple values

```python
instance.output(result=value1, summary=value2)
```

##### Example

```python
# Set outputs
instance.output("result", [1, 2, 3])
instance.output("status", "success")

# Set multiple outputs at once
instance.output(
    result=[1, 2, 3],
    status="success",
    count=3
)

# Query output
result = instance.output("result")
print(result)  # [1, 2, 3]
```

---

#### `result(name, value, **kwargs)`

Renders and outputs a result.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Result name |
| `value` | `any` | Result value |
| `**kwargs` | `dict` | Rendering options |

##### Example

```python
import pandas as pd
import plotly.express as px

# Table output
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
instance.result("table", df)

# Chart output
fig = px.line(df, x='a', y='b')
instance.result("chart", fig)

# HTML output
html = "<h1>Complete</h1>"
instance.result("html", html)
```

---

#### `drive(*path)`

Returns a storage object based on the workflow working directory.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `*path` | `str` | Path segments |

##### Return Value

`Storage` - Storage object

##### Example

```python
# Root directory
fs = instance.drive()
fs.write("output.txt", "Hello")

# Subdirectory
fs = instance.drive("data", "results")
fs.write("result.json", {"status": "ok"})

# Read file
content = fs.read("output.txt")
```

---

#### `binding(flask=None, path=None)`

Creates a web request binding object (for API apps).

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `flask` | `Flask` | Flask app object |
| `path` | `str` | Request path |

##### Return Value

`Binding` - Binding object

##### Binding Object Properties

| Property | Type | Description |
|----------|------|-------------|
| `flow` | `Flow` | Flow object |
| `input(name, default)` | `function` | Query input |
| `inputs(name)` | `function` | Query multiple inputs |
| `output(*args, **kwargs)` | `function` | Set/get output |
| `result(name, value)` | `function` | Output result |
| `drive(*path)` | `function` | Storage |
| `clear()` | `function` | Clear logs |
| `request` | `Request` | Web request object (if flask provided) |
| `response` | `Response` | Web response object (if flask provided) |
| `run(flow, **kwargs)` | `function` | Execute workflow (if flask provided) |
| `stop()` | `function` | Stop workflow (if flask provided) |

##### Example

```python
# Used in API code (app.api field)
wiz = instance.binding(flask_app, request_path)

# Query input
data = dizest.input("data", default=[])

# Set output
dizest.output("result", processed_data)

# Web response
dizest.response.json({"status": "ok"})
```

---

#### `run(threaded=True, **params)`

Executes a Flow (from within FlowInstance).

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threaded` | `bool` | `True` | Background execution flag |
| `**params` | `dict` | `{}` | Input parameters |

##### Example

```python
# Execute another Flow from current Flow
another_flow = workflow.flow("other_flow_id")
instance.run(another_flow, threaded=True, param1="value1")
```

---

## Usage Examples

### Check Flow Information

```python
workflow = dizest.Workflow("myworkflow.dwp")

for flow in workflow.flows():
    print(f"Flow: {flow.id()}")
    print(f"  Title: {flow.title()}")
    print(f"  Active: {flow.active()}")
    print(f"  App: {flow.app().title()}")
    print(f"  Inputs: {list(flow.inputs().keys())}")
    print(f"  Previous: {flow.previous()}")
    print()
```

### Check Results After Execution

```python
workflow = dizest.Workflow("myworkflow.dwp")
workflow.run()

for flow in workflow.flows():
    instance = workflow.run.instance(flow)
    print(f"Flow: {flow.id()}")
    print(f"  Status: {instance.status()}")
    print(f"  Output: {instance.output_data}")
    print(f"  Logs: {instance.log()}")
    print()
```

### Use in App Code (wiz object)

In the App's `code` field, access FlowInstance functionality through the `wiz` object:

```python
# Get inputs
data = dizest.input("data", default=[])
message = dizest.input("message", default="Hello")

# Process
result = [x * 2 for x in data]

# Outputs
dizest.output("result", result)
dizest.output("count", len(result))

# Result visualization
import pandas as pd
df = pd.DataFrame(result, columns=['value'])
dizest.result("table", df)

# Log
print(f"Processed {len(data)} items")

# Save file
fs = dizest.drive()
fs.write("result.json", {"data": result})
```

---

## Related Documentation

- [Workflow Class API](workflow.md)
- [Serve Class API](serve.md)
- [Usage Guide](../usage-guide.md)
