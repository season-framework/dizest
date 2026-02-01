# DIZEST Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Creating Workflows](#creating-workflows)
4. [Writing Apps](#writing-apps)
5. [Connecting Flows](#connecting-flows)
6. [Workflow Execution](#workflow-execution)
7. [External API Calls](#external-api-calls)
8. [Advanced Usage](#advanced-usage)

---

## Installation

### 1. Install via pip

```bash
pip install dizest
```

### 2. Create Project

```bash
dizest install myproject
```

When the project is created, an automatically generated password will be displayed:

```
dizest installed at `myproject`
password: aB3dE5fG7hI9jK1l
```

### 3. Install with Custom Password

```bash
dizest install myproject --password mysecretpass
```

### 4. Install from Source (For Developers)

```bash
cd <workspace>
wiz create dizest --uri https://github.com/season-framework/dizest-ui-angular
```

---

## Getting Started

### Running the Server

#### Normal Mode

```bash
cd myproject
dizest run --port 4000 --host 0.0.0.0
```

**Options:**
- `--port`: Web server port (default: 3000)
- `--host`: Web server host (default: 0.0.0.0)
- `--log`: Log file path (default: None)

#### Daemon Mode

```bash
dizest server start  # Start daemon
dizest server stop   # Stop daemon
```

### Accessing the Web UI

Open the following address in your browser:

```
http://localhost:4000
```

Login credentials:
- Username: `root`
- Password: Password generated during installation

---

## Creating Workflows

### 1. Create a New Workflow

1. Click the **New Workflow** button in the Web UI
2. Enter a workflow name (e.g., `my_workflow.dwp`)
3. Click **Create**

### 2. Understanding Workflow Structure

A workflow consists of two main components:

#### App (Application)
- Reusable code block
- Contains Python code, HTML, JavaScript, CSS
- Defines inputs and outputs

#### Flow
- Instance of an App
- Node placed on the canvas
- Can be connected to other Flows

---

## Writing Apps

### 1. Create a New App

Click the **Apps** tab in the left sidebar → Click **+ button**

### 2. Basic App Structure

```json
{
  "id": "unique_app_id",
  "title": "My App",
  "version": "1.0.0",
  "inputs": [
    {
      "type": "variable",
      "name": "message",
      "inputtype": "text"
    },
    {
      "type": "output",
      "name": "data"
    }
  ],
  "outputs": [
    {
      "name": "result"
    }
  ],
  "code": "# Python code"
}
```

### 3. Input Types

#### Variable

User enters the value directly:

```json
{
  "type": "variable",
  "name": "count",
  "inputtype": "number"
}
```

**inputtype options:**
- `text`: Text input
- `number`: Number input
- `checkbox`: Checkbox (boolean)
- `textarea`: Multi-line text

#### Output (Output Connection)

Connect to the output of another Flow:

```json
{
  "type": "output",
  "name": "input_data"
}
```

### 4. Writing Python Code

Write Python code in the App's `code` field.

#### Basic Example

```python
# Receive input
name = dizest.input("name", default="World")

# Set output
result = f"Hello, {name}!"
dizest.output("greeting", result)

# Print log
print(f"Processed: {name}")
```

#### Using Another Flow's Output

```python
# 'data' input is connected to another Flow's output
input_data = dizest.input("data", default=[])

# Process data
processed = [x * 2 for x in input_data]

# Output
dizest.output("result", processed)
```

#### Receiving Multiple Inputs

```python
# All outputs from Flows connected to the same input
all_inputs = dizest.inputs("data")
# Result: [data1, data2, data3, ...]

total = sum(all_inputs)
dizest.output("sum", total)
```

### 5. Visualizing Results

```python
import pandas as pd
import matplotlib.pyplot as plt

# Create data
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

# Plotly chart
import plotly.express as px
fig = px.line(df, x='x', y='y')
dizest.result("chart", fig)

# Table
dizest.result("table", df)

# HTML
html_content = "<h1>Result</h1><p>Completed.</p>"
dizest.result("html", html_content)
```

### 6. Saving and Reading Files

```python
# Storage based on workflow directory
fs = dizest.drive()

# Write file
fs.write("output.txt", "Hello World")

# Read file
content = fs.read("output.txt")

# Subdirectory
fs = dizest.drive("data", "results")
fs.write("result.json", {"status": "success"})
```

---

## Connecting Flows

### 1. Add Flow

1. Drag the desired App from the left **Apps** tab to the canvas
2. A Flow is created

### 2. Connect Flows

#### Connect Output → Input

1. Click the **output point** of the source Flow
2. Drag to the **input point** of the target Flow
3. A connection line is created

#### Connection Example

```
[Flow A] ---output---> [Flow B]
    |                      |
    └---data----------> [Flow C]
```

- Flow A's `output` is passed to Flow B's input
- Flow A's `data` is passed to Flow C's input

### 3. Flow Settings

Click a Flow to display the settings panel on the right:

- **Title**: Flow name (for display)
- **Active**: Whether active (inactive Flows are not executed)
- **Variables**: Set values for variable-type inputs

---

## Workflow Execution

### 1. Execute in Web UI

1. Click the **Run** button in the top toolbar
2. Monitor execution progress in real-time
3. Check logs and results for each Flow

### 2. Execute with Python Code

```python
import dizest

# Load workflow
workflow = dizest.Workflow("myworkflow.dwp")

# Execute
workflow.run()

# Execute only specific Flow
flow = workflow.flow("flow_id")
workflow.run(flow)

# Pass parameters
workflow.run(flow, param1="value1", param2="value2")
```

### 3. Execution Flow

DIZEST automatically calculates the execution order:

1. **Dependency Analysis**: Determine which Flows need outputs from which other Flows
2. **Order Determination**: Determine order based on DAG (Directed Acyclic Graph)
3. **Parallel Execution**: Flows without dependencies are executed simultaneously
4. **Data Transfer**: Pass outputs from previous Flows as inputs to next Flows

---

## External API Calls

### 1. Execute via REST API

```bash
curl "http://localhost:4000/dizest/api/run/myworkflow.dwp?param1=value1&param2=value2"
```

**Response:**
```json
{
  "output1": "result value",
  "output2": [1, 2, 3]
}
```

### 2. Streaming API

To receive real-time logs:

```bash
curl "http://localhost:4000/dizest/api/stream/myworkflow.dwp?param1=value1"
```

Real-time logs are sent in Server-Sent Events (SSE) format.

### 3. API Calls from Python

```python
import requests

response = requests.get(
    "http://localhost:4000/dizest/api/run/myworkflow.dwp",
    params={"message": "Hello"}
)

result = response.json()
print(result)
```

---

## Advanced Usage

### 1. Event Listeners

```python
import dizest

workflow = dizest.Workflow("myworkflow.dwp")

# Log events
def on_log(flow_id, event_name, value):
    print(f"[{flow_id}] {value}")

workflow.on('log.append', on_log)

# Status change events
def on_status(flow_id, event_name, value):
    print(f"Flow {flow_id} status: {value}")

workflow.on('flow.status', on_status)

workflow.run()
```

### 2. Custom Renderer

```python
from dizest.core.renderer import Renderer

class MyRenderer(Renderer):
    def render(self, value, **kwargs):
        # Custom rendering logic
        if isinstance(value, MyCustomType):
            return self.custom_format(value)
        return super().render(value, **kwargs)

# Apply to workflow
workflow.render = MyRenderer()
```

### 3. Embedding with Serve Class

```python
import dizest

# Create server
serve = dizest.Serve(host='0.0.0.0', port=8000)

# Event listener
serve.on('log.append', lambda flow_id, event, value: print(value))

# Run server
serve.run()
```

### 4. Conditional Execution

Dynamically change a Flow's `active` property:

```python
workflow = dizest.Workflow("myworkflow.dwp")

# Deactivate specific Flow
flow = workflow.flow("flow_id")
flow.update(active=False)

# Execute (inactive Flows are skipped)
workflow.run()
```

### 5. Workflow Analysis

```python
# Check required inputs and provided outputs
requested, outputs = workflow.spec()

print("Required inputs:", requested)
# {'flow_id': {'param1': None, 'param2': None}}

print("Final outputs:", outputs)
# {'flow_id': ['output1', 'output2']}
```

### 6. Log Size Limit

```python
workflow = dizest.Workflow(
    "myworkflow.dwp",
    max_log_size=100  # Keep maximum 100 log entries
)
```

### 7. Set Working Directory

```python
workflow = dizest.Workflow(
    "myworkflow.dwp",
    cwd="/path/to/working/directory"
)
```

---

## Best Practices

### 1. App Design Principles

- **Single Responsibility**: Each App should perform one clear function
- **Reusability**: Generalize so Apps can be used in various workflows
- **Documentation**: Specify the App's purpose in the `description` field

### 2. Error Handling

```python
try:
    # Perform work
    result = process_data(dizest.input("data"))
    dizest.output("result", result)
except Exception as e:
    # Log error
    print(f"Error: {str(e)}")
    # Output default value
    dizest.output("result", None)
```

### 3. Performance Optimization

- Save large data to files and pass only the path
- Cache intermediate results for reuse in re-execution
- Separate independent tasks into different Flows for parallel execution

### 4. Debugging

```python
# Print debug information
print(f"Input type: {type(dizest.input('data'))}")
print(f"Input value: {dizest.input('data')}")

# Check intermediate results
dizest.result("debug", intermediate_value)
```

---

## Next Steps

- Check detailed API documentation in [API Reference](api/README.md)
- Understand workflow file format in [DWP Specification](dwp-specification.md)
- Explore various use cases in [Examples](examples.md)

---

## Troubleshooting

### Workflow Not Executing

1. Verify that all Flows have `active` property set to `true`
2. Check for circular dependencies
3. Verify that all required inputs are provided

### Cannot Connect Flows

1. Verify that output type and input type match
2. Check that Flow is in active state

### Data Not Being Transferred

1. Verify that source Flow outputs data with `dizest.output()`
2. Check that output name and input name match exactly
3. Verify execution order is correct (check dependency analysis result)
