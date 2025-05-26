from assets.models import AssetCategory, AssetSubcategory
from locations.models import Branch # Branch is a proxy for Location
from employees.models import Employee

print("Creating base data...")

try:
    cat, created = AssetCategory.objects.get_or_create(
        name="أثاث مكتبي", 
        defaults={
            'description': "أثاث للمكاتب", 
            'depreciation_rate': 10.0
        }
    )
    print(f"- Category 'أثاث مكتبي' {'created' if created else 'already exists'}.")

    subcat, created = AssetSubcategory.objects.get_or_create(
        category=cat, 
        name="مكاتب",
        defaults={
            'description': "مكاتب خشبية ومعدنية"
        }
    )
    print(f"- Subcategory 'مكاتب' {'created' if created else 'already exists'}.")

    # Use Branch proxy model which inherits from Location
    branch, created = Branch.objects.get_or_create(
        name="الفرع الرئيسي",
        defaults={
            'address': "123 الشارع الرئيسي"
        }
    )
    print(f"- Branch (Location) 'الفرع الرئيسي' {'created' if created else 'already exists'}.")

    # Use 'location=branch' as Employee model expects a Location instance
    emp, created = Employee.objects.get_or_create(
        employee_id="EMP001",
        defaults={
            'name': "موظف الاختبار", 
            'position': "مسؤول IT", # Added position as it's required
            'department': "IT", 
            'location': branch # Corrected field name
        }
    )
    print(f"- Employee 'موظف الاختبار' (EMP001) {'created' if created else 'already exists'}.")

    print("Base data creation/verification complete.")

except Exception as e:
    print(f"An error occurred: {e}")


