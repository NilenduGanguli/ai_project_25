import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional
import sys
import io
from pathlib import Path
from langchain_core.tools import tool

from .models import (
    LoadCSVInput, DataInfoInput, DescribeDataInput,
    VisualizationInput, PandasCodeInput
)
from .csv_analyzer import CSVDataAnalyzer

analyzer = CSVDataAnalyzer()


# need docstring for each tool, so LLM can understand what the tool does
@tool("load_csv", args_schema=LoadCSVInput)
def load_csv_tool(file_path: str) -> str:
    """Load a CSV file for analysis

    Args:
        file_path (str): Path to the CSV file to load

    Returns:
        str: Success or error message
    """
    result = analyzer.load_csv(file_path)
    if result["success"]:
        return f"Successfully loaded CSV with shape {result['shape']}. Columns: {result['columns']}"
    else:
        return f"Error loading CSV: {result['error']}"


@tool("get_data_info", args_schema=DataInfoInput)
def get_data_info_tool() -> str:
    """Get basic information about the loaded dataset

    Returns:
        str: Dataset information
    """
    if analyzer.data is None:
        return "No data loaded. Please load a CSV file first."
    info = {
        "shape": analyzer.data.shape,
        "columns": list(analyzer.data.columns),
        "dtypes": analyzer.data.dtypes.to_dict(),
        "null_counts": analyzer.data.isnull().sum().to_dict(),
        "memory_usage": f"{analyzer.data.memory_usage(deep=True).sum() / 1024:.2f} KB",
    }
    return f"""Dataset Information:
- Shape: {info["shape"]} (rows x columns)
- Columns: {info["columns"]}
- Data Types: {info["dtypes"]}
- Null Values: {info["null_counts"]}
- Memory Usage: {info["memory_usage"]}"""


@tool("describe_data", args_schema=DescribeDataInput)
def describe_data_tool(columns: Optional[List[str]] = None) -> str:
    """Describe the data

    Args:
        columns (Optional[List[str]], optional): _description_. Defaults to None.

    Returns:
        str: _description_
    """
    if analyzer.data is None:
        return "No data loaded. Please load a CSV file first."
    if columns:
        data_subset = analyzer.data[columns]
    else:
        data_subset = analyzer.data
    numeric_desc = data_subset.select_dtypes(include=[np.number]).describe()
    categorical_info = {}
    categorical_cols = data_subset.select_dtypes(include=["object"]).columns
    for col in categorical_cols[:5]:
        categorical_info[col] = data_subset[col].value_counts(
        ).head().to_dict()
    result = f"Numeric Data Description:\n{numeric_desc.to_string()}\n\n"
    if categorical_info:
        result += "Categorical Data (Top 5 values per column):\n"
        for col, counts in categorical_info.items():
            result += f"{col}: {counts}\n"
    return result


@tool("create_visualization", args_schema=VisualizationInput)
def create_visualization_tool(
    plot_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Create a visualization

    Args:
        plot_type (str): Type of plot to create
        x_column (Optional[str], optional): _description_. Defaults to None.
        y_column (Optional[str], optional): Column to use for y-axis. Defaults to None.
        title (Optional[str], optional): Title of the plot. Defaults to None.

    Returns:
        str: Path to the saved visualization or error message
    """
    if analyzer.data is None:
        return "No data loaded. Please load a CSV file first."
    try:
        plt.figure(figsize=(10, 6))
        if plot_type == "histogram":
            if x_column:
                plt.hist(analyzer.data[x_column].dropna(), bins=30, alpha=0.7)
                plt.xlabel(x_column)
                plt.ylabel("Frequency")
            else:
                return "Histogram requires x_column parameter"
        elif plot_type == "scatter":
            if x_column and y_column:
                plt.scatter(analyzer.data[x_column],
                            analyzer.data[y_column], alpha=0.6)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
            else:
                return "Scatter plot requires both x_column and y_column parameters"
        elif plot_type == "bar":
            if x_column:
                value_counts = analyzer.data[x_column].value_counts().head(10)
                plt.bar(range(len(value_counts)), value_counts.values)
                plt.xticks(range(len(value_counts)),
                           value_counts.index, rotation=45)
                plt.xlabel(x_column)
                plt.ylabel("Count")
            else:
                return "Bar plot requires x_column parameter"
        elif plot_type == "box":
            if x_column:
                analyzer.data.boxplot(column=x_column)
                plt.ylabel(x_column)
            else:
                return "Box plot requires x_column parameter"
        elif plot_type == "heatmap":
            numeric_data = analyzer.data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                correlation_matrix = numeric_data.corr()
                sns.heatmap(correlation_matrix, annot=True,
                            cmap="coolwarm", center=0)
            else:
                return "No numeric columns found for heatmap"
        else:
            return f"Unsupported plot type: {plot_type}"
        if title:
            plt.title(title)
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plot_type}_plot_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()
        return f"Visualization created and saved as {filename}"
    except Exception as e:
        return f"Error creating visualization: {str(e)}"


@tool("execute_pandas_code", args_schema=PandasCodeInput)
def execute_pandas_code_tool(code: str, description: Optional[str] = None) -> str:
    """Execute custom pandas code on the loaded dataset

    Args:
        code (str): Pandas code to execute
        description (Optional[str], optional): Brief description of what this code does

    Returns:
        str: Result of the code execution or error message
    """
    if analyzer.data is None:
        return "No data loaded. Please load a CSV file first."
    dangerous_patterns = [
        "import os",
        "import sys",
        "import subprocess",
        "import shutil",
        "open(",
        "file(",
        "exec(",
        "eval(",
        "__import__",
        "globals()",
        "locals()",
        "vars()",
        "dir()",
        "setattr(",
        "getattr(",
        "delattr(",
        "rm ",
        "delete",
        "remove",
        "unlink",
        "socket",
        "urllib",
        "requests",
        "http",
        "ftp",
        "analyzer.data =",
        "analyzer.file_path =",
        "analyzer.load_csv(",
        "analyzer.data.to_csv(",
    ]
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            return f"Blocked: Code contains potentially dangerous operation: '{pattern}'. Please use safe pandas operations only."
    try:
        df = analyzer.data.copy()
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        plotting_keywords = [
            "plt.",
            "sns.",
            "plot(",
            "hist(",
            "scatter(",
            "bar(",
            "boxplot(",
            "seaborn.heatmap(",
            "seaborn.barplot(",
            "seaborn.boxplot(",
            "seaborn.scatterplot(",
            "seaborn.histplot(",
            "seaborn.kdeplot(",
            "seaborn.pairplot(",
            "seaborn.violinplot(",
            "seaborn.clustermap(",
            "seaborn.jointplot(",
            "seaborn.lmplot(",
            "seaborn.regplot(",
            "seaborn.residplot(",
            "seaborn.pairplot(",
            "seaborn.heatmap(",
        ]
        has_plotting = any(
            keyword in code_lower for keyword in plotting_keywords)

        safe_globals = {
            "df": df,
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns,
            "__builtins__": {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "print": print,
                "type": type,
            },
        }
        exec(code, safe_globals)
        sys.stdout = old_stdout
        output = captured_output.getvalue()

        if has_plotting:
            try:
                if plt.get_fignums():
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"custom_plot_{timestamp}.png"
                    plt.tight_layout()
                    plt.savefig(filename, dpi=300, bbox_inches="tight")
                    plt.close("all")
                    if output.strip():
                        output += f"\n\nVisualization saved as: {filename}"
                    else:
                        output = f"Visualization saved as: {filename}"
            except Exception as plot_error:
                output += (
                    f"\n\nNote: Plot generation encountered an issue: {str(plot_error)}"
                )

        if not output.strip():
            try:
                result = eval(code, safe_globals)
                if result is not None:
                    if hasattr(result, "to_string"):
                        output = result.to_string()
                    else:
                        output = str(result)
            except Exception as e:
                print(f"Error evaluating result: {str(e)}")
        description_text = f" ({description})" if description else ""
        return f"Pandas code executed successfully{description_text}:\n\n{output}"
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing pandas code: {str(e)}"
