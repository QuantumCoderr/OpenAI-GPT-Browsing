# OpenAI GPT Browsing

A project utilizing OpenAI's GPT model to enable web browsing capabilities. This project allows real-time information retrieval and interaction using custom commands.

## Features

- **Web Browsing**: Use GPT to perform web searches and extract content.
- **Custom Commands**:
  - `/search="query"`: Perform a search with the given query.
  - `/click=ID`: Extract text from a selected ID.
  - `/search_exit`: Exit the search mode.


## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/QuantumCoderr/OpenAI-GPT-Browsing.git
   cd OpenAI-GPT-Browsing
   ```

2. **Install dependencies**:

   Install the required Python packages using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   Create a `.env` file based on `template.env` and add your API key and endpoint URL:

   ```plaintext
   OPENAI_API_KEY=your_key_here
   API_BASE=https://api.openai.com/v1
   ```

   Replace `your_key_here` with your actual API key. You can use the official OpenAI API endpoint `https://api.openai.com/v1` or your custom endpoint.

### Running the Project

- **Test the browser**:

  You can test the browsing functionality by running `browse.py`:

  ```bash
  python browse.py
  ```

  This script allows you to test the basic browsing commands without engaging the full GPT model.

- **Run the GPT browser**:

  To engage the full GPT model with browsing capabilities, run `gpt_browse.py`:

  ```bash
  python gpt_browse.py
  ```

 For GPT, you don't need to use commands. It understands when to use the browser as if it were `function_calling`.

### Example Usage of `gpt_browse.py`

Simply ask the model to Google something for you.

**Me**: Google the news for 2024 and tell me what you found out.  
**AI**: Of course!

### Example Usage of `browse.py`

Simply use the command `/search="query"`, `/click=ID`, `/search_exit`.

## Troubleshooting

- **System Prompt Issues**: The model might work unstably with the browser due to the system prompt. You can modify it manually to suit your needs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes you would like to see.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
