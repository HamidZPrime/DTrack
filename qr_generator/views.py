from django.shortcuts import get_object_or_404, render
from .models import SupplierQR, ProductQR, CertificateQR

def supplier_detail(request, qr_token):
    supplier_qr = get_object_or_404(SupplierQR, qr_token=qr_token)
    return render(request, 'supplier_detail.html', {'supplier': supplier_qr.supplier})

def product_detail(request, qr_token):
    product_qr = get_object_or_404(ProductQR, qr_token=qr_token)
    return render(request, 'product_detail.html', {'product': product_qr})

def certificate_detail(request, qr_token):
    certificate_qr = get_object_or_404(CertificateQR, qr_token=qr_token)
    return render(request, 'certificate_detail.html', {'certificate': certificate_qr})
