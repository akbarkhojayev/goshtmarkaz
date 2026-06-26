from django.db import migrations


PRODUCTS = [
    ("Tomahawk Dandana Steak", 149900, "1 kg", "/images/tomahowk dandana.jpg"),
    ("Dandana Steak", 139900, "1 kg", "/images/dandana steak.jpg"),
    ("Biqin Steak", 144900, "1 kg", "/images/biqin steak.jpg"),
    ("Qo'y Dandana va Biqini", 154900, "1 kg", "/images/qoy dandana va biqini.jpg"),
    ("Qo'y Qovurg'a", 139900, "1 kg", "/images/qovurg'a.jpg"),
    ("Mol Lahm Go'shti", 169900, "1 kg", "/images/mol lahm go'shti.jpg"),
    ("Qo'y Soni", 164900, "1 kg", "/images/qoy soni.jpg"),
    ("Qo'y Qo'li", 159900, "1 kg", "/images/qoy qoli.jpg"),
    ("Dumba", 109900, "1 kg", "/images/dumba.jpg"),
    ("Dum", 99900, "1 kg", "/images/dum.jpg"),
    ("Qiyma", 139900, "1 kg", "/images/qiyma.jpg"),
    ("Jigar", 99900, "1 kg", "/images/jigar.jpg"),
    ("Yurak", 74900, "1 kg", "/images/yurak.jpg"),
    ("Buyrak", 69900, "1 kg", "/images/buyrak.jpg"),
    ("Til", 119900, "1 kg", "/images/til.jpg"),
    ("Mushak", 129900, "1 kg", "/images/mushak.jpg"),
    ("Suyak", 39900, "1 kg", "/images/suyak.jpg"),
    ("Tuyoq", 49900, "1 kg", "/images/tuyoq.jpg"),
    ("AZIM Marinad", 149900, "1 kg", "/images/about-meat.jpg"),
]


def seed_products(apps, schema_editor):
    Product = apps.get_model("main", "Product")
    for index, (name, price, weight, image) in enumerate(PRODUCTS, start=1):
        Product.objects.update_or_create(
            name=name,
            defaults={
                "description": "AZIM Marinade go'sht markazi mahsuloti",
                "price": price,
                "weight": weight,
                "image": image,
                "is_active": True,
                "sort_order": index,
            },
        )


def unseed_products(apps, schema_editor):
    Product = apps.get_model("main", "Product")
    Product.objects.filter(name__in=[product[0] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
