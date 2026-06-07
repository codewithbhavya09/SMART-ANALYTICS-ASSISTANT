# SMART-ANALYTICS-ASSISTANT
# 📊 Smart Analytics Assistant

> **Instant automated CSV analysis, dynamic visualizations, and AI-like insights — all in a single Streamlit app.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-3F4F75?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

### 📁 Data Loading
- Upload any **CSV file** (up to 200 MB)
- Automatic **encoding detection** (UTF-8 / Latin-1 fallback)
- Smart **column type inference** (numeric, categorical, datetime, boolean)

### 🔍 Automated Analysis
| Feature | Description |
|---|---|
| **Dataset Preview** | Scrollable preview with configurable row count |
| **Data Types** | Inferred type, pandas dtype, unique values, sample |
| **Missing Values** | Per-column missing count, percentage, and completeness |
| **Duplicates** | Total duplicate rows with optional display |
| **Statistical Summary** | Mean, median, mode, std, variance, skewness, kurtosis, IQR, percentiles |
| **Correlation Analysis** | Pearson correlation heatmap for all numeric columns |

### 📈 Dynamic Visualizations
| Chart | Details |
|---|---|
| **Histogram** | Configurable bins + marginal box plot |
| **Box Plot** | Optional grouping by categorical column, notched style |
| **Scatter Plot** | OLS trendline, optional color encoding |
| **Correlation Heatmap** | Full matrix with annotated r-values |
| **Pie / Donut Chart** | Top-N categories with "Other" grouping |
| **Line Chart** | Multi-series, index or column X-axis |

> 💡 The app automatically **recommends charts** based on your dataset's column types.

### 🧠 AI-Like Insights
Automatically generated insights covering:
- Dataset shape & memory footprint
- Highest / lowest values per column (with row index)
- Strong correlations (|r| ≥ 0.7) flagged with direction
- Missing data patterns
- IQR-based outlier warnings
- Distribution skewness flags
- High-cardinality categorical columns
- Constant / zero-variance columns

### ⬇️ Exports
- **Cleaned CSV** — deduped, all-null rows removed, strings stripped
- **Summary Report (.txt)** — full plain-text analysis report

---

## 🗂️ Project Structure

```
smart-analytics-assistant/
├── app.py                        # Main Streamlit entry point
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .streamlit/
│   └── config.toml               # Streamlit theme & server config
└── modules/
    ├── __init__.py
    ├── ui_components.py          # CSS, header, sidebar
    ├── data_loader.py            # CSV loading & column type detection
    ├── data_analysis.py          # Stats, missing values, duplicates, correlations
    ├── visualizations.py         # All 6 Plotly chart generators + recommender
    ├── insights.py               # Rule-based AI insight generation
    └── export.py                 # Cleaned CSV & report download
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python **3.10 or higher**
- pip

### 1 — Clone the repository
```bash
git clone https://github.com/your-username/smart-analytics-assistant.git
cd smart-analytics-assistant
```

### 2 — Create a virtual environment (recommended)
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### 4 — Run the app
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t smart-analytics .
docker run -p 8501:8501 smart-analytics
```

---

## 🖥️ Usage

1. **Upload a CSV** using the sidebar file uploader
2. The app instantly detects column types and displays a **dataset overview**
3. Expand any section to explore:
   - **Dataset Preview** → scroll through raw data
   - **Data Types** → see inferred types for every column
   - **Missing Values** → identify gaps in your data
   - **Duplicates** → find and preview duplicate rows
   - **Statistical Summary** → rich descriptive stats
   - **Correlation Analysis** → interactive heatmap
4. Use the **Chart Builder** to create custom visualizations
5. Read **AI-Like Insights** for automated observations
6. **Download** the cleaned dataset or summary report

---

## 🎨 Theming

The app supports **Light** and **Dark** chart themes via the sidebar radio button.
The base Streamlit theme is configured in `.streamlit/config.toml` with an indigo palette.

To switch to a dark Streamlit base theme, change `config.toml`:
```toml
[theme]
base = "dark"
primaryColor = "#6366f1"
```

---

## 🧩 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| **Streamlit** | ≥ 1.35 | Web app framework |
| **Pandas** | ≥ 2.0 | Data loading & transformation |
| **NumPy** | ≥ 1.26 | Numerical operations |
| **Plotly** | ≥ 5.22 | Interactive charts |
| **Statsmodels** | ≥ 0.14 | OLS trendline in scatter plots |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

Built with [Streamlit](https://streamlit.io), [Plotly](https://plotly.com/python/), and [Pandas](https://pandas.pydata.org/).
