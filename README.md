# Railway-XPanel 1.0.7

پنل مدیریت Xray برای Railway با تمرکز روی همان معماری‌ای که در پروژه قدیمی `Xhttp-main` جواب داده بود:

`V2rayNG (TLS ON + SNI=Public Domain) → Railway HTTPS Edge → HTTP → Nginx → Xray`

## چرا این نسخه با پروژه قدیمی فرق دارد؟

در پروژه قدیمی Xray مستقیماً روی پورت Railway (`$PORT`, معمولاً 8080) گوش می‌داد و کلاینت را بعداً در v2rayNG روی TLS می‌گذاشتی. این نسخه همان منطق TLS را حفظ می‌کند، اما برای اینکه **پنل + چند inbound** همزمان روی یک Public Port قابل استفاده باشند، Nginx روی `$PORT` قرار گرفته و درخواست‌های مسیرهای XHTTP/WS/HTTPUpgrade را به پورت‌های خصوصی Xray می‌فرستد.

در نتیجه برای inbound با گزینه `TLS (Railway Edge)`:

- در لینک خروجی: `security=tls`
- `sni=Public Domain`
- پورت عمومی: `443`
- در Xray داخل کانتینر: `security=none`
- TLS دوباره داخل Xray terminate نمی‌شود.

این الگو با توضیح رسمی Xray درباره جدا بودن transport و transport-security سازگار است و TLS می‌تواند با XHTTP، gRPC، WebSocket و HTTPUpgrade ترکیب شود. urlمستندات Xray Transport Configurationhttps://xtls.github.io/en/config/transport.html

## Transportها

پنل فعلاً این موارد را می‌سازد:

- VLESS + XHTTP + TLS (Railway Edge) — مسیر اصلی پیشنهادی
- VLESS + XHTTP بدون TLS
- VLESS + WebSocket + TLS
- VLESS + WebSocket بدون TLS
- VLESS + gRPC + TLS
- VLESS + gRPC بدون TLS
- VLESS + HTTPUpgrade + TLS
- VLESS + HTTPUpgrade بدون TLS

### نکته مهم درباره Railway

`gRPC` به HTTP/2 end-to-end نیاز دارد و رفتار آن در یک HTTP ingress می‌تواند به نحوه عبور HTTP/2 توسط پلتفرم وابسته باشد؛ بنابراین پنل آن را می‌سازد ولی آن را به‌عنوان transport آزمایشی روی Railway در نظر بگیر.

برای XHTTP نیز اگر reverse proxy ناسازگار باشد، مستندات Project X استفاده از `grpc_pass` را به‌عنوان یکی از روش‌های عبور از Nginx مطرح می‌کنند. urlXHTTP: Beyond REALITYhttps://xtls.github.io/en/config/transports/xhttp.html

## Login

مقادیر پیش‌فرض:

- Username: `admin`
- Password: `change-me-now`

حتماً در Railway Variables مقدارهای `ADMIN_PASSWORD` و `SECRET_KEY` را تغییر بده.

## Railway

1. Repository را در GitHub قرار بده.
2. در Railway از همان Repository یک Service بساز.
3. Builder روی Dockerfile باشد.
4. برای Service یک **Public Domain** بساز.
5. اگر `RAILWAY_PUBLIC_DOMAIN` در محیط موجود نبود، متغیر `PUBLIC_HOST` را برابر Public Domain قرار بده.
6. اگر Volume داری، Mount Path را `/data` قرار بده تا SQLite، تنظیمات و backupها باقی بمانند.
7. بعد از Deploy وارد `/login` شو.
8. ابتدا یک User بساز.
9. سپس در Inbounds یک `XHTTP + TLS (Railway Edge)` بساز.
10. در Users روی `Links / QR` بزن و لینک `Railway TLS` را بردار.

## تست v2rayNG

برای XHTTP TLS:

- Address = Public Domain
- Port = 443
- Protocol = VLESS
- UUID = UUID کاربر
- Transport = XHTTP
- TLS = ON
- SNI = همان Public Domain
- Path = همان Path پنل
- Mode = auto

لینکی که پنل با عنوان `Railway TLS` می‌دهد باید همین مقادیر را داشته باشد.

## نکته درباره «بدون TLS»

در این معماری «TLS خاموش در Xray» با «لینک کلاینت بدون TLS» یکی نیست. مسیر اصلی Railway از HTTPS Edge استفاده می‌کند. بنابراین لینک پیشنهادی پنل برای Railway، TLS را در **کلاینت** فعال می‌کند و Xray در origin بدون TLS است؛ دقیقاً همان الگویی که در پروژه قدیمی استفاده کردی.

لینک `Plain HTTP` نیز تولید می‌شود، اما روی Railway نباید آن را معادل یک اتصال عمومی VLESS بدون TLS و بدون محدودیت دانست؛ سازگاری آن به مسیر HTTP عمومی و محدودیت‌های خود Xray/کلاینت بستگی دارد.

## Subscription و QR

برای هر کاربر:

- UUID اختصاصی
- لینک جداگانه برای هر inbound
- لینک TLS مخصوص Railway
- لینک Plain HTTP
- QR برای هر لینک
- Subscription URL
- QR سابسکریپشن

Subscription فقط inboundهایی را که بتوانند لینک سازگار با Railway Edge TLS تولید کنند وارد فهرست می‌کند.

## Ubuntu 24.04 / SSH administration (v1.0.8)

The runtime image is Ubuntu 24.04 and includes OpenSSH plus common administration and networking tools. SSH listens internally on `2222` by default. To reach it from the internet, create a Railway TCP Proxy targeting internal port `2222`; the HTTP Public Domain remains dedicated to XPanel and the HTTP-based Xray transports.

Configure `SSH_USER`, `SSH_ROOT_PASSWORD`, `SSH_USER_PASSWORD`, and `SSH_PORT` as Railway variables. See `RAILWAY-SSH-UBUNTU.md` for the exact setup and the container-specific limitations compared with a full Ubuntu VPS.
