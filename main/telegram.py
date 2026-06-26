import logging
import urllib.parse
import urllib.request

from django.conf import settings

from .models import TelegramAdmin

logger = logging.getLogger(__name__)


def _money(value):
    return f"{value:,}".replace(",", " ") + " so'm"


def build_order_message(order):
    lines = [
        f"Yangi buyurtma #{order.id}",
        "",
        f"Mijoz: {order.customer.full_name}",
        f"Telefon: {order.customer.phone}",
        f"Manzil: {order.address}",
        f"To'lov: {order.get_payment_display()}",
    ]

    if order.note:
        lines.append(f"Izoh: {order.note}")

    lines.extend(["", "Mahsulotlar:"])
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} x {item.quantity} = {_money(item.line_total)}"
        )

    lines.extend(["", f"Jami: {_money(order.total_price)}"])
    return "\n".join(lines)


def get_admin_chat_ids():
    chat_ids = list(
        TelegramAdmin.objects.filter(is_active=True)
        .exclude(chat_id="")
        .values_list("chat_id", flat=True)
    )
    if chat_ids:
        return chat_ids

    fallback_chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "")
    return [fallback_chat_id] if fallback_chat_id else []


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode()

    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        return 200 <= response.status < 300


def notify_order_created(order):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_ids = get_admin_chat_ids()
    if not token or not chat_ids:
        logger.info("Telegram sozlanmagan: TELEGRAM_BOT_TOKEN yoki admin chat ID yo'q.")
        return False

    message = build_order_message(order)
    sent = False
    for chat_id in chat_ids:
        try:
            sent = send_telegram_message(token, chat_id, message) or sent
        except Exception:
            logger.exception("Telegramga buyurtma xabarini yuborib bo'lmadi: %s", chat_id)
    return sent
