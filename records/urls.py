from django.urls import path
from .views_web import (
    record_list, record_detail, write_record,
    add_prescription, lab_result_list, upload_lab_result,
)

app_name = "records"

urlpatterns = [
    path("",                                    record_list,       name="list"),
    path("<int:pk>/",                           record_detail,     name="detail"),
    path("write/<int:appointment_pk>/",         write_record,      name="write"),
    path("<int:record_pk>/prescriptions/add/",  add_prescription,  name="add-prescription"),  # HTMX
    path("labs/",                               lab_result_list,   name="lab-list"),
    path("labs/upload/<int:appointment_pk>/",   upload_lab_result, name="upload-lab"),
]
