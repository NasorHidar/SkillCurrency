from django.shortcuts import render, redirect
from .forms import IdentityUploadForm

def identity_vault(request):
    if request.method == 'POST':
        form = IdentityUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # In the future, doc.user = request.user goes here
            # form.save() 
            return redirect('vault_success') 
        else:
            # If the form fails validation (e.g., missing files)
            return redirect('vault_deny')
            
    else:
        form = IdentityUploadForm()

    context = {'form': form}
    return render(request, 'identity/identity_vault.html', context)

# New Views for the redirect pages
def vault_success(request):
    return render(request, 'identity/success.html')

def vault_deny(request):
    return render(request, 'identity/deny.html')