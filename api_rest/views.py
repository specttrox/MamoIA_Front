from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, MedicalImageUploadForm
from .models import MedicalImageUpload
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from api_rest.models import User
from django.http import HttpResponse
# from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# ----------------------------------------
# View para a página inicial (home) - faz login e redireciona
# ----------------------------------------
def home(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Usa o mecanismo de autenticação do Django (seguro e extensível)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get("next") or request.POST.get("next") or "upload_image"
                return redirect(next_url)
            else:
                return render(request, "home.html", {"login_error": "Usuário inativo."})
        else:
            return render(request, "home.html", {"login_error": "Credenciais inválidas."})

    return render(request, "home.html")


# ----------------------------------------
# View de Cadastro - cadastro.html
# ----------------------------------------
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password1"])
                user.save()

                # Autentica e faz login imediatamente após o cadastro
                user = authenticate(request, username=user.email, password=form.cleaned_data["password1"])
                if user:
                    login(request, user)

                messages.success(request, "Cadastro realizado com sucesso.")
                return redirect("home")
            except Exception as e:
                print(f"Erro ao salvar o usuário: {e}")
                messages.error(request, "Ocorreu um erro ao tentar salvar o cadastro.")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomUserCreationForm()
    return render(request, "cadastro.html", {"form": form})


# ----------------------------------------
# View de upload de imagem médica - após login/cadastro
# ----------------------------------------
@login_required
def upload_image(request):
    if request.method == "POST":
        form = MedicalImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            upload.generate_report()

            messages.success(request, "Upload realizado com sucesso!")
            return redirect(reverse("view_report", kwargs={"upload_id": upload.id}))
        else:
            messages.error(request, "Houve um erro ao fazer o upload. Por favor, tente novamente.")
    else:
        form = MedicalImageUploadForm()

    return render(request, "upload_image.html", {"form": form})


# ----------------------------------------
# View para visualizar o laudo
# ----------------------------------------
@login_required
def view_report(request, upload_id):
    upload = MedicalImageUpload.objects.get(id=upload_id, user=request.user)
    uploads = MedicalImageUpload.objects.filter(user=request.user).order_by("-upload_date")
    return render(request, "view_report.html", {"upload": upload, "uploads": uploads})


# ----------------------------------------
# View para exportar o laudo em PDF
# ----------------------------------------
@login_required
def export_pdf(request, upload_id):
    upload = MedicalImageUpload.objects.get(id=upload_id, user=request.user)
    html_string = render_to_string("view_report.html", {"upload": upload})
    # html = HTML(string=html_string)
    # pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="laudo_{upload_id}.pdf"'
    return response


# ----------------------------------------
# View para enviar o laudo por e-mail
# ----------------------------------------
@login_required
def send_email(request, upload_id):
    upload = MedicalImageUpload.objects.get(id=upload_id, user=request.user)
    email = EmailMessage(
        subject=f"Laudo da Imagem - {upload.upload_date}",
        body=f"Aqui está o laudo para a imagem enviada em {upload.upload_date}: {upload.report}",
        from_email="seu_email@gmail.com",  # ideal substituir por settings.DEFAULT_FROM_EMAIL
        to=[request.user.email],
    )
    email.send()
    messages.success(request, "Laudo enviado por email com sucesso.")
    return redirect("view_report", upload_id=upload.id)
