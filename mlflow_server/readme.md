# MLflow Tracking Server Configuration

## Setup Instructions

To configure MLflow tracking server, set the following environment variables:

```python
import os

os.environ["MLFLOW_TRACKING_USERNAME"] = "admin"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "your_password"
os.environ["MLFLOW_TRACKING_URI"] = "https://caddy-production-3734.up.railway.app/"
```

## Usage

Once configured, MLflow will use these credentials to connect to your tracking server:

```python
import mlflow

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
```

**Note:** Never commit credentials to version control. Use environment variables or secrets management tools instead.
