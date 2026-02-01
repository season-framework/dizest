# DWP File Specification Guide

## Overview

DWP (DIZEST Workflow Package) files are JSON-format files that store DIZEST workflows. The file extension `.dwp` is used.

## File Structure

### Top-Level Structure

```json
{
  "apps": {},
  "flow": {},
  "title": "",
  "description": "",
  "version": "",
  "visibility": "",
  "category": "",
  "featured": "",
  "logo": "",
  "id": "",
  "kernel_id": "",
  "executable": null,
  "executable_name": "",
  "extra": {},
  "favorite": ""
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `apps` | object | App definition dictionary |
| `flow` | object | Flow instance dictionary |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `""` | Workflow title |
| `description` | string | `""` | Workflow description |
| `version` | string | `""` | Version information |
| `visibility` | string | `"private"` | Visibility scope (`public`, `private`) |
| `category` | string | `""` | Category |
| `featured` | string | `""` | Featured workflow flag |
| `logo` | string | `""` | Logo image URL |
| `id` | string | `""` | Unique workflow ID |
| `kernel_id` | string | `""` | Execution kernel ID |
| `executable` | string/null | `null` | Executable file path |
| `executable_name` | string | `"base"` | Execution environment name |
| `extra` | object | `{}` | Additional metadata |
| `favorite` | string | `"0"` | Favorite flag |

---

## Apps Object

The `apps` object contains definitions of reusable Apps.

### Structure

```json
{
  "apps": {
    "app_id_1": { /* App definition */ },
    "app_id_2": { /* App definition */ },
    ...
  }
}
```

### App Definition

```json
{
  "id": "unique_app_id",
  "title": "App Title",
  "version": "1.0.0",
  "description": "App description",
  "cdn": {
    "js": [],
    "css": []
  },
  "inputs": [],
  "outputs": [],
  "code": "",
  "api": "",
  "html": "",
  "js": "",
  "css": ""
}
```

### App Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique app identifier |
| `title` | string | ✓ | App display name |
| `version` | string | ✗ | App version |
| `description` | string | ✗ | App description |
| `cdn` | object | ✗ | External library CDN |
| `cdn.js` | array | ✗ | JavaScript library URL list |
| `cdn.css` | array | ✗ | CSS library URL list |
| `inputs` | array | ✓ | Input definition array |
| `outputs` | array | ✓ | Output definition array |
| `code` | string | ✗ | Python execution code |
| `api` | string | ✗ | REST API code |
| `html` | string | ✗ | HTML template |
| `js` | string | ✗ | JavaScript code |
| `css` | string | ✗ | CSS styles |

### Input Definition (inputs)

```json
{
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
  ]
}
```

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✓ | Input type (`variable` or `output`) |
| `name` | string | ✓ | Input name (used as Python variable name) |
| `inputtype` | string | ✗ | Input field type (for variable type) |

#### inputtype Values

| Value | Description |
|-------|-------------|
| `text` | Text input |
| `number` | Number input |
| `textarea` | Multi-line text |
| `checkbox` | Checkbox (boolean) |
| `select` | Dropdown selection |

### Output Definition (outputs)

```json
{
  "outputs": [
    {
      "name": "result"
    },
    {
      "name": "summary"
    }
  ]
}
```

#### Output Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✓ | Output name |

---

## Flow Object

The `flow` object defines App instances placed on the canvas.

### Structure

```json
{
  "flow": {
    "flow_id_1": { /* Flow definition */ },
    "flow_id_2": { /* Flow definition */ },
    ...
  }
}
```

### Flow Definition

```json
{
  "id": "app_id-1234567890",
  "app_id": "app_id",
  "active": true,
  "title": "",
  "description": "",
  "class": "",
  "name": "",
  "typenode": false,
  "pos_x": 100,
  "pos_y": 200,
  "height": 152,
  "data": {},
  "inputs": {},
  "outputs": {}
}
```

### Flow Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique flow ID (format: `app_id-timestamp`) |
| `app_id` | string | ✓ | Referenced App ID |
| `active` | boolean | ✓ | Active status |
| `title` | string | ✗ | Flow title (uses App title if empty) |
| `description` | string | ✗ | Flow description |
| `class` | string | ✗ | CSS class |
| `name` | string | ✗ | Flow name |
| `typenode` | boolean | ✗ | Type node flag |
| `pos_x` | number | ✓ | X coordinate on canvas |
| `pos_y` | number | ✓ | Y coordinate on canvas |
| `height` | number | ✗ | Node height |
| `data` | object | ✓ | Variable input values |
| `inputs` | object | ✓ | Input connection information |
| `outputs` | object | ✓ | Output connection information |

### data Object

Stores values for variable-type inputs.

```json
{
  "data": {
    "message": "Hello World",
    "count": "10",
    "enabled": true
  }
}
```

### inputs Object

Defines connections from other Flow outputs.

```json
{
  "inputs": {
    "data": {
      "connections": [
        {
          "node": "source_flow_id",
          "input": "output_name"
        }
      ]
    }
  }
}
```

#### Input Connection Fields

| Field | Type | Description |
|-------|------|-------------|
| `connections` | array | Connection array |
| `connections[].node` | string | Source Flow ID |
| `connections[].input` | string | Source Flow output name |

### outputs Object

Defines output connections to other Flows.

```json
{
  "outputs": {
    "result": {
      "connections": [
        {
          "node": "target_flow_id",
          "output": "input_name"
        }
      ]
    }
  }
}
```

#### Output Connection Fields

| Field | Type | Description |
|-------|------|-------------|
| `connections` | array | Connection array |
| `connections[].node` | string | Target Flow ID |
| `connections[].output` | string | Target Flow input name |

---

## Complete Example

### Simple Workflow

```json
{
  "title": "Simple Workflow",
  "description": "A simple data processing workflow",
  "version": "1.0.0",
  "visibility": "private",
  "category": "data-processing",
  "apps": {
    "data_loader": {
      "id": "data_loader",
      "title": "Data Loader",
      "version": "1.0.0",
      "description": "Load data from file",
      "cdn": {
        "js": [],
        "css": []
      },
      "inputs": [
        {
          "type": "variable",
          "name": "filepath",
          "inputtype": "text"
        }
      ],
      "outputs": [
        {
          "name": "data"
        }
      ],
      "code": "import json\nwith open(filepath) as f:\n    data = json.load(f)\ndizest.output('data', data)",
      "api": "",
      "html": "",
      "js": "",
      "css": ""
    },
    "data_processor": {
      "id": "data_processor",
      "title": "Data Processor",
      "version": "1.0.0",
      "description": "Process data",
      "cdn": {
        "js": [],
        "css": []
      },
      "inputs": [
        {
          "type": "output",
          "name": "input_data"
        },
        {
          "type": "variable",
          "name": "multiplier",
          "inputtype": "number"
        }
      ],
      "outputs": [
        {
          "name": "result"
        }
      ],
      "code": "data = dizest.input('input_data', [])\nmult = dizest.input('multiplier', 1)\nresult = [x * mult for x in data]\ndizest.output('result', result)\nprint(f'Processed {len(result)} items')",
      "api": "",
      "html": "",
      "js": "",
      "css": ""
    }
  },
  "flow": {
    "data_loader-1706123456789": {
      "id": "data_loader-1706123456789",
      "app_id": "data_loader",
      "active": true,
      "title": "",
      "description": "",
      "class": "",
      "name": "",
      "typenode": false,
      "pos_x": 100,
      "pos_y": 100,
      "height": 152,
      "data": {
        "filepath": "data.json"
      },
      "inputs": {},
      "outputs": {
        "data": {
          "connections": [
            {
              "node": "data_processor-1706123456790",
              "output": "input_data"
            }
          ]
        }
      }
    },
    "data_processor-1706123456790": {
      "id": "data_processor-1706123456790",
      "app_id": "data_processor",
      "active": true,
      "title": "",
      "description": "",
      "class": "",
      "name": "",
      "typenode": false,
      "pos_x": 400,
      "pos_y": 100,
      "height": 152,
      "data": {
        "multiplier": "2"
      },
      "inputs": {
        "input_data": {
          "connections": [
            {
              "node": "data_loader-1706123456789",
              "input": "data"
            }
          ]
        }
      },
      "outputs": {
        "result": {
          "connections": []
        }
      }
    }
  },
  "id": "simple_workflow.dwp",
  "kernel_id": "root-f07b4cf6-fbf3-11f0-b01a-3a26b58698d4",
  "executable": null,
  "executable_name": "base",
  "extra": {},
  "favorite": "0"
}
```

---

## Validation Rules

### Required Validation

1. **Top-Level Structure**
   - `apps` object exists
   - `flow` object exists

2. **App Definition**
   - Each App has a unique `id`
   - `title` field exists
   - `inputs`, `outputs` arrays exist

3. **Flow Definition**
   - Each Flow has a unique `id`
   - `app_id` references an App that exists in the `apps` object
   - `active`, `pos_x`, `pos_y` fields exist

### Connection Validation

1. **Input Connections**
   - Each key in `inputs` matches a name defined in the App's `inputs`
   - `connections[].node` references an existing Flow ID
   - `connections[].input` matches the source Flow's output name

2. **Output Connections**
   - Each key in `outputs` matches a name defined in the App's `outputs`
   - `connections[].node` references an existing Flow ID
   - `connections[].output` matches the target Flow's input name

### Circular Dependency Validation

- Flow connections must not form circular structures
- Must maintain DAG (Directed Acyclic Graph) structure

---

## File Creation and Modification

### Creating DWP with Python

```python
import json

workflow = {
    "apps": {
        "my_app": {
            "id": "my_app",
            "title": "My App",
            "version": "1.0.0",
            "description": "",
            "cdn": {"js": [], "css": []},
            "inputs": [
                {"type": "variable", "name": "input1", "inputtype": "text"}
            ],
            "outputs": [
                {"name": "output1"}
            ],
            "code": "output1 = input1.upper()\ndizest.output('output1', output1)",
            "api": "",
            "html": "",
            "js": "",
            "css": ""
        }
    },
    "flow": {
        "my_app-1234567890": {
            "id": "my_app-1234567890",
            "app_id": "my_app",
            "active": True,
            "title": "",
            "description": "",
            "class": "",
            "name": "",
            "typenode": False,
            "pos_x": 100,
            "pos_y": 100,
            "height": 152,
            "data": {"input1": "hello"},
            "inputs": {},
            "outputs": {"output1": {"connections": []}}
        }
    },
    "title": "My Workflow",
    "description": "",
    "version": "1.0.0",
    "visibility": "private",
    "category": "",
    "id": "myworkflow.dwp"
}

with open("myworkflow.dwp", "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)
```

### Modifying Existing DWP

```python
import json
import dizest

# Load
workflow = dizest.Workflow("myworkflow.dwp")

# Add Flow
# (Recommended to perform in web UI)

# Save as dictionary
package = workflow.to_dict()

with open("modified.dwp", "w", encoding="utf-8") as f:
    json.dump(package, f, indent=2, ensure_ascii=False)
```

---

## Best Practices

### 1. ID Naming Conventions

- **App ID**: Use lowercase and underscores (e.g., `data_loader`, `ml_model`)
- **Flow ID**: Use `{app_id}-{timestamp}` format (e.g., `data_loader-1706123456789`)

### 2. Version Management

- Update the `version` field when modifying the workflow
- Use semantic versioning recommended (e.g., `1.0.0`, `1.1.0`, `2.0.0`)

### 3. Documentation

- Specify the workflow purpose in the `description` field
- Write functional descriptions in each App's `description`

### 4. File Management

- Include workflow files in version control systems (Git)
- Manage sensitive information (passwords, etc.) with environment variables

---

## Related Documents

- [Usage Guide](../usage-guide.md)
- [Workflow API](workflow.md)
- [Architecture](../architecture.md)
