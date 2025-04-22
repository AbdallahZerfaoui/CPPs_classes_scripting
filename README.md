
# Automating C++ Class Creation in VS Code for 42 Projects

Starting a new C++ project at 42 involves creating many classes.   
Each class requires creating two files (`.hpp` and `.cpp`), adding standard boilerplate code (like header guards, includes, the "Canonical Form" functions), declaring member variables, and defining member functions. Doing this manually every time is repetitive, slow, and prone to errors.

This guide shows you how to use a **simple Python script and a VS Code task** to automate this process, saving you time and ensuring consistency.

**The Goal:** Create a VS Code command that, when run, asks you for a **class name, member variables, and member methods**, and then automatically generates the corresponding `.hpp` and `.cpp` files with the necessary boilerplate.

**How it Works:**

1.  **A Python Script:** This script is the core engine. It takes the class name, variable list, and method list as input. It knows the structure of a standard 42 C++ class and generates the text content for both the header (`.hpp`) and source (`.cpp`) files, including the boilerplate, variable declarations/copying, and method definitions.
   
2.  **A VS Code Task:** This is how you trigger the Python script from within VS Code. It defines a custom command in VS Code's Command Palette. When you run this task, VS Code will:
    *   Prompt you for the required information (class name, variables, methods).
    *   Execute the Python script, passing your inputs as arguments.
    *   Show you the script's progress and any messages in the VS Code terminal.

---

## Step 1: Get the Python Script (The C++ File Factory)

This script contains the logic for generating your C++ code.

1.  Open your C++ project folder in VS Code.
2.  Create a new folder named `scripts` at the root level of your project (the same level as your `Makefile`).
3.  Inside the `scripts` folder, create a new file named `create_cpp_class.py`.
4.  Paste the Python code from my repo into this file.
5.  Save the file.

**What this script does:**
*   It reads the class name, the variables string, and the methods string provided as command-line arguments.
*   It parses the variables string (expected format: `"type1 name1, type2 name2, ..."`) and methods string (expected format: `"ReturnType1 method1(params1), ReturnType2 method2(params2), ..."`) into structured data.
*   It constructs the full file paths for the `.hpp` file (in an `include` directory) and the `.cpp` file (in a `src` directory). It will create these directories if they don't exist.
*   It generates the header guard name based on the class name.
*   It builds the content for the `.hpp` file, including:
    *   The header guard (`#ifndef`, `#define`, `#endif`).
    *   Basic includes (`iostream`, `string`).
    *   The `class ClassName { ... };` declaration.
    *   The canonical form declarations (`Constructor()`, `CopyConstructor()`, `operator=`, `Destructor()`).
    *   The variable declarations you provided under `private:`.
    *   The method declarations you provided under `public:`.
*   It builds the content for the `.cpp` file, including:
    *   The `#include "ClassName.hpp"`.
    *   The basic definitions for the canonical form functions (with comments indicating where to add logic).
    *   Code within the Copy Assignment Operator (`operator=`) to copy the member variables you provided.
    *   Basic function definitions (`ReturnType ClassName::methodName(params) { ... }`) for the methods you provided.
*   It writes the generated content to the respective `.hpp` and `.cpp` files.
*   It prints messages to the terminal indicating which files were created or if errors occurred (like the file already existing).

## Step 2: Make the Python Script Executable (Linux/macOS)

This step is necessary on Unix-like systems (Linux, macOS) so that VS Code can run the script directly.

1.  Open the integrated terminal in VS Code (`Terminal` -> `New Terminal` or `Ctrl+`/`Cmd+`).
2.  Make sure you are in your project's root directory.
3.  Run the following command:
    ```bash
    chmod +x scripts/create_cpp_class.py
    ```
    This gives the script file permission to be executed like a program. On Windows, running with `python3` command often handles this, but if you encounter permission issues, look into setting execute permissions for scripts on your specific Windows setup.

## Step 3: Configure the VS Code Task (The Control Panel)

This tells VS Code how to interact with your script.

1.  Open the VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
2.  Type `Tasks: Configure Task` and select it.
3.  Select `Create tasks.json file from template`.
4.  Select `Others`. This will create a `.vscode` folder with a `tasks.json` file if you don't have one already.
5.  Open the `.vscode/tasks.json` file.
6.  Replace the default content with the `tasks.json` code from my repo.
7.  Save the file.

**What this `tasks.json` configuration does:**
*   It defines a custom task named `"Create C++ Class (Enhanced)"`. This is the name you will select in the Command Palette.
*   It specifies that this task should run a `shell` command.
*   The `command` is set to `"python3"`, which tells the shell to use the Python 3 interpreter. (If `python3` doesn't work on your system, try just `"python"`).
*   The `args` list provides the arguments that will be passed to the `python3` command:
    *   `"./scripts/create_cpp_class.py"`: The first argument is the path to your script.
    *   `"${input:classNameEnhanced}"`: This special syntax means "get the value from the input prompt defined below with ID `classNameEnhanced` and pass it as an argument".
    *   `"${input:memberVarsEnhanced}"`: Passes the value from the variables input prompt.
    *   `"${input:memberMethodsEnhanced}"`: Passes the value from the methods input prompt.
*   The `inputs` section defines the interactive prompts that VS Code will show you when you run the task:
    *   It defines an input with `id: "classNameEnhanced"` that uses `type: "promptString"` to ask the user the `description: "Enter C++ class name:"`.
    *   It defines similar input prompts for member variables and member methods, guiding you on the expected format (e.g., `"string _name, int _age"`).

## Step 4: Use Your New Class Creation Tool!

Now you're ready to generate classes quickly.

1.  Open the VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
2.  Type `Tasks: Run Task` and select it.
3.  A list of available tasks will appear. Select `"Create C++ Class (Enhanced)"`.
4.  VS Code will display a sequence of input boxes at the top of the window, corresponding to the `inputs` defined in your `tasks.json`:
    *   Type the desired **class name** (e.g., `Zombie`) and press Enter.
    *   Type the **member variables** in the specified format (e.g., `std::string _name, int _brainsEaten`). Separate multiple variables with commas. Press Enter. You can leave this blank and press Enter if you have no variables to add right now.
    *   Type the **member methods** in the specified format (e.g., `void announce(), void eatBrains(int num)`). Separate multiple methods with commas. Press Enter. You can leave this blank and press Enter if you have no methods to add right now.
5.  After you press Enter for the methods, the VS Code terminal panel will open and execute the Python script with your inputs.
6.  The terminal will show messages indicating that `include/Zombie.hpp` and `src/Zombie.cpp` (or whatever class name you chose) have been created.

That's it! You have automatically generated the files and the common boilerplate code for your new C++ class using your scripted VS Code environment.

---

**Important Considerations:**

*   **Python 3:** Ensure you have Python 3 installed and the `python3` command works in your terminal.
*   **Code Location:** The script assumes `include/` and `src/` directories at your project root. Adjust the `header_dir` and `source_dir` variables in the Python script if your structure is different.
*   **Customization:** To change the generated boilerplate (add different default includes, change formatting, etc.), you must **edit the `create_cpp_class.py` script itself**. Modify the large multiline strings (`header_content` and `source_content`).
*   **Beyond Boilerplate:** Remember, this tool creates the *framework*. You still need to manually:
    *   Write the actual logic inside the method bodies (`{...}`).
    *   Initialize member variables correctly in your constructors (the script adds comments suggesting where to do this). The script handles copying in the assignment operator, but initializer lists in constructors are often preferred for member initialization.
    *   Handle complex resources (like raw pointers) that require deep copies or specific cleanup in the canonical form functions.

By setting this up, you've successfully "scripted your favorite text editor" (VS Code) to handle a repetitive part of your C++ development workflow, allowing you to focus more on writing the unique logic for each class!
