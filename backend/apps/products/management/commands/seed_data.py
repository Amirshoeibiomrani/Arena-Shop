"""
Management Command برای ساخت داده‌های تستی واقع‌گرایانه
استفاده:
    python manage.py seed_data
    python manage.py seed_data --clear   (اول داده‌های قبلی پاک شه)
"""
import random
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from apps.products.models import Category, Brand, Product
from apps.orders.models import Cart, CartItem, Order, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = 'ساخت داده‌های تستی واقع‌گرایانه برای پروژه'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='پاک کردن داده‌های قبلی قبل از seed',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  در حال پاک کردن داده‌های قبلی...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('🚀 شروع ساخت داده‌های تستی...\n'))

        # ترتیب مهمه!
        categories = self.create_categories()
        brands = self.create_brands()
        products = self.create_products(categories, brands)
        users = self.create_users()
        orders = self.create_orders(users, products)

        # خلاصه
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ ساخت داده‌های تستی با موفقیت تموم شد!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'📁 دسته‌بندی‌ها: {len(categories)}')
        self.stdout.write(f'🏷️  برندها: {len(brands)}')
        self.stdout.write(f'📦 محصولات: {len(products)}')
        self.stdout.write(f'👥 کاربران: {len(users)}')
        self.stdout.write(f'🛒 سفارش‌ها: {len(orders)}')
        self.stdout.write(self.style.SUCCESS('=' * 50 + '\n'))

    # ============================================
    # پاک کردن داده‌ها
    # ============================================
    def clear_data(self):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Product.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()
        # فقط کاربران غیر ادمین رو پاک کن
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('✓ داده‌های قبلی پاک شد\n'))

    # ============================================
    # ساخت دسته‌بندی‌ها
    # ============================================
    def create_categories(self):
        self.stdout.write('📁 ساخت دسته‌بندی‌ها...')

        categories_data = [
            {'name': 'موبایل', 'description': 'انواع گوشی‌های هوشمند'},
            {'name': 'لپ‌تاپ', 'description': 'لپ‌تاپ‌های گیمینگ و اداری'},
            {'name': 'تبلت', 'description': 'تبلت و آیپد'},
            {'name': 'هدفون', 'description': 'هدفون‌های بی‌سیم و سیمی'},
            {'name': 'ساعت هوشمند', 'description': 'اسمارت واچ و فیتنس بند'},
            {'name': 'لوازم جانبی', 'description': 'کابل، شارژر، قاب و...'},
            {'name': 'کنسول بازی', 'description': 'PlayStation, Xbox, Nintendo'},
            {'name': 'دوربین', 'description': 'دوربین‌های عکاسی و فیلم‌برداری'},
        ]

        categories = []
        for data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description'], 'is_active': True},
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'  ✓ {cat.name}')

        return categories

    # ============================================
    # ساخت برندها
    # ============================================
    def create_brands(self):
        self.stdout.write('\n🏷️  ساخت برندها...')

        brands_data = [
            {'name': 'Samsung', 'description': 'سامسونگ - برند معتبر کره‌ای'},
            {'name': 'Apple', 'description': 'اپل - بهترین برند آمریکایی'},
            {'name': 'Xiaomi', 'description': 'شیائومی - قیمت مناسب و کیفیت بالا'},
            {'name': 'Sony', 'description': 'سونی - برند ژاپنی'},
            {'name': 'Asus', 'description': 'ایسوس - تخصص در لپ‌تاپ گیمینگ'},
            {'name': 'HP', 'description': 'اچ پی - لپ‌تاپ‌های اداری'},
        ]

        brands = []
        for data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description'], 'is_active': True},
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'  ✓ {brand.name}')

        return brands

    # ============================================
    # ساخت محصولات
    # ============================================
    def create_products(self, categories, brands):
        self.stdout.write('\n📦 ساخت محصولات...')

        # دیتای واقعی محصولات بر اساس دسته‌بندی
        products_data = {
            'موبایل': [
                ('Samsung Galaxy S25 Ultra', 'Samsung', 65_000_000, 58_000_000),
                ('Samsung Galaxy A55', 'Samsung', 18_000_000, 16_500_000),
                ('iPhone 16 Pro Max', 'Apple', 95_000_000, None),
                ('iPhone 15', 'Apple', 55_000_000, 49_000_000),
                ('Xiaomi 14 Ultra', 'Xiaomi', 42_000_000, 38_000_000),
                ('Xiaomi Redmi Note 13 Pro', 'Xiaomi', 14_500_000, 13_000_000),
                ('Sony Xperia 1 VI', 'Sony', 58_000_000, None),
            ],
            'لپ‌تاپ': [
                ('Asus ROG Strix G16', 'Asus', 85_000_000, 79_000_000),
                ('Asus Vivobook 15', 'Asus', 32_000_000, 29_500_000),
                ('HP Pavilion 15', 'HP', 38_000_000, 35_000_000),
                ('HP Omen 16', 'HP', 72_000_000, None),
                ('Apple MacBook Pro M4', 'Apple', 145_000_000, 135_000_000),
                ('Apple MacBook Air M3', 'Apple', 95_000_000, None),
            ],
            'تبلت': [
                ('iPad Pro M4 13"', 'Apple', 78_000_000, 72_000_000),
                ('iPad Air 11"', 'Apple', 45_000_000, None),
                ('Samsung Galaxy Tab S10', 'Samsung', 52_000_000, 47_000_000),
                ('Xiaomi Pad 6 Pro', 'Xiaomi', 22_000_000, 19_500_000),
            ],
            'هدفون': [
                ('Sony WH-1000XM5', 'Sony', 18_500_000, 16_000_000),
                ('Apple AirPods Pro 2', 'Apple', 14_000_000, 12_500_000),
                ('Apple AirPods Max', 'Apple', 32_000_000, None),
                ('Samsung Galaxy Buds 3 Pro', 'Samsung', 9_500_000, 8_500_000),
                ('Xiaomi Buds 5 Pro', 'Xiaomi', 6_500_000, None),
            ],
            'ساعت هوشمند': [
                ('Apple Watch Series 10', 'Apple', 28_000_000, 25_500_000),
                ('Apple Watch Ultra 2', 'Apple', 48_000_000, None),
                ('Samsung Galaxy Watch 7', 'Samsung', 19_000_000, 17_500_000),
                ('Xiaomi Smart Band 9', 'Xiaomi', 2_500_000, 2_200_000),
            ],
            'لوازم جانبی': [
                ('شارژر تایپ سی Samsung 45W', 'Samsung', 850_000, 690_000),
                ('کابل لایتنینگ Apple اورجینال', 'Apple', 1_200_000, None),
                ('پاوربانک Xiaomi 20000mAh', 'Xiaomi', 1_800_000, 1_550_000),
                ('قاب MagSafe iPhone 16', 'Apple', 2_500_000, None),
            ],
            'کنسول بازی': [
                ('Sony PlayStation 5 Pro', 'Sony', 78_000_000, 72_000_000),
                ('Sony PlayStation 5 Slim', 'Sony', 52_000_000, None),
            ],
            'دوربین': [
                ('Sony Alpha A7 IV', 'Sony', 165_000_000, 155_000_000),
                ('Sony ZV-1 II', 'Sony', 42_000_000, None),
            ],
        }

        # توضیحات نمونه
        sample_descriptions = [
            'این محصول با تکنولوژی پیشرفته و کیفیت ساخت بی‌نظیر، تجربه‌ای فوق‌العاده برای شما به ارمغان می‌آورد. طراحی ارگونومیک و مدرن آن، علاوه بر زیبایی، راحتی استفاده را تضمین می‌کند.',
            'محصولی با کیفیت پریمیوم که برای کاربرانی که به دنبال بهترین تجربه هستند طراحی شده. عمر باتری طولانی و عملکرد فوق‌العاده در همه شرایط.',
            'انتخابی هوشمندانه با قیمتی منصفانه. ترکیبی از کیفیت و قیمت که نمی‌توانید رد کنید. مناسب برای استفاده روزانه و حرفه‌ای.',
            'با ضمانت اصالت کالا و گارانتی معتبر. ارسال سریع به سراسر کشور. این محصول یکی از پرفروش‌ترین محصولات ماست.',
        ]

        all_products = []

        for category in categories:
            cat_products = products_data.get(category.name, [])
            for title, brand_name, price, discount in cat_products:
                # پیدا کردن برند
                brand = next((b for b in brands if b.name == brand_name), None)

                # ساخت محصول
                product, created = Product.objects.get_or_create(
                    title=title,
                    defaults={
                        'category': category,
                        'brand': brand,
                        'short_description': f'{title} - بهترین کیفیت',
                        'description': random.choice(sample_descriptions),
                        'price': Decimal(price),
                        'discount_price': Decimal(discount) if discount else None,
                        'stock': random.randint(5, 50),
                        'status': 'published',
                        'is_featured': random.choice([True, False, False, False]),  # 25% احتمال
                        'views_count': random.randint(50, 5000),
                        'sold_count': random.randint(0, 100),
                    },
                )
                all_products.append(product)
                if created:
                    self.stdout.write(f'  ✓ {product.title}')

        return all_products

       # ============================================
    # ساخت کاربران تستی
    # ============================================
    def create_users(self):
        self.stdout.write('\n👥 ساخت کاربران تستی...')

        users_data = [
            ('ali', 'ali@test.com', 'علی', 'محمدی', '09121111111'),
            ('reza', 'reza@test.com', 'رضا', 'احمدی', '09122222222'),
            ('sara', 'sara@test.com', 'سارا', 'کریمی', '09123333333'),
            ('mohammad', 'mohammad@test.com', 'محمد', 'حسینی', '09124444444'),
            ('zahra', 'zahra@test.com', 'زهرا', 'موسوی', '09125555555'),
            ('hossein', 'hossein@test.com', 'حسین', 'رضایی', '09126666666'),
            ('fatemeh', 'fatemeh@test.com', 'فاطمه', 'صادقی', '09127777777'),
            ('mahdi', 'mahdi@test.com', 'مهدی', 'جعفری', '09128888888'),
            ('narges', 'narges@test.com', 'نرگس', 'علوی', '09129999999'),
            ('amir', 'amir@test.com', 'امیر', 'یوسفی', '09130000000'),
            ('maryam', 'maryam@test.com', 'مریم', 'حقیقی', '09131111111'),
            ('reyhane', 'reyhane@test.com', 'ریحانه', 'مرادی', '09132222222'),
            ('peyman', 'peyman@test.com', 'پیمان', 'نوری', '09133333333'),
            ('shahin', 'shahin@test.com', 'شاهین', 'فرهادی', '09134444444'),
            ('nazanin', 'nazanin@test.com', 'نازنین', 'کاظمی', '09135555555'),
        ]

        users = []
        for username, email, first_name, last_name, phone in users_data:
            # چک کن چه با ایمیل چه با یوزرنیم، اگه کاربر وجود داره skip کن
            existing_user = User.objects.filter(email=email).first() or \
                            User.objects.filter(username=username).first()

            if existing_user:
                users.append(existing_user)
                self.stdout.write(f'  ⊙ {existing_user.email} (از قبل وجود داشت)')
                continue

            # کاربر جدید بساز
            user = User.objects.create_user(
                username=username,
                email=email,
                password='test1234',
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                is_verified=True,
            )
            users.append(user)
            self.stdout.write(f'  ✓ {user.email}')

        self.stdout.write(self.style.WARNING(f'  💡 رمز عبور همه کاربران تستی: test1234'))
        return users
    # ============================================
    # ساخت سفارش‌ها
    # ============================================
    def create_orders(self, users, products):
        self.stdout.write('\n🛒 ساخت سفارش‌های تستی...')

        statuses = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled']
        # وزن‌دهی - بیشتر سفارش‌ها تحویل داده شده باشن
        status_weights = [10, 15, 15, 20, 35, 5]

        orders = []
        now = timezone.now()

        # ۳۰ سفارش در ۹۰ روز اخیر بساز
        for i in range(30):
            user = random.choice(users)
            # تاریخ تصادفی در ۹۰ روز اخیر
            days_ago = random.randint(0, 90)
            order_date = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            # وضعیت تصادفی با وزن
            status = random.choices(statuses, weights=status_weights, k=1)[0]

            # ساخت سفارش
            order = Order.objects.create(
                user=user,
                status=status,
                receiver_name=f'{user.first_name} {user.last_name}',
                receiver_phone=user.phone or '09120000000',
                shipping_address=f'تهران، خیابان {random.choice(["ولیعصر", "آزادی", "انقلاب", "شریعتی"])}، پلاک {random.randint(1, 500)}',
                postal_code=f'{random.randint(1000000000, 9999999999)}',
                shipping_cost=Decimal(random.choice([30000, 50000, 80000, 100000])),
            )

            # تاریخ ایجاد رو دستی بذار (چون auto_now_add خودکار میذاره)
            Order.objects.filter(pk=order.pk).update(created_at=order_date)

            # ۱ تا ۵ محصول تصادفی به سفارش اضافه کن
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, num_items)

            items_total = Decimal('0')
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.discount_price or product.price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_title=product.title,
                    unit_price=unit_price,
                    quantity=quantity,
                )
                items_total += unit_price * quantity

            # محاسبه قیمت کل
            order.items_total = items_total
            order.total_price = items_total + order.shipping_cost

            # اگه وضعیت paid یا بالاتر، تاریخ پرداخت رو ست کن
            if status in ['paid', 'processing', 'shipped', 'delivered']:
                order.paid_at = order_date + timedelta(minutes=random.randint(5, 60))

            # اگه delivered، تاریخ تحویل رو ست کن
            if status == 'delivered':
                order.delivered_at = order_date + timedelta(days=random.randint(2, 7))

            order.save()
            orders.append(order)
            self.stdout.write(f'  ✓ {order.order_number} ({order.get_status_display()})')

        return orders



    """
    📚 توضیح کد (نکات حرفه‌ای)
🔥 BaseCommand
هر Management Command باید از این کلاس ارث ببره و متد handle() رو پیاده‌سازی کنه.

🎯 add_arguments()
به دستور آرگومان اضافه می‌کنه. مثلاً ما --clear رو اضافه کردیم تا کاربر بتونه قبل از seed، داده‌های قدیمی رو پاک کنه.

⚡ @transaction.atomic
کل عملیات seed یه تراکنشه. اگه یه جا خطا بده، هیچی ذخیره نمی‌شه. این یعنی دیتابیست یا کاملاً پر می‌شه یا اصلاً تغییر نمی‌کنه. 🎯

💬 self.stdout.write() و self.style
به جای print() معمولی، از این استفاده می‌کنیم تا:

پیام‌ها رنگی باشن (SUCCESS, WARNING, ERROR)
خروجی استاندارد Django باشه
🎲 random.choices() با weights
به جای انتخاب کاملاً تصادفی، می‌تونی احتمال هر گزینه رو تعیین کنی:

Python

random.choices(statuses, weights=[10, 15, 15, 20, 35, 5], k=1)
یعنی سفارش‌های delivered بیشتر باشن (35% احتمال) - مثل دنیای واقعی.

💡 چرا get_or_create?
این متد عالی Django:

اگه آیتم وجود داشت → برگردونش
اگه نداشت → بسازش
پس می‌تونی دستور رو چند بار اجرا کنی بدون اینکه duplicate بسازه.

📌 گام ۳: اجرای دستور
تو ترمینال:

PowerShell

python manage.py seed_data
    """