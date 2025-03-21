import os
import ftplib
import logging
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

# Konfigurasi FTP dari .env
FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
FTP_PORT = int(os.getenv('FTP_PORT'))
FTP_FOLDER = os.getenv('FTP_FOLDER')
LOCAL_DIR = os.getenv('LOCAL_DIR')

# Konfigurasi MongoDB
MONGO_URI = "mongodb://hidroponik-sg:kcm9wb25pay1zZw@nosql.smartsystem.id:27017/hidroponik-sg"
DB_NAME = "hidroponik-sg"
COLLECTION_NAME = "histories"

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ftp_housekeeping.log'),
        logging.StreamHandler()
    ]
)

# Koneksi ke MongoDB
def connect_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        logging.info("Berhasil terhubung ke MongoDB.")
        return db[COLLECTION_NAME]
    except Exception as e:
        logging.error(f"Gagal terhubung ke MongoDB: {e}")
        raise

# Koneksi ke FTP
def connect_ftp():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_FOLDER)
        logging.info("Berhasil terhubung ke FTP.")
        return ftp
    except Exception as e:
        logging.error(f"Gagal terhubung ke FTP: {e}")
        raise

# Fungsi untuk memindahkan file berdasarkan data dari MongoDB
def move_files_from_database():
    try:
        # Koneksi ke MongoDB
        logging.info("Menghubungkan ke MongoDB...")
        collection = connect_mongodb()
        logging.info("Berhasil terhubung ke MongoDB.")

        # Koneksi ke FTP
        logging.info("Menghubungkan ke FTP...")
        ftp = connect_ftp()
        logging.info("Berhasil terhubung ke FTP.")

        # Ambil semua dokumen dengan process = False
        logging.info("Mengambil dokumen dari MongoDB")
        files_to_process = list(collection.find())
        total_files = len(files_to_process)
        logging.info(f"Menemukan {total_files} file yang belum diproses.")

        if total_files == 0:
            logging.info("Tidak ada file untuk diproses. Proses selesai.")
            return

        # Iterasi setiap dokumen
        for idx, document in enumerate(files_to_process, start=1):
            file_name = document['value']
            local_path = os.path.join(LOCAL_DIR, file_name)

            logging.info(f"[{idx}/{total_files}] Memproses file: {file_name}")
            try:
                # Unduh file dari FTP
                logging.info(f"Mengunduh file {file_name} dari FTP...")
                with open(local_path, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {file_name}', local_file.write)
                logging.info(f"File {file_name} berhasil diunduh ke {local_path}.")

                # Hapus file dari FTP
                logging.info(f"Menghapus file {file_name} dari FTP...")
                ftp.delete(file_name)
                logging.info(f"File {file_name} berhasil dihapus dari FTP.")

                # Perbarui status dokumen di MongoDB
                # logging.info(f"Memperbarui status dokumen di MongoDB untuk file {file_name}...")
                # collection.update_one(
                #     {"_id": document["_id"]},
                #     {"$set": {"process": True, "updatedAt": datetime.utcnow()}}
                # )
                # logging.info(f"Status berhasil diperbarui untuk file: {file_name}")
            except Exception as e:
                logging.error(f"Gagal memproses file {file_name}: {e}")

        ftp.quit()
        logging.info("Koneksi ke FTP ditutup. Proses selesai.")
    except Exception as e:
        logging.error(f"Gagal menjalankan move_files_from_database: {e}")


# Fungsi utama untuk menjalankan skrip
def main():
    try:
        move_files_from_database()
    except Exception as e:
        logging.error(f"Terjadi kesalahan dalam fungsi main: {e}")

if __name__ == "__main__":
    main()
