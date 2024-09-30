
# Project Overview

This project is a cloud-based application consisting of a React frontend, AWS Lambda-based backend, and Terraform-managed infrastructure. It also includes several scripts to facilitate various operations such as deployment, cloud resource management, and packaging.

**Note:** This project is a work in progress, and some components may still be under development.

## Project Structure

- **lambdas/**: Contains the AWS Lambda functions and related configuration.
  - `build-lambdas.sh`: Script to package the Lambda functions.
  - `Dockerfile`: Docker configuration for running Lambda functions locally.
  - `Docker-README.md`: Documentation for the Docker setup related to Lambdas.
  - `src/`: Contains the source code for AWS Lambda functions.
  
- **infra/**: Contains the Terraform configuration files for infrastructure setup.
  - `outputs.tf`, `global-variables.tf`, `locals.tf`, `main.tf`: Core Terraform files managing the cloud resources.
  - `modules/`: Likely contains reusable Terraform modules for provisioning infrastructure resources.

- **react-app/**: The front-end part of the project, built using React.
  - `README.md`: Documentation specific to the React app.
  - `package.json`: Lists the dependencies and npm scripts.
  - `.env`: Environment variables required for the React app.
  - `src/`: The source code for the front-end components.

- **docs/**: Documentation resources for the project.
  - `enhancement-ideas`: A file containing ideas for future enhancements.
  - `all-potential-use-cases.md`: A detailed markdown file describing various use cases of the project.
  - `OpenAI-Prompt.md`: Documentation related to the usage of OpenAI in the project.

- **scripts/**: A collection of utility scripts for deployment, testing, and managing cloud resources.
  - Notable scripts include:
    - `deploy-app.sh`: Script for deploying the application.
    - `build-react-app.sh`: Script for building the React app.

- **containers/**: Container configurations.
  - `ollama-metadata-service`: A Docker container likely responsible for handling metadata services.

## Getting Started

To get started with the project, follow the steps below:

1. **Install Dependencies**: Navigate to the `react-app` directory and install the required npm dependencies:
   ```bash
   cd react-app
   npm install
   ```

2. **Set Up Infrastructure**: Navigate to the `infra` directory and run the Terraform commands to provision the necessary cloud infrastructure:
   ```bash
   cd infra
   terraform init
   terraform apply
   ```

3. **Deploy Backend (Lambdas)**: Package and deploy the Lambda functions:
   ```bash
   cd lambdas
   ./build-lambdas.sh
   ```

4. **Run the React App**: Once the infrastructure is set up and backend is deployed, you can run the React app locally:
   ```bash
   cd react-app
   npm start
   ```

## Contributing

Contributions are welcome! Please refer to the `docs/enhancement-ideas` file for potential areas of improvement.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
