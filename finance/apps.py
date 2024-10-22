from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        import finance.signals

    def create_default_personal_details(self):
        if not PersonalDetails.objects.exists():
            PersonalDetails.objects.create(
                gst_registered=False,
                first_name='Joe',        # You can set default first name here
                last_name='Bloggs',         # You can set default last name here
                email='Joe@gmail.com',             # You can set a default email or leave it blank
                phone='027 1234 567',             # You can set a default phone number or leave it blank
                permanent_income=100000  # Default permanent income
            )
