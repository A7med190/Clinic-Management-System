from django.utils.text import slugify


def generate_unique_slug(model, name, slug_field="slug"):
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def format_currency(amount):
    return f"${amount:,.2f}"
