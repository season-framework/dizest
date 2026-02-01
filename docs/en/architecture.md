# DIZEST Architecture

## Overview

DIZEST (Data Intelligence Workflow Execution System & Tools) is a web technology-based low-code workflow platform that enables visual composition and execution of artificial intelligence and data analysis tasks.

## System Architecture

### 1. Layered Structure

DIZEST is designed with the following layered architecture:

```
┌─────────────────────────────────────────┐
│         Frontend (Angular)              │
│  - Workflow Editor                      │
│  - Visualization Interface              │
│  - Drawflow-based Canvas                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           REST API Layer                │
│  - /dizest/api/run/<workflow>           │
│  - /dizest/api/stream/<workflow>        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Core Engine Layer              │
│  - Workflow: Workflow Management        │
│  - Runnable: Execution Engine           │
│  - Renderer: Rendering Engine           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Workflow Components             │
│  - App: Reusable Components             │
│  - Flow: App Instances                  │
│  - FlowInstance: Running Flow           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Storage Layer (.dwp)           │
│  - JSON-based Workflow Package          │
└─────────────────────────────────────────┘
```

### 2. Core Components

#### 2.1 Workflow

Workflow is the central object of DIZEST, composed of multiple Apps and Flows.

**Key Responsibilities:**
- Load and manage workflow packages (.dwp)
- Manage relationships between Apps and Flows
- Execute workflows and manage state
- Handle and propagate events

**Components:**
- `apps`: Reusable component definitions (dictionary)
- `flow`: App instances and connection information (dictionary)
- `run`: Runnable object (execution engine)
- `config`: Workflow configuration

#### 2.2 App (Application)

App is a reusable functional unit. A single App can be used in multiple Flows.

**Structure:**
- `id`: Unique identifier
- `title`: Display name
- `code`: Python execution code
- `api`: REST API endpoint
- `inputs`: Input definition array
- `outputs`: Output definition array
- `html`, `js`, `css`: UI components

**Input Types:**
- `output`: Connected to output from another Flow
- `variable`: User-entered value

#### 2.3 Flow

Flow is an instance of an App, the actual node placed on the workflow canvas.

**Structure:**
- `id`: Unique identifier (e.g., `app_id-timestamp`)
- `app_id`: ID of the referenced App
- `active`: Activation status
- `inputs`: Input connection information
- `outputs`: Output connection information
- `data`: Variable values at Flow level
- `pos_x`, `pos_y`: Position on canvas

**Connection Structure:**
```json
{
  "inputs": {
    "input_name": {
      "connections": [
        {"node": "source_flow_id", "input": "output_name"}
      ]
    }
  }
}
```

#### 2.4 Runnable (Execution Engine)

The core engine responsible for executing workflows. DIZEST's most important component that manages DAG-based dependency analysis and parallel execution.

**Key Features:**
- Calculate Flow execution order (DAG-based)
- Manage parallel execution
- Pass data between Flows
- Track execution state (idle, pending, running, ready, error)

**FlowInstance:**
- Manages state of running Flow
- Caches input/output data
- Collects logs
- Emits events

**FlowInstance State Transitions:**

```
        [Created]
          ↓
     ┌─> idle ──────────┐
     │    ↓             │
     │  pending         │
     │    ↓             │
     │  running ────┐   │
     │    ↓         ↓   │
     │  ready     error │
     │    ↓         ↓   │
     └────┴─────────┴───┘
        [End/Re-run]
```

**State Descriptions:**
- `idle`: Initial state, waiting
- `pending`: Entered execution queue
- `running`: Code executing
- `ready`: Successfully completed
- `error`: Execution error occurred

**DAG Analysis Algorithm:**

The Runnable engine analyzes workflow dependencies through the `workflow.spec()` method:

```python
requested_inputs, outputs = workflow.spec(target_flows=[flow_id])
```

This method:
1. Backward traversal from target Flow
2. Check dependent Flows via each Flow's `previous()` method
3. Separate variable inputs (`variable`) from connection inputs (`output`)
4. Return required input variable list and final output list

**Parallel Execution Strategy:**

```python
# Execute Flows with no dependencies simultaneously
for flow_id in executable_flows:
    thread = util.os.Thread(target=runningThread, args=(flow_id,))
    thread.start()
```

- Each Flow runs in an independent Python thread
- Detect immediately executable Flows after dependency resolution
- Dynamic scheduling: Automatically detect next executable Flow upon completion

#### 2.5 Renderer

Renders workflow output in various formats.

**Supported Formats:**
- HTML
- Images (PIL, matplotlib)
- Plotly charts
- Tables
- JSON

### 3. Data Flow

```
User Input
    ↓
Load Workflow (.dwp file)
    ↓
Dependency Analysis (spec() method)
    ↓
Determine Execution Order (DAG)
    ↓
Execute Flows Sequential/Parallel
    ↓
Create FlowInstance
    ↓
Collect Input Data
    ↓
Execute Python Code
    ↓
Store Output Data
    ↓
Pass to Next Flow
    ↓
Return Final Result
```

### 3.1 DAG-based Dependency Analysis

DIZEST's core strength is Directed Acyclic Graph (DAG) based workflow analysis.

**DAG Structure:**

Workflows are modeled as directed acyclic graphs:
- **Node**: Each Flow
- **Edge**: Data connection between Flows (input → output)
- **Acyclic**: Detect and prevent circular dependencies

**Dependency Analysis Algorithm (workflow.spec):**

```python
def spec(self, target_flows=None):
    """
    Analyze all dependencies required to execute specific Flow
    
    Returns:
        requested_inputs: Dict[str, List] - Required external input variables
        outputs: Dict[str, List] - Final output list
    """
    requested_inputs = {}
    outputs = {}
    visited = set()
    
    def traverse(flow_id):
        if flow_id in visited:
            return
        visited.add(flow_id)
        
        flow = self.flow[flow_id]
        app = self.apps[flow.app_id]
        
        # Check all inputs
        for input_def in app.inputs:
            connections = flow.inputs.get(input_def['name'], {}).get('connections', [])
            
            if not connections:  # Variable input
                requested_inputs.setdefault(flow_id, []).append(input_def['name'])
            else:  # Connection input - recursive traversal
                for conn in connections:
                    traverse(conn['node'])
        
        # Register outputs
        for output_def in app.outputs:
            outputs.setdefault(flow_id, []).append(output_def['name'])
    
    # Backward trace from target Flow
    for flow_id in target_flows:
        traverse(flow_id)
    
    return requested_inputs, outputs
```

**Topological Sort:**

Execution order is determined through topological sorting:

```python
def topological_sort(flows, dependencies):
    """
    Topologically sort DAG to determine execution order
    
    Returns: List of execution groups (Flow groups that can run in parallel)
    """
    in_degree = {f: 0 for f in flows}
    
    # Calculate in-degree
    for flow in flows:
        for dep in dependencies[flow]:
            in_degree[flow] += 1
    
    execution_groups = []
    
    while flows:
        # Flows with in-degree 0 (can run in parallel)
        ready = [f for f in flows if in_degree[f] == 0]
        
        if not ready:
            raise CyclicDependencyError("Circular dependency detected")
        
        execution_groups.append(ready)
        
        # Remove executed Flows and update in-degree
        for flow in ready:
            flows.remove(flow)
            for dependent in get_dependents(flow):
                in_degree[dependent] -= 1
    
    return execution_groups
```

**Circular Dependency Detection:**

```python
def detect_cycle(flow_id, visited, rec_stack):
    """DFS-based cycle detection"""
    visited.add(flow_id)
    rec_stack.add(flow_id)
    
    for neighbor in get_dependencies(flow_id):
        if neighbor not in visited:
            if detect_cycle(neighbor, visited, rec_stack):
                return True
        elif neighbor in rec_stack:
            raise CyclicDependencyError(f"Circular dependency: {flow_id} → {neighbor}")
    
    rec_stack.remove(flow_id)
    return False
```

**Dependency Resolution Example:**

```
Input: target_flows = ['flow_e']

Workflow Graph:
  A → C → E (target)
  B → D → E

Analysis Result:
  requested_inputs = {
      'flow_a': ['param1'],
      'flow_b': ['param2']
  }
  outputs = {
      'flow_e': ['final_result']
  }
  execution_order = [
      [flow_a, flow_b],  # Group 1: Parallel execution
      [flow_c, flow_d],  # Group 2: Parallel execution
      [flow_e]           # Group 3: Sequential execution
  ]
```

### 4. Execution Model

DIZEST provides a multi-layered execution model to address various use cases.

#### 4.1 Synchronous Execution (run)

```python
# All Flows execute sequentially and wait until completion
result = workflow.run(inputs={'param1': 'value1'})
```

**Process:**
1. Collect and validate input variables
2. DAG analysis → Determine execution order
3. Execute each Flow in order
4. Block until all execution completes
5. Return final output

**Use Cases:** Script execution, batch jobs, simple API calls

#### 4.2 Asynchronous Execution (stream)

```python
# Real-time log streaming
# Delivers progress via Server-Sent Events (SSE)
```

**Process:**
1. Establish SSE connection
2. Start workflow execution
3. Send events to client immediately as they occur
4. Monitor progress in non-blocking manner

**Use Cases:** Web UI real-time updates, long-running task monitoring

#### 4.3 Parallel Execution Architecture

**Dependency Graph-based Parallelization:**

```
Flow A ─┐
        ├─> Flow D ─> Flow E
Flow B ─┘
        
Flow C ─────────────> Flow F
```

In this case, execution order:
1. **Parallel Group 1**: Flow A, B, C (concurrent execution)
2. **Parallel Group 2**: Flow D, F (concurrent after A, B complete)
3. **Parallel Group 3**: Flow E (after D completes)

**Parallel Execution Core Logic:**

```python
class Runnable:
    def resolve_execution_order(self, flows):
        """Determine execution order based on DAG"""
        pending = set(flows)
        completed = set()
        
        while pending:
            # Find Flows with all dependencies resolved
            ready = [f for f in pending 
                     if all(dep in completed for dep in f.dependencies())]
            
            if not ready:
                raise CyclicDependencyError("Circular dependency detected")
            
            # Parallel execution
            threads = []
            for flow in ready:
                t = Thread(target=self.execute_flow, args=(flow,))
                t.start()
                threads.append(t)
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Mark as completed
            completed.update(ready)
            pending -= set(ready)
```

**Multiprocess Isolation:**

Each Flow runs in an independent Python process to ensure stability and isolation:

```python
# Create and execute process
process = multiprocessing.Process(target=flow_executor, args=(flow_id, inputs))
process.start()
process.join(timeout=flow.timeout)
```

**Advantages:**
- No GIL (Global Interpreter Lock) constraints
- Memory isolation between Flows
- No impact on other Flows when crashed
- Parallel processing of CPU-intensive tasks

**Performance Optimization:**

- **Caching**: Reuse outputs from already-executed FlowInstances
- **Smart Scheduling**: Classify CPU/IO-bound tasks and assign optimal threads
- **Resource Pooling**: Reduce creation overhead by reusing process pools

### 5. Event System

DIZEST adopts a complete event-driven architecture to track all state changes in workflow execution in real-time.

**Event Types:**
- `workflow.status`: Overall workflow state change
- `flow.status`: Individual Flow state change (idle/pending/running/ready/error)
- `flow.index`: Flow execution order index
- `log.append`: Log addition (captures stdout/stderr)
- `log.clear`: Log deletion
- `result`: Flow execution result output

**Event Listener Registration:**
```python
workflow.on('log.append', callback_function)
workflow.on('flow.status', status_handler)
workflow.on('result', result_handler)
```

**Event Propagation Mechanism:**

```
Inside FlowInstance
      ↓
  Event Emitted
      ↓
Workflow.event() method
      ↓
Propagate to all registered listeners
      ↓
      ├─> Callback Function 1
      ├─> Callback Function 2
      └─> Callback Function N
```

**Event Payload Structure:**

```python
# flow.status event
{
    "flow_id": "my_app-1234567890",
    "status": "running",  # idle/pending/running/ready/error
    "timestamp": "2024-01-15T10:30:00"
}

# log.append event
{
    "flow_id": "my_app-1234567890",
    "message": "Processing complete",
    "level": "info"  # info/warning/error
}

# result event
{
    "flow_id": "my_app-1234567890",
    "output_name": "result",
    "value": { ... },
    "rendered": "<html>...</html>"  # Rendered output
}
```

**Server-Sent Events (SSE) Integration:**

Stream events in real-time at REST API `/dizest/api/stream/<workflow>` endpoint:

```python
# Flask response streaming
def event_stream():
    def send_event(event_name, data):
        yield f"data: {json.dumps({'event': event_name, 'data': data})}\n\n"
    
    workflow.on('log.append', lambda data: send_event('log', data))
    workflow.on('flow.status', lambda data: send_event('status', data))
    workflow.run()

return Response(event_stream(), mimetype='text/event-stream')
```

Receive in real-time at frontend with EventSource API:

```javascript
const eventSource = new EventSource('/dizest/api/stream/my_workflow');
eventSource.onmessage = (event) => {
    const {event: eventName, data} = JSON.parse(event.data);
    // Real-time UI update
};
```

### 6. Storage Structure

#### 6.1 Project Structure

```
<project_root>/
├── config.py           # Configuration file
├── password            # Encrypted password
├── project/            # Project source
│   └── main/
│       ├── bundle/     # Bundle resources
│       └── src/        # App source code
├── plugin/             # Plugins
└── public/             # Public directory
    └── app.py          # WSGI app
```

#### 6.2 Workflow File (.dwp)

Stored in JSON format and includes:
- All App definitions
- All Flow instances
- Connection information
- Metadata

### 7. Security Model

- Single mode by default: bcrypt-encrypted password
- ACL-based API access control
- Workflow execution isolation (process level)

### 8. Extensibility

#### 8.1 Plugin System

- Add plugins to `plugin/` directory
- Each plugin provides independent set of Apps

#### 8.2 Custom Renderer

- `Workflow.render` is extensible
- Support for custom output formats

#### 8.3 API Binding

- Flask-based REST API
- Can add custom endpoints
- WebSocket support (planned)

### 9. Performance Optimization

DIZEST ensures efficient execution of large-scale workflows through various optimization techniques.

#### 9.1 Caching Strategy

**FlowInstance Output Caching:**
- Return cached results on re-execution with same inputs
- Memory-based caching (valid during runtime)
- Cache key: `flow_id + input hash`

```python
class FlowInstance:
    def execute(self, inputs):
        cache_key = self._generate_cache_key(inputs)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._run_code(inputs)
        self.cache[cache_key] = result
        return result
```

#### 9.2 Parallel Processing Optimization

**Concurrent Execution of Independent Flows:**
- Automatically detect parallel executable groups through DAG analysis
- Utilize multi-core: Concurrent execution up to number of CPU cores
- Thread pool reuse: Minimize overhead

**Execution Order Optimization:**
```
Unoptimized:  A → B → C → D → E  (Sequential, 5 time units)

Optimized:    A ─┐
              B ─┴─> D ─> E      (Parallel, 3 time units)
              C ────────────┘
```

#### 9.3 Lazy Loading

- **App Code**: Load only at execution time
- **Large Data**: Read only in required Flows
- **Renderer**: Dynamically load based on output type

#### 9.4 Log Management

**Log Size Limit:**
```python
workflow.config.max_log_size = 10000  # Maximum 10,000 lines
```

- Automatically delete old logs
- Prevent memory overflow
- Maintain real-time streaming performance

#### 9.5 Memory Management

**FlowInstance Lifecycle:**
- Automatic cleanup after execution completes (GC)
- Large output data: Store on file system
- Prevent circular references: Use weakref

#### 9.6 Network Optimization

**API Response Optimization:**
- Result compression (gzip)
- Chunked streaming
- Remove unnecessary metadata

**Frontend Optimization:**
- Canvas rendering: Use Virtual DOM
- Flow results: Paging
- Large graphs: WebGL rendering

#### 9.7 Performance Benchmark

**Typical Workflow Performance:**
- 10 Flows (sequential): ~2 seconds
- 10 Flows (5 parallel): ~1 second
- 100 Flows (complex DAG): ~5-10 seconds

**Scalability:**
- Maximum tested: 1000 Flow workflow successfully executed
- Concurrent users: 100 (per server)
- Memory usage: ~10-50MB per Flow

### 10. Design Principles

1. **Modularity**: Design Apps as reusable independent units
2. **Declarative Configuration**: JSON-based declarative workflow definition
3. **Loose Coupling**: Communication only through output-input connections between Apps
4. **Event-driven**: Propagate state changes as events
5. **Extensibility**: Support for plugins and custom components

## Technology Stack

### Backend
- **Language**: Python 3.x
- **Web Framework**: Flask
- **Process Management**: multiprocessing
- **File Format**: JSON
- **Encryption**: bcrypt

### Frontend
- **Framework**: Angular
- **Workflow Editor**: Drawflow
- **Build Tool**: Webpack

### Infrastructure
- **Deployment**: WSGI (gunicorn, uWSGI)
- **Docker**: Official images provided
- **OS**: Linux, macOS, Windows

## Conclusion

DIZEST simplifies AI and data analysis tasks by combining visual workflow design, modular component reuse, and a powerful execution engine. Through its event-driven architecture and extensible plugin system, it can be applied to various use cases.
