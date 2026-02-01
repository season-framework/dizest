# DIZEST 예제 모음

다양한 활용 사례를 통해 DIZEST의 기능을 배워보세요.

## 목차

1. [기본 예제](#기본-예제)
2. [데이터 처리](#데이터-처리)
3. [머신러닝](#머신러닝)
4. [웹 크롤링](#웹-크롤링)
5. [시각화](#시각화)
6. [API 통합](#api-통합)
7. [파일 처리](#파일-처리)

---

## 기본 예제

### Hello World

**App 코드:**
```python
message = dizest.input("message", default="Hello, World!")
result = message.upper()
dizest.output("result", result)
print(result)
```

**입력:**
- `message` (text): 출력할 메시지

**출력:**
- `result`: 대문자로 변환된 메시지

---

### 간단한 계산기

**App 코드:**
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

## 데이터 처리

### CSV 파일 읽기 및 필터링

**App 1: CSV 로더**
```python
import pandas as pd

filepath = dizest.input("filepath", default="data.csv")
df = pd.read_csv(filepath)

dizest.output("data", df.to_dict('records'))
print(f"Loaded {len(df)} rows")
```

**App 2: 데이터 필터**
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

**App 3: 통계 계산**
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

### JSON 데이터 변환

**App 코드:**
```python
import json

input_json = dizest.input("json_string", default="{}")
data = json.loads(input_json)

# 데이터 변환
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

## 머신러닝

### 데이터 전처리

**App 코드:**
```python
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# 결측치 처리
df = df.fillna(df.mean())

# 수치형 컬럼만 선택
numeric_cols = df.select_dtypes(include=[np.number]).columns

# 정규화
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

dizest.output("preprocessed_data", df.to_dict('records'))
print(f"Preprocessed {len(df)} samples with {len(numeric_cols)} features")
```

---

### 선형 회귀 모델 학습

**App 코드:**
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

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 모델 학습
model = LinearRegression()
model.fit(X_train, y_train)

# 예측 및 평가
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# 모델 저장
fs = dizest.drive("models")
with open(fs.abspath("model.pkl"), "wb") as f:
    pickle.dump(model, f)

# 결과 출력
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

### 모델 예측

**App 코드:**
```python
import pandas as pd
import pickle

new_data = dizest.input("new_data", default=[])

# 모델 로드
fs = dizest.drive("models")
with open(fs.abspath("model.pkl"), "rb") as f:
    model = pickle.load(f)

# 예측
df = pd.DataFrame(new_data)
predictions = model.predict(df)

dizest.output("predictions", predictions.tolist())
print(f"Predicted {len(predictions)} samples")
```

---

## 웹 크롤링

### HTML 페이지 크롤링

**App 코드:**
```python
import requests
from bs4 import BeautifulSoup

url = dizest.input("url", default="https://example.com")

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 타이틀 추출
title = soup.find('title').text if soup.find('title') else ""

# 모든 링크 추출
links = [a.get('href') for a in soup.find_all('a', href=True)]

# 모든 이미지 추출
images = [img.get('src') for img in soup.find_all('img', src=True)]

result = {
    "title": title,
    "links": links[:10],  # 처음 10개만
    "images": images[:10]
}

dizest.output("scraped_data", result)
print(f"Scraped: {len(links)} links, {len(images)} images")
```

---

### API 데이터 수집

**App 코드:**
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

## 시각화

### Matplotlib 차트

**App 코드:**
```python
import matplotlib.pyplot as plt
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# 차트 생성
fig, ax = plt.subplots(figsize=(10, 6))
df.plot(kind='bar', ax=ax)
ax.set_title("Data Visualization")
ax.set_xlabel("Index")
ax.set_ylabel("Value")

# 결과 출력
dizest.result("chart", fig)
print("Chart created")
```

---

### Plotly 인터랙티브 차트

**App 코드:**
```python
import plotly.express as px
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# Plotly 차트
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

### 데이터 테이블

**App 코드:**
```python
import pandas as pd

data = dizest.input("data", default=[])
df = pd.DataFrame(data)

# 통계 요약
summary = df.describe()

dizest.result("data_table", df)
dizest.result("summary", summary)
print(f"Table with {len(df)} rows displayed")
```

---

## API 통합

### Slack 메시지 전송

**App 코드:**
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

### 이메일 전송

**App 코드:**
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

## 파일 처리

### 파일 읽기/쓰기

**App 코드:**
```python
import json

# 파일 읽기
fs = dizest.drive()
if fs.exists("input.json"):
    data = json.loads(fs.read("input.json"))
else:
    data = {"message": "default"}

# 데이터 처리
processed = {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}

# 파일 쓰기
fs.write("output.json", json.dumps(processed, indent=2))

dizest.output("processed_data", processed)
print("File processed and saved")
```

---

### 이미지 처리

**App 코드:**
```python
from PIL import Image
import io
import base64

# 이미지 로드
fs = dizest.drive()
img = Image.open(fs.abspath("input.jpg"))

# 리사이즈
width = dizest.input("width", default=800)
height = dizest.input("height", default=600)
resized = img.resize((width, height))

# 저장
resized.save(fs.abspath("output.jpg"))

# 결과 출력
dizest.result("resized_image", resized)
print(f"Image resized to {width}x{height}")
```

---

### 여러 파일 병합

**App 코드:**
```python
import pandas as pd

# 파일 목록
filenames = dizest.input("filenames", default="file1.csv,file2.csv").split(",")

fs = dizest.drive()
dfs = []

for filename in filenames:
    if fs.exists(filename.strip()):
        df = pd.read_csv(fs.abspath(filename.strip()))
        dfs.append(df)

# 병합
merged = pd.concat(dfs, ignore_index=True)

# 저장
merged.to_csv(fs.abspath("merged.csv"), index=False)

dizest.output("merged_data", merged.to_dict('records'))
print(f"Merged {len(dfs)} files into {len(merged)} rows")
```

---

## 고급 예제

### 병렬 처리 워크플로우

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

각 Process는 독립적으로 병렬 실행되고, Combine에서 결과를 합칩니다.

---

### 조건부 실행

**App 1: 조건 체크**
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

**App 2~4**: 각각 "high", "medium", "low" 경로에 대응하는 처리

Flow의 `active` 속성을 동적으로 조정하여 조건부 실행 가능

---

## 실행 방법

### 웹 UI에서

1. 예제 코드를 복사하여 새 App 생성
2. 필요한 입력 정의 추가
3. Flow 생성 및 연결
4. Run 버튼 클릭

### Python에서

```python
import dizest

workflow = dizest.Workflow("example.dwp")
workflow.run()
```

### REST API로

```bash
curl "http://localhost:4000/dizest/api/run/example.dwp?param=value"
```

---

## 더 많은 예제

GitHub 저장소에서 더 많은 예제를 확인하세요:
- [EXAMPLES.md](../../EXAMPLES.md)
- [USE_CASES.md](../../USE_CASES.md)

---

## 도움이 필요하신가요?

- [사용 가이드](usage-guide.md)
- [API 레퍼런스](api/README.md)
- [GitHub Issues](https://github.com/season-framework/dizest/issues)
