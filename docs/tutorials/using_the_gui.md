# Using the GUI

This tutorial will guide you through using the graphical user interface (GUI) provided by the MultiModelAgent class.

## Launching the GUI

To launch the GUI, create a MultiModelAgent instance and call the `launch_gui` method:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Launch the GUI
agent.launch_gui()
```

This will open a window titled "Apex MultiModelAgent" with controls for mission execution and self-update.

## GUI Layout

The GUI is organized into the following sections:

### Mission Input Section

This section contains:
- A label: "Enter mission description:"
- A text entry field for entering the mission description
- The text entry field has focus by default, so you can start typing immediately

### Log Output Section

This section contains:
- A scrollable text area for displaying log messages
- Log messages include timestamps, log levels, and messages
- The text area automatically scrolls to show the latest messages

### Button Section

This section contains:
- **Run Mission**: Executes the mission entered in the text entry field
- **Self Update**: Updates the codebase from the git repository
- **Exit**: Closes the GUI

### Status Bar

The status bar at the bottom of the window displays the current status of the application, such as:
- "Ready": The agent is ready to execute a mission
- "Running mission...": The agent is currently executing a mission
- "Mission started": The mission has been started in a separate thread
- "Update successful": The codebase has been successfully updated
- "Update failed": The codebase update failed

## Running a Mission

To run a mission using the GUI:

1. Enter a mission description in the text entry field
2. Click the "Run Mission" button or press Enter
3. The status bar will display "Running mission..." and then "Mission started"
4. Log messages will appear in the log output section
5. When the mission is complete, the log will show "Mission completed successfully"

Example mission descriptions:
- "Create a Python function to calculate the factorial of a number"
- "Build a CSV parser in Python"
- "Generate a FastAPI application for a todo list"

## Self-Update

The Self Update button allows you to update the codebase from the git repository:

1. Click the "Self Update" button
2. The status bar will display "Updating..."
3. If the update is successful, the status bar will display "Update successful" and a success message will be shown
4. If the update fails, the status bar will display "Update failed" and an error message will be shown

## Threading

The GUI uses threading to prevent freezing during long-running operations:

- When you run a mission, it is executed in a separate thread
- This allows the GUI to remain responsive while the mission is running
- You can continue to interact with the GUI, view logs, or even start another mission

## Log Messages

The log output section displays messages from the Python logging system:

- **INFO** messages show general information about the agent's operation
- **DEBUG** messages show detailed information for debugging purposes
- **WARNING** messages show potential issues that don't prevent operation
- **ERROR** messages show errors that prevent successful operation
- **CRITICAL** messages show critical errors that require immediate attention

## Error Handling

The GUI includes error handling for common issues:

- If you try to run a mission without entering a description, an error message will be shown
- If an error occurs during mission execution, it will be displayed in the log output section
- If a critical error occurs during GUI initialization, an error message will be shown and the application will exit

## Closing the GUI

To close the GUI, you can:
- Click the "Exit" button
- Click the window's close button (X)
- Press Alt+F4 (Windows/Linux) or Command+Q (macOS)

When the GUI is closed, a log message is generated: "GUI closed by user"

## Example Workflow

Here's an example workflow for using the GUI:

1. Launch the GUI:
   ```python
   from multi_model_agent import MultiModelAgent
   agent = MultiModelAgent()
   agent.launch_gui()
   ```

2. Enter a mission description:
   ```
   Create a Python function to calculate the Fibonacci sequence
   ```

3. Click the "Run Mission" button

4. Watch the log output as the agent:
   - Selects the appropriate model
   - Generates code
   - Writes the code to a file
   - Executes the code
   - Handles any errors

5. When the mission is complete, check the generated code in the project directory

6. Enter another mission description or close the GUI

## Customizing the GUI

The GUI can be customized by modifying the `launch_gui` method in the MultiModelAgent class. Some possible customizations include:

- Changing the window title
- Changing the window size
- Adding additional buttons or controls
- Changing the layout
- Adding keyboard shortcuts
- Adding a menu bar

## Next Steps

Now that you've learned how to use the GUI, you can:

- [Configure and use custom models](custom_models.md)
- [Generate and run FastAPI applications](fastapi_integration.md)
- [Handle errors and improve code generation](error_handling.md)

