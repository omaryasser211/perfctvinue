import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import sqlite3 

class PerfectVenueApp:
    # --- إعداد قاعدة البيانات والاتصال ---
    def __init__(self, master):
        self.master = master
        master.title("Perfect Venue - نظام إدارة القاعات")
        master.geometry("1000x700")
        
        # تهيئة لدعم اللغة العربية (اتجاه من اليمين لليسار)
        master.option_add('*Font', 'Tahoma 10')
        master.tk.call('encoding', 'system', 'utf-8') 
        
        self.current_selected_iid = None 
        
        # 1. تهيئة قاعدة البيانات والاتصال بها
        self.db_name = 'halls.db'
        self.conn = None
        self.cursor = None
        self.connect_db()

        # قائمة المحافظات يتم ملؤها من قاعدة البيانات
        self.governorates_list = self.fetch_governorates() 
        self.governorate_map = {name: id for id, name in self.governorates_list}
        # self.governorate_reverse_map = {id: name for id, name in self.governorates_list} # قد لا تحتاجها حالياً

        self.create_widgets()
        self.load_venues_data() 

    def connect_db(self):
        """الاتصال بقاعدة البيانات والتأكد من وجود الجداول والأعمدة اللازمة."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            # التأكد من وجود جدول halls (بما في ذلك عمود الملاحظات)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS halls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    facebook_url TEXT,
                    image_url TEXT,
                    governorate_id INTEGER,
                    notes TEXT,  
                    FOREIGN KEY (governorate_id) REFERENCES governorates(id)
                )
            ''')
            
            # إضافة عمود 'notes' في حالة عدم وجوده (للتوافق مع ملف halls.db قديم)
            try:
                self.cursor.execute("SELECT notes FROM halls LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE halls ADD COLUMN notes TEXT")
                self.conn.commit()
                
            self.conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("خطأ في قاعدة البيانات", f"حدث خطأ في الاتصال: {e}")
            self.master.destroy() 
            
    def __del__(self):
        """إغلاق الاتصال عند تدمير الكائن."""
        if self.conn:
            self.conn.close()

    def fetch_governorates(self):
        """جلب قائمة المحافظات من قاعدة البيانات."""
        self.cursor.execute("SELECT id, name FROM governorates ORDER BY name ASC")
        return self.cursor.fetchall()
        
    def fetch_halls(self):
        """جلب بيانات القاعات مع اسم المحافظة والملاحظات."""
        self.cursor.execute('''
            SELECT 
                h.id, 
                h.name, 
                g.name, 
                h.facebook_url,
                h.notes
            FROM halls h
            LEFT JOIN governorates g ON h.governorate_id = g.id
            ORDER BY h.name
        ''')
        return self.cursor.fetchall()

    # --- بناء الواجهة (Widgets) ---
    def create_widgets(self):
        # --- الإطار العلوي ---
        header_frame = tk.Frame(self.master, bg='#E0F2F1', padx=10, pady=10)
        header_frame.pack(fill='x')
        title_label = tk.Label(header_frame, text="✨ Perfect Venue - إدارة القاعات ✨", font=('Arial', 18, 'bold'), fg='#004D40', bg='#E0F2F1')
        title_label.pack(side='right')
        visit_btn = tk.Button(header_frame, text="🔗 زيارة موقعنا", command=self.visit_website, bg='#FFEB3B', fg='#000000', font=('Arial', 10, 'bold'), relief=tk.FLAT)
        visit_btn.pack(side='left', padx=10)

        # --- الإطار الرئيسي ---
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # إطار النموذج (اليمين)
        self.form_frame = tk.LabelFrame(main_frame, text="إضافة قاعة جديدة", font=('Arial', 12, 'bold'), bd=2, padx=10, pady=10, fg='#004D40')
        self.form_frame.pack(side='right', fill='y', padx=10, pady=0)
        
        # إطار الجدول (اليسار)
        self.table_frame = tk.Frame(main_frame)
        self.table_frame.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        
        # --- عناصر نموذج الإدخال ---
        self.entry_vars = {}
        entry_fields = [
            ("اسم القاعة:", "venue_name"), 
            ("رابط الفيسبوك:", "venue_link")
        ]
        
        current_row = 0
        for i, (label_text, var_name) in enumerate(entry_fields):
            label = tk.Label(self.form_frame, text=label_text, anchor='e')
            label.grid(row=i, column=1, sticky='e', pady=5, padx=5)
            var = tk.StringVar()
            entry = tk.Entry(self.form_frame, textvariable=var, width=30, justify='right')
            entry.grid(row=i, column=0, sticky='ew', pady=5, padx=5)
            self.entry_vars[var_name] = var
            current_row = i
        
        # حقل المحافظة (ComBoBox)
        current_row += 1
        governorate_label = tk.Label(self.form_frame, text="المحافظة:", anchor='e')
        governorate_label.grid(row=current_row, column=1, sticky='e', pady=5, padx=5)
        self.entry_vars['city'] = tk.StringVar()
        self.city_combo = ttk.Combobox(self.form_frame, 
                                       textvariable=self.entry_vars['city'],
                                       values=list(self.governorate_map.keys()),
                                       width=27,
                                       justify='right',
                                       state='readonly') # لمنع إدخال نصوص غير موجودة
        self.city_combo.grid(row=current_row, column=0, sticky='ew', pady=5, padx=5)
        
        # حقل الملاحظات (Text Widget)
        current_row += 1
        notes_label = tk.Label(self.form_frame, text="الملاحظات:", anchor='e')
        notes_label.grid(row=current_row, column=1, sticky='ne', pady=5, padx=5)
        self.notes_text = tk.Text(self.form_frame, height=5, width=30, wrap=tk.WORD, bd=1, relief=tk.SUNKEN)
        self.notes_text.grid(row=current_row, column=0, sticky='ew', pady=5, padx=5)
        self.entry_vars['notes_text_widget'] = self.notes_text 

        # أزرار الإجراءات في النموذج (حفظ ومسح)
        current_row += 1
        form_btn_frame = tk.Frame(self.form_frame, pady=10)
        form_btn_frame.grid(row=current_row, column=0, columnspan=2, pady=10)
        self.save_btn = tk.Button(form_btn_frame, text="💾 حفظ البيانات", command=self.save_or_update_venue, bg='#00796B', fg='white', font=('Arial', 10, 'bold'))
        self.save_btn.pack(side='right', padx=5)
        clear_btn = tk.Button(form_btn_frame, text="❌ مسح الحقول", command=self.clear_form, bg='#BDBDBD', fg='black', font=('Arial', 10))
        clear_btn.pack(side='left', padx=5)

        # --- الجدول (Treeview) ---
        table_toolbar = tk.Frame(self.table_frame, pady=5)
        table_toolbar.pack(fill='x')
        add_btn = tk.Button(table_toolbar, text="➕ إضافة جديدة", command=self.clear_form, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        add_btn.pack(side='right', padx=5)
        edit_btn = tk.Button(table_toolbar, text="✏️ تعديل محدد", command=self.edit_venue, bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        edit_btn.pack(side='right', padx=5)
        delete_btn = tk.Button(table_toolbar, text="🗑️ حذف محدد", command=self.delete_venue, bg='#F44336', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.pack(side='right', padx=5)
        
        # تعريف الأعمدة
        columns = ('id', 'name', 'city', 'link', 'notes') 
        self.venue_table = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        self.venue_table.heading('id', text='ID', anchor='center')
        self.venue_table.heading('name', text='اسم القاعة', anchor='e')
        self.venue_table.heading('city', text='المحافظة', anchor='e')
        self.venue_table.heading('link', text='رابط الفيسبوك', anchor='e')
        self.venue_table.heading('notes', text='ملاحظات', anchor='e')
        self.venue_table.column('id', anchor='center', width=50, stretch=tk.NO)
        self.venue_table.column('name', anchor='e', width=150)
        self.venue_table.column('city', anchor='e', width=100)
        self.venue_table.column('link', anchor='e', width=150) 
        self.venue_table.column('notes', anchor='e', width=250) 
        
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.venue_table.yview)
        self.venue_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y') 
        self.venue_table.pack(fill='both', expand=True)
        
        # ربط الأحداث
        self.venue_table.bind('<Double-1>', self.on_double_click_edit)
        self.venue_table.bind('<ButtonRelease-1>', self.on_click_open_link)
        
    def load_venues_data(self):
        """تحميل بيانات القاعات من قاعدة البيانات وعرضها في الجدول."""
        for item in self.venue_table.get_children():
            self.venue_table.delete(item)
            
        # جلب البيانات (ID, Name, Governorate Name, Link, Notes)
        venues = self.fetch_halls()
        
        # إدراج البيانات
        for venue_id, name, governorate_name, link, notes in venues:
            self.venue_table.insert('', tk.END, iid=venue_id, values=(venue_id, name, governorate_name or "", link or "", notes or ""))


    # --- وظائف الإدارة (CRUD Functions) ---
    
    def save_or_update_venue(self):
        """حفظ قاعة جديدة أو تحديث قاعة موجودة في قاعدة البيانات."""
        name = self.entry_vars['venue_name'].get().strip()
        city_name = self.entry_vars['city'].get().strip()
        venue_link = self.entry_vars['venue_link'].get().strip()
        notes = self.notes_text.get('1.0', tk.END).strip()

        if not name or not city_name:
            messagebox.showwarning("خطأ في البيانات", "الرجاء إدخال اسم القاعة والمحافظة على الأقل.")
            return
        
        governorate_id = self.governorate_map.get(city_name)
        if governorate_id is None:
             messagebox.showwarning("خطأ في المحافظة", f"المحافظة '{city_name}' غير موجودة في القائمة.")
             return
             
        if self.current_selected_iid:
            # تحديث
            venue_id = self.current_selected_iid
            try:
                self.cursor.execute('''
                    UPDATE halls SET name=?, facebook_url=?, governorate_id=?, notes=?
                    WHERE id=?
                ''', (name, venue_link, governorate_id, notes, venue_id))
                self.conn.commit()
                messagebox.showinfo("نجاح", f"تم تعديل بيانات القاعة: {name} بنجاح.")
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"فشل التحديث: {e}")
        else:
            # إضافة
            try:
                self.cursor.execute('''
                    INSERT INTO halls (name, facebook_url, governorate_id, notes)
                    VALUES (?, ?, ?, ?)
                ''', (name, venue_link, governorate_id, notes))
                
                self.conn.commit()
                messagebox.showinfo("نجاح", f"تم إضافة القاعة: {name} بنجاح.")
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"فشل الإضافة: {e}")
        
        self.load_venues_data() 
        self.clear_form() 

    def clear_form(self):
        """مسح حقول النموذج."""
        for var_name, var in self.entry_vars.items():
            if var_name in ['venue_name', 'city', 'venue_link']:
                 var.set("")
            
        self.city_combo.set('')
        self.notes_text.delete('1.0', tk.END)
            
        self.current_selected_iid = None
        self.form_frame.config(text="إضافة قاعة جديدة")
        self.save_btn.config(text="💾 حفظ البيانات")
        self.venue_table.selection_remove(self.venue_table.selection())

    def edit_venue(self):
        """تحميل بيانات القاعة المحددة في النموذج للتعديل."""
        selected_item = self.venue_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد قاعة من الجدول لتعديلها.")
            return
            
        self.current_selected_iid = int(selected_item[0]) 
        values = self.venue_table.item(self.current_selected_iid, 'values')
        
        # ملء حقول النموذج
        self.entry_vars['venue_name'].set(values[1])   
        self.entry_vars['city'].set(values[2])        
        self.entry_vars['venue_link'].set(values[3])   
        
        # ملء حقل الملاحظات
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', values[4]) 
        
        self.form_frame.config(text=f"تعديل بيانات القاعة: {values[1]}")
        self.save_btn.config(text="↩️ تحديث البيانات")
        
    def on_double_click_edit(self, event):
        """استدعاء دالة التعديل عند النقر المزدوج."""
        self.edit_venue()

    def delete_venue(self):
        """حذف القاعة المحددة."""
        selected_item = self.venue_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد قاعة من الجدول لحذفها.")
            return

        item_id = int(selected_item[0])
        venue_name = self.venue_table.item(item_id, 'values')[1]
        
        confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف القاعة: {venue_name}؟")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM halls WHERE id=?", (item_id,))
                self.conn.commit()
                
                self.venue_table.delete(item_id)
                self.clear_form()
                messagebox.showinfo("نجاح", f"تم حذف القاعة: {venue_name} بنجاح.")
            except sqlite3.Error as e:
                messagebox.showerror("خطأ", f"فشل الحذف من قاعدة البيانات: {e}")
            
    # --- وظائف مساعدة (مع التعديلات المطلوبة) ---
    def on_click_open_link(self, event):
        """يفتح الرابط عند النقر على عمود الرابط."""
        item_id = self.venue_table.identify_row(event.y)
        if not item_id:
            return
        
        col = self.venue_table.identify_column(event.x)

        if col == '#4': # عمود الرابط
            values = self.venue_table.item(item_id, 'values')
            if len(values) > 3: 
                link = values[3]
                self.open_link(link)

    def open_link(self, url):
        """فتح الرابط المحدد في المتصفح. يتم فحص الرابط وإضافة البروتوكول إذا لزم الأمر."""
        if not url:
            messagebox.showwarning("رابط فارغ", "لا يوجد رابط لفتحه.")
            return

        # إضافة https:// إذا كان الرابط لا يحتوي على بروتوكول
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            # فحص بسيط للتحقق من وجود نقطة في الرابط كحد أدنى
            if '.' in url:
                webbrowser.open_new_tab(url)
            else:
                messagebox.showwarning("رابط غير صحيح", "الرجاء إدخال رابط صحيح (تأكد من وجود http/https أو نقطة).")
        except Exception:
            messagebox.showerror("خطأ", "لا يمكن فتح الرابط في المتصفح الافتراضي.")

    def visit_website(self):
        """فتح رابط الموقع الافتراضي في المتصفح."""
        website_url = "https://www.example.com/perfectvenue" 
        try:
            webbrowser.open_new_tab(website_url)
        except Exception:
            messagebox.showerror("خطأ", "لا يمكن فتح رابط الموقع الافتراضي.")

# --- تشغيل التطبيق ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PerfectVenueApp(root)
    root.mainloop()