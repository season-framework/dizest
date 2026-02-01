# Serve Class API Reference

## Overview

The `Serve` class embeds DIZEST workflows in a Flask web server and provides them as REST APIs.

## Class Definition

```python
from dizest import Serve

serve = Serve(**config)
```

## Constructor

### `__init__(**config)`

Creates a Serve object and initializes the Flask app.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cwd` | `str` | ✗ | `os.getcwd()` | Workflow working directory |
| `max_log_size` | `int` | ✗ | `50` | Maximum number of log entries |
| `host` | `str` | ✗ | `127.0.0.1` | Web server host address |
| `port` | `int` | ✗ | `8000` | Web server port |

#### Example

```python
# Default configuration
serve = Serve()

# Custom configuration
serve = Serve(
    host='0.0.0.0',
    port=5000,
    cwd='/path/to/workdir',
    max_log_size=100
)
```

---

## Properties

### `config`

Server configuration object.

**Type**: `Config`

**Properties**:
- `cwd`: Working directory
- `max_log_size`: Maximum log size
- `host`: Server host
- `port`: Server port

### `workflow`

Internal workflow object.

**Type**: `Workflow`

### `app`

Flask app instance.

**Type**: `flask.Flask`

### `flask`

Flask module reference.

**Type**: `module`

---

## Methods

### Server Control

#### `run()`

Starts the web server (blocking).

##### Example

```python
serve = Serve(host='0.0.0.0', port=8000)
serve.run()  # Start server (exit with Ctrl+C)
```

---

### Event Handling

#### `on(name, fn)`

Registers a workflow event listener.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Event name |
| `fn` | `callable` | Event handler function |

##### Event Types

- `workflow.status`: Workflow status change
- `flow.status`: Flow status change
- `flow.index`: Flow execution order
- `log.append`: Log appended
- `log.clear`: Log cleared
- `result`: Result output

##### Example

```python
serve = Serve()

def on_log(flow_id, event_name, log_message):
    print(f"[{flow_id}] {log_message}")

serve.on('log.append', on_log)

serve.run()
```

---

### Request Handling

#### `query(key=None, default=None)`

Gets query parameters from the current request.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` or `None` | Parameter name to query (or None for all) |
| `default` | `any` | Default value |

##### Return Value

- `key=None`: Dictionary of all query parameters
- `key` specified: Value of that parameter (or `default` if not found)

##### Example

```python
from dizest import Serve

serve = Serve()

@serve.app.route('/api/test')
def test():
    # All parameters
    all_params = serve.query()
    
    # Specific parameters
    message = serve.query('message', default='Hello')
    count = serve.query('count', default=0)
    
    return {'message': message, 'count': count}

serve.run()
```

---

## Default API Endpoints

The Serve class automatically binds the following REST API endpoints:

### Health Check

**Endpoint**: `GET /health`

Checks server status.

**Response**:
```json
{
  "code": 200
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### Workflow API

#### Update Workflow

**Endpoint**: `POST /workflow/update`

Updates the workflow.

**Parameters**:
- `package` (JSON string): Workflow package

**Response**:
```json
{
  "code": 200,
  "data": { /* sync data */ }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/workflow/update \
  -d 'package={"apps":{...},"flow":{...}}'
```

---

#### Get Workflow Status

**Endpoint**: `GET /workflow/status`

Gets the workflow execution status.

**Response**:
```json
{
  "code": 200,
  "status": "idle"
}
```

**Example**:
```bash
curl http://localhost:8000/workflow/status
```

---

#### Run Workflow

**Endpoint**: `POST /workflow/run`

Executes the workflow.

**Response**:
```json
{
  "code": 200,
  "status": "start"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/workflow/run
```

---

#### Stop Workflow

**Endpoint**: `POST /workflow/stop`

Stops the running workflow.

**Response**:
```json
{
  "code": 200
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/workflow/stop
```

---

### Flow API

#### Get Flow Status

**Endpoint**: `GET /flow/status/<flow_id>`

Gets the status of a specific Flow.

**Response**:
```json
{
  "code": 200,
  "status": "idle",
  "index": -1,
  "log": []
}
```

**Example**:
```bash
curl http://localhost:8000/flow/status/my_flow-1234567890
```

---

#### Run Flow

**Endpoint**: `POST /flow/run/<flow_id>`

Executes a specific Flow.

**Parameters**: Pass inputs as URL query parameters

**Response**:
```json
{
  "code": 200,
  "status": "start"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/flow/run/my_flow-1234567890?param1=value1&param2=value2"
```

---

## Adding Custom Endpoints

### Method 1: Using Flask Decorator

```python
from dizest import Serve

serve = Serve()

@serve.app.route('/custom/api')
def custom_api():
    # Get query parameters
    message = serve.query('message', default='Hello')
    
    # Load and execute workflow
    workflow = serve.workflow
    workflow.load('myworkflow.dwp')
    workflow.run()
    
    # Return results
    return {'status': 'success', 'message': message}

serve.run()
```

### Method 2: Writing Binding Class

```python
from dizest.base.binding import BaseBinding

class CustomBinding(BaseBinding):
    NAMESPACE = "custom"
    
    def hello(self):
        name = self.serve.query('name', default='World')
        return {'code': 200, 'message': f'Hello, {name}!'}
    
    def process(self):
        data = self.serve.query('data')
        # Data processing logic
        result = process_data(data)
        return {'code': 200, 'result': result}

# Extend Serve class
from dizest import Serve

class MyServe(Serve):
    def bind(self):
        super().bind()
        CustomBinding(self).bind()

serve = MyServe()
serve.run()
```

Now you can use these endpoints:
- `GET /custom/hello?name=John`
- `POST /custom/process?data=...`

---

## Complete Usage Examples

### Basic Server

```python
from dizest import Serve

# Create server
serve = Serve(host='0.0.0.0', port=8000)

# Event listener
def on_log(flow_id, event, value):
    print(f"[{flow_id}] {value}")

serve.on('log.append', on_log)

# Run server
serve.run()
```

### Server with Custom API

```python
from dizest import Serve
import dizest

serve = Serve(host='0.0.0.0', port=5000)

@serve.app.route('/api/run/<workflow_name>')
def run_workflow(workflow_name):
    # Load workflow
    workflow_path = f'/workflows/{workflow_name}.dwp'
    workflow = dizest.Workflow(workflow_path)
    
    # Collect parameters
    params = serve.query()
    
    # Execute
    workflow.run(**params)
    
    # Collect results
    requested, outputs = workflow.spec()
    result = {}
    
    for flow_id in outputs:
        flow = workflow.flow(flow_id)
        instance = workflow.run.instance(flow)
        for output_name in outputs[flow_id]:
            result[output_name] = instance.output_data.get(output_name)
    
    return {'status': 'success', 'result': result}

serve.run()
```

### Server with Authentication

```python
from dizest import Serve
from functools import wraps

serve = Serve()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = serve.query('token')
        if token != 'secret-token':
            return {'code': 401, 'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated

@serve.app.route('/api/secure')
@require_auth
def secure_api():
    return {'code': 200, 'data': 'Secure data'}

serve.run()
```

---

## Production Deployment

### Deploy with uWSGI

```python
# app.py
from dizest import Serve

serve = Serve()

# uWSGI app object
app = serve.app

if __name__ == '__main__':
    serve.run()
```

**uWSGI Configuration** (`uwsgi.ini`):
```ini
[uwsgi]
module = app:app
master = true
processes = 4
threads = 2
socket = 0.0.0.0:8000
chmod-socket = 660
vacuum = true
die-on-term = true
```

**Run**:
```bash
uwsgi --ini uwsgi.ini
```

### Deploy with Gunicorn

```python
# app.py
from dizest import Serve

serve = Serve()
app = serve.app
```

**Run**:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Deploy with Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

---

## Error Handling

The Serve class automatically handles all exceptions and returns them as JSON responses:

```python
@serve.app.errorhandler(Exception)
def handle_exception(e):
    return {"code": 500, "data": str(e)}
```

You can add custom error handlers:

```python
@serve.app.errorhandler(404)
def not_found(e):
    return {"code": 404, "error": "Not Found"}, 404

@serve.app.errorhandler(ValueError)
def value_error(e):
    return {"code": 400, "error": str(e)}, 400
```

---

## Security Considerations

### CORS Configuration

```python
from flask_cors import CORS

serve = Serve()
CORS(serve.app)
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

serve = Serve()
limiter = Limiter(
    serve.app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@serve.app.route('/api/limited')
@limiter.limit("10 per minute")
def limited():
    return {'status': 'ok'}
```

---

## Related Documentation

- [Workflow API](workflow.md)
- [CLI API](cli.md)
- [Usage Guide](../usage-guide.md)
