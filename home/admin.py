from django.contrib import admin
from .models import Company, CompanyVideo

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class CompanyVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_company_name', 'youtube_url')
    search_fields = ('title', 'company__name')

    def get_company_name(self, obj):
        return obj.company.name
    get_company_name.admin_order_field = 'company'  # Allows column order sorting
    get_company_name.short_description = 'Company Name'  # Renames column head

admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyVideo, CompanyVideoAdmin)
