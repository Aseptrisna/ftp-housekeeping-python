import os
import ftplib
import logging
from datetime import datetime
from pymongo import MongoClient
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
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ftp_housekeeping.log'),  # Log ke file
        logging.StreamHandler()  # Log ke konsol
    ]
)

# Fungsi untuk menghubungkan ke FTP
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

# Fungsi untuk menghubungkan ke MongoDB
def connect_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        logging.info("Berhasil terhubung ke MongoDB.")
        return collection
    except Exception as e:
        logging.error(f"Gagal terhubung ke MongoDB: {e}")
        raise

# Fungsi untuk memindahkan file JPG dari FTP ke lokal dan menghapusnya dari FTP
def move_and_delete_jpg_files(ftp, local_dir, file_names):
    try:
        for file_name in file_names:
            if file_name.lower().endswith('.jpg'):
                try:
                    local_path = os.path.join(local_dir, file_name)
                    with open(local_path, 'wb') as local_file:
                        ftp.retrbinary(f'RETR {file_name}', local_file.write)
                    ftp.delete(file_name)
                    logging.info(f"Berhasil memindahkan dan menghapus: {file_name}")
                except Exception as e:
                    logging.error(f"Gagal memproses file {file_name}: {e}")
    except Exception as e:
        logging.error(f"Gagal memindahkan file: {e}")

# Fungsi untuk memindahkan semua file JPG berdasarkan data dari MongoDB
def move_all_files_from_db():
    try:
        logging.info("Memindahkan semua file berdasarkan data dari MongoDB...")
        
        # Hubungkan ke MongoDB
        collection = connect_mongodb()
        
        # Ambil semua data dari koleksi histories
        records = collection.find({})
        file_names = [record['value'] for record in records if 'value' in record]
        
        # Hubungkan ke FTP
        ftp = connect_ftp()
        
        # Pindahkan dan hapus file
        move_and_delete_jpg_files(ftp, LOCAL_DIR, file_names)
        
        # Tutup koneksi FTP
        ftp.quit()
    except Exception as e:
        logging.error(f"Gagal menjalankan move_all_files_from_db: {e}")

# Fungsi utama untuk menjalankan script
def main():
    try:
        print("Pilih fungsi yang ingin dijalankan:")
        print("1. Pindahkan semua file JPG berdasarkan data dari MongoDB")
        choice = input("Masukkan pilihan (1): ")

        if choice == '1':
            move_all_files_from_db()
        else:
            logging.warning("Pilihan tidak valid")
    except Exception as e:
        logging.error(f"Terjadi kesalahan dalam fungsi main: {e}")

if __name__ == "__main__":
    main()