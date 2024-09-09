# Chat with Terms and Conditions of any Websites 🤖

This project is a web-based application built with Streamlit that allows users to chat with the Terms and Conditions or privacy policy of various websites. The application retrieves content from specified websites, processes it, and generates context-specific answers based on the website's Terms & Conditions.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: Sign-up and login functionalities for users.
- **Interactive Chat Interface**: Users can input queries and receive responses directly based on the Terms & Conditions of a website.
- **Automatic Context Retrieval**: The application retrieves relevant sections of the website content and uses that for answering queries.
- **Powered by LLaMA 2**: Utilizes the Ollama LLaMA 2 model for generating accurate and context-based answers.
- **Embeddings for Context Matching**: Uses embeddings to create a vector database to match user queries with relevant parts of the website text.
- **Customizable UI**: Beautiful, customizable user interface with CSS styling to match a modern theme.

## Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment (optional but recommended)
- [Streamlit](https://streamlit.io/)
- Required Python libraries from `requirements.txt`
- `.env` file for environment variables

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/chat-with-terms-conditions.git
   cd chat-with-terms-conditions
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install required libraries**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**:

   Create a `.env` file in the root directory of the project and add the necessary environment variables.

5. **Run the application**:

   ```bash
   streamlit run app.py
   ```

## Usage

1. **Start the Streamlit server** by running `streamlit run app.py`.
2. **Sign up or log in** using your credentials.
3. **Enter the website name** for which you want to interact with the Terms & Conditions.
4. **Type your queries** in the input box, and the application will return responses based on the website's Terms & Conditions.

### Adding Websites

The application comes with a predefined list of websites and their URLs. If you want to add a new website:

1. Open `app.py`.
2. Add a new entry to the `websites` table in the `populate_database()` method in the `WebsiteDatabase` class.

## Examples

Here are some example queries you can try:

1. **Query**: "What is the privacy policy of WhatsApp?"
   - **Response**: Summarized answer based on the Terms and Conditions of WhatsApp.

2. **Query**: "Can I use Instagram's services if I'm under 13?"
   - **Response**: Information from Instagram's Terms of Service regarding age restrictions.

3. **Query**: "What are the GDPR policies on Facebook?"
   - **Response**: Relevant sections of Facebook's GDPR policies.

## Contributing

Contributions are welcome! If you want to contribute to this project, please fork the repository, create a new branch, and submit a pull request. Ensure your changes align with the project's coding standards and include appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **[Streamlit](https://streamlit.io/)** for the amazing framework.
- **[LangChain](https://langchain.com/)** for providing useful tools to build LLM applications.
- **[Ollama](https://ollama.com/)** for the LLaMA 2 model.
- **Contributors** who helped make this project better!

## Contact

If you have any questions or suggestions, feel free to contact the maintainer at [gabrielkelvin184@gmail.com](mailto:your.email@example.com).