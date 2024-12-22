# How to Use:

0. Send to server:
    
   ```bash
   scp 9733n-fullstack.zip USER@HOST:~/src/9733n-fullstack.zip
   ```
   
   ```bash
   chmod 755 cleanup_docker.sh
   chmod 755 unpack.sh
   chmod 755 clean.sh
   chmod 755 install_server.sh
   ```

1. Run the server setup script:
   ```bash
   ./install_server.sh 
   ```

2. The certificate will be generated and saved in the `certs/` folder.

3. The Docker image will be built, and the container will be started.

4. You can manually install the certificate on the user's local machine.
   - 4.1 Download `selfsigned.crt`
   ```bash
   curl -O http://192.168.0.100:6266/selfsigned.crt
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
   127.0.0.1 9733n.lab
   ```

docker run -it --rm 9733n-fullstack-backend sh
docker run -it --rm 9733n-fullstack-frontend sh


