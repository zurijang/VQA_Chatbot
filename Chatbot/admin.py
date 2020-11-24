from django.contrib import admin
from .models import DATA_WORKER, DATA_IMAGE, QUESTION, ANSWER

class WORKERAdmin(admin.ModelAdmin):
    list_display = ['WORKER_ID', 'WORKER_NAME']
    search_fields = ['WORKER_ID', 'WORKER_NAME']

class IMAGEAdmin(admin.ModelAdmin):
    list_display = ['IMAGE_ID', 'IMAGE', 'WORKER_ID', 'STATUS', 'DATE_WORK']
    search_fields = ['IMAGE_ID', 'WORKER_ID', 'STATUS', 'DATE_WORK']

class QUESTIONAdmin(admin.ModelAdmin):
    list_display = ['QUESTION_ID', 'IMAGE_ID', 'QUESTION', 'STATUS' ,'QUESTION_CNT']
    search_fields = ['IMAGE_ID', 'STATUS']

class ANSWERAdmin(admin.ModelAdmin):
    list_display = ['ANSWER_ID', 'QUESTION_ID', 'ANSWER']
    search_fields = ['QEUSTION_ID']

admin.site.register(DATA_WORKER, WORKERAdmin)
admin.site.register(DATA_IMAGE, IMAGEAdmin)
admin.site.register(QUESTION, QUESTIONAdmin)
admin.site.register(ANSWER, ANSWERAdmin)