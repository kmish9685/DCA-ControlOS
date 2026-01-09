# DCA-ControlOS

**Regulation-First, Contract-Aware AI OS for Debt Collection Agencies.**

## 🛡️ Overview
DCA-ControlOS is a governance platform designed to bring machine-enforceable control to external debt collection operations. It replaces loose manual processes with "Contract-as-Code" and "Predictive Intelligence".

## 🏗️ Architecture
- **Case Engine**: Dynamic management of debt inventory.
- **Contract Engine**: Validates every DCA action against JSON-defined SLA/SOP rules.
- **AI Pipeline**: Scikit-learn models predicting Recovery Probability and SLA Breach Risk.
- **Audit Ledger**: Hash-chained, append-only JSON log for immutable proof of governance.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- `pip install streamlit pandas scikit-learn numpy`

### Running the App
```bash
python app.py
```
Or directly:
```bash
streamlit run ui/dashboard.py
```

## 📂 Project Structure
- `/data`: CSV cases and JSON Audit Log.
- `/ml`: Model training pipeline and serialized `.pkl` files.
- `/rules`: Contract definitions and Rule Engine logic.
- `/ui`: Streamlit dashboard.

## ⚖️ Governance Model
1. **Contract-as-Code**: Rules define what a DCA *must* do.
2. **Auto-Escalation**: System flags breaches in real-time.
3. **Immutable Logs**: Every decision is hashed and chained.
