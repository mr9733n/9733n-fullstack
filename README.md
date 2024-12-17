# How to Use:

0. Send to server:
    
   ```bash
   scp get-sms-free.zip USER@HOST:~/src/get-sms-free.zip
   ```
   rmdir: removing directory, 'get-sms-free/'
   ```bash
   sudo rmdir --parents --ignore-fail-on-non-empty --verbose get-sms-free/
   unzip get-sms-free.zip
   cd get-sms-free
   chmod 755 install_server.sh
   ```

1. Run the server setup script:
   ```bash
   ./install_server.sh get-sms-free.lab
   ```

2. The certificate will be generated and saved in the `certs/` folder.

3. The Docker image will be built, and the container will be started.

4. You can manually install the certificate on the user's local machine.
   - 4.1 Download `selfsigned.crt`
   ```bash
   curl -O http://192.168.0.100:6166/selfsigned.crt
   ```

## Example of installing the certificate on a local machine:

- **Windows:**

   ```bash
   certutil -addstore -f "Root" selfsigned.crt
   ```

- **Linux (Ubuntu/Debian):**

   ```bash
   sudo cp selfsigned.crt /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   ```

- **macOS:**

   ```bash
   sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain selfsigned.crt
   ```

# Notes:

- Make sure you copy the `selfsigned.crt` file from the `certs/` folder to your local machine if the installation is being performed on a different server from where the container is running.

- After installing the certificate, ensure that a record for your domain is added to the `hosts` file on your local machine:

   ```plaintext
   127.0.0.1 get-sms-free.lab
   ```

The server should be accessible at https://get-sms-free.lab:8000.

