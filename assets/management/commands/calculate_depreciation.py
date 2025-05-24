from django.core.management.base import BaseCommand
from django.utils import timezone
from assets.models import Asset, DepreciationEntry
from datetime import date
import calendar

class Command(BaseCommand):
    help = 'Calculate monthly depreciation for all active assets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Month to calculate depreciation for (1-12)',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year to calculate depreciation for',
        )

    def handle(self, *args, **options):
        # Get month and year from arguments or use current month
        now = timezone.now()
        month = options['month'] if options['month'] else now.month
        year = options['year'] if options['year'] else now.year
        
        # Validate month
        if month < 1 or month > 12:
            self.stdout.write(self.style.ERROR(f'Invalid month: {month}. Month must be between 1 and 12.'))
            return
            
        # Get last day of month
        last_day = calendar.monthrange(year, month)[1]
        entry_date = date(year, month, last_day)
        
        # Get all active assets
        assets = Asset.objects.filter(status='active')
        
        self.stdout.write(f'Calculating depreciation for {assets.count()} assets for {entry_date}')
        
        created_count = 0
        skipped_count = 0
        
        for asset in assets:
            # Check if depreciation entry already exists for this month
            existing_entry = DepreciationEntry.objects.filter(
                asset=asset,
                entry_date=entry_date
            ).exists()
            
            if existing_entry:
                skipped_count += 1
                continue
                
            # Calculate monthly depreciation amount
            annual_depreciation = asset.purchase_cost * (asset.depreciation_rate / 100)
            monthly_depreciation = annual_depreciation / 12
            
            # Get latest entry to calculate accumulated depreciation
            latest_entry = DepreciationEntry.objects.filter(
                asset=asset,
                entry_date__lt=entry_date
            ).order_by('-entry_date').first()
            
            if latest_entry:
                accumulated_depreciation = latest_entry.accumulated_depreciation + monthly_depreciation
                book_value = latest_entry.book_value - monthly_depreciation
            else:
                accumulated_depreciation = monthly_depreciation
                book_value = asset.purchase_cost - monthly_depreciation
                
            # Ensure book value doesn't go below salvage value
            if book_value < asset.salvage_value:
                monthly_depreciation = max(0, book_value - asset.salvage_value)
                accumulated_depreciation = asset.purchase_cost - asset.salvage_value
                book_value = asset.salvage_value
            
            # Create new depreciation entry
            DepreciationEntry.objects.create(
                asset=asset,
                entry_date=entry_date,
                amount=monthly_depreciation,
                accumulated_depreciation=accumulated_depreciation,
                book_value=book_value,
                posted=False
            )
            
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(
            f'Successfully calculated depreciation for {created_count} assets. '
            f'Skipped {skipped_count} assets with existing entries.'
        ))
