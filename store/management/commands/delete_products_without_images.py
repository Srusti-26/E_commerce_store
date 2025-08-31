from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Delete products that do not have images'

    def handle(self, *args, **options):
        products_without_images = Product.objects.filter(image='')
        count = products_without_images.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No products without images found.'))
            return
        
        self.stdout.write(f'Found {count} products without images:')
        for product in products_without_images:
            self.stdout.write(f'- {product.name} (ID: {product.id})')
        
        products_without_images.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} products without images.'))