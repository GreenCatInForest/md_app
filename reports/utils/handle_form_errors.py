from django.shortcuts import render
from django.http import JsonResponse

def handle_form_errors (request, form, formset):
    if (request.headers.get('x-requested-with') == 'XMLHttpRequest'):
                    form_errors = {field: errors.get_json_data (escape_html = True) for field, errors in form.errors.items()}

                    formset_errors = []
                    for form in formset.forms: 
                        if form.errors:
                            formset_errors.append({field: errors.get_json_data (escape_html = True) for field, errors in form.errors.items()})
                        else:
                            formset_errors.append({})
                    errors = {
                        'form_errors': form_errors,
                        'formset_errors': formset_errors,
                    }
                    return JsonResponse({'status':'error', 'errors':errors}, status=400)
    else:
        return render(request, 'reports/report.html', {'form': form, 'formset': formset})