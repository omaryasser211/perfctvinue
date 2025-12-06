import pytest
from app import DatabaseConnection, GovernorateModel, HallModel, VisitorModel, booking_queue

# Fixture لفتح الاتصال بقاعدة البيانات
@pytest.fixture
def db_connection():
    db = DatabaseConnection("halls.db")
    conn = db.connect()
    yield conn  # إعادة الاتصال للاختبارات
    conn.close()

# اختبار الاتصال بقاعدة البيانات
def test_database_connection():
    db = DatabaseConnection("halls.db")
    conn = db.connect()
    assert conn is not None  # التأكد من أن الاتصال تم بنجاح
    conn.close()

# اختبار إدخال محافظة إلى قاعدة البيانات
def test_insert_governorate(db_connection):
    model = GovernorateModel(db_connection)
    model.insert("القاهرة")
    
    # التحقق من أن البيانات تم إضافتها بنجاح
    result = model.fetch("SELECT name FROM governorates WHERE name = ?", ("القاهرة",))
    assert result == [("القاهرة",)]  # التحقق من أن اسم المحافظة موجود في القاعدة

# اختبار استرجاع قاعات بناءً على اسم المحافظة
def test_get_halls_by_governorate(db_connection):
    hall_model = HallModel(db_connection)
    hall_model.insert(1, "قاعة 1", "https://www.facebook.com/RGarabisque")  # تم تحديث الرابط هنا
    
    result = hall_model.get_by_governorate("القاهرة")
    assert len(result) > 0  # التأكد من أن هناك قاعات تم استرجاعها
    assert result[0][2] == "https://www.facebook.com/RGarabisque"  # التحقق من رابط الفيسبوك المسترجع

# اختبار إضافة زائر إلى قاعدة البيانات
def test_insert_visitor(db_connection):
    visitor_model = VisitorModel(db_connection)
    visitor_model.insert("Nermine Adly", "01280512676", 1)  # تم تعديل الاسم ليكون بالإنجليزي
    
    result = visitor_model.fetch("SELECT user_name, phone FROM visitors WHERE user_name = ?", ("Nermine Adly",))
    assert result == [("Nermine Adly", "01280512676")]  # التحقق من أن البيانات تم إدخالها بشكل صحيح

# اختبار إضافة طلب حجز إلى قائمة الانتظار
def test_booking_queue():
    booking_queue.clear()  # التأكد من أن القائمة فارغة في البداية
    booking_queue.append({
        "name": "Nermine Adly",  # تم تعديل الاسم ليكون بالإنجليزي
        "phone": "01280512676",
        "hall": "قاعة 1"
    })
    
    assert len(booking_queue) == 1  # التأكد من أن هناك طلب حجز واحد
    assert booking_queue[0]["name"] == "Nermine Adly"  # التحقق من صحة بيانات الحجز