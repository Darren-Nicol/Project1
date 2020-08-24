import markdown2
import secrets

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse

from . import util
from markdown2 import Markdown

markdowner = Markdown()

#Create a class for a new entry form for adding new content to the entries file in markdown.

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title",widget =forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 6}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(),required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonEntry.html", {
        "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
        "entry": markdowner.convert(entryPage),
        "entryTitle": entry
        })

#Create a search function so when requested in layout.html the entries file is searched for input.

def search(request):
    value = request.GET.get('q','') #method set to GET in layout
    if(util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': value }))
        #This renders the entry by reverse engineerinig the url from the enntry, then returns the markdown file.
    else:
        subStringEntries = []
        for entry in util.list_entries(): #this sets a forloop on the list of  current entries
            if value.upper() in entry.upper(): #if value  passed in (based on  caps is same as the entry then the entry is appended to the substrinng list)
                subStringEntries.append(entry)
        #then render the  index.html passing in these values
        return render(request, "encyclopedia/index.html", {
        "entries": subStringEntries,
        "search": True,
        "value": value
    })
# The index.html file then executes logic, if search is true returns statement, then executes a  for loop that runs  through the substringentries list and renders url links to the page.


#Create a new page, if it exists add a warning to state that it is already in the database and allow edit.

def newPage(request):
    if request.method == "POST":
        form =  NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry':title}))
            else:
                return render(request, "encyclopedia/newPage.html", {
                "form": form,
                "existing":True,
                "entry": title
                })
        else:
            return render(request, "encyclopedia/newPage.html", {
            "form": form,
            "existing":False
            })
    else:
        return render(request, "encyclopedia/newPage.html", {
        "form": NewPageForm(),
        "existing":False
        })

#Should it already exist create an edit function so changes can be made.

def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonEntry.html", {
        "entryTitle": entry
        })
    else:
        form = NewPageForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newPage.html", {
        "form": form,
        "edit": form.fields["edit"].initial,
        "entryTitle": form.fields["title"].initial
        })

#Create a random page request, a link that renders a random page.

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomEntry}))

#### End ####
