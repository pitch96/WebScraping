from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from scraping import scraping_website

def members(request):
    template = loader.get_template("myfirst.html")
    return HttpResponse(template.render())

@csrf_exempt
def test(request):
    if request.method == 'POST':
        url = json.loads(request.body)
        input_url = url["url"]
        print(input_url)
        scraping_website(input_url)
        return HttpResponse("Successfully scraped")