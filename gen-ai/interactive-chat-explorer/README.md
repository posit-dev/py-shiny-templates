# Interactive Chat Explorer

This app lets you preview and run different Shiny for Python chat apps from multiple frameworks (LangChain, LlamaIndex, LLM Package, Pydantic-AI) in a single interface.

## Setup Instructions

1. **Install dependencies**

   From this folder, run:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**

   Create a `.env` file in this folder with the necessary API key for the chat apps you want to run.

   ```sh
   touch .env
   ```

   ### Add API Keys

   Open the .env file and add your API credentials:

   ```sh
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

   #### Obtaining Your OpenAI API Key

   1. Visit the [OpenAI Platform](https://platform.openai.com/api-keys)
   2. Sign in to your account or create a new one
   3. Navigate to the API Keys section
   4. Click "Create new secret key"
   5. Copy the generated key and paste it into your `.env` file

3. **Run the main Shiny app**

   ```bash
   shiny run app-core.py
   ```

4. **Preview different apps**

   - Use the sidebar to select a **Category** and **Subcategory**.
   - The selected app will launch and display in the main panel.
   - You can view the source code for each app via the provided GitHub link.

## Troubleshooting

- If an app fails to start, check that its dependencies are installed and its code is valid.
- Only one app runs at a time; switching selection will stop the previous app and start the new one.

---
