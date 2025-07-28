import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools import (
    load_csv_tool,
    get_data_info_tool,
    describe_data_tool,
    create_visualization_tool,
    execute_pandas_code_tool,
)


def create_csv_agent() -> AgentExecutor:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    tools = [
        load_csv_tool,
        get_data_info_tool,
        describe_data_tool,
        create_visualization_tool,
        execute_pandas_code_tool,
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a data analysis expert specializing in CSV data analysis and visualization.
        
You have access to powerful tools for:
- Loading and inspecting CSV files
- Performing statistical analysis
- Creating various types of visualizations
- Executing custom pandas code for advanced operations

Code Execution Options:
1. execute_pandas_code: Secure execution with safety restrictions (good for basic operations)

The execute_pandas_code tool allows you to run custom pandas operations when the predefined tools aren't sufficient. Use it for:
- Complex data transformations
- Advanced statistical calculations
- Custom aggregations
- Data cleaning operations
- Exploratory analysis that requires flexibility
- Creating custom plots and visualizations with matplotlib/seaborn


When using execute_pandas_code:
- Always use 'df' to reference the DataFrame
- Provide clear, well-commented code
- Use descriptive variable names
- Include print statements to show results
- Be aware that the original data is protected (you work with a copy)
- For plotting: Use plt.figure(), plt.bar(), plt.plot(), etc. - plots will be automatically saved
- You can create complex visualizations by combining data aggregation with plotting in the same code block
- Do NOT use import statements - pandas (pd), numpy (np), matplotlib.pyplot (plt), and seaborn (sns) are already available



When creating visualizations, choose appropriate plot types based on the data and question.

Guidelines:
- Use descriptive titles for plots
- Explain what the analysis reveals
- Suggest follow-up questions or analyses
- Handle missing data appropriately
- Provide actionable insights
- Use custom pandas code when standard tools aren't sufficient
- Always include the filename of any generated plots in your final response for easy reference
- When multiple visualizations are created, list all plot filenames clearly
- If no plots were generated, explicitly state this in your response
- If a plot is generated, always include the filename in your response
""",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
    )

    return agent_executor
