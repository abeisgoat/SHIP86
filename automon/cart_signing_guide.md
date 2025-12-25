# Ubuntu 22.04 - LattePanda IOTA

## 1. Key Generation

Install dependencies and generate an ED25519 signing key:

```bash
sudo apt install python3-pyudev
ssh-keygen -t ed25519 -f cart_signing_key
# Leave passphrase empty
```

## 2. Validator Setup

Create the trusted key directory and set permissions:

```bash
sudo mkdir -p /etc/cart_trust
sudo chmod 755 /etc/cart_trust
```

Copy your public key and set proper permissions:

```bash
sudo cp /path/to/cart.pub /etc/cart_trust/cart.pub
sudo chmod 644 /etc/cart_trust/cart.pub
sudo chown root:root /etc/cart_trust/cart.pub
```

Create the allowed signers file:

```bash
sudo sh -c 'printf "cart " > /etc/cart_trust/allowed_signers'
sudo cat /etc/cart_trust/cart.pub | sudo tee -a /etc/cart_trust/allowed_signers > /dev/null
sudo chmod 644 /etc/cart_trust/allowed_signers
sudo chown root:root /etc/cart_trust/allowed_signers
```

## 3. Signing a `cart.yaml`

Sign the file using your private key:

```bash
cat /path/to/sd/cart.yaml | ssh-keygen -Y sign -f /path/to/key/cart_signing_key -n cart > /path/to/sd/cart.yaml.sig
```

**Example:**

```bash
cat /media/laptop-dark/FD0C-1CBE/cart.yaml | ssh-keygen -Y sign -f ~/Escritorio/cart_signing/cart_signing_key -n cart > /media/laptop-dark/FD0C-1CBE/cart.yaml.sig
```

## 4. Verifying a `cart.yaml`

Verify the signature on the validator machine:

```bash
cat /path/to/sd/cart.yaml | ssh-keygen -Y verify \
  -f /etc/cart_trust/allowed_signers \
  -I cart \
  -n cart \
  -s /path/to/sd/cart.yaml.sig \
  -
```

**Example:**

```bash
cat /media/dark/FD0C-1CBE/cart.yaml | ssh-keygen -Y verify \
  -f /etc/cart_trust/allowed_signers \
  -I cart \
  -n cart \
  -s /media/dark/FD0C-1CBE/cart.yaml.sig \
  -
```

## Notes

- Replace `/path/to/sd/` with the actual SD card mount path.
- Replace `/path/to/key/` with the path to your `cart_signing_key`.
