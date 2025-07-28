from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from src.agent import create_csv_agent

load_dotenv()


def main():
    agent_executor = create_csv_agent()
    context = []

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break

            if not user_input:
                continue

            response = agent_executor.invoke(
                {"input": user_input, "chat_history": context}
            )
            print(f"Agent: {response['output']}")
            context.append(HumanMessage(content=user_input))
            context.append(AIMessage(content=response["output"]))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
