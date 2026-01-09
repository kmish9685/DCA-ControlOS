import subprocess
import sys
import os

def run():
    print("Initializing DCA-ControlOS...")
    
    # Add current directory to PYTHONPATH for local imports
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    # 1. Ensure models are trained
    if not os.path.exists("ml/recovery_model.pkl"):
        print("Training models...")
        subprocess.run([sys.executable, "ml/pipeline.py"], env=env)
        
    # 2. Start Streamlit
    print("Launching Dashboard...")
    subprocess.run(["streamlit", "run", "ui/dashboard.py"], env=env)

if __name__ == "__main__":
    run()
