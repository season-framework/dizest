# DIZEST Examples Collection

Learn DIZEST features through various use cases.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Data Processing](#data-processing)
3. [Machine Learning](#machine-learning)
4. [Web Scraping](#web-scraping)
5. [Visualization](#visualization)
6. [API Integration](#api-integration)
7. [File Processing](#file-processing)

---

## Basic Examples

### Hello World

**App Code:**
```python
message = dizest.input("message", default="Hello, World!")
result = message.upper()
dizest.output("result", result)
print(result)
```

**Input:**
- `message` (text): Message to output

**Output:**
- `result`: Message converted to uppercase

---

### Simple Calculator

**App Code:**
```python
a = dizest.input("a", default=0)
b = dizest.input("b", default=0)
operation = dizest.input("operation", default="+")

if operation == "+":
    result = a + b
elif operation == "-":
    result = a - b
elif operation == "*":
    result = a * b
elif operation == "/":
    result = a / b if b != 0 else "Division by zero"
else:
    result = "Unknown operation"

dizest.output("result", result)
print(f"{a} {operation} {b} = {result}")
```

---

## Data Processing

### CSV File Reading and Filtering

**App 1: CSV Loader**
```python
import pandas as pd

filepath = dizest.input("filepath", default="data.csv")
df = pd.read_csv(filepath)

dizest.output("data", df.to_dict('records'))
print(f"Loaded {len(df)} rows")
```

**App 2: Data Filter**
```python
import pandas as pd

data = dizest.input("data", default=[])
column = dizest.input("column", default="age")
min_value = dizest.input("min_value", default=0)

df = pd.DataFrame(data)
filtered = df[df[column] >= min_value]

dizest.output("filtered_data", filtered.to_dict('records'))
print(f"Filtered to {len(filtered)} rows")
```

**App 3: Statistics Calculation**
```python
import pandas as pd

data = dizest.input("filtered_data", default=[])
df = pd.DataFrame(data)

stats = {
    "count": len(df),
    "mean": df.select_dtypes(include='number').mean().to_dict(),
    "median": df.select_dtypes(include='number').median().to_dict(),
    "std": df.select_dtypes(include='number').std().to_dict()
}

dizest.output("statistics", stats)
dizest.result("stats", stats)
```

---

### JSON Data Transformation

**App Code:**
```python
import json

input_json = dizest.input("json_string", default="{}")
data = json.loads(input_json)

# Data transformation
transformed = {}
for key, value in data.items():
    if isinstance(value, str):
        transformed[key] = value.upper()
    elif isinstance(value, (int, float)):
        transformed[key] = value * 2
    else:
        transformed[key] = value

dizest.output("transformed_data", transformed)
print(f"Transformed {len(transformed)} fields")
```

---

## Machine Learning

### Data Preprocessing

**App Code:**
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# Handle missing values
df = df.fillna(df.mean())

# Select only numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns

# Normalization
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

dizest.output("preprocessed_data", df.to_dict('records'))
print(f"Preprocessed {len(df)} samples with {len(numeric_cols)} features")
```

---

### Linear Regression Model Training

**App Code:**
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pickle

data = dizest.input("preprocessed_data", default=[])
target_col = dizest.input("target_column", default="target")

df = pd.DataFrame(data)
X = df.drop(columns=[target_col])
y = df[target_col]

# Data split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model training
model = LinearRegression()
model.fit(X_train, y_train)

# Prediction and evaluation
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Save model
fs = dizest.drive("models")
with open(fs.abspath("model.pkl"), "wb") as f:
    pickle.dump(model, f)

# Output results
results = {
    "mse": float(mse),
    "r2": float(r2),
    "train_samples": len(X_train),
    "test_samples": len(X_test)
}

dizest.output("model_metrics", results)
dizest.result("metrics", results)
print(f"Model trained: MSE={mse:.4f}, R²={r2:.4f}")
```

---

### Model Prediction

**App Code:**
```python
import pandas as pd
import pickle

new_data = dizest.input("new_data", default=[])

# Load model
fs = dizest.drive("models")
with open(fs.abspath("model.pkl"), "rb") as f:
    model = pickle.load(f)

# Prediction
df = pd.DataFrame(new_data)
predictions = model.predict(df)

dizest.output("predictions", predictions.tolist())
print(f"Predicted {len(predictions)} samples")
```

---

## Web Scraping

### HTML Page Scraping

**App Code:**
```python
import requests
from bs4 import BeautifulSoup

url = dizest.input("url", default="https://example.com")

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract title
title = soup.find('title').text if soup.find('title') else ""

# Extract all links
links = [a.get('href') for a in soup.find_all('a', href=True)]

# Extract all images
images = [img.get('src') for img in soup.find_all('img', src=True)]

result = {
    "title": title,
    "links": links[:10],  # First 10 only
    "images": images[:10]
}

dizest.output("scraped_data", result)
print(f"Scraped: {len(links)} links, {len(images)} images")
```

---

### API Data Collection

**App Code:**
```python
import requests

api_url = dizest.input("api_url", default="https://api.example.com/data")
api_key = dizest.input("api_key", default="")

headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

response = requests.get(api_url, headers=headers)
data = response.json()

dizest.output("api_data", data)
print(f"Fetched data from API: {response.status_code}")
```

---

## Visualization

### Matplotlib Charts

**App Code:**
```python
import matplotlib.pyplot as plt
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# Create chart
fig, ax = plt.subplots(figsize=(10, 6))
df.plot(kind='bar', ax=ax)
ax.set_title("Data Visualization")
ax.set_xlabel("Index")
ax.set_ylabel("Value")

# Output results
dizest.result("chart", fig)
print("Chart created")
```

---

### Plotly Interactive Charts

**App Code:**
```python
import plotly.express as px
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# Plotly chart
fig = px.scatter(
    df,
    x=df.columns[0],
    y=df.columns[1],
    title="Interactive Scatter Plot",
    hover_data=df.columns
)

dizest.result("interactive_chart", fig)
print("Interactive chart created")
```

---

### Data Table

**App Code:**
```python
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# Statistical summary
summary = df.describe()

dizest.result("data_table", df)
dizest.result("summary", summary)
print(f"Table with {len(df)} rows displayed")
```

---

## API Integration

### Slack Message Sending

**App Code:**
```python
import requests

webhook_url = dizest.input("slack_webhook", default="")
message = dizest.input("message", default="Hello from DIZEST!")
channel = dizest.input("channel", default="#general")

payload = {
    "channel": channel,
    "text": message
}

response = requests.post(webhook_url, json=payload)

dizest.output("status", response.status_code)
print(f"Message sent to Slack: {response.status_code}")
```

---

### Email Sending

**App Code:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = dizest.input("smtp_server", default="smtp.gmail.com")
smtp_port = dizest.input("smtp_port", default=587)
sender = dizest.input("sender_email", default="")
password = dizest.input("password", default="")
recipient = dizest.input("recipient", default="")
subject = dizest.input("subject", default="DIZEST Notification")
body = dizest.input("body", default="")

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
    
    dizest.output("status", "success")
    print("Email sent successfully")
except Exception as e:
    dizest.output("status", "failed")
    print(f"Failed to send email: {str(e)}")
```

---

## File Processing

### File Reading/Writing

**App Code:**
```python
import json

# Read file
fs = dizest.drive()
if fs.exists("input.json"):
    data = json.loads(fs.read("input.json"))
else:
    data = {"message": "default"}

# Process data
processed = {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}

# Write file
fs.write("output.json", json.dumps(processed, indent=2))

dizest.output("processed_data", processed)
print("File processed and saved")
```

---

### Image Processing

**App Code:**
```python
from PIL import Image
import io
import base64

# Load image
fs = dizest.drive()
img = Image.open(fs.abspath("input.jpg"))

# Resize
width = dizest.input("width", default=800)
height = dizest.input("height", default=600)
resized = img.resize((width, height))

# Save
resized.save(fs.abspath("output.jpg"))

# Output results
dizest.result("resized_image", resized)
print(f"Image resized to {width}x{height}")
```

---

### Multiple File Merging

**App Code:**
```python
import pandas as pd

# File list
filenames = dizest.input("filenames", default="file1.csv,file2.csv").split(",")

fs = dizest.drive()
dfs = []

for filename in filenames:
    if fs.exists(filename.strip()):
        df = pd.read_csv(fs.abspath(filename.strip()))
        dfs.append(df)

# Merge
merged = pd.concat(dfs, ignore_index=True)

# Save
merged.to_csv(fs.abspath("merged.csv"), index=False)

dizest.output("merged_data", merged.to_dict('records'))
print(f"Merged {len(dfs)} files into {len(merged)} rows")
```

---

## Advanced Examples

### Parallel Processing Workflow

```
                    ┌─────────────┐
                    │ Data Loader │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
        │ Process A │ │Process B│ │Process C │
        └─────┬─────┘ └───┬────┘ └────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │   Combine   │
                    └─────────────┘
```

Each Process runs independently in parallel, and the Combine aggregates the results.

---

### Conditional Execution

**App 1: Condition Check**
```python
value = dizest.input("value", default=0)

if value > 10:
    dizest.output("path", "high")
elif value > 5:
    dizest.output("path", "medium")
else:
    dizest.output("path", "low")

print(f"Value {value} -> Path: {dizest.output('path')}")
```

**App 2~4**: Processing corresponding to "high", "medium", and "low" paths respectively

Conditional execution is possible by dynamically adjusting the `active` attribute of the Flow

---

## How to Run

### In Web UI

1. Copy example code and create a new App
2. Add required input definitions
3. Create Flow and connections
4. Click Run button

### From Python

```python
import dizest

workflow = dizest.Workflow("example.dwp")
workflow.run()
```

### Via REST API

```bash
curl "http://localhost:4000/dizest/api/run/example.dwp?param=value"
```

---

## More Examples

Check out more examples in the GitHub repository:
- [EXAMPLES.md](../../EXAMPLES.md)
- [USE_CASES.md](../../USE_CASES.md)

---

## Need Help?

- [Usage Guide](usage-guide.md)
- [API Reference](api/README.md)
- [GitHub Issues](https://github.com/season-framework/dizest/issues)
