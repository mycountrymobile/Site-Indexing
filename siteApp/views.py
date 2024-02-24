import csv
import random
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import SiteInfo,Project
from django.db import models
from django.db.models import Count, Max,Q

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 EdgA/91.0.864.59',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/76.0.4017.177',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    
]

def is_indexed(site_url):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(site_url, headers=headers)
        
        if response.status_code == 200:
            if "noindex" not in response.text.lower() and "X-Robots-Tag" not in response.headers:
                return True
            else:
                return False
        else:
            return None  
    except Exception as e:
        return None

from django.db import IntegrityError
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            csv_file = request.FILES['file']

            # Check if the project already exists
            project, created = Project.objects.get_or_create(name=project_name)

            reader = csv.reader(csv_file.read().decode('utf-8').splitlines())

            for row in reader:
                if len(row) > 0:
                    url = row[0]
                    indexing_status = is_indexed(url)

                    existing_record = SiteInfo.objects.filter(url=url, project=project).first()

                    if existing_record:
                        existing_record.is_indexed = indexing_status
                        existing_record.save()
                    else:
                        SiteInfo.objects.create(url=url, is_indexed=indexing_status, project=project)

            return redirect('success')
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})

def success(request):
    return render(request,'success.html')

def view(request):
    all_urls = SiteInfo.objects.all()

    is_indexed_filter = request.GET.get('is_indexed')
    if is_indexed_filter in ['Yes', 'No']:
        is_indexed_filter = (is_indexed_filter == 'Yes')
        all_urls = all_urls.filter(is_indexed=is_indexed_filter)
    elif is_indexed_filter == 'Not Specified':
        all_urls = all_urls.filter(is_indexed__isnull=True)
        
    project_info_list = Project.objects.annotate(
        project_name=models.F('name'),
        upload_time=models.Max('siteinfo__created_at'),
        indexed_count=Count('siteinfo', filter=models.Q(siteinfo__is_indexed=True)),
        not_indexed_count=Count('siteinfo', filter=models.Q(siteinfo__is_indexed=False)),
        not_specified_count=Count('siteinfo', filter=models.Q(siteinfo__is_indexed=None)),
    ).values('project_name', 'upload_time', 'indexed_count', 'not_indexed_count','not_specified_count')

    context = {'all_urls': all_urls, 'is_indexed_filter': is_indexed_filter,'project_info_list': project_info_list}
    return render(request,'view.html',context )
    



def download_data(request):
    project_name = request.GET.get('project_name')
    data_type = request.GET.get('data_type')

    project_id = Project.objects.filter(name=project_name).values('id').first()['id']

    site_info_query = SiteInfo.objects.filter(project_id=project_id)

    if data_type == 'indexed':
        site_info_query = site_info_query.filter(is_indexed=True)
    elif data_type == 'not_specified':
        site_info_query = site_info_query.filter(is_indexed=None)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project_name}_{data_type}_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['URL', 'Is Indexed'])

    for site_info in site_info_query:
        is_indexed = 'Yes' if site_info.is_indexed else 'No'
        writer.writerow([site_info.url, is_indexed])

    return response
