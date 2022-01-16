{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 0,
   "id": "518cf836",
   "metadata": {},
   "outputs": [],
   "source": [
    "from django.urls import path\n",
    "from . import views\n",
    " \n",
    "urlpatterns = [\n",
    "    path('callback', views.callback)\n",
    "    path('data', views.data)\n",
    "    path('images', views.file)\n",
    "]"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

from django.urls import path
from . import views
 
urlpatterns = [
    path('callback', views.callback),
    path('data', views.data),
    path('images', views.images),
    path('uploadImage',views.uploadImage),
    path('uploadVideo',views.uploadVideo),
    path('resultImage',views.resultImage),
    path('resultVideo',views.resultVideo),
    
]
