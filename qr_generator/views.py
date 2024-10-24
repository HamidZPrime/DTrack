from django.shortcuts import get_object_or_404, render
from .models import SupplierQR, ProductQR, CertificateQR

def supplier_detail(request, qr_token):
    supplier_qr = get_object_or_404(SupplierQR, qr_token=qr_token)
    supplier = supplier_qr.supplier
    profile = getattr(supplier, 'profile', None)  # Retrieve the profile if it exists
    return render(request, 'qr_generator/supplier_detail.html', {
        'supplier': supplier,
        'profile': profile
    })

def product_detail(request, qr_token):
    product_qr = get_object_or_404(ProductQR, qr_token=qr_token)
    supplier = product_qr.supplier
    profile = getattr(supplier, 'profile', None)  # Retrieve the profile if it exists
    return render(request, 'qr_generator/product_detail.html', {
        'product': product_qr,
        'supplier': supplier,
        'profile': profile
    })

def certificate_detail(request, qr_token):
    certificate_qr = get_object_or_404(CertificateQR, qr_token=qr_token)
    supplier = certificate_qr.supplier
    profile = getattr(supplier, 'profile', None)  # Retrieve the profile if it exists
    return render(request, 'qr_generator/certificate_detail.html', {
        'certificate': certificate_qr,
        'supplier': supplier,
        'profile': profile
    })
