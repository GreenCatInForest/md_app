from django.shortcuts import render
from django.http import JsonResponse

def is_ajax(request):
    # return request.headers.get('x-requested-with') == 'XMLHttpRequest'
    return request.GET.get('ajax') == '1'


def handle_form_errors_ajax_http(request, form, formset):
    if is_ajax(request):
        form_errors = {field: errors.get_json_data(escape_html=True) for field, errors in form.errors.items()}

        formset_errors = []
        if formset:
            for f in formset.forms:
                if f.errors:
                    formset_errors.append({field: errors.get_json_data(escape_html=True) for field, errors in form.errors.items()})
                else:
                    formset_errors.append({})
        else:
            formset_errors = None
        
        errors = {
            'form_errors': form_errors,
            'formset_errors': formset_errors,
        }
        return JsonResponse({'status':'error', 'errors':errors}, status=400)
    else:
        context = {
            'form':form,
            'formset':formset
        }
        return render(request, 'reports/report.html', context)

