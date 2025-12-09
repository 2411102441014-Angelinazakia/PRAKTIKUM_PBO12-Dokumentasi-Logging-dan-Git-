import logging
from abc import ABC, abstractmethod

# --- Konfigurasi Dasar Logging ---
# 
# Konfigurasi dasar: Semua log level INFO ke atas akan ditampilkan
# Format: Waktu Level Nama Kelas/Fungsi Pesan
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s - %(name)s %(message)s'
)
# Tambahkan logger untuk kelas yang akan kita gunakan
LOGGER = logging.getLogger('Checkout')

# --- ABSTRAKSI (Kontrak untuk OCP/DIP)
# Anggap class Order sudah didefinisikan di file ini atau diimport
class Order:
    """Class representasi objek pesanan."""
    def __init__(self, customer_name, total_price):
        self.customer_name = customer_name
        self.total_price = total_price
        self.status = "pending"

class IPaymentProcessor(ABC):
    """
    Kontrak (Interface) untuk semua prosesor pembayaran.
    
    Memastikan semua implementasi konkret memiliki method 'process'.
    """
    @abstractmethod
    def process(self, order: Order) -> bool:
        """
        Memproses pembayaran untuk objek Order tertentu.
        
        Args:
            order (Order): Objek pesanan yang akan diproses.
            
        Returns:
            bool: True jika pembayaran sukses, False jika gagal.
        """
        pass

class INotificationService(ABC):
    """
    Kontrak (Interface) untuk semua layanan notifikasi.
    
    Memastikan semua implementasi konkret memiliki method 'send'.
    """
    @abstractmethod
    def send(self, order: Order):
        """
        Mengirim notifikasi terkait Order.
        
        Args:
            order (Order): Objek pesanan yang menjadi subjek notifikasi.
        """
        pass

# --- IMPLEMENTASI KONKRIT (Plug-in)
class CreditCardProcessor(IPaymentProcessor):
    def process(self, order: Order) -> bool:
        # Ganti print() dengan logging.INFO [cite: 52]
        LOGGER.info(f"Payment: Memproses Kartu Kredit untuk {order.customer_name}.")
        return True

class EmailNotifier(INotificationService):
    def send(self, order: Order):
        # Ganti print() dengan logging.INFO [cite: 52]
        LOGGER.info(f"Notif: Mengirim email konfirmasi ke {order.customer_name}.")

# --- KELAS KOORDINATOR (SRP & DIP)
class CheckoutService:
    """
    Kelas high-level untuk mengkoordinasi proses transaksi pembayaran. [cite: 36]
    
    Kelas ini memisahkan logika pembayaran dan notifikasi (memenuhi SRP). [cite: 37]
    """
    def __init__(self, payment_processor: IPaymentProcessor, notifier: INotificationService):
        """
        Menginisialisasi CheckoutService dengan dependensi yang diperlukan. [cite: 40]
        
        Args:
            payment_processor (IPaymentProcessor): Implementasi interface pembayaran. [cite: 42]
            notifier (INotificationService): Implementasi interface notifikasi. [cite: 42]
        """
        # Dependency Injection (DIP): Bergantung pada Abstraksi, bukan Konkrit
        self.payment_processor = payment_processor
        self.notifier = notifier

    def run_checkout(self, order: Order) -> bool:
        """
        Menjalankan proses checkout dan memvalidasi pembayaran. [cite: 45]
        
        Args:
            order (Order): Objek pesanan yang akan diproses. [cite: 47]
            
        Returns:
            bool: True jika checkout sukses, False jika gagal. [cite: 49]
        """
        # Logging alih-alih print() [cite: 57]
        LOGGER.info(f"Memulai checkout untuk {order.customer_name}. Total: {order.total_price}")
        
        payment_success = self.payment_processor.process(order)
        
        if payment_success:
            order.status = "paid"
            self.notifier.send(order)
            # Ganti print() dengan logging.INFO [cite: 62]
            LOGGER.info("Checkout Sukses. Status pesanan: PAID.")
            return True
        
        # Ganti print() dengan logging.ERROR/WARNING [cite: 65]
        LOGGER.error("Pembayaran gagal. Transaksi dibatalkan.")
        return False
    

# --- PROGRAM UTAMA
andi_order = Order("Andi", 500000)
email_service = EmailNotifier()

# Setup Dependencies
# 1. Inject implementasi Credit Card
cc_processor = CreditCardProcessor()
checkout_cc = CheckoutService(payment_processor=cc_processor, notifier=email_service)
print("\n--- Skenario 1: Credit Card ---")
checkout_cc.run_checkout(andi_order)

# 2. Pembuktian OCP: Menambah Metode Pembayaran QRIS (Tanpa Mengubah Checkout Service)
class QrisProcessor(IPaymentProcessor):
    def process(self, order: Order) -> bool:
        # Ganti print() dengan logging.INFO [cite: 52]
        LOGGER.info(f"Payment: Memproses QRIS untuk {order.customer_name}.")
        return True

budi_order = Order("Budi", 100000)
qris_processor = QrisProcessor()

# Inject implementasi QRIS yang baru dibuat
checkout_qris = CheckoutService(payment_processor=qris_processor, notifier=email_service)
print("\n--- Skenario 2: Pembuktian OCP (QRIS) ---")
checkout_qris.run_checkout(budi_order)