# Technology Stack: Revly

This document outlines the core technologies and libraries utilized in the MathReferee project.

### Programming Language
*   **Python 3.11+**: The primary programming language, chosen for its extensive libraries in AI/ML, data science, and web development, as well as its readability and community support.

### Web Frameworks
*   **FastAPI**: Used for building the high-performance API backend. FastAPI is selected for its speed, automatic interactive API documentation (Swagger UI/ReDoc), and strong type hints support, which aligns with robust development practices.
*   **Next.js (React)**: Utilized for building the interactive frontend user interface. Next.js provides a powerful React framework for production-grade applications, offering server-side rendering, static site generation, and an excellent developer experience for creating dynamic user interfaces.
*   **Material-UI (MUI)**: The primary UI component library, providing a comprehensive suite of pre-built React components that implement Google's Material Design. Used to ensure a consistent, modern, and accessible user interface.

### AI/ML & Scientific Libraries
*   **Gemini Pro**: The core AI model powering the autonomous referee system, responsible for multi-step reasoning, critique, and synthesis of paper reviews.
*   **SymPy**: A Python library for symbolic mathematics. It is used for performing symbolic computation and algebraic manipulations, essential for deep mathematical analysis within the AI referee agent.
*   **SciPy/statsmodels**: These libraries provide advanced scientific computing capabilities, including statistical analysis tools, which are critical for evaluating statistical methodologies and claims in academic papers.

### Data Validation & Modeling
*   **Pydantic**: Utilized for data validation and settings management. Pydantic ensures that data structures are type-safe and validated at runtime, enhancing the reliability and maintainability of the application's data models.

### External Integrations
*   **arXiv**: Integrated for programmatic access and retrieval of pre-print academic papers, forming a primary source of documents for the AI referee system.
*   **Semantic Scholar**: Used for literature search, providing a comprehensive database of academic publications to enable the AI to contextualize and cross-reference findings.

### Testing
*   **Jest & React Testing Library**: Employed for unit and integration testing of the frontend application. Jest serves as the test runner, while React Testing Library provides utilities to test React components in a way that resembles how they are used by end users.