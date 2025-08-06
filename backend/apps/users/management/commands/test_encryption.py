"""
Management command to test and validate the encryption system
"""
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from utils.encryption import (
    test_encryption_roundtrip, 
    validate_encryption_setup,
    fix_multiple_encrypted_data,
    encrypt_data,
    decrypt_data
)
from apps.users.models import UserProfile
from apps.authentication.models import CustomUser


class Command(BaseCommand):
    help = 'Test and validate the encryption system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-corrupted', 
            action='store_true',
            help='Fix multiply encrypted data'
        )
        parser.add_argument(
            '--validate-all',
            action='store_true', 
            help='Validate all encrypted data in the database'
        )
        parser.add_argument(
            '--test-basic',
            action='store_true',
            help='Run basic encryption tests'
        )

    def handle(self, *args, **options):
        if options['test_basic']:
            self.test_basic_encryption()
        
        if options['fix_corrupted']:
            self.fix_corrupted_data()
        
        if options['validate_all']:
            self.validate_all_data()
        
        # Always run system validation
        self.validate_system()

    def test_basic_encryption(self):
        """Test basic encryption functionality"""
        self.stdout.write("=== Testing Basic Encryption ===")
        
        test_data = "Hello, this is a test message for encryption!"
        
        # Test encryption roundtrip
        try:
            encrypted = encrypt_data(test_data)
            decrypted = decrypt_data(encrypted)
            
            success = test_data == decrypted
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS("✓ Basic encryption test PASSED")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Basic encryption test FAILED")
                )
                self.stdout.write(f"Original: {test_data}")
                self.stdout.write(f"Decrypted: {decrypted}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Basic encryption test FAILED with error: {e}")
            )

    def validate_system(self):
        """Validate encryption system configuration"""
        self.stdout.write("=== System Validation ===")
        
        validation = validate_encryption_setup()
        
        if validation['encryption_enabled']:
            self.stdout.write(self.style.SUCCESS("✓ Encryption is enabled"))
        else:
            self.stdout.write(self.style.ERROR("✗ Encryption is not enabled"))
        
        if validation['key_configured']:
            self.stdout.write(self.style.SUCCESS("✓ Encryption key is configured"))
        else:
            self.stdout.write(self.style.ERROR("✗ Encryption key is not configured"))
        
        if validation['roundtrip_test']:
            self.stdout.write(self.style.SUCCESS("✓ Roundtrip test passed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Roundtrip test failed"))
        
        if validation['recommendations']:
            self.stdout.write(self.style.WARNING("Recommendations:"))
            for rec in validation['recommendations']:
                self.stdout.write(f"  - {rec}")

    def fix_corrupted_data(self):
        """Fix multiply encrypted data"""
        self.stdout.write("=== Fixing Corrupted Data ===")
        
        # Fix UserProfile data
        self.stdout.write("Fixing UserProfile data...")
        stats = fix_multiple_encrypted_data(
            UserProfile, 
            ['phone_number', 'address', 'bio']
        )
        
        self.stdout.write(f"UserProfile Stats:")
        self.stdout.write(f"  Processed: {stats['processed']}")
        self.stdout.write(f"  Fixed: {stats['fixed']}")
        self.stdout.write(f"  Skipped: {stats['skipped']}")
        self.stdout.write(f"  Failed: {stats['failed']}")
        
        # Fix CustomUser data
        self.stdout.write("Fixing CustomUser data...")
        stats = fix_multiple_encrypted_data(
            CustomUser, 
            ['first_name', 'last_name', 'full_name', 'phone_number', 'address']
        )
        
        self.stdout.write(f"CustomUser Stats:")
        self.stdout.write(f"  Processed: {stats['processed']}")
        self.stdout.write(f"  Fixed: {stats['fixed']}")
        self.stdout.write(f"  Skipped: {stats['skipped']}")
        self.stdout.write(f"  Failed: {stats['failed']}")

    def validate_all_data(self):
        """Validate all encrypted data in the database"""
        self.stdout.write("=== Validating All Data ===")
        
        # Check UserProfile data
        self.stdout.write("Checking UserProfile data...")
        profiles_checked = 0
        profiles_with_issues = 0
        
        for profile in UserProfile.objects.all():
            profiles_checked += 1
            has_issues = False
            
            for field in profile.ENCRYPTED_FIELDS:
                try:
                    decrypted = profile.get_decrypted_field(field)
                    # If decryption worked, check if result makes sense
                    if decrypted and len(decrypted) > 500:
                        # Suspiciously long, might still be encrypted
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠ {profile.user.username}.{field} might still be encrypted (length: {len(decrypted)})"
                            )
                        )
                        has_issues = True
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ {profile.user.username}.{field} decryption failed: {e}"
                        )
                    )
                    has_issues = True
            
            if has_issues:
                profiles_with_issues += 1
        
        self.stdout.write(f"UserProfiles checked: {profiles_checked}")
        self.stdout.write(f"UserProfiles with issues: {profiles_with_issues}")
        
        # Check CustomUser data
        self.stdout.write("Checking CustomUser data...")
        users_checked = 0
        users_with_issues = 0
        
        for user in CustomUser.objects.all():
            users_checked += 1
            has_issues = False
            
            for field in user.ENCRYPTED_FIELDS:
                try:
                    decrypted = user.get_decrypted_field(field)
                    # If decryption worked, check if result makes sense
                    if decrypted and len(decrypted) > 500:
                        # Suspiciously long, might still be encrypted
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠ {user.username}.{field} might still be encrypted (length: {len(decrypted)})"
                            )
                        )
                        has_issues = True
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ {user.username}.{field} decryption failed: {e}"
                        )
                    )
                    has_issues = True
            
            if has_issues:
                users_with_issues += 1
        
        self.stdout.write(f"Users checked: {users_checked}")
        self.stdout.write(f"Users with issues: {users_with_issues}")
        
        if profiles_with_issues == 0 and users_with_issues == 0:
            self.stdout.write(self.style.SUCCESS("✓ All data validated successfully!"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Found issues in {profiles_with_issues + users_with_issues} records"
                )
            )
