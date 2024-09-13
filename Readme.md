# Vaato FastAPI Backend 

AI Interviewer is a project designed to automate the process of conducting interviews. It uses advanced AI algorithms to analyze responses and provide insightful feedback. The project was created to streamline the interview process and make it more efficient.

## How to Use

### Building the Docker Image

This command will build a Docker image with the tag 'ai_interviewer' using the Dockerfile in the current directory:

```bash
docker build -t ai_interviewer .
```

### Running the Docker Image

To run the Docker image, use the following command:

```bash
docker run -p 8000:8000 ai_interviewer
```

Once the application is running, you can access it by navigating to `localhost:8000` in your web browser.

## Additional Information

### Technologies Used

- Docker
- Python
- AI Algorithms

### Project Structure

The project is structured as follows:

- `Dockerfile`: This file contains the instructions for building the Docker image.
- `src/`: This directory contains the application code.
- `tests/`: This directory contains the tests for the application.

Please refer to the individual files and directories for more detailed information.


## Azure redeploy commands
```bash
az acr build --resource-group vaatobackend --registry vaato --image vaato:latest .
az webapp update --resource-group vaatobackend --name vaato
az webapp restart --name vaato --resource-group vaatobackend

```
