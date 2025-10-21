import os
import io
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ----------------------- وضعیت هر چت -----------------------
state = {}

def get_state(cid: int):
    if cid not in state:
        state[cid] = {"points": [], "waiting_for_time": False, "waiting_for_location": False, "time": None}
    return state[cid]


HELP_TEXT = (
    "راهنمای استفاده:\n"
    "• ابتدا از دکمه‌های منو برای افزودن نقطه استفاده کنید.\n\n"
    "دستورات:\n"
    "/help — همین راهنما\n"
    "/start — شروع مجدد\n\n"
    "هر نقطه شامل زمان (T) و مکان (X) است.\n"
    "پس از افزودن حداقل دو نقطه می‌توانید گزینه‌ی «محاسبه» را بزنید."
)

# ----------------------- ابزارک‌ها -----------------------
def _buf_fig(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def compute_all(pts):
    """محاسبه سرعت، شتاب و مقادیر میانگین"""
    t = np.array([float(p[0]) for p in pts], dtype=float)
    s = np.array([float(p[1]) for p in pts], dtype=float)

    # مرتب‌سازی بر اساس زمان
    order = np.argsort(t)
    t, s = t[order], s[order]

    dt = np.diff(t)
    ds = np.diff(s)

    if np.any(dt == 0):
        raise ValueError("مقادیر زمان نباید تکراری باشند (ΔT=0).")

    v_avg = ds / dt
    t_mid_v = t[:-1] + dt / 2.0

    if len(v_avg) >= 2:
        dv = np.diff(v_avg)
        dt_v = np.diff(t_mid_v)
        if np.any(dt_v == 0):
            raise ValueError("ΔT برای محاسبه شتاب صفر است.")
        a_avg = dv / dt_v
        t_mid_a = t_mid_v[:-1] + dt_v / 2.0
    else:
        a_avg = np.array([])
        t_mid_a = np.array([])

    return t, s, t_mid_v, v_avg, t_mid_a, a_avg


def generate_plot(t, s, t_mid_v, v_avg, t_mid_a, a_avg):
    """سه نمودار: s(t), v_avg(t_mid), a_avg(t_mid)"""
    rows = 3 if len(a_avg) > 0 else 2
    if rows == 3:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 10))
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 8))

    # s(t)
    ax1.plot(t, s, marker='o', label='s(t)')
    ax1.set_xlabel("زمان (T)")
    ax1.set_ylabel("مکان (X)")
    ax1.set_title("نمودار زمان-مکان")
    ax1.grid(True)

    # v_avg در زمان‌های میانی
    if len(v_avg) > 0:
        ax2.plot(t_mid_v, v_avg, marker='o', label='v_avg')
        ax2.set_xlabel("زمان میانی (T)")
        ax2.set_ylabel("سرعت میانگین (V_avg)")
        ax2.set_title("نمودار سرعت میانگین (بین نقاط)")
        ax2.grid(True)

    # a_avg در زمان‌های میانی سرعت
    if rows == 3 and len(a_avg) > 0:
        ax3.plot(t_mid_a, a_avg, marker='o', label='a_avg')
        ax3.set_xlabel("زمان میانی سرعت (T)")
        ax3.set_ylabel("شتاب میانگین (A_avg)")
        ax3.set_title("نمودار شتاب میانگین (بین سرعت‌های متوالی)")
        ax3.grid(True)

    return fig


# ----------------------- دکمه‌ها -----------------------
def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ افزودن نقطه", callback_data='add_point')],
        [InlineKeyboardButton("➖ حذف آخرین نقطه", callback_data='remove_point')],
        [InlineKeyboardButton("📊 محاسبه", callback_data='calculate')],
    ]
    return InlineKeyboardMarkup(keyboard)

# ----------------------- هندلرها -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(update.effective_chat.id)
    await update.message.reply_text(
        "سلام 👋\nبرای شروع از منوی زیر استفاده کنید:",
        reply_markup=get_menu_keyboard()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, reply_markup=get_menu_keyboard())


async def add_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    st = get_state(update.effective_chat.id)
    st["waiting_for_time"] = True
    st["waiting_for_location"] = False
    st["time"] = None

    await q.message.reply_text("لطفاً زمان (T) را وارد کنید:")


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ورود زمان و مکان"""
    st = get_state(update.effective_chat.id)
    text = update.message.text.strip()

    if st["waiting_for_time"]:
        st["time"] = text
        st["waiting_for_time"] = False
        st["waiting_for_location"] = True
        await update.message.reply_text(f"⏱ زمان ثبت شد: {st['time']}\nحالا مکان (X) را وارد کنید:")
        return

    if st["waiting_for_location"]:
        st["location"] = text
        st["waiting_for_location"] = False
        st["points"].append((st["time"], st["location"]))
        await update.message.reply_text(
            f"✅ نقطه ثبت شد: T={st['time']}, X={st['location']}\n"
            f"🔹 تعداد نقاط فعلی: {len(st['points'])}",
            reply_markup=get_menu_keyboard()
        )
        return

    await update.message.reply_text("برای افزودن نقطه جدید، روی «افزودن نقطه» بزنید.", reply_markup=get_menu_keyboard())


async def remove_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    st = get_state(update.effective_chat.id)
    if not st["points"]:
        await q.message.reply_text("⚠️ هیچ نقطه‌ای برای حذف وجود ندارد.")
        return

    removed = st["points"].pop()
    await q.message.reply_text(
        f"✅ آخرین نقطه حذف شد: T={removed[0]}, X={removed[1]}  (مانده: {len(st['points'])})",
        reply_markup=get_menu_keyboard()
    )


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    st = get_state(update.effective_chat.id)
    pts = st["points"]
    if len(pts) < 2:
        await q.message.reply_text("⚠️ برای محاسبه حداقل دو نقطه لازم است.")
        return

    try:
        t, s, t_mid_v, v_avg, t_mid_a, a_avg = compute_all(pts)
    except ValueError as e:
        await q.message.reply_text(f"❌ خطا در محاسبات: {e}")
        return

    # فرمول‌ها
    v_avg_formula = "V_avg = ΔX / ΔT"
    a_avg_formula = "A_avg = ΔV / ΔT"
    s_avg_formula = "S_avg = ΔX / ΔT  (روی کل بازه)"

    # محاسبهٔ سرعت/جابجایی میانگین کلی (شیب خط بین اولین و آخرین نقطه)
    s_avg = (s[-1] - s[0]) / (t[-1] - t[0])


    def nice(arr):
        if arr is None or len(arr) == 0:
            return "—"
        # گرد کردن اعداد برای پیام
        return np.round(arr, 4).tolist()

    msg = (
        "✅ **فرمول‌ها و محاسبات انجام شد:**\n\n"
        
        "### 1️⃣ سرعت میانگین بین هر دو نقطه:\n"
        "فرمول سرعت میانگین بین دو نقطه:\n"
        "V_avg = ΔX / ΔT\n"
        "که در آن ΔX تغییر مکان (X) و ΔT تغییر زمان (T) است.\n\n"
        "نتایج برای هر بازه زمانی به شرح زیر است:\n"
        f"**V_avg** = {nice(v_avg)}\n\n"
        
        "### 2️⃣ شتاب میانگین بین سرعت‌های متوالی:\n"
        "فرمول شتاب میانگین:\n"
        "A_avg = ΔV / ΔT\n"
        "که در آن ΔV تغییر سرعت و ΔT تغییر زمان بین دو سرعت متوالی است.\n\n"
        f"**A_avg** = {nice(a_avg)}\n\n"
        
        "### 3️⃣ سرعت/جابجایی میانگین روی کل بازه:\n"
        "فرمول جابجایی میانگین به این صورت است:\n"
        "S_avg = (X_last - X_first) / (T_last - T_first)\n"
        "که در آن ΔX تغییر مکان کل مسیر و ΔT تغییر زمان کل بازه است.\n\n"
        f"محاسبه جابجایی میانگین به صورت زیر است:\n"
        f"S_avg = ({s[-1]} - {s[0]}) / ({t[-1]} - {t[0]}) = {s[-1] - s[0]} / {t[-1] - t[0]} = **{np.round(s_avg, 4)}**\n\n"
        
        "🔹 **نتیجه‌گیری:**\n"
        "نتایج محاسبات به شرح زیر است:\n\n"
        f"🟢 **سرعت میانگین** بین هر دو نقطه: {nice(v_avg)}\n"
        f"🟠 **شتاب میانگین** بین سرعت‌ها: {nice(a_avg)}\n"
        f"🔵 **جابجایی میانگین** روی کل بازه: {np.round(s_avg, 4)}\n"
    )



    # نمودار
    fig = generate_plot(t, s, t_mid_v, v_avg, t_mid_a, a_avg)
    buf = _buf_fig(fig)

    await q.message.reply_text(msg)
    await q.message.reply_photo(InputFile(buf, "time_position_plot.png"), reply_markup=get_menu_keyboard())




# ----------------------- راه‌اندازی بات -----------------------
def get_token():
    tok = os.getenv("BOT_TOKEN")
    if tok:
        return tok
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("BOT_TOKEN", "")
    return ""


def main():
    token = get_token()
    if not token:
        raise RuntimeError("❌ BOT_TOKEN تنظیم نشده است.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(CallbackQueryHandler(add_point,    pattern='^add_point$'))
    app.add_handler(CallbackQueryHandler(remove_point, pattern='^remove_point$'))
    app.add_handler(CallbackQueryHandler(calculate,    pattern='^calculate$'))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    print("✅ Bot is running…")
    app.run_polling()


if __name__ == "__main__":
    main()
