import mysql.connector
from dotenv import load_dotenv
import os
import logging

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantısı için sınıf oluşturma
class DatabaseConnection:
    def __init__(self):
        # .env dosyasından alınan bilgiler
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "sertifikalar_db")
        self.conn = None

    def connect(self):
        """Veritabanı bağlantısını başlat."""
        if self.conn is None:
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            except mysql.connector.Error as err:
                logging.error(f"Veritabanı bağlantısı başarısız: {err}")
                raise

    def get_data(self):
        """Veritabanından veri çek."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sertifikalar ORDER BY eklenme_tarihi DESC")  # Veritabanını sorgula
        data = cursor.fetchall()  # Veriyi çek
        cursor.close()
        return data

    def close_connection(self):
        """Veritabanı bağlantısını kapat."""
        if self.conn:
            self.conn.close()
def save_to_database(data):
    """Yeni veriyi veritabanına kaydet."""
    db_connection = DatabaseConnection()
    try:
        db_connection.connect()
        cursor = db_connection.conn.cursor()

        # Sertifika tablosuna veri ekleme
        insert_query = """INSERT INTO sertifikalar (urun_tanim, kalite, firma, sertifika_no, eklenme_tarihi)
                          VALUES (%s, %s, %s, %s, %s)"""
        added_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(insert_query, (data[0], data[1], data[2], data[3], added_date))
        db_connection.conn.commit()
        cursor.close()
    except Exception as e:
        logging.error(f"Veri kaydetme başarısız: {e}")
        raise
    finally:
        db_connection.close_connection()
if st.button('Ürün Ekle'):
    if urun_tanim and kalite and firma and sertifika_no:
        # Yeni veriyi veritabanına kaydedelim
        new_data = [urun_tanim, kalite, firma, sertifika_no]  # Gerekli veriler
        save_to_database(new_data)  # Veritabanına kaydet

        # Excel dosyasına da kaydedelim
        excel_file = save_to_excel([new_data], image_folder)

        # Kullanıcıya Excel dosyasını indirme seçeneği sunalım
        with open(excel_file, "rb") as file:
            st.download_button(
                label="Excel Dosyasını İndir",
                data=file,
                file_name='Sertifika_Kayitlari.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success('Yeni ürün başarıyla eklendi ve veritabanına kaydedildi.')
    else:
        st.error("Lütfen ürün tanımı, kalite, firma ve sertifika numarası alanlarını doldurun.")
# Veritabanındaki verileri güncellemek için buton
if st.button("Veri Güncelle"):
    db_connection = DatabaseConnection()
    try:
        data = db_connection.get_data()
        db_connection.close_connection()
        
        # Veriyi Streamlit üzerinden göster
        st.write(data)  # Burada veriyi tablodan veya istediğiniz formatta gösterebilirsiniz
    except Exception as e:
        st.error(f"Veri güncelleme işlemi başarısız: {e}")
