from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from assets.models import Asset, DepreciationEntry, AssetTransfer, AssetDisposal
from accounts.models import Role

class Command(BaseCommand):
    help = 'Set up initial roles and permissions for the fixed assets system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up roles and permissions...')
        
        # Create content types for our models if they don't exist
        asset_ct = ContentType.objects.get_for_model(Asset)
        depreciation_ct = ContentType.objects.get_for_model(DepreciationEntry)
        transfer_ct = ContentType.objects.get_for_model(AssetTransfer)
        disposal_ct = ContentType.objects.get_for_model(AssetDisposal)
        
        # Define roles and their permissions
        roles = {
            'admin': {
                'name': 'مدير النظام',
                'permissions': [
                    # Asset permissions
                    {'codename': 'add_asset', 'name': 'Can add asset', 'content_type': asset_ct},
                    {'codename': 'change_asset', 'name': 'Can change asset', 'content_type': asset_ct},
                    {'codename': 'delete_asset', 'name': 'Can delete asset', 'content_type': asset_ct},
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    # Depreciation permissions
                    {'codename': 'add_depreciationentry', 'name': 'Can add depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'change_depreciationentry', 'name': 'Can change depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'delete_depreciationentry', 'name': 'Can delete depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'view_depreciationentry', 'name': 'Can view depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'post_depreciationentry', 'name': 'Can post depreciation entry', 'content_type': depreciation_ct},
                    # Transfer permissions
                    {'codename': 'add_assettransfer', 'name': 'Can add asset transfer', 'content_type': transfer_ct},
                    {'codename': 'change_assettransfer', 'name': 'Can change asset transfer', 'content_type': transfer_ct},
                    {'codename': 'delete_assettransfer', 'name': 'Can delete asset transfer', 'content_type': transfer_ct},
                    {'codename': 'view_assettransfer', 'name': 'Can view asset transfer', 'content_type': transfer_ct},
                    # Disposal permissions
                    {'codename': 'add_assetdisposal', 'name': 'Can add asset disposal', 'content_type': disposal_ct},
                    {'codename': 'change_assetdisposal', 'name': 'Can change asset disposal', 'content_type': disposal_ct},
                    {'codename': 'delete_assetdisposal', 'name': 'Can delete asset disposal', 'content_type': disposal_ct},
                    {'codename': 'view_assetdisposal', 'name': 'Can view asset disposal', 'content_type': disposal_ct},
                ],
            },
            'asset_entry': {
                'name': 'مدخل بيانات الأصول',
                'permissions': [
                    {'codename': 'add_asset', 'name': 'Can add asset', 'content_type': asset_ct},
                    {'codename': 'change_asset', 'name': 'Can change asset', 'content_type': asset_ct},
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    {'codename': 'view_depreciationentry', 'name': 'Can view depreciation entry', 'content_type': depreciation_ct},
                ],
            },
            'depreciation_manager': {
                'name': 'مدير الإهلاك',
                'permissions': [
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    {'codename': 'add_depreciationentry', 'name': 'Can add depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'view_depreciationentry', 'name': 'Can view depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'post_depreciationentry', 'name': 'Can post depreciation entry', 'content_type': depreciation_ct},
                ],
            },
            'report_viewer': {
                'name': 'مشاهد التقارير',
                'permissions': [
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    {'codename': 'view_depreciationentry', 'name': 'Can view depreciation entry', 'content_type': depreciation_ct},
                    {'codename': 'view_assettransfer', 'name': 'Can view asset transfer', 'content_type': transfer_ct},
                    {'codename': 'view_assetdisposal', 'name': 'Can view asset disposal', 'content_type': disposal_ct},
                ],
            },
            'transfer_manager': {
                'name': 'مدير نقل الأصول',
                'permissions': [
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    {'codename': 'add_assettransfer', 'name': 'Can add asset transfer', 'content_type': transfer_ct},
                    {'codename': 'view_assettransfer', 'name': 'Can view asset transfer', 'content_type': transfer_ct},
                ],
            },
            'disposal_manager': {
                'name': 'مدير استبعاد الأصول',
                'permissions': [
                    {'codename': 'view_asset', 'name': 'Can view asset', 'content_type': asset_ct},
                    {'codename': 'add_assetdisposal', 'name': 'Can add asset disposal', 'content_type': disposal_ct},
                    {'codename': 'view_assetdisposal', 'name': 'Can view asset disposal', 'content_type': disposal_ct},
                ],
            },
        }
        
        # Create custom permission for posting depreciation entries
        post_depreciation_perm, created = Permission.objects.get_or_create(
            codename='post_depreciationentry',
            name='Can post depreciation entry',
            content_type=depreciation_ct,
        )
        if created:
            self.stdout.write(f'Created custom permission: {post_depreciation_perm}')
        
        # Create roles and assign permissions
        for role_code, role_data in roles.items():
            # Create or get Django Group
            group, created = Group.objects.get_or_create(name=role_data['name'])
            if created:
                self.stdout.write(f'Created group: {group.name}')
            
            # Create or get our custom Role
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': f'Role for {role_data["name"]}'}
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')
            
            # Assign permissions to group
            for perm_data in role_data['permissions']:
                try:
                    # Get or create permission
                    perm, created = Permission.objects.get_or_create(
                        codename=perm_data['codename'],
                        content_type=perm_data['content_type'],
                        defaults={'name': perm_data['name']}
                    )
                    
                    # Add permission to group
                    group.permissions.add(perm)
                    
                    self.stdout.write(f'Added permission {perm.codename} to {group.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error adding permission {perm_data["codename"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully set up roles and permissions'))
