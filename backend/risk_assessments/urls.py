from django.urls import path
from risk_assessments.views import DrugRiskAssessmentView
 
app_name = "risk_assessments"
 
urlpatterns = [
    path(
        "drug-compatibility",
        DrugRiskAssessmentView.as_view(),
        name="drug-compatibility",
    ),
]
 