
from sentiment_agent import SentimentAgent


def main():
    try:
        agent = SentimentAgent()
    except Exception as error:
        print(f"Startup failed: {error}")
        return

    print("\n=== UC03: Social Media Sentiment Agent ===")
    print(f"Loaded {len(agent.df)} tweets.")
    print("Type 'exit' to stop.")
    print("For a custom tweet, type: analyze: Your tweet here\n")

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("Agent: Goodbye!")
                break

            if not question:
                continue

            print("\nAgent:")
            print(agent.answer(question))
            print()

        except KeyboardInterrupt:
            print("\nAgent: Goodbye!")
            break
        except Exception as error:
            print(f"Request failed: {error}\n")


if __name__ == "__main__":
    main()
