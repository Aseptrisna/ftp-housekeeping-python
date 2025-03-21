# FTP Housekeeping with Python 2025

Script Python untuk memindahkan file JPG dari server FTP ke direktori lokal, menghapus file dari FTP setelah dipindahkan, dan menjalankan fungsi berdasarkan waktu tertentu. Dilengkapi dengan logging untuk pelacakan aktivitas.

## Fitur
- Memindahkan file JPG dari FTP ke direktori lokal.
- Menghapus file JPG dari FTP setelah dipindahkan.
- Pilihan untuk memindahkan file:
  - Dari 1 hari kemarin (berjalan setiap jam 00:00).
  - Dari 1 bulan lalu (berjalan setiap tanggal 30).
  - Semua file sekaligus.
- Informasi akses FTP disimpan di file `.env` untuk keamanan.
- Logging aktivitas ke file `ftp_housekeeping.log` dan konsol.

## Persyaratan
- Python 3.x
- Library `python-dotenv` (untuk membaca file `.env`).

## Instalasi
1. Clone repository ini:
   ```bash
   git clone https://github.com/username/ftp-housekeeping-python.git
   cd ftp-housekeeping-python