FROM ubuntu:latest

# Install necessary dependencies
RUN apt-get update &&  apt-get install -y postgresql-client
RUN apt-get update && apt-get install -y python3

# Copy the backup scripts
COPY backup_script.sh /
COPY convert_to_yaml.py /

# Set the executable permissions
RUN chmod +x /backup_script.sh /convert_to_yaml.py

# Set the working directory
WORKDIR /

# Define the command to run the backup script
CMD ["/backup_script.sh"]
