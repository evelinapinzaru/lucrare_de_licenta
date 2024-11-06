from django.http import HttpResponse
import transformers
import torch
import tensorflow

def print_versions(request):
    print('transformers : ' + transformers.__version__)
    print('torch : ' + torch.__version__)
    print('tensorflow : ' + tensorflow.__version__)

    return HttpResponse("The library versions have been printed to the terminal.")
