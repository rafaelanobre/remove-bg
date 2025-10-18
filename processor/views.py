from django.shortcuts import render

def home(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if uploaded_file:
            return render(request, 'processor/home.html', {'message': f'File "{uploaded_file.name}" uploaded successfully.'})
    return render(request, 'processor/home.html')