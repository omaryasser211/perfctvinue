from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import requests
from config import AppConfig
from collections import deque  # لعمل Queue

app = Flask(__name__)
cfg = AppConfig.load()

# ============================================================
#   مبدأ OOP: Encapsulation (التغليف)
# ============================================================
# يتم تعريف فصل اتصال قاعدة البيانات لاحتواء كل التفاصيل الخاصة بالاتصال داخل فئة واحدة
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

# ============================================================
#   مبدأ OOP: Abstraction (التجريد)
# ============================================================
# هذه الفئة توفر واجهتين: تنفيذ الاستعلامات (execute) وقراءة البيانات (fetch)
class BaseModel:
    def __init__(self, conn):
        self.conn = conn
        self.c = conn.cursor()

    def execute(self, query, params=()):
        self.c.execute(query, params)
        self.conn.commit()

    def fetch(self, query, params=()):
        self.c.execute(query, params)
        return self.c.fetchall()

# ============================================================
#   مبدأ OOP: Inheritance (الوراثة)
# ============================================================
# فئة GovernorateModel: مسؤول عن العمليات المتعلقة بالمحافظات
class GovernorateModel(BaseModel):
    def insert(self, name):
        # إدخال محافظة جديدة إذا كانت غير موجودة
        self.execute("INSERT OR IGNORE INTO governorates (name) VALUES (?)", (name,))

    def get_id(self, name):
        # جلب ID للمحافظة حسب الاسم
        res = self.fetch("SELECT id FROM governorates WHERE name = ?", (name,))
        return res[0][0] if res else None

# فئة HallModel: مسؤول عن العمليات المتعلقة بالقاعات
class HallModel(BaseModel):
    def get_by_governorate(self, gov_name):
        # جلب القاعات بناءً على اسم المحافظة
        return self.fetch("""
            SELECT halls.id, halls.name, halls.facebook_url, halls.image_url
            FROM halls
            JOIN governorates ON governorates.id = halls.governorate_id
            WHERE governorates.name = ?
        """, (gov_name,))

    def insert(self, gov_id, name, url):
        # إدخال قاعة جديدة
        self.execute("""
            INSERT OR IGNORE INTO halls (governorate_id, name, facebook_url)
            VALUES (?, ?, ?)
        """, (gov_id, name, url))

# فئة VisitorModel: مسؤول عن العمليات المتعلقة بالزوار
class VisitorModel(BaseModel):
    def insert(self, name, phone, hall_id):
        # إدخال بيانات زائر جديد
        self.execute("""
            INSERT INTO visitors (user_name, phone, hall_id)
            VALUES (?, ?, ?)
        """, (name, phone, hall_id))

# ============================================================
#   Polymorphism تعدد الاشكال 
# ============================================================
# الفئة الأساسية لتهيئة قاعدة البيانات
class BaseInitializer:
    def create(self):
        return "Base initializer running..."

# الفئة المشتقة لتهيئة قاعدة البيانات باستخدام تعدد الأشكال
class DatabaseInitializer(BaseInitializer):
    def __init__(self, conn):
        self.conn = conn
        self.gov = GovernorateModel(conn)
        self.hall = HallModel(conn)

    def create(self):
        # تهيئة قاعدة البيانات، إنشاء الجداول وإدخال البيانات الأولية
        self.create_tables()
        self.insert_initial_data()
        return "Database initialized with polymorphism!"

    def create_tables(self):
        # إنشاء الجداول إذا لم تكن موجودة مسبقًا
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS governorates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            facebook_url TEXT,
            image_url TEXT,
            governorate_id INTEGER,
            FOREIGN KEY (governorate_id) REFERENCES governorates(id)
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            phone TEXT,
            hall_id INTEGER,
            FOREIGN KEY (hall_id) REFERENCES halls(id)
        );
        """)
        self.conn.commit()

    def insert_initial_data(self):
        # إدخال البيانات الأولية للمحافظات
        governorates = [
            "القاهرة", "الإسكندرية", "الجيزة", "القليوبية", "المنوفية",
            "الإسماعيلية", "الأقصر", "المنيا", "البحر الأحمر", "البحيرة"
        ]

        for g in governorates:
            self.gov.insert(g)

# ============================================================
#   تشغيل قاعدة البيانات
# ============================================================
# تهيئة قاعدة البيانات عند تشغيل التطبيق
def init_database():
    db = DatabaseConnection("halls.db")
    conn = db.connect()

    init = DatabaseInitializer(conn)
    init.create()

    conn.close()

init_database()

# ============================================================
#   Initialize page_stack as an empty list
# ============================================================
# لتخزين تاريخ الصفحات التي تم زيارتها في قائمة stack
page_stack = []

# تعريف هيكل الشجرة وحجز القاعات كـ Queue
tree = {}  # هيكل الشجرة
booking_queue = deque()  # قائمة الحجز

# تعريف قائمة الزوار لتخزين أسماء الزوار
visitors_list = []

# ============================================================
#   Routes
# ============================================================
@app.route('/')
def index():
    # إضافة الصفحة الرئيسية إلى الـ page_stack
    page_stack.append("index")  # Use append() بدلاً من push
    return render_template('index.html')


@app.route('/halls', methods=['POST'])
def show_halls():
    # إضافة صفحة القاعات إلى الـ page_stack
    page_stack.append("halls")  # Use append() بدلاً من push

    name = request.form['name']
    phone = request.form['phone']
    governorate = request.form['governorate']

    # إضافة اسم الزائر إلى قائمة الزوار
    visitors_list.append(name)  # إضافة الاسم إلى قائمة الزوار

    db = DatabaseConnection("halls.db")
    conn = db.connect()
    hall_model = HallModel(conn)

    result = hall_model.get_by_governorate(governorate)

    halls = [{"id": r[0], "name": r[1], "url": r[2], "image": r[3]} for r in result]

    conn.close()

    # إضافة القاعات إلى الشجرة حسب المحافظة
    if governorate not in tree:
        tree[governorate] = []
    tree[governorate].extend(halls)

    return render_template(
        'halls.html',
        name=name,
        phone=phone,
        governorate=governorate,
        halls=halls
    )


@app.route('/book_hall', methods=['POST'])
def book_hall():
    # إضافة صفحة الحجز إلى الـ page_stack
    page_stack.append("book_hall")  # Use append() بدلاً من push

    name = request.form['name']
    phone = request.form['phone']
    hall_id = request.form['hall_id']  # استخدام hall_id بدلاً من hall_name
    hall_name = request.form['hall_name']  # للعرض فقط

    # إضافة طلب الحجز إلى قائمة الانتظار
    booking_queue.append({
        "name": name,
        "phone": phone,
        "hall": hall_name
    })

    db = DatabaseConnection("halls.db")
    conn = db.connect()
    visitor = VisitorModel(conn)

    visitor.insert(name, phone, hall_id)  # إدخال hall_id الصحيح

    conn.close()

    return render_template("success.html", name=name, hall_name=hall_name)


@app.route('/debug')
def debug_data():
    # عرض بيانات الـ page_stack، الزوار، الحجز، والشجرة في صفحة الـ debug
    return jsonify({
        "stack": page_stack,  # عرض الـ page_stack مباشرة
        "visitors_list": visitors_list,  # إرسال قائمة الزوار
        "booking_queue": list(booking_queue),
        "tree": tree  # عرض هيكل الشجرة
    })


@app.route('/chatbot')
def chatbot():
    # إضافة صفحة chatbot إلى الـ page_stack
    page_stack.append("chatbot")  # Use append() بدلاً من push
    return render_template('chatbot.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        # الحصول على الرسائل من الـ API
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        
        # استخراج رسالة المستخدم
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
        
        # نظام الرد التلقائي (Fallback) - يعمل بدون API
        fallback_responses = {
            "مرحبا": "مرحباً بك! 👋 أنا هنا لمساعدتك في حجز القاعات. كيف يمكنني مساعدتك؟",
            "السلام": "وعليكم السلام ورحمة الله وبركاته! 🌟 كيف يمكنني مساعدتك اليوم؟",
            "قاعة": "لدينا قاعات متنوعة في جميع المحافظات! اختر المحافظة من الصفحة الرئيسية لعرض القاعات المتاحة. 🏛️",
            "حجز": "لحجز قاعة، اختر المحافظة من الصفحة الرئيسية، ثم اختر القاعة المناسبة واضغط 'ابحث الآن'. 📝",
            "سعر": "الأسعار تختلف حسب القاعة والمحافظة. يمكنك التواصل مع القاعة مباشرة عبر صفحة الفيسبوك للاستفسار عن الأسعار. 💰",
            "محافظة": "نوفر قاعات في: القاهرة، الجيزة، الإسكندرية، القليوبية، المنوفية، الإسماعيلية، الأقصر، المنيا، البحر الأحمر، والبحيرة. 🗺️",
            "كيف": "يمكنك حجز قاعة بسهولة! فقط اختر المحافظة، ثم اختر القاعة المناسبة. 😊",
            "مساعدة": "أنا هنا للمساعدة! يمكنني إرشادك لحجز القاعات، معرفة المحافظات المتاحة، أو الإجابة على أسئلتك. 🤝",
            "شكرا": "العفو! سعيد بمساعدتك. إذا كان لديك أي سؤال آخر، أنا هنا! 😊",
        }
        
        # البحث عن رد مناسب
        response_text = None
        for keyword, response in fallback_responses.items():
            if keyword in user_message:
                response_text = response
                break
        
        # رد افتراضي إذا لم يتم العثور على كلمة مفتاحية
        if not response_text:
            response_text = "شكراً لتواصلك معنا! 😊 يمكنني مساعدتك في:\n• حجز القاعات\n• معرفة المحافظات المتاحة\n• الإجابة على أسئلتك\n\nما الذي تحتاج مساعدة فيه؟"
        
        # محاولة استخدام API إذا كان متاحاً
        api_key = cfg.openrouter_api_key()
        if api_key and cfg.get("openrouter.enabled", True):
            try:
                payload = {
                    "model": cfg.get("openrouter.model", "openrouter/auto"),
                    "messages": messages
                }
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if resp.status_code == 200:
                    js = resp.json()
                    api_text = (js.get("choices") or [{}])[0].get("message", {}).get("content", "")
                    if api_text:
                        response_text = api_text
            except:
                # إذا فشل API، استخدم الرد التلقائي
                pass
        
        return jsonify({"text": response_text})
        
    except Exception as e:
        # في حالة أي خطأ، أرجع رد تلقائي
        return jsonify({
            "text": "عذراً، حدث خطأ مؤقت. 😊 يمكنك المحاولة مرة أخرى أو التواصل معنا مباشرة."
        })


if __name__ == '__main__':
    import os
    # للنشر على الإنترنت، استخدم المتغيرات البيئية
    host = os.environ.get('HOST', cfg.get('server.host', '127.0.0.1'))
    port = int(os.environ.get('PORT', cfg.get('server.port', 5000)))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true' if os.environ.get('DEBUG') else cfg.get('server.debug', True)
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
