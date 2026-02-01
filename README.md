<div align="center">
  <h1>DIZEST</h1>
  <p><strong>A Low-Code Platform for Workflow-Driven AI and Data Analysis</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
  [![PyPI version](https://badge.fury.io/py/dizest.svg)](https://badge.fury.io/py/dizest)
  
  <p>
    <a href="#key-features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#documentation">Documentation</a> •
    <a href="#examples">Examples</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
</div>

---

## 📖 Overview

DIZEST provides a visual, web-based environment for building and executing AI and data analysis workflows. With its intuitive drag-and-drop interface and modular architecture, you can rapidly develop complex data pipelines without extensive coding.

![DIZEST Main Interface](./screenshots/DIZEST_main.gif)

> 💡 **The modular structure** allows you to connect reusable components through inputs and outputs, making workflow development efficient and maintainable.

## ✨ Key Features

### Core Capabilities

- 🎨 **Visual Workflow Editor** - Intuitive drag-and-drop interface powered by Drawflow for building complex workflows
- 🧩 **Component-Based Architecture** - Modular App system with reusable components (create once, use everywhere)
- 🔀 **DAG-Based Execution Engine** - Directed Acyclic Graph resolver for automatic dependency analysis and parallel execution
- ⚡ **Intelligent Parallelization** - Automatic detection and concurrent execution of independent workflow branches
- 📡 **Event-Driven System** - Real-time event propagation for workflow status, logs, and results

### Execution & Integration

- 🐍 **Python-Native** - Full Python ecosystem support with dynamic code execution and sys.path integration
- 🌐 **Dual API Modes** - REST API (synchronous) and Server-Sent Events (streaming) for real-time execution
- 🔄 **Multi-Process Architecture** - Isolated process execution for workflow safety and resource management
- 📊 **Advanced Rendering** - Multi-format output support (HTML, Plotly, Matplotlib, Pandas, PIL, JSON)

### Developer Experience

- 🔌 **Plugin Architecture** - Extensible spawner system and custom renderer support
- 🚀 **Production-Ready** - Docker, systemd service integration, and daemon mode
- 🎯 **Type-Aware Inputs** - Variable type checking and automatic conversion (text, number, checkbox)
- 🔐 **Security Built-in** - Bearer token authentication, ACL system, and bcrypt password encryption

## 🚀 Quick Start

### Installation

```bash
pip install dizest
```

### Create Your First Project

```bash
# Create a new project
dizest install myproject

# Navigate to project directory
cd myproject

# Start the server
dizest run --port 4000 --host 0.0.0.0
```

Open your browser and navigate to `http://localhost:4000`

### Your First Workflow

1. Click **New Workflow** in the web UI
2. Create a new App with this Python code:
   ```python
   # Get input
   message = wiz.input("message", default="Hello, DIZEST!")
   
   # Process
   result = message.upper()
   
   # Output
   wiz.output("result", result)
   print(f"Processed: {result}")
   ```
3. Drag the App onto the canvas to create a Flow
4. Click **Run** to execute

## 📚 Documentation

### Core Documentation

- **[English Documentation](./docs/en/README.md)** - Complete Guide
  - [Architecture](./docs/en/architecture.md)
  - [Usage Guide](./docs/en/usage-guide.md)
  - [API Reference](./docs/en/api/README.md)
  - [DWP Specification](./docs/en/dwp-specification.md)

- **[Korean Documentation](./docs/kr/README.md)** - 한국어 문서 (완전한 가이드)
  - [아키텍처](./docs/kr/architecture.md)
  - [사용 가이드](./docs/kr/usage-guide.md)
  - [API 레퍼런스](./docs/kr/api/README.md)
  - [DWP 파일 규격](./docs/kr/dwp-specification.md)

### Additional Resources

- **[Examples](./EXAMPLES.md)** - Practical workflow examples
- **[Use Cases](./USE_CASES.md)** - Real-world applications
- **[Release Notes](./RELEASES.md)** - Version history and changelog 

## 💻 Usage

### Run the Server

**Foreground mode:**
```bash
cd myproject
dizest run --port 4000 --host 0.0.0.0
```

**Daemon mode:**
```bash
dizest server start  # Start daemon
dizest server stop   # Stop daemon
dizest server restart # Restart daemon
```

### Execute Workflows via API

**Direct execution:**
```bash
curl "http://127.0.0.1:4000/dizest/api/run/myworkflow.dwp?message=Hello"
```

**Streaming execution (real-time logs):**
```bash
curl "http://127.0.0.1:4000/dizest/api/stream/myworkflow.dwp?param=value"
```

### Python Integration

```python
import dizest

# Load workflow
workflow = dizest.Workflow("myworkflow.dwp")

# Add event listener
workflow.on('log.append', lambda f, e, log: print(log))

# Execute
workflow.run()

# Get results
requested, outputs = workflow.spec()
for flow_id in outputs:
    flow = workflow.flow(flow_id)
    instance = workflow.run.instance(flow)
    print(instance.output_data)
```

### Upgrade

```bash
pip install dizest --upgrade
cd myproject
dizest upgrade
```

## 🛠️ CLI Reference

### Project Management

| Command | Description |
|---------|-------------|
| `dizest install <PROJECT_NAME>` | Create a new DIZEST project |
| `dizest upgrade` | Upgrade project to latest version |
| `dizest password <PASSWORD>` | Change root password (single mode) |

**Options:**
- `--password`: Set custom password (default: auto-generated)

**Example:**
```bash
dizest install myapp --password mysecret
cd myapp
dizest upgrade
```

### Server Management

| Command | Description |
|---------|-------------|
| `dizest run` | Run server in foreground |
| `dizest server start` | Start server as daemon |
| `dizest server stop` | Stop daemon server |
| `dizest server restart` | Restart daemon server |

**Options:**
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 3000)
- `--log`: Log file path

**Example:**
```bash
dizest run --port=4000 --host=0.0.0.0
dizest server start --log=dizest.log
```

### Service Management (systemd)

| Command | Description |
|---------|-------------|
| `dizest service install <NAME>` | Register systemd service |
| `dizest service uninstall <NAME>` | Remove systemd service |
| `dizest service start <NAME>` | Start service |
| `dizest service stop <NAME>` | Stop service |
| `dizest service restart <NAME>` | Restart service |
| `dizest service status <NAME>` | Check service status |
| `dizest service list` | List all services |

**Example:**
```bash
sudo dizest service install myapp
sudo dizest service start myapp
sudo dizest service status myapp
```

## 🎯 Examples

### 1. LLM-Powered Chatbot with RAG

Build enterprise chatbots with retrieval-augmented generation:

```
[Document Loader] → [Text Splitter] → [Embedding] → [Vector Store]
                                                            ↓
[User Query] → [Similarity Search] → [LLM (GPT/Claude)] → [Response]
```

**Use Cases:**
- Customer support with company knowledge base
- Internal documentation Q&A system
- Domain-specific conversational AI

**Technologies:** LangChain, OpenAI/Anthropic API, ChromaDB/Pinecone

### 2. Object Detection Pipeline

Deep learning-based visual inspection system:

```
[Image Input] → [Preprocessing] → [YOLO/RCNN Detection] → [Post-processing] → [Alert/Report]
```

**Use Cases:**
- Manufacturing defect detection
- Agricultural crop monitoring
- Quality control automation
- Safety compliance verification

**Technologies:** PyTorch, TensorFlow, OpenCV, YOLOv8

### 3. Time-Series Prediction

LSTM-based sensor data forecasting:

```
[IoT Sensors] → [Data Cleaning] → [Feature Engineering] → [LSTM Model] → [Prediction] → [Alert System]
```

**Use Cases:**
- Ship structural damage prediction
- Predictive maintenance
- Environmental monitoring
- Energy consumption forecasting

**Technologies:** TensorFlow, Keras, Pandas, NumPy

### 4. Multi-Modal Analysis

Combine vision and language models:

```
[Image Input] → [Image-to-3D] → [Feature Extraction]
                                        ↓
[Text Description] → [Embedding] → [Similarity Matching] → [Classification]
```

**Use Cases:**
- Cultural heritage artifact classification
- Product catalog matching
- Medical image analysis with clinical notes

**Technologies:** CLIP, Stable Diffusion, NeRF, Vision Transformers

### 5. Data Processing Pipeline

Traditional data science workflow:

```
[Load CSV] → [Filter Data] → [Transform] → [Analyze] → [Visualize (Plotly/Matplotlib)]
```

**Use Cases:**
- Business intelligence dashboards
- Scientific data analysis
- Report automation

For detailed examples, see [EXAMPLES.md](./EXAMPLES.md) and [USE_CASES.md](./USE_CASES.md)

## 🐳 Docker Deployment

```dockerfile
FROM python:3.9

WORKDIR /app

# Install DIZEST
RUN pip install dizest

# Create project
RUN dizest install myproject

WORKDIR /app/myproject

EXPOSE 4000

CMD ["dizest", "run", "--port", "4000", "--host", "0.0.0.0"]
```

**Run:**
```bash
docker build -t dizest-app .
docker run -p 4000:4000 dizest-app
```

## 🏗️ Architecture

DIZEST implements a layered, event-driven architecture with DAG-based workflow execution:

```
┌─────────────────────────────────────────────────────────┐
│                 Presentation Layer                       │
│  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │   Web UI         │  │   CLI Interface             │ │
│  │  (Angular 18+)   │  │  - Project Management       │ │
│  │  - Drawflow      │  │  - Server Control           │ │
│  │  - Visual Editor │  │  - Service Management       │ │
│  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                     │
│  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │  REST Endpoints  │  │  SSE Streaming              │ │
│  │  /api/run        │  │  /api/stream                │ │
│  │  /api/status     │  │  - Real-time logs           │ │
│  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Workflow Engine (Core)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Workflow Manager                                 │  │
│  │  - Package loader (.dwp JSON parser)             │  │
│  │  - App & Flow registry                           │  │
│  │  - Event dispatcher (workflow.on)                │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DAG Resolver (workflow.spec)                     │  │
│  │  - Dependency analysis                            │  │
│  │  - Input/Output mapping                          │  │
│  │  - Execution order determination                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Runnable Engine                                  │  │
│  │  - Multi-process orchestration                   │  │
│  │  - FlowInstance lifecycle management             │  │
│  │  - Status tracking (idle/pending/running/ready)  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Renderer                                         │  │
│  │  - HTML, Plotly, Matplotlib, Pandas, PIL, JSON   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Component Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │   App    │  │   Flow   │  │   FlowInstance     │    │
│  │  (Spec)  │  │(Instance)│  │  (Runtime State)   │    │
│  │          │  │          │  │  - input/output    │    │
│  │ - code   │  │ - app_id │  │  - status/logs     │    │
│  │ - inputs │  │ - active │  │  - process handle  │    │
│  │ - outputs│  │ - data   │  │  - event emission  │    │
│  └──────────┘  └──────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Storage & External Systems                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ .dwp Files   │  │ Drive System │  │ Spawners     │  │
│  │ (JSON)       │  │ (File I/O)   │  │ (Extensible) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Execution Flow

1. **Workflow Loading**: Parse `.dwp` file → Create App/Flow objects
2. **Dependency Analysis**: Build DAG → Identify required inputs & final outputs
3. **Execution Planning**: Determine parallel execution groups
4. **Process Spawning**: Create isolated FlowInstance per active Flow
5. **Event Propagation**: Real-time status/log emission to listeners
6. **Result Collection**: Aggregate outputs → Render via multi-format renderer

For detailed architecture documentation, see [architecture.md](./docs/en/architecture.md)

## 📚 Research & Publications

DIZEST has been featured in academic research and industry applications:

### International Publications

**Journal Articles:**
- "DIZEST: A Low-Code AI Workflow Execution Platform" - *SoftwareX*, Elsevier (2026)
  - [DOI: 10.1016/j.softx.2026.102519](https://www.sciencedirect.com/science/article/pii/S2352711026000130)
  - Core architecture and design principles of DIZEST platform

**Conference Proceedings:**
- IEEE International Conference (2024):
  - [Korean Speech Recognition via Retrieval-Augmented Generation-Based Intent-Aware Keyword Correction](https://ieeexplore.ieee.org/document/11262073)
  - [Automated Viability Classification of Human Lymphocytes via Machine Learning-Assisted Digital In-Line Holography](https://ieeexplore.ieee.org/document/11262080)  
  - [A Low-Code Methodology for Developing AI Kiosks: A Case Study with the DIZEST Platform](https://ieeexplore.ieee.org/document/11262171)

- Korea Information Technology Society Conference:
  - [Low-Code Based LLM Optimization Methods for Industrial Applications](https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE12024839) (2024)
    - Application of DIZEST with LangChain and RAG for industrial LLM deployment
  
  - [A Case Study of Deep Learning-Based Low-Code Models for Object Detection](https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE11651888) (2023)
    - Object detection pipeline using DIZEST for agricultural applications
  
  - [Study on Low-Code-Based Chatbot Service Development Using LangChain and RAG](https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE11825396) (2024)
    - Building conversational AI services with DIZEST low-code framework
  
  - [Low-Code AI Simulator for Temperature and Humidity-Based Damage Prediction](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12545260) (2025)
    - Ship damage prediction using 3D reconstruction and LSTM
  
  - [A Query Adjustment Framework for Roof Tile Classification and Retrieval](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12545281) (2025)
    - Multi-modal RAG system for archaeological artifact analysis

### Industrial Applications

**AI & Machine Learning:**
- Large Language Model (LLM) optimization and deployment
- Deep learning model training and inference pipelines  
- Object detection systems for manufacturing quality control
- Multi-modal RAG systems for cultural heritage analysis

**Data Science:**
- Time-series prediction for IoT sensor data
- Image-to-3D reconstruction pipelines
- Ship damage prediction using LSTM and environmental data
- Predictive maintenance for industrial equipment

**Enterprise Solutions:**
- Chatbot services with Retrieval-Augmented Generation (RAG)
- Custom AI workflow automation for domain experts
- Low-code AI platforms enabling non-technical users
- Industrial process optimization and monitoring

### Research Domains

- **Computer Vision**: Object detection, image classification, 3D reconstruction
- **Natural Language Processing**: LLM integration, RAG systems, chatbots
- **Time-Series Analysis**: Predictive maintenance, sensor data analytics
- **Cultural Heritage**: Digital archiving, pattern recognition in artifacts
- **Industrial AI**: Manufacturing automation, quality inspection
- **Maritime Engineering**: Ship damage prediction, structural analysis

> 📖 For research collaboration or citing DIZEST in academic work, please contact: research@season.co.kr

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/season-framework/dizest.git
cd dizest

# Install in development mode
pip install -e .

# Run tests
python -m pytest
```

## 📋 Requirements

- **Python**: 3.7 or higher
- **OS**: Linux, macOS, Windows
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Memory**: Minimum 2GB RAM recommended
- **Disk**: ~100MB per project

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/season-framework/dizest/issues)
- **Documentation**: [Complete guides](./docs/en/README.md)
- **Email**: proin@season.co.kr

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2021-2026 SEASON CO. LTD.

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

## 🌟 Star History

If you find DIZEST useful, please consider giving it a star! ⭐

## 👥 Authors

- **SEASON CO. LTD.** - [Website](https://season.co.kr)

## 🙏 Acknowledgments

### Funding Support

This work was supported in part by the Technology Innovation Program for SMEs (TIPA) grant funded by the Korea government (MSS), in part by the AKF of the Department of Foreign Affairs and Trade, and in part by the MSIT (Ministry of Science, ICT), Korea, under the National Program for Excellence in SW, supervised by the IITP (Institute of Information & communications Technology Planing & Evaluation) in 2025 (2023-0-00065).

**Detailed Grant Information:**

- **Technology Innovation Program for SMEs (TIPA)** - Korea government (MSS)
  - Project No. **RS-2023-00256711**: "Cloud-based intelligence dashboard solution and widget open market service"
    - Program: Technology Development for Startup and Growth (Stepping Stone)
    - Period: May 2023 - April 2024
  
  - Project No. **RS-2024-00441746**: "Customized business automation solution using workflow-based Langchain technology"
    - Program: Technology Development for Startup and Growth (TIPS)
    - Period: July 2024 - June 2026

- **Institute of Information & communications Technology Planning & Evaluation (IITP)** - Korea government (MSIT)
  - Project No. **2023-0-00065**: "National Program for Excellence in SW"
    

- **Australia-Korea Foundation (AKF)** - Department of Foreign Affairs and Trade
  - Supporting international collaboration and technology exchange

### Technology Stack

- Built with [Flask](https://flask.palletsprojects.com/) and [Angular](https://angular.io/)
- Workflow visualization powered by [Drawflow](https://github.com/jerosoler/Drawflow)
- Thanks to all [contributors](https://github.com/season-framework/dizest/graphs/contributors)

---

<div align="center">
  <p>Made with ❤️ by <a href="https://season.co.kr">SEASON CO. LTD.</a></p>
  <p>
    <a href="https://github.com/season-framework/dizest">GitHub</a> •
    <a href="./docs/en/README.md">Documentation</a> •
    <a href="./RELEASES.md">Releases</a>
  </p>
</div>