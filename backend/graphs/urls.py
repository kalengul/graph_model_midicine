from django.urls import path

from graphs.views import (GraphView, LoadGraphView, BayeseView, MergeView,
                          GraphStorageView)


urlpatterns = [
    path('graphs/', GraphView.as_view(), name='graph-list-create'),
    path('graphs/<int:id>/', GraphView.as_view(), name='graph-detail'),
    path('polifarmakoterapiya-bayes/', BayeseView.as_view(), name='bayes'),
    path('graphs/merge/', MergeView.as_view(), name='merge'),
    path('graphs_from_json_to_db/', LoadGraphView.as_view(),
         name='graphs_from_json_to_db'),
    path('storage_graph/', GraphStorageView.as_view(), name='storage_graph'),
]
