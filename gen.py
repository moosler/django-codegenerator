import os
import json

functions = {
    "filters": {
        "fileName": "filters.py",
        "funcName": "genFilter",
        "result": "",
    },
    "tables": {
        "fileName": "tables.py",
        "funcName": "genTable",
        "result": "",
    },
    "forms": {
        "fileName": "forms.py",
        "funcName": "genForm",
        "result": "",
    },
    "views": {
        "fileName": "views.py",
        "funcName": "genViews",
        "result": "",
    },
    "urls": {
        "fileName": "urls.py",
        "funcName": "genUrls",
        "result": "",
    },
}

templates = {
    "fileName": "temaplates.py",
    "funcName": {
        "index": "setIndexTemplate",
        "edit": "setEditTemplate",
    },
    "result": {
        "index": "",
        "edit": "",
        # "delete" : "",
    },
}

# Example how things shoudld be extracted from the model
# device = {
#     "name": "Device",
#     "attributes": {
#         "name": "char",
#         "rack_id": "int",
#         "netelements": "foreign",
#     },
#     "tableName": "devices"
# }
# models = [device]
appName = "traffic"
models = []
space = "    "
s = space
s2 = s+s
s3 = s+s+"   "
s4 = "    "


def setStrings():
    for model in models:
        for key, value in functions.items():
            funcName = value["funcName"]
            value["result"] += globals()[funcName](model)


def genFilter(model):
    names = []
    for name, type in model["attributes"].items():
        typ = "['icontains']"
        if type == "int":
            typ = "['exact']"
        elif type == "foreign":
            typ = "['exact']"
        names.append("'"+name+"' :  "+typ)
    fieldNames = ",\n ***".join(names)
    fieldNames = fieldNames.replace('***', s3)

    str = '''class {model}Filter(django_filters.FilterSet):

    class Meta:
        model = {model}
        fields = {{
            {fields}
        }}
'''.format(model=model["name"], fields=fieldNames)
    str += "\n\n"
    return str


def genTable(model):
    fieldNames = ','.join('"{0}"'.format(w) for w in model["attributes"])
    str = '''class {model}Table(BaseTable):

    class Meta(BaseTable.Meta):
        model = {model}
        fields = ({fields})
    '''.format(model=model["name"], fields=fieldNames)
    str += "\n\n"
    return str


def genForm(model):
    # fieldNames = ','.join('"{0}"'.format(w) for w in attributes)
    str = '''class {model}Form(forms.ModelForm):

    class Meta:
        model = {model}
        app_label = '{app}'
        db_table = '{table}'
        fields = "__all__"
    '''.format(model=model["name"], table=model["tableName"], app=appName)
    str += "\n\n"
    return str


def genViews(model):
    # fieldNames = ','.join('"{0}"'.format(w) for w in attributes)
    lower = model["name"].lower()
    str = '''class {model}IndexView(BaseView):
    template_name = '{lower}s/index.html'
    model = {model}
    filterset_class = {model}
    table_class = tables.{model}Table
    filter_class = filters.{model}Filter
    paginator_class = LazyPaginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class {model}EditView(ObjectEditView):
    template_name = '{model}s/edit.html'
    queryset = {model}.objects.all()
    model_form = forms.{model}Form
    '''.format(model=model["name"], lower=lower)
    str += "\n\n"
    return str


def genUrls(model):
    lower = model["name"].lower()
    str = '''path('{lower}s/', views.{model}IndexView.as_view(), name='{lower}_index'),
path('{lower}s/add', views.{model}EditView.as_view(), name='{lower}_add'),
path('{lower}s/edit/<int:pk>', views.{model}EditView.as_view(), name='{lower}_edit'),
    '''.format(model=model["name"], lower=lower)
    str += "\n\n"
    return str


## Templates ###

def setIndexTemplate(model):
    lower = model["name"].lower()
    str = '''{{% extends "layouts/base.html" %}}
{{% load helpers %}}
{{% block title %}} Index {{% endblock %}}
{{% block stylesheets %}}{{% endblock stylesheets %}}
{{% block content %}}
{{% load render_table from django_tables2 %}}
<div class="container-fluid">
  <div class="row">
    <div class="col-md-auto">
      {{% if table %}}
      {{% render_table table %}}
      {{% else %}}
      <p>No data are available.</p>
      {{% endif %}}
    </div>
    <div class="col-sm-auto noprint">
      {{% include 'includes/search_panel.html' %}}
    </div>
  </div>
    {{% endblock content %}}
    {{% block javascripts %}} {{% endblock javascripts %}}
  </div>
</div>
    '''.format(model=model["name"], lower=lower)
    str += "\n\n"
    return str


def setEditTemplate(model):
    lower = model["name"].lower()
    names = []
    for name, type in model["attributes"].items():
        names.append("{% render_field form."+name+" %}")
    fieldNames = ",\n ***".join(names)
    fieldNames = fieldNames.replace('***', s4)
    str = '''{{% extends 'obj_edit.html' %}}
{{% load form_helpers %}}
{{% block form %}}
<div class="panel panel-default">
  <div class="card-header">
    <h3 class="card-title">{model}</h3>
  </div>
  <div class="card-body">
    {formFields}
  </div>
</div>
{{% endblock %}}
    '''.format(model=model["name"], formFields=fieldNames, lower=lower)
    str += "\n\n"
    return str


def createDir(path):
    current_directory = os.getcwd()
    p = os.path.join(current_directory, path)
    if os.path.exists(p) != True:
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)


def genTemplates():
    createDir("templates")
    for model in models:
        lower = model["name"].lower()+"s"
        dir = os.path.join("templates", lower)
        createDir(dir)
        for k, v in templates["funcName"].items():
            templates["result"][k] = globals()[v](model)
            filePath = os.path.join(dir, k + ".html")
            f = open(filePath, "w")
            f.write(templates["result"][k])
            f.close()


def setModels():
    f = open("models.py", "r")
    lastkey = 0
    ignore = False
    lines = f.readlines()
    for line in lines:
        wline = line.strip()
        if wline.startswith('#'):
            continue
        if wline.startswith('class') and not wline.startswith('class Meta'):
            obj = {
                "name": "",
                "attributes": {},
                "tableName": "",
            }
            className = wline.split("class ", 1)[1].split("(", 1)[0]
            obj["name"] = className
            models.append(obj)
            lastkey = len(models)-1
            continue
        if wline.startswith('class Meta'):
            ignore = True
            continue
        if ignore == True and "db_table" in wline:
            table = wline.split("=", 1)[1]
            models[lastkey]["tableName"] = table
            continue
        if "=" not in wline:
            ignore = False
        if ignore == False and "=" in wline:
            fieldName = wline.split("=", 1)[0].split("(", 1)[0]
            type = "char"
            if "IntegerField" in wline:
                type = "int"
            elif "ForeignKey" in wline:
                type = "foreign"
            models[lastkey]["attributes"][fieldName] = type
    f.close()
    # json_mylist = json.dumps(models, separators=(',', ':'))
    # f = open("tets.py", "w")
    # f.write(json_mylist)
    # f.close()


def generate():
    setModels()
    setStrings()
    for key, value in functions.items():
        print(key)
        f = open(key+".py", "w")
        f.write(value["result"])
        f.close()
    genTemplates()


generate()
