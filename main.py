
import os
import datetime
import webbrowser
import arabic_reshaper
from bidi.algorithm import get_display
from num2words import num2words
import streamlit as st
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ========== تهيئة الخط العربي ==========
def setup_font():
    try:
        font_path = os.path.join(os.path.dirname(__file__), "amiri.ttf")
        if not os.path.exists(font_path):
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "amiri.ttf")

        if not os.path.exists(font_path):
            st.error("لم يتم العثور على ملف الخط amiri.ttf في مجلد السكربت")
            return False

        pdfmetrics.registerFont(TTFont("Amiri", font_path))
        return True
    except Exception as e:
        st.error(f"تعذر تحميل الخط:\n{str(e)}")
        return False

if not setup_font():
    st.stop()

# ========== إعداد مجلد الفواتير ==========
if not os.path.exists("الفواتير"):
    try:
        os.makedirs("الفواتير")
    except Exception as e:
        st.error(f"تعذر إنشاء مجلد الفواتير:\n{str(e)}")
        st.stop()

# ========== الدوال المساعدة ==========
def get_next_invoice_number():
    counter_file = "invoice_counter.txt"
    try:
        with open(counter_file, 'r') as f:
            last_num = int(f.read().strip())
    except:
        last_num = 0

    next_num = last_num + 1
    with open(counter_file, 'w') as f:
        f.write(str(next_num))

    return str(next_num).zfill(4)

def format_arabic(text):
    try:
        if any("\u0600" <= c <= "\u06FF" for c in text):
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        return text
    except:
        return text

def number_to_arabic_words(number):
    try:
        number = float(number)
        if number.is_integer():
            words = num2words(int(number), lang='ar')
        else:
            words = num2words(number, lang='ar')

        if words:
            return words + " دينار عراقي فقط"
        return ""
    except:
        return ""

def create_receipt_pdf(name, from_name, place_of_receipt, amount, reason, invoice_number):
    try:
        file_name = f"وصل_{invoice_number}_{name.replace(' ', '')}.pdf"
        file_path = os.path.join("الفواتير", file_name)

        c = canvas.Canvas(file_path, pagesize=A6)
        width, height = A6

        c.setFillColorRGB(0, 0, 0.5)
        c.rect(0, height - 77, width, 10, fill=1, stroke=0)

        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 10, height - 70, width=50, height=50, mask='auto')

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Amiri", 8)
        c.drawCentredString(width / 2, height - 75, "RIMAH AL EAMAR COMPANY for General Contracting")

        c.setFillColorRGB(0, 0, 0.5)
        c.rect(0, height - 402, width, 10, fill=1, stroke=0)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Amiri", 8)
        c.drawCentredString(width / 2, height - 400, format_arabic("العنوان : الموصل شارع الجمهورية رقم الهاتف : 07518039693"))

        c.setFillColorRGB(0, 0, 0.5)
        c.setFont("Amiri", 12)
        c.drawRightString(width - 8, height - 25, format_arabic("شركة رماح الاعمار"))
        c.drawRightString(width - 8, height - 50, format_arabic("للتجارة والمقاولات العامة المحدودة"))

        c.setFont("Amiri", 14)
        c.drawCentredString(width / 2, height - 90, format_arabic("وصل قبض"))

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Amiri", 8)
        c.drawString(8, height - 87, format_arabic(f"الــتـاريــخ: {date_str}"))

        c.setFillColorRGB(1, 0, 0)
        c.setFont("Amiri", 8)
        c.drawString(31, height - 98, format_arabic(f"الوصل: {invoice_number}"))

        y_pos = height - 120
        c.setFont("Amiri", 12)
        details = [
            f"{float(amount):,} DIQ",
            f"إني المُستلم: {name}",
            f"إستلمتُ مِن: {from_name}",
            f"مكان الاستلام: {place_of_receipt}",
            f"مبلغ قدره: {number_to_arabic_words(amount)}",
            f"وذلك عن: {reason}",
            "الاسم والتوقيع: __"
        ]

        for i, detail in enumerate(details):
            if i == 0:
                c.setFillColorRGB(1, 0, 0)
            else:
                c.setFillColorRGB(0, 0, 0)
            c.drawRightString(width - 10, y_pos, format_arabic(detail))
            y_pos -= 25

        c.save()
        return file_path
    except Exception as e:
        st.error(f"فشل إنشاء الوصل:\n{str(e)}")
        return None

st.set_page_config(page_title="برنامج وصل قبض", layout="centered")

st.markdown("""
    <style>
        .title {
            font-family: 'Amiri', serif;
            font-size: 36px;
            font-weight: bold;
            color: #0B3D91;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-label {
            font-family: 'Amiri', serif;
            font-size: 18px;
            color: #073763;
            margin-bottom: 5px;
        }
        .stTextInput>div>div>input {
            text-align: right !important;
            font-family: 'Amiri', serif !important;
            font-size: 16px !important;
        }
        .stButton>button {
            background-color: #0B3D91;
            color: white;
            font-weight: bold;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #08306B;
            color: #FFFFFF;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #888888;
            font-size: 12px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">برنامج وصل قبض</div>', unsafe_allow_html=True)

with st.form("receipt_form"):
    name = st.text_input("اسم المستلم:", placeholder="ادخل اسم المستلم")
    from_name = st.text_input("المستلم منه:", placeholder="ادخل اسم الجهة المستلمة")
    place_of_receipt = st.text_input("مكان الاستلام:", placeholder="ادخل مكان الاستلام")
    amount = st.text_input("المبلغ (DIQ):", placeholder="ادخل المبلغ")
    reason = st.text_input("وذلك عن:", placeholder="سبب الاستلام")

    submit = st.form_submit_button("✔ معاينة الوصل")

if submit:
    if not all([name.strip(), from_name.strip(), place_of_receipt.strip(), amount.strip(), reason.strip()]):
        st.warning("يرجى تعبئة جميع الحقول!")
    else:
        try:
            amount_float = float(amount.replace(',', ''))
            if amount_float <= 0:
                st.error("المبلغ يجب أن يكون أكبر من الصفر!")
            else:
                invoice_number = get_next_invoice_number()
                pdf_path = create_receipt_pdf(name, from_name, place_of_receipt, amount, reason, invoice_number)
                if pdf_path:
                    st.success(f"تم إنشاء الوصل بنجاح: {pdf_path}")
                    with open(pdf_path, "rb") as f:
                        btn = st.download_button(label="تحميل الوصل PDF", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")
                    try:
                        webbrowser.open(pdf_path)
                    except:
                        pass
                else:
                    st.error("فشل في إنشاء الوصل!")
        except ValueError:
            st.error("المبلغ يجب أن يكون رقماً صحيحاً أو عشرياً!")
