# DIZEST English Documentation

![DIZEST Logo](../../screenshots/DIZEST_main.gif)

Welcome to DIZEST (Data Intelligence Workflow Execution System & Tools).

## Introduction

DIZEST is a web-based low-code workflow platform that enables visual composition and execution of artificial intelligence and data analysis tasks.

### Key Features

- 🎨 **Visual Workflow Editor**: Intuitive drag-and-drop UI
- 🔄 **Reusable Components**: Create Apps once, use everywhere
- ⚡ **Parallel Execution**: Automatic parallel processing of independent tasks
- 🐍 **Python-Based**: Write logic in familiar Python
- 🌐 **REST API Support**: Instantly deploy workflows as web APIs
- 📊 **Rich Visualizations**: Support for Matplotlib, Plotly, Pandas, and more
- 🔌 **Extensible**: Expand functionality through plugin system

## Quick Start

### Installation

```bash
pip install dizest
dizest install myproject
cd myproject
dizest run --port 4000
```

Open your browser and navigate to `http://localhost:4000`

### Create Your First Workflow

1. Click the **New Workflow** button
2. Select the **Apps** tab in the left sidebar
3. Create a new App with the **+ button**
4. Write Python code:
   ```python
   message = dizest.input("message", default="Hello")
   result = message.upper()
   dizest.output("result", result)
   print(f"Processed: {result}")
   ```
5. Drag the App to the canvas to create a Flow
6. Click the **Run** button to execute

## Documentation Structure

### 📘 Core Guides

- [Architecture](architecture.md) - Overall structure and design principles of DIZEST
- [Usage Guide](usage-guide.md) - From installation to advanced usage
- [DWP File Specification](dwp-specification.md) - Workflow file format

### 📗 API Reference

- [Workflow Class](api/workflow.md) - Workflow management and execution
- [Flow, App, FlowInstance Classes](api/flow-app-instance.md) - Workflow components
- [Serve Class](api/serve.md) - Web server and REST API
- [CLI Commands](api/cli.md) - Command-line interface

### 📙 Examples and Applications

- [Examples](examples.md) - Various use cases
- [Use Cases](../../USE_CASES.md) - Real project applications

## Core Concepts

### App (Application)

A reusable functional unit that can include Python code, HTML, JavaScript, and CSS.

```python
# App code example
data = dizest.input("data", default=[])
processed = [x * 2 for x in data]
dizest.output("result", processed)
```

### Flow

An instance of an App, represented as a node on the canvas. Workflows are composed by connecting multiple Flows.

### Workflow

A complete task flow composed of multiple Apps and Flows. Saved as a `.dwp` file.

## Usage Examples

### Execute in Python Script

```python
import dizest

# Load workflow
workflow = dizest.Workflow("myworkflow.dwp")

# Event listener
workflow.on('log.append', lambda f, e, log: print(log))

# Execute
workflow.run()
```

### Execute via REST API

```bash
curl "http://localhost:4000/dizest/api/run/myworkflow.dwp?param1=value1"
```

### Custom Server

```python
from dizest import Serve

serve = Serve(host='0.0.0.0', port=8000)

@serve.app.route('/custom')
def custom():
    return {'status': 'ok'}

serve.run()
```

## Real-World Use Cases

### Data Analysis Pipeline

```
[Load Data] → [Preprocessing] → [Analysis] → [Visualization] → [Generate Report]
```

### Machine Learning Workflow

```
[Data Collection] → [Feature Engineering] → [Model Training] → [Evaluation] → [Deployment]
```

### Web Scraping and Processing

```
[Scraping] → [Parsing] → [Cleaning] → [Storage] → [Notification]
```

## System Requirements

- **Python**: 3.7 or higher
- **OS**: Linux, macOS, Windows
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Memory**: Minimum 2GB RAM recommended
- **Disk**: Approximately 100MB per project

## Installation Options

### Basic Installation via pip

```bash
pip install dizest
```

### Install Development Version

```bash
pip install git+https://github.com/season-framework/dizest.git
```

### Using Docker

```bash
docker pull seasonframework/dizest
docker run -p 4000:4000 seasonframework/dizest
```

## Community and Support

- **GitHub**: [https://github.com/season-framework/dizest](https://github.com/season-framework/dizest)
- **Issue Tracker**: [GitHub Issues](https://github.com/season-framework/dizest/issues)
- **Email**: proin@season.co.kr
- **License**: MIT License

## Contributing

DIZEST is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Version History

- **v2.4**: Latest stable version
- **v2.3**: Performance improvements and bug fixes
- **v2.2**: New renderers added
- **v2.1**: API improvements
- **v2.0**: Major architecture update

For detailed changes, see [RELEASES.md](../../RELEASES.md).

## FAQ

### Q: What's the difference between DIZEST and Apache Airflow?

A: DIZEST is a low-code platform focused on visual workflow editing and immediate execution. While Airflow excels at scheduling and monitoring, DIZEST is better suited for rapid prototyping and interactive execution.

### Q: Can I use it in commercial projects?

A: Yes, you can freely use it in commercial projects under the MIT License.

### Q: Can it handle large-scale data processing?

A: Since DIZEST is Python-based, you can process large-scale data using libraries like Pandas, Dask, and PySpark.

### Q: Is cloud deployment possible?

A: Yes, you can deploy to any cloud platform (AWS, GCP, Azure, etc.) using Docker.

## License

```
MIT License

Copyright (c) 2021 SEASON CO. LTD.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Build workflows easier and faster with DIZEST!** 🚀
