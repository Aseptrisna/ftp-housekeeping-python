import os
import ftplib
import logging
from datetime import datetime, timedelta
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

# Fungsi untuk memindahkan file JPG dari FTP ke lokal dan menghapusnya dari FTP
def move_and_delete_jpg_files(ftp, local_dir, date_filter=None):
    try:
        files = ftp.nlst()
        logging.info(f"Menemukan {len(files)} file di FTP.")
        for file in files:
            if file.lower().endswith('.jpg'):
                if date_filter:
                    try:
                        file_date = datetime.strptime(file.split('_')[0], '%Y%m%d')
                        if date_filter(file_date):
                            local_path = os.path.join(local_dir, file)
                            with open(local_path, 'wb') as local_file:
                                ftp.retrbinary(f'RETR {file}', local_file.write)
                            ftp.delete(file)
                            logging.info(f"Berhasil memindahkan dan menghapus: {file}")
                    except Exception as e:
                        logging.error(f"Gagal memproses file {file}: {e}")
                else:
                    try:
                        local_path = os.path.join(local_dir, file)
                        with open(local_path, 'wb') as local_file:
                            ftp.retrbinary(f'RETR {file}', local_file.write)
                        ftp.delete(file)
                        logging.info(f"Berhasil memindahkan dan menghapus: {file}")
                    except Exception as e:
                        logging.error(f"Gagal memproses file {file}: {e}")
    except Exception as e:
        logging.error(f"Gagal memindahkan file: {e}")

# Fungsi untuk memindahkan file JPG dari 1 hari kemarin
def move_yesterday_files():
    try:
        yesterday = datetime.now() - timedelta(days=1)
        date_filter = lambda x: x.date() == yesterday.date()
        logging.info("Memindahkan file dari 1 hari kemarin...")
        ftp = connect_ftp()
        move_and_delete_jpg_files(ftp, LOCAL_DIR, date_filter)
        ftp.quit()
    except Exception as e:
        logging.error(f"Gagal menjalankan move_yesterday_files: {e}")

# Fungsi untuk memindahkan file JPG dari 1 bulan lalu
def move_last_month_files():
    try:
        today = datetime.now()
        last_month = today.replace(day=1) - timedelta(days=1)
        date_filter = lambda x: x.year == last_month.year and x.month == last_month.month
        logging.info("Memindahkan file dari 1 bulan lalu...")
        ftp = connect_ftp()
        move_and_delete_jpg_files(ftp, LOCAL_DIR, date_filter)
        ftp.quit()
    except Exception as e:
        logging.error(f"Gagal menjalankan move_last_month_files: {e}")

# Fungsi untuk memindahkan semua file JPG
def move_all_files():
    try:
        logging.info("Memindahkan semua file...")
        ftp = connect_ftp()
        move_and_delete_jpg_files(ftp, LOCAL_DIR)
        ftp.quit()
    except Exception as e:
        logging.error(f"Gagal menjalankan move_all_files: {e}")

# Fungsi utama untuk menjalankan script berdasarkan pilihan
def main():
    try:
        print("Pilih fungsi yang ingin dijalankan:")
        print("1. Pindahkan file JPG dari 1 hari kemarin")
        print("2. Pindahkan file JPG dari 1 bulan lalu")
        print("3. Pindahkan semua file JPG")
        choice = input("Masukkan pilihan (1/2/3): ")

        if choice == '1':
            move_yesterday_files()
        elif choice == '2':
            move_last_month_files()
        elif choice == '3':
            move_all_files()
        else:
            logging.warning("Pilihan tidak valid")
    except Exception as e:
        logging.error(f"Terjadi kesalahan dalam fungsi main: {e}")

if __name__ == "__main__":
    main()