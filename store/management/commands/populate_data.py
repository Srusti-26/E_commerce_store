from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Category, Product
from decimal import Decimal
import requests
import os

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Install requests if not available
        try:
            import requests
        except ImportError:
            self.stdout.write('Installing requests library...')
            os.system('pip install requests')
            import requests
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Clothing', 'slug': 'clothing'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Home & Garden', 'slug': 'home-garden'},
            {'name': 'Sports', 'slug': 'sports'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products with your actual images
        products_data = [
            {
                'name': 'Premium Laptop',
                'slug': 'premium-laptop',
                'category': 'electronics',
                'description': 'High-performance laptop perfect for work and gaming with latest processor and graphics.',
                'price': Decimal('999.99'),
                'image_path': 'products/2025/07/29/laptop.jpg',
            },
            {
                'name': 'Wireless Headphones',
                'slug': 'wireless-headphones',
                'category': 'electronics',
                'description': 'Crystal clear sound with noise cancellation technology and 30-hour battery life.',
                'price': Decimal('199.99'),
                'image_path': 'products/2025/07/29/Wireless Headphones.jpg',
            },
            {
                'name': 'Smartphone Pro',
                'slug': 'smartphone-pro',
                'category': 'electronics',
                'description': 'Latest smartphone with advanced camera system and 5G connectivity.',
                'price': Decimal('699.99'),
                'image_path': 'products/2025/07/29/Smartphone Pro.png',
            },
            {
                'name': 'Smart Watch',
                'slug': 'smart-watch',
                'category': 'electronics',
                'description': 'Feature-rich smartwatch with health monitoring and GPS tracking.',
                'price': Decimal('299.99'),
                'image_path': 'products/2025/07/29/Smart Watch.webp',
            },
            {
                'name': 'Running Shoes',
                'slug': 'running-shoes',
                'category': 'sports',
                'description': 'Professional running shoes with advanced cushioning and breathable material.',
                'price': Decimal('129.99'),
                'image_path': 'products/2025/07/29/Running Shoes.jpg',
            },
            {
                'name': 'Programming Guide',
                'slug': 'programming-guide',
                'category': 'books',
                'description': 'Complete guide to modern programming languages and best practices.',
                'price': Decimal('49.99'),
                'image_path': 'products/2025/07/29/Programming Guide.jpg',
            },

            {
                'name': 'Yoga Mat',
                'slug': 'yoga-mat',
                'category': 'sports',
                'description': 'High-quality mat for your yoga and fitness routines.',
                'price': Decimal('39.99'),
                'image_path': 'products/2025/07/29/yoga-mat.jpg',
            },
            {
                'name': 'Gaming Mouse',
                'slug': 'gaming-mouse',
                'category': 'electronics',
                'description': 'Precision gaming mouse with RGB lighting and programmable buttons.',
                'price': Decimal('79.99'),
                'image_path': 'products/2025/07/29/gaming-mouse.jpg',
            },
        ]
        
        for prod_data in products_data:
            try:
                category = Category.objects.get(slug=prod_data['category'])
                product, created = Product.objects.get_or_create(
                    slug=prod_data['slug'],
                    defaults={
                        'name': prod_data['name'],
                        'category': category,
                        'description': prod_data['description'],
                        'price': prod_data['price'],
                        'available': True,
                    }
                )
                if created:
                    # Set the image path to your uploaded images
                    if 'image_path' in prod_data:
                        product.image = prod_data['image_path']
                        product.save()
                        self.stdout.write(f'Set image for: {product.name} -> {prod_data["image_path"]}')
                    
                    self.stdout.write(f'Created product: {product.name}')
                else:
                    # Update existing product with image if not set
                    if not product.image and 'image_path' in prod_data:
                        product.image = prod_data['image_path']
                        product.save()
                        self.stdout.write(f'Updated image for existing product: {product.name}')
            except Category.DoesNotExist:
                self.stdout.write(f'Category {prod_data["category"]} not found')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with your images!')
        )
        self.stdout.write('All products now use your uploaded images from media/products/2025/07/29/')