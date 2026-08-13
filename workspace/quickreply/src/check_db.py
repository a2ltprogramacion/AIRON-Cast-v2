import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickreply.settings')
django.setup()

from reply.models import MessageTemplate

templates = MessageTemplate.objects.all()
print(f"Total templates: {templates.count()}")
print("\nÚltimos 5 templates:")
for t in templates.order_by('-id')[:5]:
    print(f"  ID: {t.id} | {t.titulo[:50]} | Cat: {t.categoria}")

print("\nTemplates con 'bomba' (case-insensitive):")
for t in templates.filter(titulo__icontains='bomba'):
    print(f"  {t.titulo}")
