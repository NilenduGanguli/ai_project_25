import pandas as pd
from typing import Dict, Any, Optional


class CSVDataAnalyzer:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None

    def load_csv(self, file_path: str) -> Dict[str, Any]:
        try:
            self.data = pd.read_csv(file_path)
            self.file_path = file_path
            return {
                "success": True,
                "shape": self.data.shape,
                "columns": list(self.data.columns),
                "dtypes": self.data.dtypes.to_dict(),
                "sample": self.data.head().to_dict(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
