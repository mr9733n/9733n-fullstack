# How to Use:

1. Run the server setup script:

   ```bash
   ./install_server.sh get-sms-free.lab
   ```

2. The certificate will be generated and saved in the `certs/` folder.

3. The Docker image will be built, and the container will be started.

4. You can manually install the certificate on the user's local machine.

## Example of installing the certificate on a local machine:

- **Windows:**

   ```bash
   certutil -addstore -f "Root" certs/selfsigned.crt
   ```

- **Linux (Ubuntu/Debian):**

   ```bash
   sudo cp certs/selfsigned.crt /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   ```

- **macOS:**

   ```bash
   sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/selfsigned.crt
   ```

# Notes:

- Make sure you copy the `selfsigned.crt` file from the `certs/` folder to your local machine if the installation is being performed on a different server from where the container is running.

- After installing the certificate, ensure that a record for your domain is added to the `hosts` file on your local machine:

   ```plaintext
   127.0.0.1 get-sms-free.lab
   ```

The server should be accessible at https://get-sms-free.lab:8000.

