# Interactive Chat Explorer

This app lets you preview and run different Shiny for Python chat apps from multiple providers (LangChain, LlamaIndex, LLM Package, Pydantic-AI) in a single interface.

## Setup Instructions

1. **Install dependencies**

   From this folder, run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main Shiny app**

   ```bash
   shiny run app-core.py
   ```

3. **Preview different apps**

   - Use the sidebar to select a **Category** and **Subcategory**.
   - The selected app will launch and display in the main panel.
   - You can view the source code for each app via the provided GitHub link.

## Troubleshooting
- If an app fails to start, check that its dependencies are installed and its code is valid.
- Only one app runs at a time; switching selection will stop the previous app and start the new one.

---
