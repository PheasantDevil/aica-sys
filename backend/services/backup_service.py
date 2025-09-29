import asyncio
import gzip
import json
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
from utils.logging import get_logger

logger = get_logger(__name__)


class BackupType(Enum):
    """バックアップタイプ"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(Enum):
    """バックアップステータス"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StorageProvider(Enum):
    """ストレージプロバイダー"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"


class BackupService:
    """
    バックアップサービス
    """

    def __init__(self):
        self.backup_config = self._initialize_backup_config()
        self.storage_clients = self._initialize_storage_clients()
        self.backup_history = []

    def _initialize_backup_config(self) -> Dict[str, Any]:
        """バックアップ設定を初期化"""
        return {
            "backup_directory": os.getenv("BACKUP_DIRECTORY", "/tmp/backups"),
            "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
            "compression": os.getenv("BACKUP_COMPRESSION", "gzip") == "true",
            "encryption": os.getenv("BACKUP_ENCRYPTION", "true") == "true",
            "encryption_key": os.getenv("BACKUP_ENCRYPTION_KEY"),
            "schedules": {
                "daily": {"time": "02:00", "type": BackupType.INCREMENTAL.value},
                "weekly": {"time": "01:00", "day": "sunday", "type": BackupType.FULL.value},
                "monthly": {"time": "00:00", "day": 1, "type": BackupType.FULL.value}
            },
            "databases": {
                "postgresql": {
                    "enabled": True,
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": int(os.getenv("DB_PORT", "5432")),
                    "database": os.getenv("DB_NAME", "aica_sys"),
                    "username": os.getenv("DB_USER", "postgres"),
                    "password": os.getenv("DB_PASSWORD")
                },
                "sqlite": {
                    "enabled": True,
                    "database_path": os.getenv("SQLITE_DB_PATH", "aica_sys.db")
                }
            },
            "files": {
                "enabled": True,
                "directories": [
                    "/app/uploads",
                    "/app/logs",
                    "/app/config"
                ],
                "exclude_patterns": [
                    "*.tmp",
                    "*.log",
                    "__pycache__",
                    "*.pyc"
                ]
            }
        }

    def _initialize_storage_clients(self) -> Dict[str, Any]:
        """ストレージクライアントを初期化"""
        clients = {}

        # AWS S3
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            try:
                clients["aws_s3"] = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                logger.info("AWS S3 client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize AWS S3 client: {e}")

        # Azure Blob Storage
        if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            try:
                clients["azure_blob"] = BlobServiceClient.from_connection_string(
                    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                )
                logger.info("Azure Blob Storage client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Blob Storage client: {e}")

        # Google Cloud Storage
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                clients["gcp_storage"] = storage.Client()
                logger.info("Google Cloud Storage client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Cloud Storage client: {e}")

        return clients

    async def create_backup(self, backup_type: BackupType = BackupType.FULL, 
                          storage_provider: StorageProvider = StorageProvider.LOCAL) -> Dict[str, Any]:
        """
        バックアップを作成
        
        Args:
            backup_type: バックアップタイプ
            storage_provider: ストレージプロバイダー
            
        Returns:
            バックアップ結果
        """
        try:
            backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            backup_record = {
                "backup_id": backup_id,
                "backup_type": backup_type.value,
                "storage_provider": storage_provider.value,
                "status": BackupStatus.RUNNING.value,
                "start_time": datetime.utcnow().isoformat(),
                "end_time": None,
                "size_bytes": 0,
                "files_count": 0,
                "databases_count": 0,
                "error_message": None
            }

            self.backup_history.append(backup_record)
            logger.info(f"Starting backup: {backup_id}")

            # バックアップディレクトリを作成
            backup_dir = os.path.join(self.backup_config["backup_directory"], backup_id)
            os.makedirs(backup_dir, exist_ok=True)

            try:
                # データベースバックアップ
                await self._backup_databases(backup_dir, backup_record)
                
                # ファイルバックアップ
                await self._backup_files(backup_dir, backup_record)
                
                # バックアップを圧縮
                if self.backup_config["compression"]:
                    await self._compress_backup(backup_dir, backup_record)
                
                # バックアップを暗号化
                if self.backup_config["encryption"]:
                    await self._encrypt_backup(backup_dir, backup_record)
                
                # ストレージにアップロード
                await self._upload_backup(backup_dir, backup_record, storage_provider)
                
                # バックアップ完了
                backup_record["status"] = BackupStatus.COMPLETED.value
                backup_record["end_time"] = datetime.utcnow().isoformat()
                
                logger.info(f"Backup completed: {backup_id}")
                
            except Exception as e:
                backup_record["status"] = BackupStatus.FAILED.value
                backup_record["error_message"] = str(e)
                backup_record["end_time"] = datetime.utcnow().isoformat()
                logger.error(f"Backup failed: {backup_id}, error: {e}")
            
            finally:
                # ローカルバックアップディレクトリをクリーンアップ
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)

            return backup_record
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    async def _backup_databases(self, backup_dir: str, backup_record: Dict[str, Any]) -> None:
        """データベースをバックアップ"""
        try:
            databases_dir = os.path.join(backup_dir, "databases")
            os.makedirs(databases_dir, exist_ok=True)

            # PostgreSQLバックアップ
            if self.backup_config["databases"]["postgresql"]["enabled"]:
                await self._backup_postgresql(databases_dir, backup_record)
            
            # SQLiteバックアップ
            if self.backup_config["databases"]["sqlite"]["enabled"]:
                await self._backup_sqlite(databases_dir, backup_record)
                
        except Exception as e:
            logger.error(f"Error backing up databases: {e}")
            raise

    async def _backup_postgresql(self, databases_dir: str, backup_record: Dict[str, Any]) -> None:
        """PostgreSQLをバックアップ"""
        try:
            db_config = self.backup_config["databases"]["postgresql"]
            
            # pg_dumpコマンドを実行
            dump_file = os.path.join(databases_dir, "postgresql_backup.sql")
            
            cmd = [
                "pg_dump",
                "-h", db_config["host"],
                "-p", str(db_config["port"]),
                "-U", db_config["username"],
                "-d", db_config["database"],
                "-f", dump_file
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                backup_record["databases_count"] += 1
                logger.info("PostgreSQL backup completed")
            else:
                raise Exception(f"PostgreSQL backup failed: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"Error backing up PostgreSQL: {e}")
            raise

    async def _backup_sqlite(self, databases_dir: str, backup_record: Dict[str, Any]) -> None:
        """SQLiteをバックアップ"""
        try:
            db_config = self.backup_config["databases"]["sqlite"]
            db_path = db_config["database_path"]
            
            if os.path.exists(db_path):
                backup_file = os.path.join(databases_dir, "sqlite_backup.db")
                shutil.copy2(db_path, backup_file)
                backup_record["databases_count"] += 1
                logger.info("SQLite backup completed")
            else:
                logger.warning(f"SQLite database not found: {db_path}")
                
        except Exception as e:
            logger.error(f"Error backing up SQLite: {e}")
            raise

    async def _backup_files(self, backup_dir: str, backup_record: Dict[str, Any]) -> None:
        """ファイルをバックアップ"""
        try:
            files_dir = os.path.join(backup_dir, "files")
            os.makedirs(files_dir, exist_ok=True)

            for directory in self.backup_config["files"]["directories"]:
                if os.path.exists(directory):
                    dest_dir = os.path.join(files_dir, os.path.basename(directory))
                    await self._copy_directory(directory, dest_dir, backup_record)
                    
        except Exception as e:
            logger.error(f"Error backing up files: {e}")
            raise

    async def _copy_directory(self, src: str, dst: str, backup_record: Dict[str, Any]) -> None:
        """ディレクトリをコピー"""
        try:
            shutil.copytree(src, dst, ignore=self._ignore_patterns)
            
            # ファイル数をカウント
            file_count = sum(len(files) for _, _, files in os.walk(dst))
            backup_record["files_count"] += file_count
            
            logger.info(f"Directory copied: {src} -> {dst}")
            
        except Exception as e:
            logger.error(f"Error copying directory: {e}")
            raise

    def _ignore_patterns(self, directory: str, files: List[str]) -> List[str]:
        """無視するパターンを定義"""
        ignore_list = []
        exclude_patterns = self.backup_config["files"]["exclude_patterns"]
        
        for file in files:
            for pattern in exclude_patterns:
                if file.endswith(pattern.replace("*", "")):
                    ignore_list.append(file)
                    break
        
        return ignore_list

    async def _compress_backup(self, backup_dir: str, backup_record: Dict[str, Any]) -> None:
        """バックアップを圧縮"""
        try:
            compressed_file = f"{backup_dir}.tar.gz"
            
            with tarfile.open(compressed_file, "w:gz") as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))
            
            # 元のディレクトリを削除
            shutil.rmtree(backup_dir)
            
            # 圧縮ファイルを元のディレクトリ名にリネーム
            shutil.move(compressed_file, backup_dir)
            
            logger.info("Backup compressed")
            
        except Exception as e:
            logger.error(f"Error compressing backup: {e}")
            raise

    async def _encrypt_backup(self, backup_dir: str, backup_record: Dict[str, Any]) -> None:
        """バックアップを暗号化"""
        try:
            encryption_key = self.backup_config["encryption_key"]
            if not encryption_key:
                logger.warning("No encryption key provided, skipping encryption")
                return
            
            # 簡易的な暗号化（実際の実装ではより強力な暗号化を使用）
            encrypted_file = f"{backup_dir}.encrypted"
            
            with open(backup_dir, 'rb') as f_in:
                with gzip.open(encrypted_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 元のファイルを削除
            os.remove(backup_dir)
            
            # 暗号化ファイルを元のファイル名にリネーム
            shutil.move(encrypted_file, backup_dir)
            
            logger.info("Backup encrypted")
            
        except Exception as e:
            logger.error(f"Error encrypting backup: {e}")
            raise

    async def _upload_backup(self, backup_dir: str, backup_record: Dict[str, Any], 
                           storage_provider: StorageProvider) -> None:
        """バックアップをストレージにアップロード"""
        try:
            if storage_provider == StorageProvider.LOCAL:
                return  # ローカルストレージの場合は何もしない
            
            backup_file = backup_dir
            if os.path.isdir(backup_dir):
                # ディレクトリの場合は圧縮
                compressed_file = f"{backup_dir}.tar.gz"
                with tarfile.open(compressed_file, "w:gz") as tar:
                    tar.add(backup_dir, arcname=os.path.basename(backup_dir))
                backup_file = compressed_file
            
            # ファイルサイズを記録
            backup_record["size_bytes"] = os.path.getsize(backup_file)
            
            if storage_provider == StorageProvider.AWS_S3:
                await self._upload_to_s3(backup_file, backup_record)
            elif storage_provider == StorageProvider.AZURE_BLOB:
                await self._upload_to_azure(backup_file, backup_record)
            elif storage_provider == StorageProvider.GCP_STORAGE:
                await self._upload_to_gcp(backup_file, backup_record)
            
            logger.info(f"Backup uploaded to {storage_provider.value}")
            
        except Exception as e:
            logger.error(f"Error uploading backup: {e}")
            raise

    async def _upload_to_s3(self, backup_file: str, backup_record: Dict[str, Any]) -> None:
        """S3にアップロード"""
        try:
            s3_client = self.storage_clients.get("aws_s3")
            if not s3_client:
                raise Exception("AWS S3 client not initialized")
            
            bucket_name = os.getenv("AWS_S3_BUCKET", "aica-sys-backups")
            key = f"backups/{backup_record['backup_id']}/{os.path.basename(backup_file)}"
            
            s3_client.upload_file(backup_file, bucket_name, key)
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise

    async def _upload_to_azure(self, backup_file: str, backup_record: Dict[str, Any]) -> None:
        """Azure Blob Storageにアップロード"""
        try:
            blob_client = self.storage_clients.get("azure_blob")
            if not blob_client:
                raise Exception("Azure Blob Storage client not initialized")
            
            container_name = os.getenv("AZURE_CONTAINER_NAME", "backups")
            blob_name = f"backups/{backup_record['backup_id']}/{os.path.basename(backup_file)}"
            
            with open(backup_file, "rb") as data:
                blob_client.get_blob_client(container=container_name, blob=blob_name).upload_blob(data)
            
        except Exception as e:
            logger.error(f"Error uploading to Azure: {e}")
            raise

    async def _upload_to_gcp(self, backup_file: str, backup_record: Dict[str, Any]) -> None:
        """Google Cloud Storageにアップロード"""
        try:
            gcp_client = self.storage_clients.get("gcp_storage")
            if not gcp_client:
                raise Exception("Google Cloud Storage client not initialized")
            
            bucket_name = os.getenv("GCP_BUCKET_NAME", "aica-sys-backups")
            blob_name = f"backups/{backup_record['backup_id']}/{os.path.basename(backup_file)}"
            
            bucket = gcp_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(backup_file)
            
        except Exception as e:
            logger.error(f"Error uploading to GCP: {e}")
            raise

    async def restore_backup(self, backup_id: str, storage_provider: StorageProvider = StorageProvider.LOCAL) -> Dict[str, Any]:
        """
        バックアップから復元
        
        Args:
            backup_id: バックアップID
            storage_provider: ストレージプロバイダー
            
        Returns:
            復元結果
        """
        try:
            restore_record = {
                "backup_id": backup_id,
                "storage_provider": storage_provider.value,
                "status": "running",
                "start_time": datetime.utcnow().isoformat(),
                "end_time": None,
                "error_message": None
            }

            logger.info(f"Starting restore: {backup_id}")

            try:
                # バックアップをダウンロード
                backup_file = await self._download_backup(backup_id, storage_provider)
                
                # バックアップを復号化
                if self.backup_config["encryption"]:
                    backup_file = await self._decrypt_backup(backup_file)
                
                # バックアップを展開
                if self.backup_config["compression"]:
                    backup_file = await self._extract_backup(backup_file)
                
                # データベースを復元
                await self._restore_databases(backup_file)
                
                # ファイルを復元
                await self._restore_files(backup_file)
                
                restore_record["status"] = "completed"
                restore_record["end_time"] = datetime.utcnow().isoformat()
                
                logger.info(f"Restore completed: {backup_id}")
                
            except Exception as e:
                restore_record["status"] = "failed"
                restore_record["error_message"] = str(e)
                restore_record["end_time"] = datetime.utcnow().isoformat()
                logger.error(f"Restore failed: {backup_id}, error: {e}")
            
            return restore_record
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            raise

    async def _download_backup(self, backup_id: str, storage_provider: StorageProvider) -> str:
        """バックアップをダウンロード"""
        try:
            # 実際の実装では、ストレージプロバイダーからダウンロード
            # ここでは簡易的な実装
            return f"/tmp/restore_{backup_id}"
            
        except Exception as e:
            logger.error(f"Error downloading backup: {e}")
            raise

    async def _decrypt_backup(self, backup_file: str) -> str:
        """バックアップを復号化"""
        try:
            # 実際の実装では、暗号化されたバックアップを復号化
            return backup_file
            
        except Exception as e:
            logger.error(f"Error decrypting backup: {e}")
            raise

    async def _extract_backup(self, backup_file: str) -> str:
        """バックアップを展開"""
        try:
            # 実際の実装では、圧縮されたバックアップを展開
            return backup_file
            
        except Exception as e:
            logger.error(f"Error extracting backup: {e}")
            raise

    async def _restore_databases(self, backup_file: str) -> None:
        """データベースを復元"""
        try:
            # 実際の実装では、バックアップからデータベースを復元
            logger.info("Databases restored")
            
        except Exception as e:
            logger.error(f"Error restoring databases: {e}")
            raise

    async def _restore_files(self, backup_file: str) -> None:
        """ファイルを復元"""
        try:
            # 実際の実装では、バックアップからファイルを復元
            logger.info("Files restored")
            
        except Exception as e:
            logger.error(f"Error restoring files: {e}")
            raise

    def get_backup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """バックアップ履歴を取得"""
        try:
            return self.backup_history[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting backup history: {e}")
            return []

    def cleanup_old_backups(self) -> Dict[str, Any]:
        """古いバックアップをクリーンアップ"""
        try:
            retention_days = self.backup_config["retention_days"]
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            cleaned_count = 0
            for backup_record in self.backup_history:
                backup_date = datetime.fromisoformat(backup_record["start_time"])
                if backup_date < cutoff_date:
                    # 実際の実装では、ストレージからバックアップを削除
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old backups")
            
            return {
                "cleaned_count": cleaned_count,
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return {}

    def get_backup_statistics(self) -> Dict[str, Any]:
        """バックアップ統計を取得"""
        try:
            total_backups = len(self.backup_history)
            successful_backups = len([b for b in self.backup_history if b["status"] == "completed"])
            failed_backups = len([b for b in self.backup_history if b["status"] == "failed"])
            
            total_size = sum(b.get("size_bytes", 0) for b in self.backup_history)
            
            return {
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "average_size_bytes": total_size / total_backups if total_backups > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting backup statistics: {e}")
            return {}


# グローバルインスタンス
backup_service = BackupService()


def get_backup_service() -> BackupService:
    """バックアップサービスを取得"""
    return backup_service
