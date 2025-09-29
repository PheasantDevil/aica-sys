import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from utils.logging import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """
    データ暗号化・復号化サービス
    """

    def __init__(self):
        self.symmetric_key = self._get_or_create_symmetric_key()
        self.fernet = Fernet(self.symmetric_key)
        self.rsa_private_key = self._get_or_create_rsa_private_key()
        self.rsa_public_key = self.rsa_private_key.public_key()

    def _get_or_create_symmetric_key(self) -> bytes:
        """対称鍵を取得または作成"""
        key_env = os.getenv("ENCRYPTION_KEY")
        if key_env:
            try:
                return base64.b64decode(key_env)
            except Exception:
                logger.warning("Invalid encryption key in environment, generating new one")
        
        # 新しい鍵を生成
        key = Fernet.generate_key()
        logger.info("Generated new symmetric encryption key")
        return key

    def _get_or_create_rsa_private_key(self) -> rsa.RSAPrivateKey:
        """RSA秘密鍵を取得または作成"""
        key_env = os.getenv("RSA_PRIVATE_KEY")
        if key_env:
            try:
                return serialization.load_pem_private_key(
                    base64.b64decode(key_env),
                    password=None
                )
            except Exception:
                logger.warning("Invalid RSA private key in environment, generating new one")
        
        # 新しい鍵を生成
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        logger.info("Generated new RSA key pair")
        return private_key

    def encrypt_symmetric(self, data: Union[str, bytes]) -> str:
        """
        対称暗号化でデータを暗号化
        
        Args:
            data: 暗号化するデータ
            
        Returns:
            暗号化されたデータ（Base64エンコード）
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.fernet.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise

    def decrypt_symmetric(self, encrypted_data: str) -> str:
        """
        対称暗号化でデータを復号化
        
        Args:
            encrypted_data: 暗号化されたデータ（Base64エンコード）
            
        Returns:
            復号化されたデータ
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise

    def encrypt_asymmetric(self, data: Union[str, bytes]) -> str:
        """
        非対称暗号化でデータを暗号化
        
        Args:
            data: 暗号化するデータ
            
        Returns:
            暗号化されたデータ（Base64エンコード）
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.rsa_public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data asymmetrically: {e}")
            raise

    def decrypt_asymmetric(self, encrypted_data: str) -> str:
        """
        非対称暗号化でデータを復号化
        
        Args:
            encrypted_data: 暗号化されたデータ（Base64エンコード）
            
        Returns:
            復号化されたデータ
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.rsa_private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data asymmetrically: {e}")
            raise

    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        データをハッシュ化
        
        Args:
            data: ハッシュ化するデータ
            algorithm: ハッシュアルゴリズム（sha256, sha512, md5）
            
        Returns:
            ハッシュ値（16進数文字列）
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
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
            logger.error(f"Error hashing data: {e}")
            raise

    def generate_salt(self, length: int = 32) -> str:
        """
        ランダムなソルトを生成
        
        Args:
            length: ソルトの長さ（バイト）
            
        Returns:
            ソルト（Base64エンコード）
        """
        salt = secrets.token_bytes(length)
        return base64.b64encode(salt).decode('utf-8')

    def hash_with_salt(self, data: Union[str, bytes], salt: str, algorithm: str = 'sha256') -> str:
        """
        ソルト付きハッシュ化
        
        Args:
            data: ハッシュ化するデータ
            salt: ソルト（Base64エンコード）
            algorithm: ハッシュアルゴリズム
            
        Returns:
            ソルト付きハッシュ値
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            salt_bytes = base64.b64decode(salt.encode('utf-8'))
            salted_data = salt_bytes + data
            
            return self.hash_data(salted_data, algorithm)
        except Exception as e:
            logger.error(f"Error hashing data with salt: {e}")
            raise

    def encrypt_field(self, field_value: Any, field_type: str = 'text') -> Dict[str, str]:
        """
        データベースフィールドを暗号化
        
        Args:
            field_value: 暗号化する値
            field_type: フィールドタイプ（text, email, phone, ssn等）
            
        Returns:
            暗号化情報の辞書
        """
        try:
            if field_value is None:
                return {"encrypted": "", "salt": "", "algorithm": ""}
            
            # フィールドタイプに応じた暗号化方法を選択
            if field_type in ['ssn', 'credit_card', 'password']:
                # 高機密データは非対称暗号化
                encrypted_value = self.encrypt_asymmetric(str(field_value))
                algorithm = "RSA-OAEP"
            else:
                # 一般データは対称暗号化
                encrypted_value = self.encrypt_symmetric(str(field_value))
                algorithm = "AES-256"
            
            return {
                "encrypted": encrypted_value,
                "salt": self.generate_salt(),
                "algorithm": algorithm
            }
        except Exception as e:
            logger.error(f"Error encrypting field: {e}")
            raise

    def decrypt_field(self, encrypted_info: Dict[str, str]) -> str:
        """
        データベースフィールドを復号化
        
        Args:
            encrypted_info: 暗号化情報の辞書
            
        Returns:
            復号化された値
        """
        try:
            if not encrypted_info.get("encrypted"):
                return ""
            
            algorithm = encrypted_info.get("algorithm", "AES-256")
            encrypted_value = encrypted_info["encrypted"]
            
            if algorithm == "RSA-OAEP":
                return self.decrypt_asymmetric(encrypted_value)
            else:
                return self.decrypt_symmetric(encrypted_value)
        except Exception as e:
            logger.error(f"Error decrypting field: {e}")
            raise

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        ファイルを暗号化
        
        Args:
            file_path: 暗号化するファイルのパス
            output_path: 出力ファイルのパス（指定しない場合は元ファイルを上書き）
            
        Returns:
            暗号化されたファイルのパス
        """
        try:
            if not output_path:
                output_path = file_path + ".encrypted"
            
            with open(file_path, 'rb') as infile:
                data = infile.read()
            
            encrypted_data = self.fernet.encrypt(data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error encrypting file: {e}")
            raise

    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        ファイルを復号化
        
        Args:
            encrypted_file_path: 暗号化されたファイルのパス
            output_path: 出力ファイルのパス（指定しない場合は元ファイル名から.encryptedを除去）
            
        Returns:
            復号化されたファイルのパス
        """
        try:
            if not output_path:
                if encrypted_file_path.endswith('.encrypted'):
                    output_path = encrypted_file_path[:-10]
                else:
                    output_path = encrypted_file_path + ".decrypted"
            
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error decrypting file: {e}")
            raise

    def get_public_key_pem(self) -> str:
        """
        RSA公開鍵をPEM形式で取得
        
        Returns:
            PEM形式の公開鍵
        """
        try:
            pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting public key: {e}")
            raise

    def get_private_key_pem(self) -> str:
        """
        RSA秘密鍵をPEM形式で取得
        
        Returns:
            PEM形式の秘密鍵
        """
        try:
            pem = self.rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            return pem.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting private key: {e}")
            raise

    def rotate_keys(self) -> Dict[str, str]:
        """
        暗号化鍵をローテーション
        
        Returns:
            新しい鍵の情報
        """
        try:
            # 新しい対称鍵を生成
            old_symmetric_key = self.symmetric_key
            self.symmetric_key = Fernet.generate_key()
            self.fernet = Fernet(self.symmetric_key)
            
            # 新しいRSA鍵ペアを生成
            old_private_key = self.rsa_private_key
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.rsa_public_key = self.rsa_private_key.public_key()
            
            logger.info("Encryption keys rotated successfully")
            
            return {
                "symmetric_key": base64.b64encode(self.symmetric_key).decode('utf-8'),
                "public_key": self.get_public_key_pem(),
                "private_key": self.get_private_key_pem(),
                "rotation_time": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error rotating keys: {e}")
            raise

    def verify_integrity(self, data: Union[str, bytes], hash_value: str, algorithm: str = 'sha256') -> bool:
        """
        データの整合性を検証
        
        Args:
            data: 検証するデータ
            hash_value: 期待されるハッシュ値
            algorithm: ハッシュアルゴリズム
            
        Returns:
            整合性が保たれているかどうか
        """
        try:
            calculated_hash = self.hash_data(data, algorithm)
            return calculated_hash == hash_value
        except Exception as e:
            logger.error(f"Error verifying integrity: {e}")
            return False


# グローバルインスタンス
encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    """暗号化サービスを取得"""
    return encryption_service
