# 🛡️ LoanGuard AI

### AI-powered loan agreement safety analyzer

**Read smarter. Borrow safer. Know the hidden cost before you sign.**

LoanGuard AI is a fintech AI prototype built to protect borrowers from risky loan agreements. It analyzes loan documents, detects suspicious clauses, identifies hidden charges, calculates the real borrowing cost, and generates a safety report within seconds.

Built as a hackathon MVP with a clean modular architecture that can be extended into a full-scale fintech product.

---

## 🚀 Key Features

### 📄 Smart Agreement Analysis

* Upload loan agreement PDF or paste agreement text
* Automatic document text extraction
* AI-style clause scanning engine

### 🛡️ Risk Detection Engine

Detects common borrower risks including:

* Hidden fees & processing charges
* High penalties
* Unclear repayment conditions
* Contact/data access permissions
* Third-party data sharing
* Aggressive recovery clauses
* Unfair lender terms

### 📊 Loan Safety Score

* Generates safety score out of 10
* Categorizes agreement risk:

  * 🟢 LOW Risk
  * 🟡 MEDIUM Risk
  * 🔴 HIGH Risk

### 💰 True Cost Calculator

Compare:

* Promised loan amount
* Actual received amount
* Hidden deductions
* Effective borrowing cost

### 📥 Safety Report Generator

Creates a complete borrower safety report containing:

* Risk summary
* Cost analysis
* Important warnings
* Recommendations

Downloadable report included.

---

# 🏗️ Project Structure

```
LoanGuard-AI/
│
├── app.py
│
├── modules/
│   ├── pdf_processor.py
│   ├── risk_analyzer.py
│   ├── cost_calculator.py
│   └── report_generator.py
│
├── assets/
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Setup

Clone the repository:

```bash
git clone <repository-url>

cd LoanGuard-AI
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
streamlit run app.py
```

Open:

```
http://localhost:8501
```

---

# 🧪 Demo Testing Text

Paste this sample agreement:

```
The borrower agrees to a processing fee deducted from the loan amount.

Late payment penalty of 5% per month shall apply.

The lender may access phone contacts and share personal data with third-party partners.

Recovery agents may visit home or workplace.

Repayment terms may change according to lender policy.
```

LoanGuard AI will detect risky clauses and generate a safety report.

---

# 🛠️ Tech Stack

* Python
* Streamlit
* PDF Processing
* Rule-based NLP Analysis
* Modular Python Backend

---

# 🔮 Future Improvements

* Machine Learning risk prediction model
* FastAPI backend
* User authentication
* Database support
* Multi-language agreement analysis
* Advanced legal AI assistant

---

# ⚠️ Disclaimer

LoanGuard AI is created for educational and demonstration purposes.

It does not provide official legal or financial advice. Always consult a certified professional before making financial decisions.

---

### Built to make digital lending safer 🚀
