from django.shortcuts import render,redirect

from rest_framework import status
from rest_framework import response
from django.core.urlresolvers import reverse
from django.template import loader

import pyrebase
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from .forms import LoginForm,ProjectForm,InventoryForm


config = {
    "apiKey": "AIzaSyBhNfOC3Grp4EtYcptjssBwal6LDpSRJW8",
    "authDomain": "builder-f0eb2.firebaseapp.com",
    "databaseURL": "https://builder-f0eb2.firebaseio.com",
   # "projectId": "builder-f0eb2",
    "storageBucket": "builder-f0eb2.appspot.com",
    "serviceAccount": "/home/mukul/restfirst/djangorest/djangorest/bob.json"

  };
firebase=pyrebase.initialize_app(config)
auth=firebase.auth();
#auth.sign_in_with_email_and_password("mukulkathpalia@gmail.com","")
db = firebase.database()
def login(request):
    if request.method == 'GET':
        idToken = request.COOKIES.get('idToken')
        if idToken:
            info = auth.get_account_info(idToken)
            if info:
                return redirect(reverse('projects'))

        context = {'f': LoginForm()};
        return render(request, 'login.html', context);
    else:
        f = LoginForm(request.POST);
        if not f.is_valid():
            return render(request, 'login.html', {'f': f});
        else:
            email = f.cleaned_data['email']
            password = f.cleaned_data['password']
            user = auth.sign_in_with_email_and_password(email, password)
            # response = (request,'index.html')  # django.http.HttpResponse
            response = redirect(reverse('projects', kwargs={}));

            response.set_cookie(key='idToken', value=user['idToken'])
            return response


def get_projects(request):
    idToken = request.COOKIES.get('idToken')

    if idToken == None:
        return Http404
    info = auth.get_account_info(idToken)
    localId = info["users"][0]["localId"]
    data = db.child("Builder").child(localId).get(idToken).val()
    projectIds = data['ProjectIDs'].values()
    projects_list = []
    for each in projectIds:
        k = db.child("Projects").child(str(each)).get(idToken).val()
        projects_list.append(k)
    context = {
        "projects_list": projects_list,
        "builderId": localId
    }
    return render(request, 'projects.html', context)


def logout(request):
    response = redirect(reverse('login'))
    response.delete_cookie('idToken')
    return response


def project(request, id=None):
    idToken = request.COOKIES.get('idToken')
    if idToken == None:
        return Http404
    k = db.child("Projects").child(str(id)).get(idToken).val()
    colors = ["#b87333", "silver", "gold", "#e5e4e2", "red", "green", "blue", "yellow"]
    base_array = ["Item", "Qty", {"role": "style"}]
    return_array = []
    # return_array.append(base_array)
    all_agents = db.child("Inventory").get(idToken).val()
    all_agents = dict(all_agents)
    i = 0
    # print(all_agents)
    for value in all_agents.values():
        print(value, "#########")
        temp = []
        temp.append(value["inventoryName"])
        temp.append(value["inventoryQty"])
        temp.append(colors[i])
        i = i + 1
        if (i == 8):
            i = 0
        return_array.append(temp)
    # print(str(return_array).replace("'", ""))
    context = {
        "project": k,
        "projectID": id,
        "chart_array": return_array
    }
    return render(request, 'project.html', context)


@require_http_methods(['GET', 'POST'])
def add_project(request, builderId=None):
    idToken = request.COOKIES.get('idToken')
    if idToken == None:
        return Http404
    if builderId == None:
        return Http404
    if request.method == 'GET':
        context = {'f': ProjectForm(), 'builderId': builderId}
        return render(request, 'add_project.html', context)
    else:
        f = ProjectForm(request.POST)
        if not f.is_valid():
            return render(request, 'add_project.html', {'f': f})
        else:
            address = f.cleaned_data['address']
            current_expenses = f.cleaned_data['current_expenses']
            total_budget = f.cleaned_data['total_budget']
            name = f.cleaned_data['name']
            builderId = str(builderId)
            projct = {"name": name, "address": address, "currentExpenses": current_expenses, "builderId": builderId,
                      "totalBudget": total_budget}
            p = db.child("Projects").push(projct, idToken)
            p = p["name"]
            db.child("Projects").child(p).update({"projectID": p}, idToken)
            data = db.child("Builder").child(str(builderId)).get(idToken).val()
            projectIds = data['ProjectIDs']
            projectIds.update({p: p})
            db.child("Builder").child(str(builderId)).update({"ProjectIDs": projectIds}, idToken)
            return redirect(reverse('projects'))


def get_inventories(request, projectID=None):
    idToken = request.COOKIES.get('idToken')
    if idToken == None:
        return Http404
    if projectID == None:
        return Http404
    data = db.child("Projects").child(str(projectID)).get(idToken).val()
    print(data)
    if not "inventoryIDs" in data:
        raise Http404
    inventoryIDs = data["inventoryIDs"]
    inventory_list = []
    inventories = inventoryIDs
    for each in inventories:
        data1 = db.child("Inventory").child(each).get(idToken).val()
        inventory_list.append(data1)
    print(inventory_list)
    return render(request, 'inventory_list.html', {'inventory_list': inventory_list, "projectID": projectID})


@require_http_methods(['GET', 'POST'])
def add_inventory(request, projectID=None):
    idToken = request.COOKIES.get('idToken')
    if idToken == None:
        return Http404
    if projectID == None:
        return Http404
    if request.method == 'GET':
        context = {'f': InventoryForm(), "projectID": projectID}
        return render(request, 'add_inventory.html', context)
    if request.method == 'POST':
        f = InventoryForm(request.POST)
        if not f.is_valid():
            return render(request, 'add_inventory.html', {'f': f, "projectID": projectID})
        else:
            inventoryName = f.cleaned_data['inventory_name']
            inventoryQty = f.cleaned_data['inventory_qty']
            invent = {'inventoryName': inventoryName, 'inventoryQty': inventoryQty}
            invent = db.child("Inventory").push(invent, idToken)
            invent = invent['name']
            db.child("Inventory").child(str(invent)).update({"inventoryId": invent}, idToken)

            data = db.child("Projects").child(str(projectID)).get(idToken).val()
            inventoryIDs = data["inventoryIDs"]
            # append_invent=db.child("Inventory").child(str(invent)).get(idToken).val()
            inventoryIDs.append(invent)
            db.child("Projects").child(str(projectID)).update({"inventoryIDs": inventoryIDs}, idToken)
            return redirect(reverse('inventories', kwargs={"projectID": projectID}))


'''@require_http_methods(['GET', 'POST'])
def add_transaction(request,inventoryId=None,projectID=None):
	idToken=request.COOKIES.get('idToken')
	if idToken==None:
		return Http404
	if inventoryId==None:
		raise Http404
	if transactionId==None:
		raise Http404
	if request.method=='GET':
		f=TransactionForm()
		context={"f":f,'inventoryId':inventoryId,'builderId':transactionId,'projectID':}
		return render(request,'add_transaction.html'.context)
	if request.method=='POST':
		if not f.is_valid():
			return render(request,'add_transaction.html','transactionId':transactionId)
		comment=f.cleaned_data['comment']
		creatorID=str(builderId)
		delta=f.cleaned_data['delta']
		inventoryID=str(inventoryId)
		type=f.cleaned_data['inc_dec']
		data1 = db.child("Inventory").child(str(inventoryID)).get(idToken).val()
		data2 = db.child("Projects").child(str(projectID)).get(idToken).val()
		builderId=data2['builderID']
		trans={'comment':comment,'creatorID':builderId,'delta':delta,'inventoryID':inventoryID,'type':type}

		qty=int(data1["inventoryQty"])
		if(type==0):
			qty=qty-delta
		else:
			qty=qty+delta
		invent=db.child("Transaction").push(trans, idToken)
		invent=invent["name"]
		db.child("Inventory").child(str(inventoryId)).update({"inventoryQty":qty},idToken)
		db.child("Transaction").child(str(invent)).update({"transactionID": str(invent)},idToken)
		return redirect(reverse("inventories",kwargs={"projectID":projectID}))'''


"""def send_msg(request, contractor=None):
    body = loader.render_to_string('msg.txt', {'contractor': contractor})

    client.messages.create(to="+918587072927",
                           from_="+13312562601",
                           body=body)
    return JsonResponse({'status': 'sucess'})

# client.messages.create(to="+919582020023",from="+13312562601",body=body)


"""


# Create your views here.
