To ensure that the compiled and zipped Lambda functions are added to your local `build` directory, the process involves mounting the local directory to the Docker container. This way, when the container creates the `.zip` files, they are directly written to the local file system.

### Here's How It Works:

1. **Volume Mounting**:
   When you run the Docker container, you mount your local `build` directory to a directory inside the Docker container. This is done using the `-v` option in the `docker run` command. The mounted directory inside the container is where the `.zip` files are written.

2. **Zipping the Lambda Functions**:
   Inside the Docker container, the `build_lambda.sh` script packages each Lambda function and outputs the `.zip` files to the `/lambda-package/build` directory, which is mounted to your local `build` directory.

3. **Local Directory Update**:
   Because the directory inside the container is mounted to your local `build` directory, the zipped Lambda functions appear in your local directory as soon as they are created by the Docker container.

### Detailed Steps:

#### 1. **Directory Structure on Your Local Machine**:
   Assume your project structure is as follows:

   ```
   /your-project
   ├── backend
   │   ├── lambdas           # Contains your Lambda functions and requirements.txt
   │   │   ├── lambda1.py
   │   │   ├── lambda2.py
   │   │   └── requirements.txt
   │   ├── build             # Empty initially, but will contain the .zip files after packaging
   ├── Dockerfile
   └── build_lambda.sh
   ```

#### 2. **Build the Docker Image**:
   Build the Docker image with the following command:
   ```bash
   docker build -t lambda-packager .
   ```

#### 3. **Run the Docker Container with Volume Mounting**:
   Run the container and mount your local `build` directory:
   ```bash
   docker run --rm -v $(pwd)/backend/build:/lambda-package/build lambda-packager
   ```

   - `$(pwd)/backend/build` refers to your local `build` directory.
   - `/lambda-package/build` is the directory inside the Docker container where the `.zip` files are created.
   - The `-v` option mounts the local `build` directory to the container's `/lambda-package/build` directory.

#### 4. **Script Execution**:
   The `build_lambda.sh` script is executed inside the container:
   - It packages each Lambda function into a `.zip` file.
   - These `.zip` files are written to `/lambda-package/build`, which is actually your local `build` directory due to the volume mount.

#### 5. **Result**:
   After the container finishes running, the `.zip` files appear in your local `build` directory:
   - `backend/build/lambda1.zip`
   - `backend/build/lambda2.zip`

### Example Command Flow:
1. **Docker Build**:
   ```bash
   docker build -t lambda-packager .
   ```

2. **Docker Run with Volume Mounting**:
   ```bash
   docker run --rm -v $(pwd)/backend/build:/lambda-package/build lambda-packager
   ```

3. **Check Output**:
   The `backend/build` directory will now contain `lambda1.zip`, `lambda2.zip`, etc., depending on the Lambda functions you had in the `lambdas` directory.

### Summary:
- **Volume Mounting**: By mounting the local `build` directory to the container, the compiled and zipped Lambda functions are directly written to your local file system.
- **Execution**: The script inside the container packages the Lambdas, and the output is synchronized with your local directory due to the mounted volume.