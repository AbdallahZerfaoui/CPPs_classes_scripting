#!/usr/bin/env python3

import sys
import os
import re
import shlex # For more robust splitting of input strings

def format_variable(var_str):
    """Parses a variable string 'type name' and returns a tuple (type, name)."""
    parts = shlex.split(var_str.strip())
    if len(parts) < 2:
        print(f"Warning: Skipping malformed variable input '{var_str}'. Expected 'type name'.", file=sys.stderr)
        return None, None
    var_type = parts[0]
    var_name = parts[-1] # Handle potential pointers/references like "int *" or "std::string &"
    # Basic validation: name shouldn't contain invalid characters
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
         print(f"Warning: Skipping variable '{var_str}' due to invalid name '{var_name}'.", file=sys.stderr)
         return None, None
    return var_type, var_name

def format_method(method_str):
    """Parses a method string 'ReturnType name(Params)' and returns (return_type, name, params)."""
    method_str = method_str.strip()
    if '(' not in method_str or ')' not in method_str:
         print(f"Warning: Skipping malformed method input '{method_str}'. Expected 'ReturnType name(Params)'.", file=sys.stderr)
         return None, None, None

    parts = method_str.split('(', 1) # Split only on the first '('
    signature_part = parts[0].strip()
    params_part = '(' + parts[1].strip() # Keep the parentheses for the output

    # Try to split signature_part into return type and name
    sig_parts = shlex.split(signature_part)
    if len(sig_parts) < 2:
        print(f"Warning: Skipping malformed method signature '{signature_part}'. Expected 'ReturnType name'.", file=sys.stderr)
        return None, None, None

    return_type = sig_parts[0]
    method_name = sig_parts[-1] # Handle potential return types like "std::string &"

    # Basic validation: name shouldn't contain invalid characters
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', method_name):
         print(f"Warning: Skipping method '{method_str}' due to invalid name '{method_name}'.", file=sys.stderr)
         return None, None, None

    return return_type, method_name, params_part

def create_cpp_class_files(class_name, variables_str, methods_str):
    """
    Generates .hpp and .cpp files with boilerplate for a C++ class,
    including provided variables and methods.
    """
    if not class_name:
        print("Error: Class name is required.", file=sys.stderr)
        return False

    # Define file paths
    header_dir = "include"
    source_dir = "src"
    header_file = os.path.join(header_dir, f"{class_name}.hpp")
    source_file = os.path.join(source_dir, f"{class_name}.cpp")

    # Generate header guard name
    header_guard = re.sub(r'[^0-9A-Z_]', '_', class_name.upper())
    header_guard = re.sub(r'_+', '_', header_guard).strip('_')
    header_guard = f"{header_guard}_HPP"

    # --- Parse variables and methods ---
    variables = []
    if variables_str:
        for var_str in variables_str.split(','):
            var_type, var_name = format_variable(var_str)
            if var_type and var_name:
                variables.append({'type': var_type, 'name': var_name})

    methods = []
    if methods_str:
        for method_str in methods_str.split(','):
            return_type, method_name, params = format_method(method_str)
            if return_type and method_name and params:
                 methods.append({'return_type': return_type, 'name': method_name, 'params': params})


    # --- Create the Header File (.hpp) ---
    os.makedirs(header_dir, exist_ok=True)
    if os.path.exists(header_file):
        print(f"Error: Header file '{header_file}' already exists.", file=sys.stderr)
        return False

    # Build variables string for header
    variables_decl = ""
    if variables:
        variables_decl = "\n" # Add a newline if variables exist
        for var in variables:
            variables_decl += f"\t{var['type']} {var['name']};\n"
        variables_decl += "\n" # Add a newline after variables

    # Build methods string for header
    methods_decl = ""
    if methods:
        methods_decl = "\n" # Add a newline if methods exist
        for method in methods:
            methods_decl += f"\t{method['return_type']} {method['name']}{method['params']};\n"
        methods_decl += "\n" # Add a newline after methods

    header_content = f"""\
#ifndef {header_guard}
# define {header_guard}

# include <iostream> // Common include, adjust as needed
# include <string>   // Common include, adjust as needed

// Add other necessary includes here

class {class_name}
{{
private:{variables_decl}\
	// Member variables (declared above or add more manually)

public:
	// Canonical Form
	{class_name}();                            // Default constructor
	{class_name}(const {class_name}& other); // Copy constructor
	{class_name}& operator=(const {class_name}& other); // Copy assignment operator
	~{class_name}();                           // Destructor{methods_decl}\
	// Add other member functions here (declared above or add more manually)

}};

// Optional: Overload stream insertion operator (common 42 practice)
// std::ostream& operator<<(std::ostream& os, const {class_name}& obj);

#endif /* {header_guard} */
"""
    try:
        with open(header_file, 'w') as f:
            f.write(header_content)
        print(f"Created header file: {header_file}")
    except IOError as e:
        print(f"Error writing header file {header_file}: {e}", file=sys.stderr)
        return False

    # --- Create the Source File (.cpp) ---
    os.makedirs(source_dir, exist_ok=True)
    if os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' already exists.", file=sys.stderr)
        # Clean up header file if source file failed
        if os.path.exists(header_file):
             os.remove(header_file)
             print(f"Cleaned up header file: {header_file}", file=sys.stderr)
        return False

    # Build variable copying string for copy constructor and assignment operator
    variables_copy = ""
    if variables:
        variables_copy = "\n\t// Copy member variables"
        for var in variables:
            # Use other.name for copy constructor, this->name = other.name for assignment
            # We'll include this in the assignment operator and mention it for copy ctor
            variables_copy += f"\n\t\tthis->{var['name']} = other.{var['name']};"
        variables_copy += "\n" # Add a newline after copying

    # Build method definitions string for source
    methods_def = ""
    if methods:
         methods_def = "\n" # Add a newline before method definitions
         for method in methods:
              methods_def += f"""
// {method['name']} method
{method['return_type']} {class_name}::{method['name']}{method['params']}
{{
	// Method implementation here
}}
"""

    source_content = f"""\
#include "{class_name}.hpp"

// Default constructor
{class_name}::{class_name}()
{{
	// std::cout << "{class_name} default constructor called" << std::endl;
	// Initialize member variables here (e.g., this->_name = "Default Name";)
}}

// Copy constructor
{class_name}::{class_name}(const {class_name}& other)
{{
	// std::cout << "{class_name} copy constructor called" << std::endl;
	// Copy member variables from 'other'.
	// Often done by calling the copy assignment operator:
    *this = other;
    // Alternatively, copy them directly here:
    // {variables_copy.replace("this->", "")} # Simple variables don't need 'this->' here, just 'name'
}}

// Copy assignment operator
{class_name}& {class_name}::operator=(const {class_name}& other)
{{
	// std::cout << "{class_name} copy assignment operator called" << std::endl;
	if (this != &other)
	{{
		// Clean up existing resources if necessary

        {variables_copy}\
		// Assign member variables from 'other' (assigned above or add more manually)
	}}
	return *this;
}}

// Destructor
{class_name}::~{class_name}()
{{
	// std::cout << "{class_name} destructor called" << std::endl;
	// Clean up resources if necessary
}}{methods_def}\

// Add other member function definitions here (declared above or add more manually)

// Optional: Overload stream insertion operator definition
// std::ostream& operator<<(std::ostream& os, const {class_name}& obj)
// {{
//     // Output object state to stream
//     return os;
// }}
"""

    try:
        with open(source_file, 'w') as f:
            f.write(source_content)
        print(f"Created source file: {source_file}")
    except IOError as e:
        print(f"Error writing source file {source_file}: {e}", file=sys.stderr)
        # Clean up header file if source file failed
        if os.path.exists(header_file):
             os.remove(header_file)
             print(f"Cleaned up header file: {header_file}", file=sys.stderr)
        return False

    # Optional: Open the files in VS Code after creation (requires 'code' command in PATH)
    # try:
    #     import subprocess
    #     subprocess.run(["code", header_file, source_file])
    # except FileNotFoundError:
    #     print("VS Code 'code' command not found. Files created but not opened.")


if __name__ == "__main__":
    # Expecting 3 arguments: script_name, class_name, variables_string, methods_string
    # The variable and methods strings can be empty ""
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python3 scripts/create_cpp_class.py <ClassName> [Variables String] [Methods String]", file=sys.stderr)
        print("Example Vars String: \"std::string _name, int _age\"", file=sys.stderr)
        print("Example Methods String: \"void speak(), int getAge() const\"", file=sys.stderr)
        sys.exit(1)

    class_name = sys.argv[1]
    variables_str = sys.argv[2] if len(sys.argv) > 2 else ""
    methods_str = sys.argv[3] if len(sys.argv) > 3 else ""

    if create_cpp_class_files(class_name, variables_str, methods_str):
        sys.exit(0)
    else:
        sys.exit(1)
