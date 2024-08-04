import dotenv
import os
from openai import OpenAI
import json
from browse import search, click, extract_data
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE")
)


def get_gpt_response(messages):
    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True
        )

        print("\nAI: ", end='', flush=True)
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                full_response += content

        print("\n")
        return full_response

    except Exception as e:
        logging.error(f"Error in API call: {e}")
        return None


def extract_command(text):
    search_match = re.search(r'/search="([^"]*)"', text)
    if search_match:
        return 'search', search_match.group(1)

    click_match = re.search(r'/click=(\d+)', text)
    if click_match:
        return 'click', int(click_match.group(1))

    if '/search_done' in text:
        return 'search_done', None

    return None, None


def truncate_content(content, max_length=4000):
    if len(content) > max_length:
        return content[:max_length] + "... [truncated]"
    return content


def main():
    messages = [
        {"role": "system", "content": """
        BROWSING:

You can use Google to search. Use the following commands to perform search queries and retrieve information:

/search="query" - Executes an internet search for the specified query. You will receive a list of page titles with their IDs.

/click=ID - Retrieves the text from the page with the specified ID. Note: the text is limited to the first 1000 characters.

/open_link="url" - Opens the specified link.

/search_done - Indicates that you have finished browsing and want to summarize the information.

Example usage:

You: /search="latest news about GPT-4"

System: [list of titles with IDs]

You: /click=1

System: [text from the page]

You: /open_link="https://example.com"

System: [link opened]

You: /search_done

System: Browsing completed. You can now summarize the information for the user.

Important Notes:

You need to write the command once.
You will receive a response from the system after entering the command.
You must independently enter the command /click=ID or /search_done without extra words when you receive the response.
And tell the user everything you learned inside the site and indicate the sources.
YOU ARE RESPONSIBLE TO REPORT THE RECEIVED TEXT FROM THE SITE OF THE SUMMARY VERSION.
If a user asks to "Google the news" in general terms, then search for the news, but instead of providing a summary from the most general site, provide a summary from the internal links you accessed through /click=ID.
Look at a minimum of 3 pages.
Use /search_done when you're ready to summarize the information.
Even when you have entered the command, add <!END!> at the end. This is important.
        """}
    ]

    user_query = input("Enter your query: ")
    messages.append({"role": "user", "content": user_query})

    pages_viewed = 0
    last_results = None
    browsing = False

    while True:
        response = get_gpt_response(messages)
        if not response:
            logging.error("Failed to get AI response")
            break

        command, arg = extract_command(response)

        if command == 'search':
            browsing = True
            pages_viewed = 0
            print("Browsing...")
            results = search(arg)
            last_results = results
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "system", "content": truncate_content(json.dumps(results, ensure_ascii=False))})
        elif command == 'click' and browsing:
            if last_results:
                print("Browsing...")
                try:
                    data = click(arg, last_results)
                    truncated_data = truncate_content(json.dumps(json.loads(data), ensure_ascii=False))
                    messages.append({"role": "assistant", "content": response})
                    messages.append({"role": "system", "content": truncated_data})
                    pages_viewed += 1
                except Exception as e:
                    logging.error(f"Error in click command: {e}")
                    messages.append({"role": "system", "content": f"Error retrieving data: {str(e)}"})
            else:
                messages.append(
                    {"role": "system", "content": "No search results available. Please perform a search first."})
        elif command == 'search_done':
            browsing = False
            messages.append({"role": "system", "content": "Browsing completed. You can now summarize the information for the user."})
        elif not browsing:
            print("AI is processing your request...")
            messages.append({"role": "assistant", "content": response})
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                break
            messages.append({"role": "user", "content": user_input})
        else:
            messages.append(
                {"role": "system", "content": "Invalid command. Use /search=\"query\", /click=ID, or /search_done"})

        logging.info(f"Current message count: {len(messages)}")
        logging.info(f"Last message content length: {len(messages[-1]['content'])}")


if __name__ == "__main__":
    main()