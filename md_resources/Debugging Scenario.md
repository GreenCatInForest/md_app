Debugging Scenario. 

1. Understand the Problem 
Before diving into the code, take a moment to clarify the bug:

- What’s the error message?
Read the full error message carefully.
- Identify the **key parts** (e.g., 'str' object has no attribute 'path' tells you it’s treating a string as an object).
- When does it happen?
Is it triggered by a specific action (e.g., a form submission)?
- Where does it happen?
- Which part of your app or which file/function is mentioned in the traceback?

2. Break the Problem into Smaller Pieces
Instead of trying to solve the entire bug at once:

- Find the Smallest Failing Step:
What’s the first point in the code where something goes wrong?
- Trace the Flow of Data:
Follow how data moves through your code, step by step.
Example: How does room_pictures get passed from the form to the task?

3. Use Strategic Debugging Techniques
Here are practical tools and strategies:

A. Logging
1) Add debug logs at key points in the code to inspect variables and flow:
logger.debug(f"Variable name: {variable}, Type: {type(variable)}")

2) Log before and after major operations:
logger.debug("Starting task...")
logger.debug("Finished resizing image.")

B. Isolate the Problem
Comment out unrelated sections of code to focus on the failing part.
Test smaller parts of the functionality (e.g., test resize_and_save_image independently).

C. Reproduce the Issue
Find the minimum input or action that triggers the bug.
Repeat the process in a controlled environment (e.g., development server or test cases).

D. Add Assertions
Temporarily add checks to ensure variables are in the expected state:
assert isinstance(room_pictures, list), "room_pictures must be a list"

4. Use the Scientific Method
Debugging is like solving a mystery. Follow these steps:

- Form a Hypothesis:
Based on the error message and logs, make an educated guess about the cause.
- Test Your Hypothesis:
Modify the code or data to confirm/deny your guess.
- Observe Results:
Did the change fix the bug? If not, refine your hypothesis.
- Repeat Until Resolved.

6. Learn Common Debugging Patterns
Here are some patterns to recognize and steps to resolve them:

A. Type Mismatch
Error: 'str' object has no attribute 'path'
Solution:
Log the type of the variable.
Confirm it’s being passed/handled as the correct type (e.g., file paths vs. objects).

B. File Not Found
Error: File does not exist
Solution:
Log the file path to ensure it’s correct.
Check if the file is being saved in the expected directory.

C. KeyError or AttributeError
Error: KeyError: 'key_name'
Solution:
Log the dictionary or object before accessing the key/attribute.
Add a fallback or check for existence:
value = data.get('key_name', 'default_value')

D. Race Conditions
Error: Inconsistent results when multiple processes interact.
Solution:
Ensure that shared resources (e.g., files, databases) are handled atomically.

7. Build a Debugging Checklist
Use this checklist for every bug:

1. What is the error?
Read the error message and traceback.
2. Where is it failing?
Identify the file and line number.
3. What inputs cause the issue?
Reproduce the bug with specific data.
4. What should happen?
Clarify the expected behavior.
5. What’s actually happening?
Log variables to see their actual state.
6. What’s the smallest fix?
Apply a change and test the results.