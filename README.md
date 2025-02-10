# Tax Calculator Project

This project is a comprehensive tax calculator that helps users estimate their income tax liability under both the old and new tax regimes in India. It takes into account various factors such as income, age, gender, city, rent, investments, and deductions to provide an accurate tax calculation.

I have created this when I was plannign my tax filing for the FY 25. Please use the generated report as an input to discuss with your Investment advisor/ CA / Tax consultant. 

## Technologies Used

*   React
*   TypeScript
*   Shadcn UI
*   Tailwind CSS
*   Flask (Backend API)

## Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone <YOUR_GIT_URL>
    ```
2.  **Navigate to the project directory:**

    ```bash
    cd calculo-simplify
    ```
3.  **Install dependencies:**

    ```bash
    npm install
    # or
    bun install
    ```
4.  **Start the development server:**

    ```bash
    npm run dev
    # or
    bun run dev
    ```

## API Information

The backend API is built using Flask and provides the following endpoint:

*   **/api/calculateTax (POST):** This endpoint accepts a JSON payload containing user-specific financial information and returns the calculated tax liability under both the old and new tax regimes.

## File Structure

*   **/api:** Contains the Flask backend API code.
    *   [app.py](cci:7://file:///c:/Users/kamal/calculo-simplify/api/app.py:0:0-0:0): Main Flask application file with tax calculation logic and API endpoint.
*   **/src:** Contains the React frontend code.
    *   **/components:** Reusable React components.
    *   **/api:** TypeScript functions for interacting with the backend API.
    *   `main.tsx`: Entry point for the React application.
*   **/public:** Contains static assets such as the favicon and logo.
