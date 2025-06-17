# Target Architecture and Functionality

My web app lets each user choose to sign up / log in, if they want to.
If he doesn't do any of these, then no data about his learning progress is stored and no recent files are there to be accessed.
If he does any of these, on the other hand, then there's going to be information about his progress stored and he would be able <!--
-->to access some recent files he previously uploaded, and eventually, some more information about his learning progress is going to be stored.

Each user has to have a personal concept registry, where the level of complexity for each concept, the level of <!--
-->understanding the user currently has of each concept is stored and which files each concept appears in.
Each file needs to have: 1) a list of the programming concepts the file explores, 2) a map showing how often each <!--
-->concept appears together with others in the same paragraph or code block.

Then, if not logged in, the user has to upload a university course file (a pdf, word, etc.). <!--
-->The file and its corresponding list and map are stored temporarily in memory / some short-lived database storage. <!--
-->This data is linked to a unique session ID and is discarded at the end of the current session.
If he is logged in, he can either choose a file from his previously uploaded ones or upload a new course file. <!--
-->When he uploads a new file, it is going to be stored permanently and associated with their account.

Therefore, if the file was previously uploaded, it needs to have its list and map already saved (since it was created already on <!--
-->upload in a previous session). But, if the file is newly uploaded, this list and map need to be created from scratch. <!--
-->In the scenario where the list and map need to be created from scratch, the newly uploaded file needs to be parsed and analyzed, <!--
-->so programming concepts can be extracted from it.
At some point - while adding each concept during the parsing process - each extracted concept is compared against the user's personal <!--
-->concept registry. This registry stores all the programming concepts extracted from previously uploaded files, along with indices of <!--
-->how complex each concept is and how well the user currently understands it. If a concept already exists in the user’s registry, the <!--
-->app reuses the stored information and links the concept to the new file, to avoid duplication. However, if the concept is not yet in <!--
-->the registry, the app adds it by assigning a complexity level based on the file's difficulty, the context in which the concept appears, <!--
-->and how frequently it is mentioned. The user’s understanding level for the concept is initially set to the lowest value, and the concept <!--
-->is associated with the file it came from.
When extracting programming concepts from the uploaded course file, the app builds a map showing how often each concept appears together <!--
-->with others in the same paragraph or code block. This co-occurrence map is then used to generate coding exercises that <!--
-->focus on 1 concept at a time while optionally blending in 1–2 related concepts that the user still needs to learn.

For the file uploaded/selected, the user can now choose one out of two options : 1) coding exercises; 2*) real-time vocal conversation with a bot. 

**Scenario Nr. 1 - Coding Exercises\:**

If the user chooses this option, the backend needs to generate coding exercises with the concepts from the list of the programming concepts <!--
-->explored in the file, taking into account their level of complexity and understanding so it can generate appropriate exercises. The exercises <!--
-->need to be generated one by one, and each of them will target 1 concept or more related to each other (co-occurring in the same paragraph or <!--
-->code block) concepts from list. The app sends these concepts and the current user understanding level to the model to generate a tailored <!--
-->coding exercise. When generating a coding exercise, the app sends the model a structured prompt asking for: a coding exercise statement, <!--
-->a list of concepts involved in the task, a working solution in code, a few input/output test cases. <!--
-->The model is instructed to return its response in a specific JSON format. This allows the app to generate exercises that match the user’s <!--
-->current skill level and track which concepts are practiced.
When an exercise is returned, the app extracts the targeted concepts from the model’s JSON response, or uses string matching against <!--
-->known concept names to confirm which ones appear in the exercise. While the user works on the exercise, the app can optionally prefetch <!--
-->the next one. Once the user completes the exercise, the app evaluates the solution (for correctness and code use), and updates the <!--
-->understanding level for each involved concept. This updated information is then used to determine the next concept to target.
The app runs the user’s code against the test cases provided by the model. <!--
-->If the user’s output matches the expected output for all cases, the solution is marked as correct.

**Scenario Nr. 2 - Real-Time Vocal Conversation With a Bot\:**

-