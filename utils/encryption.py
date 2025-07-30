import os
import base64
import hashlib
import secrets
from typing import Union, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import pandas as pd
import json

class DataEncryption:
    """Data encryption utility for securing sensitive data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encoding = 'utf-8'
        
        # Create encryption keys directory
        os.makedirs('config/keys', exist_ok=True)
    
    def generate_key(self) -> bytes:
        """
        Generate a new Fernet encryption key
        
        Returns:
            Encryption key as bytes
        """
        return Fernet.generate_key()
    
    def save_key(self, key: bytes, key_name: str = "default") -> str:
        """
        Save encryption key to file
        
        Args:
            key: Encryption key
            key_name: Name for the key file
        
        Returns:
            Path to saved key file
        """
        try:
            key_path = f"config/keys/{key_name}.key"
            
            with open(key_path, 'wb') as f:
                f.write(key)
            
            self.logger.info(f"Encryption key saved to {key_path}")
            return key_path
            
        except Exception as e:
            self.logger.error(f"Error saving encryption key: {str(e)}")
            raise
    
    def load_key(self, key_name: str = "default") -> Optional[bytes]:
        """
        Load encryption key from file
        
        Args:
            key_name: Name of the key file
        
        Returns:
            Encryption key as bytes or None if not found
        """
        try:
            key_path = f"config/keys/{key_name}.key"
            
            if not os.path.exists(key_path):
                self.logger.warning(f"Key file not found: {key_path}")
                return None
            
            with open(key_path, 'rb') as f:
                key = f.read()
            
            self.logger.info(f"Encryption key loaded from {key_path}")
            return key
            
        except Exception as e:
            self.logger.error(f"Error loading encryption key: {str(e)}")
            return None
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password string
            salt: Salt bytes (generated if None)
        
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key, salt
    
    def encrypt_data(self, data: Union[str, bytes, dict], key: bytes = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data using Fernet encryption
        
        Args:
            data: Data to encrypt (string, bytes, or dict)
            key: Encryption key (generated if None)
        
        Returns:
            Tuple of (encrypted_data, key)
        """
        try:
            if key is None:
                key = self.generate_key()
            
            cipher = Fernet(key)
            
            # Convert data to bytes
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode(self.encoding)
            elif isinstance(data, str):
                data_bytes = data.encode(self.encoding)
            else:
                data_bytes = data
            
            encrypted_data = cipher.encrypt(data_bytes)
            
            self.logger.info("Data encrypted successfully")
            return encrypted_data, key
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data using Fernet encryption
        
        Args:
            encrypted_data: Encrypted data bytes
            key: Encryption key
        
        Returns:
            Decrypted data as bytes
        """
        try:
            cipher = Fernet(key)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            self.logger.info("Data decrypted successfully")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    def encrypt_dataframe(self, df: pd.DataFrame, columns: list = None, 
                         key: bytes = None) -> Tuple[pd.DataFrame, bytes]:
        """
        Encrypt specified columns in a DataFrame
        
        Args:
            df: Input DataFrame
            columns: List of columns to encrypt (all if None)
            key: Encryption key (generated if None)
        
        Returns:
            Tuple of (encrypted_dataframe, key)
        """
        try:
            if key is None:
                key = self.generate_key()
            
            cipher = Fernet(key)
            encrypted_df = df.copy()
            
            if columns is None:
                columns = df.columns.tolist()
            
            for col in columns:
                if col in df.columns:
                    # Encrypt each value in the column
                    encrypted_values = []
                    for value in df[col]:
                        if pd.isna(value):
                            encrypted_values.append(value)  # Keep NaN as is
                        else:
                            value_bytes = str(value).encode(self.encoding)
                            encrypted_value = cipher.encrypt(value_bytes)
                            # Convert to base64 string for storage
                            encrypted_values.append(base64.b64encode(encrypted_value).decode())
                    
                    encrypted_df[col] = encrypted_values
            
            self.logger.info(f"Encrypted {len(columns)} columns in DataFrame")
            return encrypted_df, key
            
        except Exception as e:
            self.logger.error(f"Error encrypting DataFrame: {str(e)}")
            raise
    
    def decrypt_dataframe(self, encrypted_df: pd.DataFrame, columns: list = None, 
                         key: bytes = None) -> pd.DataFrame:
        """
        Decrypt specified columns in a DataFrame
        
        Args:
            encrypted_df: Encrypted DataFrame
            columns: List of columns to decrypt (all if None)
            key: Decryption key
        
        Returns:
            Decrypted DataFrame
        """
        try:
            if key is None:
                raise ValueError("Decryption key is required")
            
            cipher = Fernet(key)
            decrypted_df = encrypted_df.copy()
            
            if columns is None:
                columns = encrypted_df.columns.tolist()
            
            for col in columns:
                if col in encrypted_df.columns:
                    # Decrypt each value in the column
                    decrypted_values = []
                    for value in encrypted_df[col]:
                        if pd.isna(value):
                            decrypted_values.append(value)  # Keep NaN as is
                        else:
                            try:
                                # Decode from base64 and decrypt
                                encrypted_bytes = base64.b64decode(value.encode())
                                decrypted_bytes = cipher.decrypt(encrypted_bytes)
                                decrypted_value = decrypted_bytes.decode(self.encoding)
                                decrypted_values.append(decrypted_value)
                            except Exception:
                                # If decryption fails, keep original value
                                decrypted_values.append(value)
                    
                    decrypted_df[col] = decrypted_values
            
            self.logger.info(f"Decrypted {len(columns)} columns in DataFrame")
            return decrypted_df
            
        except Exception as e:
            self.logger.error(f"Error decrypting DataFrame: {str(e)}")
            raise
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Create hash of data for integrity verification
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, md5)
        
        Returns:
            Hex digest of hash
        """
        try:
            if isinstance(data, str):
                data = data.encode(self.encoding)
            
            if algorithm == 'sha256':
                hash_obj = hashlib.sha256(data)
            elif algorithm == 'sha512':
                hash_obj = hashlib.sha512(data)
            elif algorithm == 'md5':
                hash_obj = hashlib.md5(data)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error hashing data: {str(e)}")
            raise
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA public/private key pair
        
        Args:
            key_size: Size of RSA key in bits
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys to PEM format
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            self.logger.info(f"Generated RSA key pair with {key_size} bits")
            return private_pem, public_pem
            
        except Exception as e:
            self.logger.error(f"Error generating RSA key pair: {str(e)}")
            raise
    
    def encrypt_with_rsa(self, data: bytes, public_key_pem: bytes) -> bytes:
        """
        Encrypt data using RSA public key
        
        Args:
            data: Data to encrypt
            public_key_pem: RSA public key in PEM format
        
        Returns:
            Encrypted data
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting with RSA: {str(e)}")
            raise
    
    def decrypt_with_rsa(self, encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """
        Decrypt data using RSA private key
        
        Args:
            encrypted_data: Encrypted data
            private_key_pem: RSA private key in PEM format
        
        Returns:
            Decrypted data
        """
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )
            
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error decrypting with RSA: {str(e)}")
            raise
    
    def secure_delete(self, data: Union[str, bytes, bytearray]) -> None:
        """
        Securely delete sensitive data from memory
        
        Args:
            data: Data to securely delete
        """
        try:
            if isinstance(data, str):
                # Convert to bytearray for overwriting
                data_bytes = bytearray(data.encode(self.encoding))
            elif isinstance(data, bytes):
                data_bytes = bytearray(data)
            elif isinstance(data, bytearray):
                data_bytes = data
            else:
                return
            
            # Overwrite with random data
            for i in range(len(data_bytes)):
                data_bytes[i] = secrets.randbits(8)
            
            # Clear the bytearray
            data_bytes.clear()
            
        except Exception as e:
            self.logger.error(f"Error in secure delete: {str(e)}")
    
    def create_encrypted_backup(self, data: pd.DataFrame, backup_name: str, 
                               password: str = None) -> str:
        """
        Create encrypted backup of DataFrame
        
        Args:
            data: DataFrame to backup
            backup_name: Name for backup file
            password: Password for encryption (generated if None)
        
        Returns:
            Path to encrypted backup file
        """
        try:
            if password is None:
                password = secrets.token_urlsafe(32)
            
            # Derive key from password
            key, salt = self.derive_key_from_password(password)
            
            # Convert DataFrame to JSON
            data_json = data.to_json(orient='records')
            
            # Encrypt data
            encrypted_data, _ = self.encrypt_data(data_json, key)
            
            # Save encrypted backup
            backup_path = f"exports/backups/{backup_name}_encrypted.backup"
            
            backup_info = {
                'salt': base64.b64encode(salt).decode(),
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'created_at': pd.Timestamp.now().isoformat(),
                'shape': data.shape
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_info, f)
            
            self.logger.info(f"Encrypted backup created: {backup_path}")
            
            # Save password separately (in production, this should be handled securely)
            password_file = f"config/keys/{backup_name}_password.txt"
            with open(password_file, 'w') as f:
                f.write(password)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error creating encrypted backup: {str(e)}")
            raise
    
    def restore_encrypted_backup(self, backup_path: str, password: str) -> pd.DataFrame:
        """
        Restore DataFrame from encrypted backup
        
        Args:
            backup_path: Path to encrypted backup file
            password: Decryption password
        
        Returns:
            Restored DataFrame
        """
        try:
            with open(backup_path, 'r') as f:
                backup_info = json.load(f)
            
            # Extract components
            salt = base64.b64decode(backup_info['salt'])
            encrypted_data = base64.b64decode(backup_info['encrypted_data'])
            
            # Derive key from password
            key, _ = self.derive_key_from_password(password, salt)
            
            # Decrypt data
            decrypted_data = self.decrypt_data(encrypted_data, key)
            data_json = decrypted_data.decode(self.encoding)
            
            # Restore DataFrame
            data = pd.read_json(data_json, orient='records')
            
            self.logger.info(f"Encrypted backup restored from: {backup_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error restoring encrypted backup: {str(e)}")
            raise
