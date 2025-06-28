from django.db import migrations

def forwards_func(apps, schema_editor):
    Article = apps.get_model('library_admin', 'Article')
    Category = apps.get_model('library_admin', 'Category')
    from django.db import transaction
    with transaction.atomic():
        # Find all unique string categories in Article
        unique_cats = set(
            Article.objects.exclude(category=None).values_list('category', flat=True)
        )
        # Create Category objects for each unique string
        cat_map = {}
        for cat_name in unique_cats:
            if not cat_name:
                continue
            cat_obj, created = Category.objects.get_or_create(name=cat_name)
            cat_map[cat_name] = cat_obj
        # Update Article.category to point to the correct Category
        for article in Article.objects.all():
            if article.category and isinstance(article.category, str):
                cat_obj = cat_map.get(article.category)
                if cat_obj:
                    article.category = cat_obj
                    article.save()

def backwards_func(apps, schema_editor):
    # No-op: don't reverse
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('library_admin', '0015_category_keyword_alter_article_category_and_more'),
    ]
    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ] 