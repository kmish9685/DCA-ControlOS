import json
import hashlib
import time
import os
from datetime import datetime

class RuleEngine:
    def __init__(self, contract_path="rules/contracts.json"):
        with open(contract_path, "r") as f:
            self.contracts = json.load(f)
            
    def validate_case(self, case):
        dca_config = self.contracts['dca_configs'].get(case['dca_id'])
        if not dca_config:
            return {"status": "error", "message": "Unknown DCA"}
        
        status = case['status']
        days = case['days_overdue']
        
        breach = False
        escalation_flag = False
        reason = "Clean"
        
        for rule in dca_config['sla_rules']:
            if rule['trigger_status'] == status:
                if days > rule['max_days_allowed']:
                    breach = True
                    reason = f"Exceeded {rule['max_days_allowed']} days in status {status}. Required: {rule['required_action']}"
                    if rule['escalation_level'] >= 2:
                        escalation_flag = True
                    break
        
        return {
            "is_breached": breach,
            "escalate": escalation_flag,
            "message": reason
        }

class AuditLogger:
    def __init__(self, log_path="data/audit_log.json"):
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                json.dump([], f)
                
    def log(self, actor, action, case_id, metadata):
        with open(self.log_path, "r") as f:
            logs = json.load(f)
        
        prev_hash = logs[-1]['hash'] if logs else "0" * 64
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "case_id": case_id,
            "metadata": metadata,
            "prev_hash": prev_hash
        }
        
        # Hash chaining
        entry_str = json.dumps(entry, sort_keys=True)
        entry['hash'] = hashlib.sha256(entry_str.encode()).hexdigest()
        
        logs.append(entry)
        with open(self.log_path, "w") as f:
            json.dump(logs, f, indent=2)
        
        return entry['hash']

if __name__ == "__main__":
    re = RuleEngine()
    test_case = {"dca_id": "DCA_ALPHA", "status": "New", "days_overdue": 5}
    print(f"Rule Validation: {re.validate_case(test_case)}")
    
    logger = AuditLogger()
    logger.log("SYSTEM", "VALIDATE", 1001, {"result": "breach"})
    print("Audit Log updated.")
