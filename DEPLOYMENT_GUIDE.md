# Deployment Guide

This guide provides step-by-step instructions for deploying the backend to Render and the frontend to Vercel.

## Prerequisites

1.  **GitHub Repository**: Your code must be in a GitHub repository. If you haven't done so, create a new repository on GitHub and push your project files.
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    git push -u origin main
    ```

2.  **Accounts**: You need an account on [Render](https://render.com/) and [Vercel](https://vercel.com/).

---

## Part 1: Deploying the Backend to Render

We will deploy the FastAPI backend as a "Web Service" on Render.

1.  **Create a New Web Service**:
    *   Log in to your Render dashboard.
    *   Click the **"New +"** button and select **"Web Service"**.

2.  **Connect Your Repository**:
    *   Connect your GitHub account and select the repository containing your project.

3.  **Configure the Service**:
    *   **Name**: Give your service a name (e.g., `pdf-extractor-backend`).
    *   **Root Directory**: Set this to `backend`. This tells Render to run the commands from within the `backend` folder.
    *   **Environment**: Select `Python 3`.
    *   **Region**: Choose a region close to you.
    *   **Branch**: Select `main`.
    *   **Build Command**: Render will automatically detect `requirements.txt` and use `pip install -r requirements.txt`. You can leave this as is.
    *   **Start Command**: Use the following command:
        ```bash
        uvicorn app.main:app --host 0.0.0.0 --port 8000
        ```
    *   **Instance Type**: The `Free` plan is sufficient for this project.

4.  **Add Environment Variables**:
    *   Go to the **"Environment"** tab for your new service.
    *   Click **"Add Environment Variable"**.
    *   Add the following variable:
        *   **Key**: `GOOGLE_API_KEY`
        *   **Value**: Paste your actual Google AI Studio API key here.

5.  **Deploy**:
    *   Click the **"Create Web Service"** button.
    *   Render will start building and deploying your application. You can monitor the progress in the "Logs" tab.
    *   Once deployed, Render will provide you with a public URL for your backend (e.g., `https://pdf-extractor-backend.onrender.com`). **Copy this URL.**

---

## Part 2: Deploying the Frontend to Vercel

Now, we'll deploy the React frontend to Vercel and connect it to our live backend.

1.  **Create a New Project**:
    *   Log in to your Vercel dashboard.
    *   Click the **"Add New..."** button and select **"Project"**.

2.  **Import Your Repository**:
    *   Connect your GitHub account and select the same repository you used for the backend.

3.  **Configure the Project**:
    *   Vercel will automatically detect that you have a Create React App project.
    *   Expand the **"Root Directory"** section and when prompted to select the directory, choose `frontend`.

4.  **Add Environment Variables**:
    *   Expand the **"Environment Variables"** section.
    *   Add the following variable:
        *   **Key**: `REACT_APP_API_URL`
        *   **Value**: Paste the URL of your deployed Render backend from Part 1 and append `/api` to it. For example: `https://pdf-extractor-backend.onrender.com/api`

5.  **Deploy**:
    *   Click the **"Deploy"** button.
    *   Vercel will build and deploy your frontend.
    *   Once finished, you will be given a public URL for your live application.

Your application is now fully deployed and live! The frontend on Vercel will make API requests to the backend running on Render.
