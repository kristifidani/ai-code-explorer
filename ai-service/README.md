# 🧠 AI Service

The **AI Service** is a core component of CodeWhisperer, designed to enable semantic codebase search and intelligent Q&A over your source code. It bridges the gap between natural language queries and code understanding by leveraging embeddings, a vector database (ChromaDB), and fast search interfaces. The service allows users to ask questions about their codebase and receive context-aware answers powered by large language models (LLMs).

## Current Functionalities

- **Semantic Search:** Uses code embeddings to find relevant code snippets in the project for a given natural language question.
- **Intelligent Q&A:** Synthesizes answers to user questions by combining information from multiple relevant code snippets and LLM reasoning.
- **ChromaDB Integration:** Stores and queries code embeddings for fast and accurate retrieval.
- **Dynamic Prompting:** Adjusts the prompt sent to the LLM based on the relevance and number of code snippets found.
- **Basic Input Validation:** Ensures that user inputs (such as repository URLs) are valid.

## Recommendations & Potential Improvements

1. **Enhance Prompt Engineering (Crucial):** The prompt in `answer_question()` should be more dynamic.  Instead of just providing the context, it should:

    - **Evaluate Relevance:** Analyze the results from the ChromaDB query. If *multiple* relevant code snippets are returned, this indicates a clear project purpose is present. If only *one* snippet or none is returned, it suggests the query is vague or the codebase is less structured.
    - **Adjust Prompt Based on Relevance:**
        - **High Relevance (Multiple Snippets):** The prompt should emphasize the need to synthesize information from the multiple snippets to fully answer the question.  For example: "Based on the following code snippets, describe the purpose of this project and how it works.  Combine the information from all snippets to provide a complete answer."
        - **Low Relevance (Single/No Snippet):** The prompt should switch to a more general approach, falling back on the user's question or a broader description.  "Based on the provided code snippet, describe the purpose of this project and how it works. If the snippet does not provide enough information, please provide a general explanation of the project's goals and functionalities."  Or, something like "Please describe the project's goal and its key functionalities."

2. **Refine ChromaDB Querying:**

    - **Query Expansion:** Consider expanding the ChromaDB queries to include more synonyms or related terms to improve recall.  (This can be complex and needs careful tuning.)
    - **Relevance Scoring:**  Implement a relevance scoring mechanism in the ChromaDB query to rank the results. This could be based on the similarity between the question embedding and the code snippet embeddings.

3. **Logging and Monitoring:**  Add more logging to track the following:

    - The exact user question.
    - The embeddings used for the question and the code snippets.
    - The results of the ChromaDB queries (the ranked list of snippets).
    - The full prompt sent to the LLM.
    - The LLM's response.
    - Any errors encountered during the process.  This is *critical* for debugging and improving the system.

4. **Consider Chunking Strategy:**  The way code is split into chunks for embedding is important.  The current strategy (whole files) might be too coarse-grained. Experiment with different chunk sizes.

5. **Input Validation**: Validate the `repo_url` to ensure it's a valid Git repository URL.
