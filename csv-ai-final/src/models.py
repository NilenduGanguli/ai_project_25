from pydantic import BaseModel, Field
from typing import List, Optional


class LoadCSVInput(BaseModel):
    file_path: str = Field(description="Path to the CSV file to load")


class DataInfoInput(BaseModel):
    pass


class DescribeDataInput(BaseModel):
    columns: Optional[List[str]] = Field(
        default=None, description="Specific columns to describe (optional)"
    )


class VisualizationInput(BaseModel):
    plot_type: str = Field(
        description="Type of plot (histogram, scatter, bar, box, heatmap)"
    )
    x_column: Optional[str] = Field(default=None, description="X-axis column")
    y_column: Optional[str] = Field(default=None, description="Y-axis column")
    title: Optional[str] = Field(default=None, description="Plot title")


class PandasCodeInput(BaseModel):
    code: str = Field(
        description="Pandas code to execute. Use 'df' to reference the loaded DataFrame. Code should be safe and not modify the original data permanently."
    )
    description: Optional[str] = Field(
        default=None, description="Brief description of what this code does"
    )
