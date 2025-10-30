from django.urls import path

from graphs.views import (GraphView, LoadGraphView, BayeseView, MergeView,
                          GraphStorageView, GraphVisualizationView,
                          CRUDGraphView, BayesTableView)


urlpatterns = [
    path('graph/', GraphView.as_view(), name='graph-list-create'),
    path('graph/<int:id>/', GraphView.as_view(), name='graph-detail'),
    path('polifarmakoterapiya-bayes/', BayeseView.as_view(), name='bayes'),
    path('graph/get_list/', CRUDGraphView.as_view(), name='get_list'),
    path('graph/merge/', MergeView.as_view(), name='merge'),
    path('graphs_from_json_to_db/', LoadGraphView.as_view(),
         name='graphs_from_json_to_db'),
    path('graph/storage_graph/', GraphStorageView.as_view(),
         name='storage_graph'),
    path('graph/visualization/', GraphVisualizationView.as_view(),
         name='visualization'),
	path('statisticFile', BayesTableView.as_view(),
		 name='statisticFile'),
]
