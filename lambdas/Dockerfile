# Use Amazon Linux 2 as the base image to match AWS Lambda environment
FROM amazonlinux:2

# Install Python 3 and pip
RUN yum install -y python3 python3-pip zip

# Set the working directory inside the container
WORKDIR /lambda-package

# Copy the Lambda functions and their subfolders from the 'src' folder to the container
COPY src /lambda-package/src

# Create the build directory for packaging
RUN mkdir -p /lambda-package/packages

# Copy the build script into the container
COPY build-lambdas.sh /lambda-package/

# Make the script executable
RUN chmod +x /lambda-package/build-lambdas.sh

# Run the script to package the Lambdas
CMD ["/lambda-package/build-lambdas.sh"]