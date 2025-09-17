from django.urls import path

from graphs.views import (GraphView, LoadGraphView, BayeseView, MergeView,
                          GraphStorageView)


urlpatterns = [
    path('graph/', GraphView.as_view(), name='graph-list-create'),
    path('graph/<int:id>/', GraphView.as_view(), name='graph-detail'),
    path('polifarmakoterapiya-bayes/', BayeseView.as_view(), name='bayes'),
    path('graph/merge/', MergeView.as_view(), name='merge'),
    path('graphs_from_json_to_db/', LoadGraphView.as_view(),
         name='graphs_from_json_to_db'),
    path('graph/storage_graph/', GraphStorageView.as_view(),
         name='storage_graph'),
]
