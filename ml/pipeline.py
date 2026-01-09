import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class MLPipeline:
    def __init__(self, data_path="data/cases.csv", model_dir="ml"):
        self.data_path = data_path
        self.model_dir = model_dir
        self.recovery_model = None
        self.sla_risk_model = None
        self.le_tier = LabelEncoder()
        
    def prepare_data(self):
        df = pd.read_csv(self.data_path)
        
        # Simple encoding
        df['customer_tier_encoded'] = self.le_tier.fit_transform(df['customer_tier'])
        
        # Synthetic labels for training (since we don't have historical outcomes in the CSV)
        # We simulate that higher amount and higher days_overdue reduce recovery probability
        np.random.seed(42)
        df['recovery_target'] = (1.0 - (df['amount_due'] / 60000) - (df['days_overdue'] / 150)) * np.random.uniform(0.8, 1.2, size=len(df))
        df['recovery_target'] = df['recovery_target'].clip(0, 1)
        
        # SLA breach risk simulation: higher if days_overdue / SLA_limit is high
        # (Assuming a baseline of 5 days for the risk model)
        df['sla_risk_target'] = (df['days_overdue'] / 60).clip(0, 1)
        
        return df

    def train(self):
        df = self.prepare_data()
        
        X = df[['amount_due', 'days_overdue', 'customer_tier_encoded']]
        
        # Model 1: Recovery Probability
        self.recovery_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.recovery_model.fit(X, df['recovery_target'])
        
        # Model 2: SLA Breach Risk
        self.sla_risk_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.sla_risk_model.fit(X, df['sla_risk_target'])
        
        # Save models
        os.makedirs(self.model_dir, exist_ok=True)
        with open(os.path.join(self.model_dir, "recovery_model.pkl"), "wb") as f:
            pickle.dump(self.recovery_model, f)
        with open(os.path.join(self.model_dir, "sla_risk_model.pkl"), "wb") as f:
            pickle.dump(self.sla_risk_model, f)
        with open(os.path.join(self.model_dir, "le_tier.pkl"), "wb") as f:
            pickle.dump(self.le_tier, f)
            
    def predict(self, df_input):
        X = df_input[['amount_due', 'days_overdue', 'customer_tier_encoded']]
        rec_prob = self.recovery_model.predict(X)
        sla_risk = self.sla_risk_model.predict(X)
        return rec_prob, sla_risk

if __name__ == "__main__":
    pipeline = MLPipeline()
    pipeline.train()
    print("Models trained and saved.")
