# DCA-ControlOS: A Regulation-First Governance Platform

**Technical Prototype | Hackathon Version 1.0**

## 1. Problem FedEx Faces
FedEx manages thousands of overdue accounts through external Debt Collection Agencies (DCAs). Currently, this oversight is fragmented across manual spreadsheets and emails. This results in:
*   **Operational Friction**: Delays in case updates and recovery.
*   **Weak Governance**: No programmatic way to enforce Service Level Agreements (SLAs).
*   **SLA Violations**: Breaches are often discovered weeks after they occur.
*   **Audit Gaps**: No tamper-evident trail for regulatory reviews.

## 2. Our Core Insight
**The core problem is governance failure, not a lack of analytics.** 

Modern operations have plenty of dashboards, but dashboards alone are passive. They show you that an SLA was broken, but they do not prevent it. Basic analytics cannot solve for the accountability required in regulated debt collection. We shift the paradigm by treating DCAs as programmable, regulated operators.

## 3. What We Built
This prototype focuses on a "vertical slice" of governance logic.

### Fully Implemented
*   **Contract-as-Code Engine**: Programmatic validation of every agency action against machine-readable JSON contracts.
*   **SLA Risk Modeling**: ML models that predict breach probability based on current case dwell time.
*   **Immutable Audit Ledger**: A hash-chained JSON ledger that provides a mathematical guarantee of data integrity.
*   **Prioritization Matrix**: A strategic view for mangers to focus on high-recovery/high-risk cases.

### Intentionally Simplified
*   **State Management**: Data is stored in CSV/JSON format instead of a robust SQL database (PostgreSQL).
*   **Identity**: Simple role-selection in the sidebar replaces a formal Auth0 or Okta implementation.
*   **Data Source**: Synthetic datasets are used to simulate real-world recovery patterns.

## 4. How Control Is Enforced
Governance is "baked into" the system logic rather than layered on top as an afterthought:
*   **Contract-as-Code**: Every update from a DCA is validated against a machine-readable schema. If an action violates a timeline or SOP, the system flags it instantly.
*   **Compliance Risk Prediction**: Using Random Forest regressors, the system flags cases with a high probability of breaching SLA windows before the breach occurs.
*   **Auto-Escalation**: Cases that enter a "Breached" state are visually highlighted and flagged for management intervention.
*   **Immutable Ledger**: Each log entry contains a SHA-256 hash of the previous entry. Any attempt to modify historical records breaks the chain, alerting auditors to tampering.

## 5. Why This Is Different
*   **Excel vs. Enforcement**: Passive spreadsheets rely on manual follow-up. This system uses a state machine to enforce contract terms.
*   **Predictive vs. Reactive**: Standard dashboards show you what already went wrong. Our ML pipeline shows you what is *about to* go wrong.
*   **Audit-Ready**: Rather than preparing for an audit for weeks, the hash-chaining mechanism provides an instant, self-verifying trail of every decision.

## 6. Prototype Walkthrough
When opening the dashboard, a judge will observe:
1.  **Governance KPIs**: Immediate visibility into "At Risk" and "Critical Breaches" count.
2.  **Prioritization Matrix**: A scatter plot with quadrant lines separating standard inventory from cases requiring "Immediate Governance Attention."
3.  **Case Inventory**: A color-coded table (Neutral / Amber / Red) showing the real-time SLA status for every account.
4.  **Audit Ledger**: A technical view of the hash-chained logs, showing the timestamped actor, action, and unique SHAnd-hash for every event.

## 7. How to Run
To run the prototype locally, ensure you have Python installed, then run:
```powershell
python app.py
```
*Note: This script will verify dependencies, train the ML models if necessary, and launch the dashboard.*

## 8. Deployment Architecture
> [!IMPORTANT]
> **Honest Architecture Note**: This project follows a "Local Truth / Web Visualization" model.
> - **Core Logic (Local Source of Truth)**: The Python-based Contract-as-Code engine, ML pipelines, and Immutable Audit are implemented for high-fidelity evaluation and local demonstration. Run via `python app.py`.
> - **Frontend (Web Visualization)**: A zero-friction web interface is deployed on Vercel to allow judges to immediately visualize the dashboard's design and intent. All data shown is generated from the Python case engine outputs to reflect real system behavior.
> - **Separation**: No Python or ML code is executed on Vercel; it serves purely as a visualization layer.

## 9. Scalability Path (Conceptual)
In a production environment, DCA-ControlOS would scale as follows:
*   **Event Infrastructure**: Migrating from local calls to an event-driven architecture (Kafka) to handle millions of case updates.
*   **Distributed Ledger**: Mirroring the hash-chained logs to a cloud-native immutable database like AWS QLDB.
*   **Enterprise Integration**: Connecting the Rule Engine directly into payment gateways and external legal platforms to close the loop on enforcement.
